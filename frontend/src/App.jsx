import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  Container,
  Form,
  Row,
  Table,
} from "react-bootstrap";
import { apiFetch, API_BASE } from "./api";

function App() {
  const [health, setHealth] = useState("Checking backend...");
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [currentUser, setCurrentUser] = useState(null);

  const [loginForm, setLoginForm] = useState({
    username: "",
    password: "",
  });

  const [registerForm, setRegisterForm] = useState({
    full_name: "",
    email: "",
    password: "",
    role: "operator",
  });

  const [deviceForm, setDeviceForm] = useState({
    hostname: "",
    ip_address: "",
    type: "router",
    location: "",
    status: "up",
  });

  const [editingDeviceId, setEditingDeviceId] = useState("");

  const [logForm, setLogForm] = useState({
    device_id: "",
    log_level: "warning",
    message: "",
  });

  const [incidentForm, setIncidentForm] = useState({
    status: "open",
    severity: "low",
    linked_logs: [],
  });

  const [devices, setDevices] = useState([]);
  const [logs, setLogs] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedLogToLink, setSelectedLogToLink] = useState("");

  const [loadingDevices, setLoadingDevices] = useState(false);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [loadingIncidents, setLoadingIncidents] = useState(false);
  const [runningAnalysis, setRunningAnalysis] = useState(false);
  const [submittingLog, setSubmittingLog] = useState(false);
  const [submittingRegister, setSubmittingRegister] = useState(false);
  const [submittingDevice, setSubmittingDevice] = useState(false);
  const [submittingIncident, setSubmittingIncident] = useState(false);
  const [linkingLog, setLinkingLog] = useState(false);
  const [deletingDeviceId, setDeletingDeviceId] = useState("");
  const [selectedLog, setSelectedLog] = useState(null);

  useEffect(() => {
    checkHealth();
  }, []);

  useEffect(() => {
    if (token) {
      loadCurrentUser();
      loadDevices();
      loadLogs();
      loadIncidents();
    }
  }, [token]);

  async function checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/health`);
      setHealth(res.ok ? "Backend is running" : "Backend responded with an error");
    } catch {
      setHealth("Backend not reachable");
    }
  }

  function clearMessages() {
    setError("");
    setSuccessMessage("");
  }

  async function loadCurrentUser() {
    try {
      const data = await apiFetch("/auth/me");
      setCurrentUser(data.data || data);
    } catch (err) {
      setCurrentUser(null);
      setError(err.message);
    }
  }

  async function handleRegister(e) {
    e.preventDefault();
    clearMessages();
    setSubmittingRegister(true);

    try {
      await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify(registerForm),
      });

      setSuccessMessage("User registered successfully. You can now log in.");
      setRegisterForm({
        full_name: "",
        email: "",
        password: "",
        role: "operator",
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingRegister(false);
    }
  }

  async function handleLogin(e) {
    e.preventDefault();
    clearMessages();

    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: loginForm.username,
          password: loginForm.password,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        let errorMessage = "Login failed";

        if (typeof data.detail === "string") {
          errorMessage = data.detail;
        } else if (Array.isArray(data.detail)) {
          errorMessage = data.detail.map((item) => item.msg).join(", ");
        } else if (typeof data.message === "string") {
          errorMessage = data.message;
        }

        throw new Error(errorMessage);
      }

      const accessToken =
        data.access_token ||
        data.token ||
        data.data?.access_token ||
        data.data?.token;

      if (!accessToken) {
        throw new Error("No access token returned from login");
      }

      localStorage.setItem("token", accessToken);
      setToken(accessToken);
      setSuccessMessage("Login successful");
    } catch (err) {
      setError(err.message);
    }
  }

  function handleLogout() {
    localStorage.removeItem("token");
    setToken("");
    setCurrentUser(null);
    setDevices([]);
    setLogs([]);
    setIncidents([]);
    setSelectedIncident(null);
    setAnalysisResult(null);
    setSuccessMessage("Logged out");
    setError("");
  }

  async function loadDevices() {
    clearMessages();
    setLoadingDevices(true);

    try {
      const data = await apiFetch("/devices");
      setDevices(data.data || data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingDevices(false);
    }
  }

  async function loadLogs() {
    clearMessages();
    setLoadingLogs(true);

    try {
      const data = await apiFetch("/logs");
      setLogs(data.data || data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingLogs(false);
    }
  }

  async function openLog(logId) {
  clearMessages();

  try {
    const data = await apiFetch(`/logs/${logId}`);
    const log = data.data || data;
    setSelectedLog(log);
  } catch (err) {
    setError(err.message);
  }
}

  async function loadIncidents() {
    clearMessages();
    setLoadingIncidents(true);

    try {
      const data = await apiFetch("/incidents");
      setIncidents(data.data || data || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingIncidents(false);
    }
  }

  async function handleDeviceSubmit(e) {
    e.preventDefault();
    clearMessages();
    setSubmittingDevice(true);

    try {
      if (editingDeviceId) {
        await apiFetch(`/devices/${editingDeviceId}`, {
          method: "PUT",
          body: JSON.stringify(deviceForm),
        });
        setSuccessMessage("Device updated successfully");
      } else {
        await apiFetch("/devices", {
          method: "POST",
          body: JSON.stringify(deviceForm),
        });
        setSuccessMessage("Device created successfully");
      }

      setDeviceForm({
        hostname: "",
        ip_address: "",
        type: "router",
        location: "",
        status: "up",
      });
      setEditingDeviceId("");
      await loadDevices();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingDevice(false);
    }
  }

  function handleEditDevice(device) {
    setEditingDeviceId(device.id);
    setDeviceForm({
      hostname: device.hostname || "",
      ip_address: device.ip_address || "",
      type: device.type || "router",
      location: device.location || "",
      status: device.status || "up",
    });
  }

  async function handleDeleteDevice(deviceId) {
    clearMessages();
    setDeletingDeviceId(deviceId);

    try {
      await apiFetch(`/devices/${deviceId}`, {
        method: "DELETE",
      });
      setSuccessMessage("Device deleted successfully");
      await loadDevices();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingDeviceId("");
    }
  }

  async function submitLog(e) {
    e.preventDefault();
    clearMessages();
    setSubmittingLog(true);

    try {
      await apiFetch("/logs/ingest", {
        method: "POST",
        body: JSON.stringify(logForm),
      });

      setSuccessMessage("Log submitted successfully");
      setLogForm({
        device_id: "",
        log_level: "warning",
        message: "",
      });
      await loadLogs();
      await loadIncidents();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingLog(false);
    }
  }

  async function createIncident(e) {
    e.preventDefault();
    clearMessages();
    setSubmittingIncident(true);

    try {
      await apiFetch("/incidents", {
        method: "POST",
        body: JSON.stringify(incidentForm),
      });

      setSuccessMessage("Incident created successfully");
      setIncidentForm({
        status: "open",
        severity: "low",
        linked_logs: [],
      });
      await loadIncidents();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmittingIncident(false);
    }
  }

  async function openIncident(incidentId) {
    clearMessages();

    try {
      const data = await apiFetch(`/incidents/${incidentId}`);
      const incident = data.data || data;
      setSelectedIncident(incident);
      setAnalysisResult(incident.ai_report || null);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleLinkLog() {
    if (!selectedIncident || !selectedLogToLink) return;

    clearMessages();
    setLinkingLog(true);

    try {
      await apiFetch(`/incidents/${selectedIncident.id}/link-log/${selectedLogToLink}`, {
        method: "POST",
      });

      setSuccessMessage("Log linked to incident successfully");
      setSelectedLogToLink("");
      await openIncident(selectedIncident.id);
      await loadIncidents();
    } catch (err) {
      setError(err.message);
    } finally {
      setLinkingLog(false);
    }
  }

  async function runAnalysis() {
    if (!selectedIncident) return;

    clearMessages();
    setRunningAnalysis(true);

    try {
      const data = await apiFetch(`/incidents/${selectedIncident.id}/analyze`, {
        method: "POST",
      });

      const report = data.data || data;
      setAnalysisResult(report);
      setSuccessMessage("Incident analyzed successfully");

      await openIncident(selectedIncident.id);
      await loadIncidents();
    } catch (err) {
      setError(err.message);
    } finally {
      setRunningAnalysis(false);
    }
  }

  function severityVariant(severity) {
    const value = (severity || "").toLowerCase();
    if (value === "critical") return "danger";
    if (value === "high") return "warning";
    if (value === "medium") return "info";
    return "secondary";
  }

  const unlinkedLogs = useMemo(() => {
    if (!selectedIncident) return logs;
    const linkedIds = new Set((selectedIncident.linked_logs || []).map((log) => log.id));
    return logs.filter((log) => !linkedIds.has(log.id));
  }, [logs, selectedIncident]);

  function renderStringList(items) {
    if (!items?.length) return <p className="mb-0 text-muted">None</p>;
    return (
      <ul className="mb-0">
        {items.map((item, index) => (
          <li key={`${item}-${index}`}>{item}</li>
        ))}
      </ul>
    );
  }

  return (
    <Container fluid className="py-4 px-4">
      <Row className="mb-4">
        <Col>
          <h1 className="mb-1">NetOps Copilot 2026</h1>
          <p className="text-muted mb-0">{health}</p>
          <p className="text-muted small mb-0">API: {API_BASE}</p>
        </Col>
      </Row>

      {error && (
        <Row className="mb-3">
          <Col>
            <Alert variant="danger">{error}</Alert>
          </Col>
        </Row>
      )}

      {successMessage && (
        <Row className="mb-3">
          <Col>
            <Alert variant="success">{successMessage}</Alert>
          </Col>
        </Row>
      )}

      <Row className="g-4">
        <Col lg={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title className="mb-3">Authentication</Card.Title>

              {!token ? (
                <>
                  <Form onSubmit={handleLogin} className="mb-4">
                    <h6>Login</h6>
                    <Form.Group className="mb-3">
                      <Form.Label>Email</Form.Label>
                      <Form.Control
                        type="text"
                        value={loginForm.username}
                        onChange={(e) =>
                          setLoginForm({ ...loginForm, username: e.target.value })
                        }
                        placeholder="Enter email"
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Password</Form.Label>
                      <Form.Control
                        type="password"
                        value={loginForm.password}
                        onChange={(e) =>
                          setLoginForm({ ...loginForm, password: e.target.value })
                        }
                        placeholder="Enter password"
                      />
                    </Form.Group>

                    <Button type="submit">Login</Button>
                  </Form>

                  <hr />

                  <Form onSubmit={handleRegister}>
                    <h6>Register</h6>
                    <Form.Group className="mb-3">
                      <Form.Label>Full Name</Form.Label>
                      <Form.Control
                        type="text"
                        value={registerForm.full_name}
                        onChange={(e) =>
                          setRegisterForm({ ...registerForm, full_name: e.target.value })
                        }
                        placeholder="Enter full name"
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Email</Form.Label>
                      <Form.Control
                        type="email"
                        value={registerForm.email}
                        onChange={(e) =>
                          setRegisterForm({ ...registerForm, email: e.target.value })
                        }
                        placeholder="Enter email"
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Password</Form.Label>
                      <Form.Control
                        type="password"
                        value={registerForm.password}
                        onChange={(e) =>
                          setRegisterForm({ ...registerForm, password: e.target.value })
                        }
                        placeholder="Create password"
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Role</Form.Label>
                      <Form.Select
                        value={registerForm.role}
                        onChange={(e) =>
                          setRegisterForm({ ...registerForm, role: e.target.value })
                        }
                      >
                        <option value="admin">admin</option>
                        <option value="operator">operator</option>
                        <option value="viewer">viewer</option>
                      </Form.Select>
                    </Form.Group>

                    <Button type="submit" variant="outline-success" disabled={submittingRegister}>
                      {submittingRegister ? "Registering..." : "Register User"}
                    </Button>
                  </Form>
                </>
              ) : (
                <>
                  <Alert variant="success" className="mb-3">
                    Logged in
                  </Alert>

                  {currentUser && (
                    <div className="mb-3 text-start">
                      <p className="mb-1"><strong>Email:</strong> {currentUser.email}</p>
                      <p className="mb-1"><strong>Role:</strong> {currentUser.role}</p>
                      <p className="mb-0"><strong>User ID:</strong> {currentUser.id}</p>
                    </div>
                  )}

                  <Button variant="outline-danger" onClick={handleLogout}>
                    Logout
                  </Button>
                </>
              )}
            </Card.Body>
          </Card>

          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title className="mb-3">Device Form</Card.Title>

              <Form onSubmit={handleDeviceSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Hostname</Form.Label>
                  <Form.Control
                    value={deviceForm.hostname}
                    onChange={(e) =>
                      setDeviceForm({ ...deviceForm, hostname: e.target.value })
                    }
                    placeholder="Router_01"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>IP Address</Form.Label>
                  <Form.Control
                    value={deviceForm.ip_address}
                    onChange={(e) =>
                      setDeviceForm({ ...deviceForm, ip_address: e.target.value })
                    }
                    placeholder="192.168.1.1"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Type</Form.Label>
                  <Form.Control
                    value={deviceForm.type}
                    onChange={(e) =>
                      setDeviceForm({ ...deviceForm, type: e.target.value })
                    }
                    placeholder="router"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Location</Form.Label>
                  <Form.Control
                    value={deviceForm.location}
                    onChange={(e) =>
                      setDeviceForm({ ...deviceForm, location: e.target.value })
                    }
                    placeholder="Server Room A"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Status</Form.Label>
                  <Form.Select
                    value={deviceForm.status}
                    onChange={(e) =>
                      setDeviceForm({ ...deviceForm, status: e.target.value })
                    }
                  >
                    <option value="up">up</option>
                    <option value="down">down</option>
                    <option value="maintenance">maintenance</option>
                  </Form.Select>
                </Form.Group>

                <div className="d-flex gap-2">
                  <Button type="submit" disabled={!token || submittingDevice}>
                    {submittingDevice
                      ? "Saving..."
                      : editingDeviceId
                      ? "Update Device"
                      : "Add Device"}
                  </Button>

                  {editingDeviceId && (
                    <Button
                      type="button"
                      variant="outline-secondary"
                      onClick={() => {
                        setEditingDeviceId("");
                        setDeviceForm({
                          hostname: "",
                          ip_address: "",
                          type: "router",
                          location: "",
                          status: "up",
                        });
                      }}
                    >
                      Cancel Edit
                    </Button>
                  )}
                </div>
              </Form>
            </Card.Body>
          </Card>

          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title className="mb-3">Log Ingestion</Card.Title>

              <Form onSubmit={submitLog}>
                <Form.Group className="mb-3">
                  <Form.Label>Device</Form.Label>
                  <Form.Select
                    value={logForm.device_id}
                    onChange={(e) =>
                      setLogForm({ ...logForm, device_id: e.target.value })
                    }
                  >
                    <option value="">Select a device</option>
                    {devices.map((device) => (
                      <option key={device.id} value={device.id}>
                        {device.hostname}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Log Level</Form.Label>
                  <Form.Select
                    value={logForm.log_level}
                    onChange={(e) =>
                      setLogForm({ ...logForm, log_level: e.target.value })
                    }
                  >
                    <option value="info">info</option>
                    <option value="warning">warning</option>
                    <option value="error">error</option>
                    <option value="critical">critical</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Message</Form.Label>
                  <Form.Control
                    as="textarea"
                    rows={4}
                    value={logForm.message}
                    onChange={(e) =>
                      setLogForm({ ...logForm, message: e.target.value })
                    }
                    placeholder="Enter log message"
                  />
                </Form.Group>

                <Button type="submit" disabled={submittingLog || !token}>
                  {submittingLog ? "Submitting..." : "Submit Log"}
                </Button>
              </Form>
            </Card.Body>
          </Card>

          <Card className="shadow-sm">
            <Card.Body>
              <Card.Title className="mb-3">Create Incident</Card.Title>

              <Form onSubmit={createIncident}>
                <Form.Group className="mb-3">
                  <Form.Label>Status</Form.Label>
                  <Form.Select
                    value={incidentForm.status}
                    onChange={(e) =>
                      setIncidentForm({ ...incidentForm, status: e.target.value })
                    }
                  >
                    <option value="open">open</option>
                    <option value="investigating">investigating</option>
                    <option value="resolved">resolved</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Severity</Form.Label>
                  <Form.Select
                    value={incidentForm.severity}
                    onChange={(e) =>
                      setIncidentForm({ ...incidentForm, severity: e.target.value })
                    }
                  >
                    <option value="low">low</option>
                    <option value="medium">medium</option>
                    <option value="high">high</option>
                    <option value="critical">critical</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Initial Linked Logs</Form.Label>
                  <Form.Select
                    multiple
                    value={incidentForm.linked_logs}
                    onChange={(e) => {
                      const selected = Array.from(e.target.selectedOptions).map(
                        (option) => option.value
                      );
                      setIncidentForm({ ...incidentForm, linked_logs: selected });
                    }}
                  >
                    {logs.map((log) => (
                      <option key={log.id} value={log.id}>
                        {log.log_level} - {log.message}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                <Button type="submit" disabled={submittingIncident || !token}>
                  {submittingIncident ? "Creating..." : "Create Incident"}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={8}>
          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <div className="d-flex gap-2 mb-3 flex-wrap">
                <Button onClick={loadDevices} disabled={loadingDevices || !token}>
                  {loadingDevices ? "Loading Devices..." : "Load Devices"}
                </Button>

                <Button onClick={loadLogs} disabled={loadingLogs || !token}>
                  {loadingLogs ? "Loading Logs..." : "Load Logs"}
                </Button>

                <Button onClick={loadIncidents} disabled={loadingIncidents || !token}>
                  {loadingIncidents ? "Loading Incidents..." : "Load Incidents"}
                </Button>
              </div>

              <Card.Title>Devices</Card.Title>
              <Table striped bordered hover responsive size="sm" className="mt-3">
                <thead>
                  <tr>
                    <th>Hostname</th>
                    <th>IP Address</th>
                    <th>Type</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {devices.length > 0 ? (
                    devices.map((device) => (
                      <tr key={device.id}>
                        <td>{device.hostname}</td>
                        <td>{device.ip_address}</td>
                        <td>{device.type}</td>
                        <td>{device.location}</td>
                        <td>{device.status}</td>
                        <td className="d-flex gap-2 flex-wrap">
                          <Button
                            size="sm"
                            variant="outline-secondary"
                            onClick={() => handleEditDevice(device)}
                          >
                            Edit
                          </Button>
                          <Button
                            size="sm"
                            variant="outline-danger"
                            disabled={deletingDeviceId === device.id}
                            onClick={() => handleDeleteDevice(device.id)}
                          >
                            {deletingDeviceId === device.id ? "Deleting..." : "Delete"}
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="text-center">
                        No devices loaded
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
          
                    {selectedLog && (
            <Card className="mb-4 shadow-sm">
              <Card.Body>
                <Card.Title>Log Details</Card.Title>
                <p><strong>ID:</strong> {selectedLog.id}</p>
                <p><strong>Timestamp:</strong> {selectedLog.timestamp}</p>
                <p><strong>Device ID:</strong> {selectedLog.device_id}</p>
                <p><strong>Log Level:</strong> {selectedLog.log_level}</p>
                <p><strong>Message:</strong> {selectedLog.message}</p>

                <Button
                  size="sm"
                  variant="outline-secondary"
                  onClick={() => setSelectedLog(null)}
                >
                  Close
                </Button>
              </Card.Body>
            </Card>
          )}

          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title>Logs</Card.Title>
              <Table striped bordered hover responsive size="sm" className="mt-3">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Timestamp</th>
                    <th>Device ID</th>
                    <th>Level</th>
                    <th>Message</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.length > 0 ? (
                    logs.map((log) => (
                      <tr key={log.id}>
                        <td>{log.id.slice(-6)}</td>
                        <td>{log.timestamp}</td>
                        <td>{log.device_id}</td>
                        <td>{log.log_level}</td>
                        <td>{log.message}</td>
                        <td>
                          <Button
                            size="sm"
                            variant="outline-primary"
                            onClick={() => openLog(log.id)}
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="text-center">
                        No logs loaded
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          <Card className="mb-4 shadow-sm">
            <Card.Body>
              <Card.Title>Incidents</Card.Title>
              <Table striped bordered hover responsive size="sm" className="mt-3">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Severity</th>
                    <th>Created By</th>
                    <th>Open</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.length > 0 ? (
                    incidents.map((incident) => (
                      <tr key={incident.id}>
                        <td>{incident.id.slice(-6)}</td>
                        <td>{incident.status}</td>
                        <td>
                          <Badge bg={severityVariant(incident.severity)}>
                            {incident.severity}
                          </Badge>
                        </td>
                        <td>{incident.created_by}</td>
                        <td>
                          <Button
                            size="sm"
                            variant="outline-primary"
                            onClick={() => openIncident(incident.id)}
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="5" className="text-center">
                        No incidents loaded
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          {selectedIncident && (
            <Card className="shadow-sm">
              <Card.Body>
                <div className="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                  <Card.Title className="mb-0">Incident Details</Card.Title>
                  <Button onClick={runAnalysis} disabled={runningAnalysis}>
                    {runningAnalysis ? "Running Analysis..." : "Run AI Analysis"}
                  </Button>
                </div>

                <Row className="mb-3">
                  <Col md={6}>
                    <p><strong>ID:</strong> {selectedIncident.id}</p>
                    <p><strong>Status:</strong> {selectedIncident.status}</p>
                    <p><strong>Severity:</strong> {selectedIncident.severity}</p>
                  </Col>
                  <Col md={6}>
                    <p><strong>Created By:</strong> {selectedIncident.created_by}</p>
                    <p><strong>Created At:</strong> {selectedIncident.created_at}</p>
                  </Col>
                </Row>

                <Card className="mb-4">
                  <Card.Body>
                    <h5 className="mb-3">Link Another Log</h5>
                    <div className="d-flex gap-2 flex-wrap">
                      <Form.Select
                        value={selectedLogToLink}
                        onChange={(e) => setSelectedLogToLink(e.target.value)}
                      >
                        <option value="">Select log to link</option>
                        {unlinkedLogs.map((log) => (
                          <option key={log.id} value={log.id}>
                            {log.log_level} - {log.message}
                          </option>
                        ))}
                      </Form.Select>

                      <Button
                        onClick={handleLinkLog}
                        disabled={!selectedLogToLink || linkingLog}
                      >
                        {linkingLog ? "Linking..." : "Link Log"}
                      </Button>
                    </div>
                  </Card.Body>
                </Card>

                <h5>Linked Logs</h5>
                <Table striped bordered hover responsive size="sm" className="mb-4">
                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Level</th>
                      <th>Message</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedIncident.linked_logs?.length > 0 ? (
                      selectedIncident.linked_logs.map((log) => (
                        <tr key={log.id}>
                          <td>{log.timestamp}</td>
                          <td>{log.log_level}</td>
                          <td>{log.message}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="3" className="text-center">
                          No linked logs
                        </td>
                      </tr>
                    )}
                  </tbody>
                </Table>

                <h5>AI Report</h5>
                {analysisResult ? (
                  <div className="border rounded p-3 text-start">
                    <p><strong>Summary:</strong> {analysisResult.summary}</p>
                    <p><strong>Probable Cause:</strong> {analysisResult.probable_cause}</p>
                    <p>
                      <strong>Severity:</strong>{" "}
                      <Badge bg={severityVariant(analysisResult.severity)}>
                        {analysisResult.severity}
                      </Badge>
                    </p>

                    <div className="mb-3">
                      <strong>Recommended Actions</strong>
                      {renderStringList(analysisResult.recommended_actions)}
                    </div>

                    <div className="mb-3">
                      <strong>Supporting Evidence</strong>
                      {renderStringList(analysisResult.supporting_evidence)}
                    </div>

                    <div className="mb-3">
                      <strong>Uncertainties</strong>
                      {renderStringList(analysisResult.uncertainties)}
                    </div>

                    <div className="mb-0">
                      <strong>Follow-Up Questions</strong>
                      {renderStringList(analysisResult.follow_up_questions)}
                    </div>
                  </div>
                ) : (
                  <Alert variant="secondary" className="mb-0">
                    No AI report available yet
                  </Alert>
                )}
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
}

export default App;