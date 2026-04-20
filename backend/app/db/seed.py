from datetime import datetime, timezone

from app.db.mongo import db
from app.auth.password import hash_password


def seed_users():
    if db.users.count_documents({}) == 0:
        users = [
            {
                "email": "admin@test.com",
                "password": hash_password("admin123"),
                "role": "admin",
            },
            {
                "email": "operator@test.com",
                "password": hash_password("operator123"),
                "role": "operator",
            },
            {
                "email": "viewer@test.com",
                "password": hash_password("viewer123"),
                "role": "viewer",
            },
        ]
        db.users.insert_many(users)
        print("Users seeded")


def seed_devices():
    if db.devices.count_documents({}) == 0:
        devices = [
            {
                "hostname": "router-1",
                "ip_address": "192.168.1.1",
                "type": "router",
                "location": "Data Center",
                "status": "up",
            },
            {
                "hostname": "switch-1",
                "ip_address": "192.168.1.2",
                "type": "switch",
                "location": "Office",
                "status": "warning",
            },
        ]
        db.devices.insert_many(devices)
        print("Devices seeded")


def seed_logs():
    if db.logs.count_documents({}) == 0:
        devices = list(db.devices.find())
        if not devices:
            return

        logs = [
            {
                "device_id": devices[0]["_id"],
                "timestamp": datetime.now(timezone.utc),
                "log_level": "error",
                "message": "Interface down on port Gig0/1",
            },
            {
                "device_id": devices[1]["_id"],
                "timestamp": datetime.now(timezone.utc),
                "log_level": "warning",
                "message": "High CPU usage detected",
            },
        ]
        db.logs.insert_many(logs)
        print("Logs seeded")


def seed_all():
    seed_users()
    seed_devices()
    seed_logs()


if __name__ == "__main__":
    seed_all()