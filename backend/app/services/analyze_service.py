from __future__ import annotations

import hashlib
import json
import math
import os
import time
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

from app.db.mongo import get_db
from app.models.incident_model import INCIDENT_SEVERITIES
from app.schemas.incident_schema import AIReport

try:
    from google import genai
except Exception:  # pragma: no cover
    genai = None


# ----------------------------
# Config
# ----------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Use stable model names when possible to avoid preview-only limits/changes.
# Adjust if your team has standardized a different one.
GEMINI_GENERATION_MODEL = os.getenv("GEMINI_GENERATION_MODEL", "gemini-2.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

# Keep retrieval small to reduce prompt size.
TOP_K_DOCS = int(os.getenv("RAG_TOP_K_DOCS", "3"))
MAX_LOGS_FOR_ANALYSIS = int(os.getenv("MAX_LOGS_FOR_ANALYSIS", "5"))
MAX_EVIDENCE_ITEMS = int(os.getenv("MAX_EVIDENCE_ITEMS", "3"))

# Small in-process cooldown to reduce hammering Gemini after 429s.
_RATE_LIMIT_UNTIL = 0.0


# ----------------------------
# Helpers
# ----------------------------

def parse_object_id(value: str, field_name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return -1.0

    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return -1.0

    return dot / (norm1 * norm2)


def safe_json_loads(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="Model returned invalid JSON. Analysis was not saved."
        )


def build_incident_fingerprint(incident: dict, logs: list[dict], device: dict | None) -> str:
    payload = {
        "incident_id": str(incident.get("_id")),
        "severity": incident.get("severity"),
        "status": incident.get("status"),
        "device_id": str(device.get("_id")) if device else None,
        "device_hostname": device.get("hostname") if device else None,
        "logs": [
            {
                "id": str(log.get("_id")),
                "timestamp": str(log.get("timestamp")),
                "level": log.get("log_level"),
                "message": log.get("message"),
            }
            for log in logs
        ],
    }
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        value = (item or "").strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def summarize_logs_for_prompt(logs: list[dict]) -> str:
    lines = []
    for idx, log in enumerate(logs[:MAX_LOGS_FOR_ANALYSIS], start=1):
        lines.append(
            f"{idx}. [{log.get('timestamp')}] "
            f"level={log.get('log_level')} "
            f"message={log.get('message')}"
        )
    return "\n".join(lines)


def build_incident_query_text(incident: dict, logs: list[dict], device: dict | None) -> str:
    device_text = ""
    if device:
        device_text = (
            f"Device hostname: {device.get('hostname')}\n"
            f"Device IP: {device.get('ip_address')}\n"
            f"Device type: {device.get('type')}\n"
            f"Device location: {device.get('location')}\n"
            f"Device status: {device.get('status')}\n"
        )

    logs_text = summarize_logs_for_prompt(logs)

    return (
        f"Incident severity: {incident.get('severity')}\n"
        f"Incident status: {incident.get('status')}\n"
        f"{device_text}"
        f"Linked logs:\n{logs_text}"
    ).strip()


def get_genai_client():
    if not GEMINI_API_KEY:
        return None
    if genai is None:
        return None
    return genai.Client(api_key=GEMINI_API_KEY)


def embed_text(text: str) -> list[float] | None:
    """
    One embedding call per analyze request.
    Returns None if Gemini is unavailable so we can still fall back safely.
    """
    client = get_genai_client()
    if client is None:
        return None

    global _RATE_LIMIT_UNTIL
    now = time.time()
    if now < _RATE_LIMIT_UNTIL:
        return None

    try:
        response = client.models.embed_content(
            model=GEMINI_EMBEDDING_MODEL,
            contents=text,
        )

        # Different SDK versions may shape this slightly differently.
        # Handle the common structure.
        if hasattr(response, "embeddings") and response.embeddings:
            first = response.embeddings[0]
            if hasattr(first, "values"):
                return list(first.values)

        if hasattr(response, "embedding") and hasattr(response.embedding, "values"):
            return list(response.embedding.values)

        return None

    except Exception as exc:
        msg = str(exc).lower()
        if "429" in msg or "rate" in msg or "quota" in msg:
            _RATE_LIMIT_UNTIL = time.time() + 30
            return None
        return None


def retrieve_top_k_docs(db, query_embedding: list[float] | None, k: int = TOP_K_DOCS) -> list[dict]:
    """
    Cheap retrieval path:
    - assumes your KB docs collection already contains stored embeddings
    - does local cosine similarity in Python
    - no extra Gemini calls here
    """
    if not query_embedding:
        return []

    docs = list(db.knowledge_base.find({}, {"content": 1, "title": 1, "embedding": 1}))
    scored = []

    for doc in docs:
        embedding = doc.get("embedding")
        if not isinstance(embedding, list):
            continue

        score = cosine_similarity(query_embedding, embedding)
        scored.append(
            {
                "title": doc.get("title", "Untitled"),
                "content": doc.get("content", ""),
                "score": score,
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:k]


def build_prompt(incident: dict, logs: list[dict], device: dict | None, retrieved_docs: list[dict]) -> str:
    incident_context = build_incident_query_text(incident, logs, device)

    docs_text = "\n\n".join(
        [
            f"Document {idx} - {doc['title']}:\n{doc['content'][:1200]}"
            for idx, doc in enumerate(retrieved_docs, start=1)
        ]
    ).strip()

    return f"""
You are analyzing a network operations incident.

Rules:
- Use only the provided logs, device metadata, and retrieved documents.
- Do not invent facts.
- If something is uncertain, state it in uncertainties.
- Return JSON only.
- Severity must be one of: low, medium, high, critical.
- recommended_actions, supporting_evidence, uncertainties, and follow_up_questions must be arrays of strings.

Incident context:
{incident_context}

Retrieved knowledge:
{docs_text if docs_text else "No retrieved knowledge documents were available."}

Return exactly this JSON shape:
{{
  "summary": "string",
  "probable_cause": "string",
  "severity": "low|medium|high|critical",
  "recommended_actions": ["string"],
  "supporting_evidence": ["string"],
  "uncertainties": ["string"],
  "follow_up_questions": ["string"]
}}
""".strip()


def generate_ai_report(prompt: str) -> dict[str, Any] | None:
    """
    One generation call per analyze request.
    Returns None on rate-limit or availability issues so caller can fallback safely.
    """
    client = get_genai_client()
    if client is None:
        return None

    global _RATE_LIMIT_UNTIL
    now = time.time()
    if now < _RATE_LIMIT_UNTIL:
        return None

    try:
        response = client.models.generate_content(
            model=GEMINI_GENERATION_MODEL,
            contents=prompt,
        )

        text = getattr(response, "text", None)
        if not text:
            return None

        return safe_json_loads(text)

    except Exception as exc:
        msg = str(exc).lower()
        if "429" in msg or "rate" in msg or "quota" in msg:
            _RATE_LIMIT_UNTIL = time.time() + 30
            return None
        return None


def build_local_fallback_report(incident: dict, logs: list[dict], retrieved_docs: list[dict]) -> dict[str, Any]:
    evidence = dedupe_preserve_order([str(log.get("message", "")) for log in logs])[:MAX_EVIDENCE_ITEMS]

    summary = (
        f"Fallback analysis based on linked logs: "
        f"{evidence[0] if evidence else 'Operational issue requires review'}"
    )

    doc_titles = [doc.get("title", "Untitled") for doc in retrieved_docs[:2]]

    return {
        "summary": summary,
        "probable_cause": (
            "Linked logs and available troubleshooting guidance suggest a possible "
            "network, interface, or service issue requiring operator review."
        ),
        "severity": incident.get("severity") if incident.get("severity") in INCIDENT_SEVERITIES else "medium",
        "recommended_actions": [
            "Review the most recent linked logs for repeated patterns",
            "Verify device reachability, interface state, and recent changes",
            "Escalate to an operator if the issue persists or affects production traffic",
        ],
        "supporting_evidence": evidence or ["No usable linked log evidence was available"],
        "uncertainties": [
            "AI generation was unavailable or rate-limited, so this report used fallback logic",
            "Root cause is not fully confirmed from linked logs alone",
        ],
        "follow_up_questions": [
            "Did the device have any recent configuration changes?",
            "Are similar alerts occurring on related devices or interfaces?",
        ] + ([f"Should the operator review guidance from: {', '.join(doc_titles)}?"] if doc_titles else []),
    }


def validate_report(report_data: dict[str, Any]) -> dict[str, Any]:
    validated = AIReport(**report_data)

    if validated.severity not in INCIDENT_SEVERITIES:
        raise HTTPException(
            status_code=502,
            detail="Model returned an invalid severity value. Analysis was not saved."
        )

    return validated.model_dump()


def fetch_linked_logs(db, linked_logs: list[str]) -> list[dict]:
    logs = []
    for log_id in linked_logs:
        try:
            log_object_id = parse_object_id(log_id, "log_id")
            log = db.logs.find_one({"_id": log_object_id})
            if log:
                logs.append(log)
        except HTTPException:
            continue

    # newest first if timestamps exist
    logs.sort(key=lambda item: str(item.get("timestamp", "")), reverse=True)
    return logs[:MAX_LOGS_FOR_ANALYSIS]


def fetch_device_for_logs(db, logs: list[dict]) -> dict | None:
    """
    Best-effort lookup: if your logs have device_id, use the first valid one.
    """
    for log in logs:
        device_id = log.get("device_id")
        if not device_id:
            continue
        try:
            device_object_id = parse_object_id(device_id, "device_id")
            return db.devices.find_one({"_id": device_object_id})
        except HTTPException:
            continue
    return None


# ----------------------------
# Main service
# ----------------------------

def analyze_incident(incident_id: str):
    db = get_db()

    incident_object_id = parse_object_id(incident_id, "incident_id")
    incident = db.incidents.find_one({"_id": incident_object_id})
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    linked_logs = incident.get("linked_logs", [])
    logs = fetch_linked_logs(db, linked_logs)

    if not logs:
        raise HTTPException(status_code=400, detail="No linked logs found for analysis")

    device = fetch_device_for_logs(db, logs)
    fingerprint = build_incident_fingerprint(incident, logs, device)

    # Return cached result if same context was already analyzed.
    existing_report = incident.get("ai_report")
    existing_fingerprint = incident.get("analysis_fingerprint")
    if existing_report and existing_fingerprint == fingerprint:
        return existing_report

    # One embedding call only.
    query_text = build_incident_query_text(incident, logs, device)
    query_embedding = embed_text(query_text)

    # Retrieval is local.
    retrieved_docs = retrieve_top_k_docs(db, query_embedding, TOP_K_DOCS)

    # One generation call only.
    prompt = build_prompt(incident, logs, device, retrieved_docs)
    generated = generate_ai_report(prompt)

    if generated is None:
        report_data = build_local_fallback_report(incident, logs, retrieved_docs)
    else:
        report_data = generated

    validated = validate_report(report_data)

    db.incidents.update_one(
        {"_id": incident_object_id},
        {
            "$set": {
                "ai_report": validated,
                "analysis_fingerprint": fingerprint,
                "analysis_generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "analysis_source": "gemini" if generated is not None else "fallback",
                "retrieved_doc_titles": [doc["title"] for doc in retrieved_docs],
            }
        },
    )

    return validated