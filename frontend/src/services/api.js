// API base URL — set REACT_APP_API_URL env var on Vercel for production.
// Falls back to localhost:8000 for local development automatically.
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
  };
};

// ── Auth ──────────────────────────────────────────────────────────────────────
export const fetchSummary = async () => {
  const response = await fetch(`${API_URL}/dashboard/summary`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch dashboard summary');
  return response.json();
};

/**
 * New aggregated chart-data endpoint.
 * Returns { pie_data, bar_data } — pre-computed server-side.
 * Replaces fetching all 300 predictions on the Dashboard page.
 */
export const fetchDashboardChartData = async () => {
  const response = await fetch(`${API_URL}/dashboard/chart-data`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch chart data');
  return response.json();
};

// ── Vehicles ─────────────────────────────────────────────────────────────────
export const fetchVehicles = async (page = 1) => {
  const response = await fetch(`${API_URL}/vehicles?page=${page}&page_size=25`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch vehicles');
  return response.json(); // { count, next, previous, results }
};

export const fetchVehicleDetails = async (id) => {
  const response = await fetch(`${API_URL}/vehicles/${id}`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch vehicle details');
  return response.json();
};

export const fetchVehicleTyres = async (id) => {
  const response = await fetch(`${API_URL}/vehicles/${id}/tyres`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch tyres');
  return response.json();
};

// ── Predictions ───────────────────────────────────────────────────────────────
export const fetchPredictions = async (page = 1) => {
  const response = await fetch(`${API_URL}/predictions?page=${page}&page_size=50`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch predictions');
  return response.json(); // paginated: { count, next, previous, results }
};

export const fetchVehiclePredictions = async (id) => {
  const response = await fetch(`${API_URL}/predictions/${id}`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch predictions');
  return response.json();
};

// ── Alerts ────────────────────────────────────────────────────────────────────
export const fetchAlerts = async (page = 1) => {
  const response = await fetch(`${API_URL}/alerts?page=${page}&page_size=50`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch alerts');
  return response.json(); // paginated
};

// ── Reports ───────────────────────────────────────────────────────────────────
export const fetchReportsSummary = async () => {
  const response = await fetch(`${API_URL}/reports/summary`, { headers: getHeaders() });
  if (!response.ok) throw new Error('Failed to fetch reports summary');
  return response.json();
};

// ── Simulator ─────────────────────────────────────────────────────────────────
export const startSimulator = async () => {
  const response = await fetch(`${API_URL}/simulator/start`, {
    method: 'POST',
    headers: getHeaders(),
  });
  if (!response.ok) throw new Error('Failed to start simulator');
  return response.json();
};
