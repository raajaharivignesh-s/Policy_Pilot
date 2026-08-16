import { useState, useEffect, useCallback } from 'react';
import {
  getFolders, createFolder, deleteFolder,
  getDocuments, uploadDocument, deleteDocument, getDocumentDownloadUrl,
} from '../api/wallet';

export default function DashboardPage({ user, token, onLogout, onGoBack }) {
  const [folders, setFolders]               = useState([]);
  const [activeFolder, setActiveFolder]     = useState(null);
  const [documents, setDocuments]           = useState([]);
  const [newFolderName, setNewFolderName]   = useState('');
  const [isCreatingFolder, setIsCreating]   = useState(false);
  const [isUploading, setIsUploading]       = useState(false);
  const [folderError, setFolderError]       = useState('');
  const [uploadError, setUploadError]       = useState('');
  const [docsLoading, setDocsLoading]       = useState(false);

  // ── Load folders ─────────────────────────────────────────────────────────────
  const loadFolders = useCallback(async () => {
    if (!token) return;
    try {
      const data = await getFolders(token);
      setFolders(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error('loadFolders:', e);
    }
  }, [token]);

  useEffect(() => { loadFolders(); }, [loadFolders]);

  // ── Load documents when active folder changes ────────────────────────────────
  useEffect(() => {
    if (!activeFolder) { setDocuments([]); return; }
    setDocsLoading(true);
    setUploadError('');
    getDocuments(token, activeFolder.id)
      .then(d => setDocuments(Array.isArray(d) ? d : []))
      .catch(e => { console.error(e); setDocuments([]); })
      .finally(() => setDocsLoading(false));
  }, [activeFolder, token]);

  // ── Create folder ────────────────────────────────────────────────────────────
  const handleCreateFolder = async (e) => {
    e.preventDefault();
    const name = newFolderName.trim();
    if (!name) { setFolderError('Please enter a folder name.'); return; }
    setFolderError('');
    setIsCreating(true);
    try {
      const folder = await createFolder(token, name);
      if (!folder || !folder.id) throw new Error('Unexpected server response.');
      setFolders(prev => [...prev, folder]);
      setActiveFolder(folder);
      setNewFolderName('');
    } catch (err) {
      console.error('createFolder:', err);
      setFolderError(err.message || 'Could not create folder. Is the server running?');
    } finally {
      setIsCreating(false);
    }
  };

  // ── Delete folder ────────────────────────────────────────────────────────────
  const handleDeleteFolder = async (folderId, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this folder and all its documents?')) return;
    try {
      await deleteFolder(token, folderId);
      setFolders(prev => prev.filter(f => f.id !== folderId));
      if (activeFolder?.id === folderId) { setActiveFolder(null); setDocuments([]); }
    } catch (err) {
      alert('Delete failed: ' + (err.message || 'Unknown error'));
    }
  };

  // ── Upload document ──────────────────────────────────────────────────────────
  const handleFileUpload = async (e) => {
    if (!e.target.files?.length || !activeFolder) return;
    setUploadError('');
    setIsUploading(true);
    try {
      const doc = await uploadDocument(token, activeFolder.id, e.target.files[0]);
      if (!doc || !doc.id) throw new Error('Unexpected server response.');
      setDocuments(prev => [...prev, doc]);
    } catch (err) {
      setUploadError(err.message || 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };

  // ── Delete document ──────────────────────────────────────────────────────────
  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Delete this document?')) return;
    try {
      await deleteDocument(token, docId);
      setDocuments(prev => prev.filter(d => d.id !== docId));
    } catch (err) {
      alert('Delete failed: ' + (err.message || 'Unknown error'));
    }
  };

  // ── Download document ────────────────────────────────────────────────────────
  const handleDownload = (docId) => {
    getDocumentDownloadUrl(token, docId)().catch(err => alert('Download failed: ' + err.message));
  };

  const initials = user?.name
    ? user.name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
    : '?';

  const S = {
    page:          { minHeight: '100vh', background: 'linear-gradient(135deg,#fff8f5 0%,#fafafa 60%,#f0f4ff 100%)', fontFamily: 'Inter,system-ui,sans-serif', display: 'flex', flexDirection: 'column' },
    header:        { background: 'white', borderBottom: '1px solid #eee', padding: '0 24px', height: 64, display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 10, boxShadow: '0 1px 8px rgba(0,0,0,.06)' },
    backBtn:       { width: 40, height: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid #e5e7eb', borderRadius: 12, background: '#f9fafb', cursor: 'pointer', color: '#374151', fontSize: 18 },
    logoutBtn:     { padding: '8px 16px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 10, color: '#dc2626', fontSize: 13, fontWeight: 600, cursor: 'pointer' },
    main:          { flex: 1, maxWidth: 1200, width: '100%', margin: '0 auto', padding: '32px 24px', display: 'flex', flexDirection: 'column', gap: 32 },
    profileSect:   { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, paddingBottom: 32, borderBottom: '1px solid #f3f4f6' },
    avatar:        { width: 96, height: 96, borderRadius: '50%', background: 'linear-gradient(135deg,#FF6B00,#FF8A33)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: 36, fontWeight: 700, boxShadow: '0 8px 24px rgba(255,107,0,.35)' },
    walletSect:    { display: 'flex', gap: 24, alignItems: 'flex-start', flexWrap: 'wrap' },
    sidebar:       { width: 280, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 16 },
    card:          { background: 'white', borderRadius: 20, border: '1px solid #e5e7eb', padding: 20, boxShadow: '0 2px 12px rgba(0,0,0,.05)' },
    folderInput:   { padding: '10px 14px', borderRadius: 10, border: '1.5px solid #e5e7eb', fontSize: 14, outline: 'none', background: '#f9fafb', width: '100%', boxSizing: 'border-box' },
    addBtn:        (disabled) => ({ padding: '10px 16px', background: disabled ? '#e5e7eb' : 'linear-gradient(135deg,#FF6B00,#FF8A33)', color: disabled ? '#9ca3af' : 'white', border: 'none', borderRadius: 10, fontSize: 14, fontWeight: 600, cursor: disabled ? 'not-allowed' : 'pointer', width: '100%' }),
    docsArea:      { flex: 1, minWidth: 320, background: 'white', borderRadius: 20, border: '1px solid #e5e7eb', boxShadow: '0 2px 12px rgba(0,0,0,.05)', display: 'flex', flexDirection: 'column', minHeight: 480 },
    uploadLabel:   { display: 'flex', alignItems: 'center', gap: 8, padding: '10px 20px', background: 'linear-gradient(135deg,#FF6B00,#FF8A33)', color: 'white', borderRadius: 12, fontSize: 13, fontWeight: 600, cursor: 'pointer', boxShadow: '0 4px 12px rgba(255,107,0,.3)', userSelect: 'none' },
    docGrid:       { display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(200px,1fr))', gap: 16 },
    docCard:       { border: '1px solid #e5e7eb', borderRadius: 14, padding: 16, background: '#fafafa' },
    iconBtn:       { width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'white', border: '1px solid #e5e7eb', borderRadius: 8, cursor: 'pointer', color: '#6b7280', fontSize: 12 },
  };

  return (
    <div style={S.page}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}input:focus{border-color:#FF6B00!important}`}</style>

      {/* Header */}
      <header style={S.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <button onClick={onGoBack} style={S.backBtn}>←</button>
          <div>
            <h1 style={{ fontSize: 18, fontWeight: 700, color: '#111827', margin: 0 }}>Document Wallet</h1>
            <p style={{ fontSize: 12, color: '#6b7280', margin: 0 }}>Manage your saved documents</p>
          </div>
        </div>
        <button onClick={onLogout} style={S.logoutBtn}>Logout</button>
      </header>

      <main style={S.main}>

        {/* ── Profile ─── */}
        <section style={S.profileSect}>
          <div style={S.avatar}>{initials}</div>
          <h2 style={{ fontSize: 24, fontWeight: 800, color: '#111827', margin: 0 }}>{user?.name || 'Citizen'}</h2>
          {user?.email && <p style={{ fontSize: 14, color: '#6b7280', margin: 0 }}>{user.email}</p>}
          <div style={{ display: 'flex', gap: 32, marginTop: 8 }}>
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: 22, fontWeight: 700, color: '#FF6B00', margin: 0 }}>{folders.length}</p>
              <p style={{ fontSize: 12, color: '#9ca3af', margin: 0 }}>Folders</p>
            </div>
            <div style={{ width: 1, background: '#e5e7eb' }} />
            <div style={{ textAlign: 'center' }}>
              <p style={{ fontSize: 22, fontWeight: 700, color: '#FF6B00', margin: 0 }}>{documents.length}</p>
              <p style={{ fontSize: 12, color: '#9ca3af', margin: 0 }}>Documents</p>
            </div>
          </div>
        </section>

        {/* ── Wallet ─── */}
        <section style={S.walletSect}>

          {/* Sidebar */}
          <div style={S.sidebar}>

            {/* Create folder card */}
            <div style={S.card}>
              <h3 style={{ fontSize: 15, fontWeight: 700, color: '#111827', margin: '0 0 14px' }}>📁 New Folder</h3>
              <form onSubmit={handleCreateFolder} style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <input
                  type="text"
                  value={newFolderName}
                  onChange={e => { setNewFolderName(e.target.value); setFolderError(''); }}
                  placeholder="e.g. Student Scheme Docs"
                  style={{ ...S.folderInput, borderColor: folderError ? '#ef4444' : '#e5e7eb' }}
                  disabled={isCreatingFolder}
                />
                {folderError && <p style={{ fontSize: 12, color: '#ef4444', margin: 0 }}>⚠ {folderError}</p>}
                <button type="submit" disabled={isCreatingFolder || !newFolderName.trim()} style={S.addBtn(isCreatingFolder || !newFolderName.trim())}>
                  {isCreatingFolder ? 'Creating...' : '+ Add Folder'}
                </button>
              </form>
            </div>

            {/* Folder list card */}
            <div style={{ background: 'white', borderRadius: 20, border: '1px solid #e5e7eb', overflow: 'hidden', boxShadow: '0 2px 12px rgba(0,0,0,.05)' }}>
              <div style={{ padding: '16px 20px', borderBottom: '1px solid #f3f4f6' }}>
                <h3 style={{ fontSize: 15, fontWeight: 700, color: '#111827', margin: 0 }}>My Folders ({folders.length})</h3>
              </div>
              <div style={{ maxHeight: 380, overflowY: 'auto' }}>
                {folders.length === 0 ? (
                  <div style={{ padding: '32px 20px', textAlign: 'center' }}>
                    <p style={{ fontSize: 13, color: '#9ca3af', margin: 0 }}>No folders yet.<br />Create one above.</p>
                  </div>
                ) : folders.map(folder => {
                  const isActive = activeFolder?.id === folder.id;
                  return (
                    <div
                      key={folder.id}
                      onClick={() => setActiveFolder(folder)}
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', cursor: 'pointer', background: isActive ? '#fff8f5' : 'transparent', borderLeft: isActive ? '3px solid #FF6B00' : '3px solid transparent', borderBottom: '1px solid #f9fafb', transition: 'background .15s' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
                        <span style={{ fontSize: 18 }}>📁</span>
                        <span style={{ fontSize: 13, fontWeight: isActive ? 700 : 500, color: isActive ? '#FF6B00' : '#374151', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{folder.name}</span>
                      </div>
                      <button
                        onClick={e => handleDeleteFolder(folder.id, e)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#d1d5db', padding: 4, borderRadius: 6 }}
                        title="Delete folder"
                      >✕</button>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Documents area */}
          <div style={S.docsArea}>
            {activeFolder ? (
              <>
                {/* Area header */}
                <div style={{ padding: '20px 24px', borderBottom: '1px solid #f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
                  <div>
                    <h3 style={{ fontSize: 18, fontWeight: 700, color: '#111827', margin: '0 0 2px' }}>{activeFolder.name}</h3>
                    <p style={{ fontSize: 13, color: '#6b7280', margin: 0 }}>{documents.length} document{documents.length !== 1 ? 's' : ''}</p>
                  </div>
                  <label style={S.uploadLabel}>
                    {isUploading ? 'Uploading...' : '⬆ Upload Document'}
                    <input type="file" style={{ display: 'none' }} onChange={handleFileUpload} disabled={isUploading} accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" />
                  </label>
                </div>

                {uploadError && (
                  <div style={{ margin: '12px 24px 0', padding: '10px 14px', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 10, color: '#dc2626', fontSize: 13 }}>
                    ⚠ {uploadError}
                  </div>
                )}

                <div style={{ flex: 1, padding: 24, overflowY: 'auto' }}>
                  {docsLoading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
                      <span style={{ width: 32, height: 32, border: '3px solid #f3f4f6', borderTopColor: '#FF6B00', borderRadius: '50%', display: 'inline-block', animation: 'spin .8s linear infinite' }} />
                    </div>
                  ) : documents.length === 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 240, textAlign: 'center' }}>
                      <div style={{ fontSize: 48, marginBottom: 16 }}>📄</div>
                      <h4 style={{ fontSize: 16, fontWeight: 600, color: '#374151', margin: '0 0 6px' }}>No documents yet</h4>
                      <p style={{ fontSize: 13, color: '#9ca3af', maxWidth: 280, margin: 0 }}>Upload documents like Aadhaar, PAN, Income Certificate, or educational certificates to use for scheme eligibility checks.</p>
                    </div>
                  ) : (
                    <div style={S.docGrid}>
                      {documents.map(doc => (
                        <div key={doc.id} style={S.docCard}>
                          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 10 }}>
                            <div style={{ width: 44, height: 44, background: '#fff8f5', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22 }}>
                              {doc.file_type?.includes('pdf') ? '📑' : doc.file_type?.includes('image') ? '🖼️' : '📄'}
                            </div>
                            <div style={{ display: 'flex', gap: 4 }}>
                              <button onClick={() => handleDownload(doc.id)} title="Download" style={S.iconBtn}>⬇</button>
                              <button onClick={() => handleDeleteDocument(doc.id)} title="Delete" style={S.iconBtn}>✕</button>
                            </div>
                          </div>
                          <h4 style={{ fontSize: 13, fontWeight: 600, color: '#111827', margin: '0 0 4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={doc.filename}>{doc.filename}</h4>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#9ca3af' }}>
                            <span>{doc.file_size ? (doc.file_size / 1024).toFixed(1) + ' KB' : '—'}</span>
                            <span>{doc.created_at ? new Date(doc.created_at).toLocaleDateString() : ''}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 40 }}>
                <div style={{ fontSize: 56, marginBottom: 20 }}>📁</div>
                <h4 style={{ fontSize: 18, fontWeight: 700, color: '#374151', margin: '0 0 8px' }}>Select a Folder</h4>
                <p style={{ fontSize: 14, color: '#9ca3af', maxWidth: 300, margin: 0 }}>Create or select a folder from the left panel to view and manage your uploaded documents.</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
