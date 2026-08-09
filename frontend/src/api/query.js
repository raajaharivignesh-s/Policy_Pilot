// API layer — all backend communication lives here

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Send a query to the PolicyPilot AI backend
 * @param {string} query
 * @param {object} userProfile
 * @returns {Promise<object>} API response
 */
export async function submitQuery(query, userProfile = {}) {
  const response = await fetch(`${API_BASE}/api/v1/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, user_profile: userProfile }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

/**
 * Check backend health status
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(3000),
    });
    const data = await response.json();
    return data.status === 'Healthy' || response.ok;
  } catch {
    return false;
  }
}
