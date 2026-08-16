// API layer — all backend communication lives here

const API_BASE = '/api';

/**
 * Send a query to the PolicyPilot AI backend
 * @param {string} query
 * @param {object} userProfile
 * @param {string|null} conversationId
 * @param {Array} conversationHistory
 * @returns {Promise<object>} API response
 */
export async function submitQuery(
  query,
  userProfile = {},
  conversationId = null,
  conversationHistory = [],
  token = null,
  targetFolderId = null,
  userId = null,
) {
  const body = {
    query,
    user_profile: userProfile,
  };

  if (userId) {
    body.user_id = userId;
  }

  if (targetFolderId) {
    body.target_folder_id = targetFolderId;
  }

  if (conversationId) {
    body.conversation_id = conversationId;
  }

  if (conversationHistory && conversationHistory.length > 0) {
    body.conversation_history = conversationHistory;
  }

  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}/v1/query`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
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
