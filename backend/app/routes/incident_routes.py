from fastapi import APIRouter, Depends
from app.schemas.common import APIResponse
from app.schemas.incident_schema import IncidentCreate
from app.services.incident_service import create_incident, list_incidents, get_incident, link_log_to_incident
from app.services.analyze_service import analyze_incident
from app.dependencies import get_current_user
from app.auth.rbac import require_role


router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", response_model=APIResponse)
def create_incident_route(payload: IncidentCreate, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator"])
    return APIResponse(
        success=True,
        message="Incident created successfully",
        data=create_incident(payload, current_user),
    )


@router.get("", response_model=APIResponse)
def list_incidents_route(current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator", "viewer"])
    return APIResponse(success=True, message="Incidents fetched successfully", data=list_incidents())


@router.get("/{incident_id}", response_model=APIResponse)
def get_incident_route(incident_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator", "viewer"])
    return APIResponse(success=True, message="Incident fetched successfully", data=get_incident(incident_id))


@router.post("/{incident_id}/link-log/{log_id}", response_model=APIResponse)
def link_log_route(incident_id: str, log_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator"])
    return APIResponse(
        success=True,
        message="Log linked to incident successfully",
        data=link_log_to_incident(incident_id, log_id),
    )


@router.post("/{incident_id}/analyze", response_model=APIResponse)
def analyze_incident_route(incident_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator"])
    return APIResponse(
        success=True,
        message="Incident analyzed successfully",
        data=analyze_incident(incident_id),
    )
