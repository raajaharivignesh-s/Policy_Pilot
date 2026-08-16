import { useState } from 'react';
import { createFolder, uploadDocument } from '../api/wallet';

export default function DocumentsCard({ 
  requiredDocuments, 
  folders = [], 
  token, 
  runQuery, 
  setTargetFolderId, 
  lastQuery, 
  refreshFolders 
}) {
  const [mode, setMode] = useState(null); // 'wallet' | 'new' | null
  const [selectedFolder, setSelectedFolder] = useState('');
  const [newFolderName, setNewFolderName] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState({}); // { [docName]: File }
  const [isVerifying, setIsVerifying] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  if (!requiredDocuments || requiredDocuments.length === 0) return null;

  const handleWalletVerify = async () => {
    if (!selectedFolder) {
      setErrorMsg('Please select a folder from your wallet.');
      return;
    }
    setErrorMsg(null);
    setIsVerifying(true);
    try {
      setTargetFolderId(selectedFolder);
      // Pass folder ID directly to runQuery to avoid stale closure
      runQuery(lastQuery, selectedFolder);
    } catch (err) {
      console.error(err);
      setErrorMsg('Failed to process documents. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleFileChange = (docName, file) => {
    setUploadedFiles(prev => ({
      ...prev,
      [docName]: file
    }));
  };

  const handleUploadAndVerify = async () => {
    if (!newFolderName.trim()) {
      setErrorMsg('Please enter a name for the new folder.');
      return;
    }
    const uploadedKeys = Object.keys(uploadedFiles);
    if (uploadedKeys.length === 0) {
      setErrorMsg('Please select at least one document to upload.');
      return;
    }
    setErrorMsg(null);
    setIsVerifying(true);

    try {
      // 1. Create a new folder
      const folder = await createFolder(token, newFolderName.trim());
      const newFolderId = folder.id;

      // 2. Upload each selected document to the folder
      for (const docName of uploadedKeys) {
        const file = uploadedFiles[docName];
        if (file) {
          await uploadDocument(token, newFolderId, file);
        }
      }

      // 3. Update the folder selection states
      setTargetFolderId(newFolderId);
      if (refreshFolders) refreshFolders();

      // 4. Run the query with new folder context — pass folder ID directly
      runQuery(lastQuery, newFolderId);
      setMode(null);

    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to create folder or upload documents. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="bg-white border border-[#E6E4DF] rounded-2xl p-6 shadow-xs animate-fade-up">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-9 h-9 rounded-xl bg-orange-50 flex items-center justify-center text-lg">
          📄
        </div>
        <div>
          <h3 className="font-heading font-bold text-base text-gray-900">Required Documents</h3>
          <p className="text-xs text-gray-400">Documents needed to verify eligibility</p>
        </div>
      </div>

      {/* Required List */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-6">
        {requiredDocuments.map((doc, i) => (
          <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 border border-gray-200 text-xs font-medium text-gray-700">
            <div className="flex items-center gap-2.5">
              <span className="text-[#FF5500] text-sm">📁</span>
              <span>{doc}</span>
            </div>
            {mode === 'new' && (
              <label className="cursor-pointer bg-white border border-gray-300 hover:border-[#FF5500] text-gray-700 hover:text-[#FF5500] px-2.5 py-1 rounded-md text-[11px] transition-all">
                {uploadedFiles[doc] ? '✓ Selected' : 'Choose File'}
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  className="hidden"
                  onChange={(e) => handleFileChange(doc, e.target.files[0])}
                />
              </label>
            )}
          </div>
        ))}
      </div>

      {errorMsg && (
        <div className="mb-4 text-xs text-red-600 font-semibold bg-red-50 border border-red-100 p-2.5 rounded-lg">
          ⚠️ {errorMsg}
        </div>
      )}

      {/* Verification Selection */}
      {!mode ? (
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={() => setMode('wallet')}
            className="flex-1 py-3 px-4 rounded-xl bg-gray-900 text-white font-semibold text-xs hover:bg-gray-800 transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            💼 Select from Wallet
          </button>
          <button
            onClick={() => setMode('new')}
            className="flex-1 py-3 px-4 rounded-xl bg-[#FF5500] text-white font-semibold text-xs hover:bg-[#E64D00] transition-all flex items-center justify-center gap-2 cursor-pointer"
          >
            📤 Upload New Documents
          </button>
        </div>
      ) : mode === 'wallet' ? (
        <div className="space-y-4 bg-gray-50 p-4 rounded-xl border border-gray-200 animate-fade-down">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-900">Choose Wallet Folder</span>
            <button onClick={() => setMode(null)} className="text-xs text-gray-500 hover:text-gray-900 font-semibold cursor-pointer">Cancel</button>
          </div>
          <div className="flex gap-2">
            <select
              value={selectedFolder}
              onChange={(e) => setSelectedFolder(e.target.value)}
              className="flex-1 bg-white border border-gray-300 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#FF5500]"
            >
              <option value="">-- Select a Folder --</option>
              {folders.map(f => (
                <option key={f.id} value={f.id}>{f.name}</option>
              ))}
            </select>
            <button
              onClick={handleWalletVerify}
              disabled={isVerifying}
              className="bg-[#FF5500] hover:bg-[#E64D00] disabled:bg-gray-300 text-white font-bold text-xs px-4 py-2 rounded-lg transition-colors cursor-pointer"
            >
              {isVerifying ? 'Verifying...' : 'Verify'}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4 bg-gray-50 p-4 rounded-xl border border-gray-200 animate-fade-down">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-gray-900">Upload &amp; Save Documents</span>
            <button onClick={() => { setMode(null); setUploadedFiles({}); }} className="text-xs text-gray-500 hover:text-gray-900 font-semibold cursor-pointer">Cancel</button>
          </div>

          <div className="space-y-2">
            <label className="block text-[11px] font-bold text-gray-500 uppercase tracking-wider">New Folder Name</label>
            <input
              type="text"
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              placeholder="e.g. My Education Credentials"
              className="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-[#FF5500]"
            />
          </div>

          <div className="flex justify-end pt-2">
            <button
              onClick={handleUploadAndVerify}
              disabled={isVerifying}
              className="w-full sm:w-auto bg-[#FF5500] hover:bg-[#E64D00] disabled:bg-gray-300 text-white font-bold text-xs px-5 py-2.5 rounded-lg transition-colors cursor-pointer"
            >
              {isVerifying ? 'Uploading & Verifying...' : 'Create Folder & Verify'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
