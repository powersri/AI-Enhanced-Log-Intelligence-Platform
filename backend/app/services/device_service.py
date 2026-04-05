
# Import ObjectId and error for MongoDB ID validation
from bson import ObjectId
from bson.errors import InvalidId
# Import FastAPI exception for error handling
from fastapi import HTTPException
# Import database connection utility
from app.db.mongo import get_db
# Import valid device statuses
from app.models.device_model import DEVICE_STATUSES
# Import device schema classes
from app.schemas.device_schema import DeviceCreate, DeviceUpdate



# Helper function to safely parse a string as a MongoDB ObjectId
# Raises HTTP 400 if invalid
def parse_object_id(value: str, field_name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")



# Create a new device in the database
def create_device(payload: DeviceCreate):
    # Validate the device status
    if payload.status not in DEVICE_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid device status")

    # Convert the payload to a dictionary and ensure IP is a string
    doc = payload.model_dump()
    doc["ip_address"] = str(payload.ip_address)

    # Insert the device document into the database
    result = get_db().devices.insert_one(doc)

    # Return the public device info
    return {
        "id": str(result.inserted_id),
        "hostname": doc["hostname"],
        "ip_address": doc["ip_address"],
        "type": doc["type"],
        "location": doc["location"],
        "status": doc["status"],
    }



# List all devices in the database
def list_devices():
    items = []
    # Iterate over all device documents and build a list of public info
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



# Get a single device by its ID
def get_device(device_id: str):
    device_object_id = parse_object_id(device_id, "device_id")
    device = get_db().devices.find_one({"_id": device_object_id})
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Return the public device info
    return {
        "id": str(device["_id"]),
        "hostname": device["hostname"],
        "ip_address": device["ip_address"],
        "type": device["type"],
        "location": device["location"],
        "status": device["status"],
    }



# Update an existing device by its ID
def update_device(device_id: str, payload: DeviceUpdate):
    device_object_id = parse_object_id(device_id, "device_id")
    # Only include fields that are not None
    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

    # Ensure IP address is stored as a string
    if "ip_address" in update_data:
        update_data["ip_address"] = str(update_data["ip_address"])

    # Validate the device status if provided
    if "status" in update_data and update_data["status"] not in DEVICE_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid device status")

    # Update the device document in the database
    result = get_db().devices.update_one(
        {"_id": device_object_id},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")

    # Return the updated device info
    return get_device(device_id)



# Delete a device by its ID
def delete_device(device_id: str):
    device_object_id = parse_object_id(device_id, "device_id")
    result = get_db().devices.delete_one({"_id": device_object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")

    # Return confirmation of deletion
    return {"deleted": True}