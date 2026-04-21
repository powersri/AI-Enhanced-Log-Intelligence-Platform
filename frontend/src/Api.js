const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    let errorMessage = "Request failed";

if (typeof data.detail === "string") {
  errorMessage = data.detail;
} else if (Array.isArray(data.detail)) {
  errorMessage = data.detail.map((item) => item.msg).join(", ");
} else if (typeof data.message === "string") {
  errorMessage = data.message;
}

throw new Error(errorMessage);
  }

  return data;
}

export { API_BASE };