const API_BASE = '/api';

export async function getFolders(token) {
  const response = await fetch(`${API_BASE}/v1/wallet/folders`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) throw new Error('Failed to fetch folders');
  return response.json();
}

export async function createFolder(token, name) {
  const response = await fetch(`${API_BASE}/v1/wallet/folders`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ name })
  });
  if (!response.ok) throw new Error('Failed to create folder');
  return response.json();
}

export async function deleteFolder(token, folderId) {
  const response = await fetch(`${API_BASE}/v1/wallet/folders/${folderId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) throw new Error('Failed to delete folder');
  return response.json();
}

export async function getDocuments(token, folderId) {
  const response = await fetch(`${API_BASE}/v1/wallet/folders/${folderId}/documents`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) throw new Error('Failed to fetch documents');
  return response.json();
}

export async function uploadDocument(token, folderId, file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE}/v1/wallet/folders/${folderId}/documents`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  if (!response.ok) throw new Error('Failed to upload document');
  return response.json();
}

export async function deleteDocument(token, documentId) {
  const response = await fetch(`${API_BASE}/v1/wallet/documents/${documentId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!response.ok) throw new Error('Failed to delete document');
  return response.json();
}

export function getDocumentDownloadUrl(token, documentId) {
  // Using query param for token in URL is one way, or we fetch as blob
  // For simplicity, we can fetch as blob
  return async () => {
    const response = await fetch(`${API_BASE}/v1/wallet/documents/${documentId}/download`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Failed to download document');
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    // Try to get filename from content-disposition header if possible, else default
    const contentDisposition = response.headers.get('content-disposition');
    let filename = 'document';
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) filename = match[1];
    }
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  };
}
