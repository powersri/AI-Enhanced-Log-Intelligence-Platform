from fastapi import APIRouter, Depends
from app.schemas.common import APIResponse
from app.schemas.log_schema import LogIngest
from app.services.log_service import ingest_log, list_logs, get_log
from app.dependencies import get_current_user
from app.auth.rbac import require_role


router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/ingest", response_model=APIResponse)
def ingest_log_route(payload: LogIngest, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator"])
    return APIResponse(success=True, message="Log ingested successfully", data=ingest_log(payload))


@router.get("", response_model=APIResponse)
def list_logs_route(current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator"])
    return APIResponse(success=True, message="Logs fetched successfully", data=list_logs())


@router.get("/{log_id}", response_model=APIResponse)
def get_log_route(log_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator"])
    return APIResponse(success=True, message="Log fetched successfully", data=get_log(log_id))
