# NetOps Copilot 2026 Backend

A FastAPI + MongoDB backend for network operations, device management, log ingestion, incident tracking, and AI-powered analysis. Features JWT authentication, role-based access control (RBAC), and a full REST API for managing devices, logs, and incidents.

---

## 1. Project Overview

**NetOps Copilot 2026** is a backend service for:
- Managing network devices
- Ingesting and querying logs
- Tracking and analyzing incidents
- Authenticating users with JWT tokens
- Enforcing RBAC (admin, operator, viewer)
- Placeholder AI analysis for incidents

**Tech stack:**
- [FastAPI](https://fastapi.tiangolo.com/) (Python web framework)
- [MongoDB](https://www.mongodb.com/) (NoSQL database)
- JWT authentication
- Role-based access control (RBAC)

---

## 2. Setup Instructions in VS Code

1. **Open the project in VS Code**
   - Use `File > Open Folder...` and select the backend folder.

2. **Open a terminal**
   - `Terminal > New Terminal` (bottom panel)

3. **Move into the backend folder**
   ```sh
   cd AI-Enhanced-Log-Intelligence-Platform-main/backend
   ```

4. **Create a virtual environment**
   ```sh
   python -m venv .venv
   ```

5. **Activate the virtual environment (Windows)**
   ```sh
   .venv\Scripts\activate
   ```

6. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

7. **Create a `.env` file**
   - In the backend folder, create a file named `.env` (see sample below).

8. **Run the backend with Uvicorn**
   ```sh
   uvicorn app.main:app --reload
   ```

9. **Open Swagger docs**
   - Go to [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

---

## 3. Environment Variables

Create a `.env` file in the backend folder with the following (use only safe placeholders):

```env
MONGODB_URL=YOUR_MONGODB_URL_HERE
JWT_SECRET=YOUR_JWT_SECRET_HERE
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY =
```

- **MongoDB**: Must be running locally (default: `mongodb://localhost:27017`) or use an Atlas URI.
- **Never commit real secrets to GitHub.**

---

## 4. Swagger Authentication Flow

1. **Register a user**
   - Use `POST /auth/register` with a JSON body (see below).
2. **Login**
   - Use `POST /auth/login` with your credentials.
3. **Copy the access token**
   - From the login response, copy the `access_token` value.
4. **Authorize in Swagger**
   - Click the `Authorize` button in Swagger UI.
   - Enter:
     ```
     Bearer YOUR_ACCESS_TOKEN_HERE
     ```
   - Click `Authorize` to apply the token to all requests.

---

## 5. Full Endpoint Testing Order

Recommended test flow:

1. `GET /` (welcome)
2. `GET /health` (health check)
3. `POST /auth/register` (create user)
4. `POST /auth/login` (get token)
5. `GET /auth/me` (get current user info)
6. `POST /devices` (add device)
7. `GET /devices` (list devices)
8. `GET /devices/{device_id}` (get device)
9. `PUT /devices/{device_id}` (update device)
10. `POST /logs/ingest` (add log)
11. `GET /logs` (list logs)
12. `GET /logs/{log_id}` (get log)
13. `POST /incidents` (create incident)
14. `GET /incidents` (list incidents)
15. `GET /incidents/{incident_id}` (get incident)
16. `POST /incidents/{incident_id}/link-log/{log_id}` (link log)
17. `POST /incidents/{incident_id}/analyze` (AI analysis)
18. `GET /incidents/{incident_id}` (verify ai_report)

---

## 6. Endpoint Templates

**Register User** (`POST /auth/register`)
```json
{
  "username": "your_username",
  "password": "your_password",
  "role": "operator"
}
```

**Login** (`POST /auth/login`)
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Create Device** (`POST /devices`)
```json
{
  "name": "Router 1",
  "ip_address": "192.168.1.1",
  "status": "up"
}
```

**Update Device** (`PUT /devices/{device_id}`)
```json
{
  "name": "Router 1A",
  "ip_address": "192.168.1.10",
  "status": "maintenance"
}
```

**Create Log** (`POST /logs/ingest`)
```json
{
  "device_id": "PASTE_DEVICE_ID_HERE",
  "level": "info",
  "message": "Device started successfully."
}
```

**Create Incident** (`POST /incidents`)
```json
{
  "title": "Network Outage",
  "description": "No connectivity in building A.",
  "severity": "high",
  "status": "open"
}
```

---

## 7. Validation Reference

- **Device statuses:** `up`, `down`, `warning`, `maintenance`
- **Log levels:** `debug`, `info`, `warning`, `error`, `critical`
- **Incident statuses:** `open`, `investigating`, `resolved`
- **Incident severities:** `low`, `medium`, `high`, `critical`
- **Roles:** `admin`, `operator`, `viewer`

---

## 8. Incident Workflow Explanation

1. **Create an incident** (`POST /incidents`)
2. **Create a log** (`POST /logs/ingest`)
3. **Link the log to the incident** (`POST /incidents/{incident_id}/link-log/{log_id}`)
4. **Analyze the incident** (`POST /incidents/{incident_id}/analyze`)
   - This triggers placeholder AI analysis and saves an `ai_report` to the incident.
5. **Verify the AI report** (`GET /incidents/{incident_id}`)
   - Check that the `ai_report` field is present in the response.

## - example of a rag workflow - explain how rag works with the KB and produce 
---

## 9. RBAC Summary

- **admin**: Full access to all endpoints and actions
- **operator**: Can manage devices, logs, incidents, but not user management
- **viewer**: Can view devices, logs, incidents, but cannot create or modify

---

## 10. Troubleshooting

- **401 Unauthorized**: Make sure you added the JWT token using the Swagger Authorize button.
- **MongoDB not running**: Ensure MongoDB is running locally or update `MONGODB_URL` to a valid Atlas URI.
- **Invalid status or log level**: Use only the allowed values listed above.
- **Invalid ObjectId**: Use valid MongoDB ObjectId strings for device, log, or incident IDs.
- **Uvicorn import/module errors**: Make sure you are in the correct backend folder when running `uvicorn app.main:app --reload`.
- **Module import issues**: Check your Python environment and that all dependencies are installed.

---

## 11. Quick Start Summary

1. Clone or download the project
2. Open the backend folder in VS Code
3. Open a terminal and create/activate a virtual environment
4. Install requirements: `pip install -r requirements.txt`
5. Create a `.env` file with safe placeholder values
6. Start MongoDB locally or use an Atlas URI
7. Run the backend: `uvicorn app.main:app --reload`
8. Open [http://localhost:8000/docs](http://localhost:8000/docs) and start testing endpoints in order

---

**Enjoy building with NetOps Copilot 2026!**

*For educational use only. Do not use real secrets or production data.*
