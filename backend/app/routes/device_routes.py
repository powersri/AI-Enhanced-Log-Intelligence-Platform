from fastapi import APIRouter, Depends
from app.schemas.common import APIResponse
from app.schemas.device_schema import DeviceCreate, DeviceUpdate
from app.services.device_service import create_device, list_devices, get_device, update_device, delete_device
from app.dependencies import get_current_user
from app.auth.rbac import require_role


router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("", response_model=APIResponse)
def create_device_route(payload: DeviceCreate, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin"])
    item = create_device(payload)
    return APIResponse(success=True, message="Device created successfully", data=item)


@router.get("", response_model=APIResponse)
def list_devices_route(current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator", "viewer"])
    return APIResponse(success=True, message="Devices fetched successfully", data=list_devices())


@router.get("/{device_id}", response_model=APIResponse)
def get_device_route(device_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin", "operator", "viewer"])
    return APIResponse(success=True, message="Device fetched successfully", data=get_device(device_id))


@router.put("/{device_id}", response_model=APIResponse)
def update_device_route(device_id: str, payload: DeviceUpdate, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin"])
    return APIResponse(success=True, message="Device updated successfully", data=update_device(device_id, payload))


@router.delete("/{device_id}", response_model=APIResponse)
def delete_device_route(device_id: str, current_user: dict = Depends(get_current_user)):
    require_role(current_user["role"], ["admin"])
    return APIResponse(success=True, message="Device deleted successfully", data=delete_device(device_id))
