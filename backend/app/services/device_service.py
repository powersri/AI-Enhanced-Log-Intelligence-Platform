from fastapi import HTTPException

from app.db.mongo import get_db, parse_object_id
from app.models.device_model import DEVICE_STATUSES
from app.schemas.device_schema import DeviceCreate, DeviceUpdate


def create_device(payload: DeviceCreate):
    status_value = payload.status.lower()

    if status_value not in DEVICE_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid device status")

    doc = payload.model_dump()
    doc["ip_address"] = str(payload.ip_address)
    doc["status"] = status_value

    result = get_db().devices.insert_one(doc)

    return {
        "id": str(result.inserted_id),
        "hostname": doc["hostname"],
        "ip_address": doc["ip_address"],
        "type": doc["type"],
        "location": doc["location"],
        "status": doc["status"],
    }


def list_devices():
    items = []
    for device in get_db().devices.find():
        items.append({
            "id": str(device["_id"]),
            "hostname": device["hostname"],
            "ip_address": device["ip_address"],
            "type": device["type"],
            "location": device["location"],
            "status": device["status"],
        })
    return items


def get_device(device_id: str):
    device_object_id = parse_object_id(device_id)
    device = get_db().devices.find_one({"_id": device_object_id})

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "id": str(device["_id"]),
        "hostname": device["hostname"],
        "ip_address": device["ip_address"],
        "type": device["type"],
        "location": device["location"],
        "status": device["status"],
    }


def update_device(device_id: str, payload: DeviceUpdate):
    device_object_id = parse_object_id(device_id)
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    if "ip_address" in update_data:
        update_data["ip_address"] = str(update_data["ip_address"])

    if "status" in update_data:
        update_data["status"] = update_data["status"].lower()
        if update_data["status"] not in DEVICE_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid device status")

    result = get_db().devices.update_one(
        {"_id": device_object_id},
        {"$set": update_data},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")

    return get_device(device_id)


def delete_device(device_id: str):
    device_object_id = parse_object_id(device_id)
    result = get_db().devices.delete_one({"_id": device_object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")

    return {"deleted": True}