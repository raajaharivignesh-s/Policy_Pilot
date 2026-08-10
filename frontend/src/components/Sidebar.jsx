import { useState, useEffect } from 'react';
import { checkHealth } from '../api/query';
import LogoMark from './LogoMark';

// Inline SVG icons (outline/skeleton, no color)
const IconEdit = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
  </svg>
);
const IconX = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
  </svg>
);
const IconUser = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="8" r="4"/><path d="M20 21a8 8 0 1 0-16 0"/>
  </svg>
);

export default function Sidebar({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onRenameChat,
  onDeleteChat,
  onClearAll,
  isOpen,
  onCloseMobile,
  onGoToLanding,
}) {
  const [healthy, setHealthy] = useState(null);
  const [editingChatId, setEditingChatId] = useState(null);
  const [editTitle, setEditTitle] = useState('');

  useEffect(() => {
    checkHealth().then(setHealthy);
  }, []);

  const handleStartRename = (chat, e) => {
    if (e) e.stopPropagation();
    setEditingChatId(chat.id);
    setEditTitle(chat.title || 'New Conversation');
  };

  const handleSaveRename = (chatId, e) => {
    if (e) e.stopPropagation();
    if (editTitle.trim()) {
      onRenameChat(chatId, editTitle.trim());
    }
    setEditingChatId(null);
  };

  const handleCancelRename = (e) => {
    if (e) e.stopPropagation();
    setEditingChatId(null);
  };

  const handleKeyDownRename = (chatId, e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSaveRename(chatId, e);
    } else if (e.key === 'Escape') {
      e.preventDefault();
      handleCancelRename(e);
    }
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/40 z-40 lg:hidden backdrop-blur-xs"
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static top-0 bottom-0 left-0 z-50
        w-64 bg-white text-gray-800 flex flex-col h-full border-r border-gray-200
        transition-transform duration-300 ease-in-out font-sans shadow-sm
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Brand Header */}
        <div className="p-5 flex items-center justify-between border-b border-gray-100">
          <div
            className="flex items-center gap-2 cursor-pointer select-none"
            onClick={onGoToLanding}
          >
            <LogoMark size={24} />
            <span className="font-sans font-bold text-xl text-gray-900 tracking-tight">
              PolicyPilot <span className="text-[#FF5500] font-normal">AI</span>
            </span>
          </div>
          <button
            onClick={onGoToLanding}
            className="text-gray-400 hover:text-gray-700 text-xs p-1 rounded-md transition-colors"
            title="Home"
          >
            «
          </button>
        </div>

        {/* + New Chat Button */}
        <div className="p-4">
          <button
            onClick={() => {
              onNewChat();
              if (onCloseMobile) onCloseMobile();
            }}
            className="w-full py-2.5 px-4 bg-[#FFF8F5] hover:bg-[#FFF2EC] border border-[#FFD8CC] text-[#FF6B00] font-semibold text-xs rounded-xl flex items-center justify-center gap-2 transition-all cursor-pointer shadow-sm"
          >
            <span className="text-base font-normal">+</span> New Chat
          </button>
        </div>

        {/* Chat History — only section */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <div className="px-3 pb-2 flex items-center justify-between">
            <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
              Chat History
            </span>
            {chats.length > 0 && (
              <button
                onClick={onClearAll}
                className="text-[10px] text-gray-400 hover:text-rose-600 transition-colors"
              >
                Clear all
              </button>
            )}
          </div>

          {chats.length === 0 ? (
            <div className="px-3 py-3 text-xs text-gray-400 italic font-sans">
              No recent chats
            </div>
          ) : (
            chats.map(chat => {
              const isActive = activeChatId === chat.id;
              const isEditing = editingChatId === chat.id;

              if (isEditing) {
                return (
                  <div
                    key={chat.id}
                    className="p-1.5 bg-white border border-[#FF6B00] rounded-xl shadow-sm flex items-center gap-1"
                  >
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => handleKeyDownRename(chat.id, e)}
                      autoFocus
                      className="w-full text-xs text-gray-900 bg-gray-50 border border-gray-200 rounded-lg px-2 py-1 outline-none focus:bg-white"
                    />
                    <button
                      onClick={(e) => handleSaveRename(chat.id, e)}
                      className="text-[#FF6B00] hover:bg-orange-50 px-1.5 py-0.5 rounded text-xs font-bold"
                      title="Save"
                    >
                      ✓
                    </button>
                    <button
                      onClick={handleCancelRename}
                      className="text-gray-400 hover:bg-gray-100 px-1.5 py-0.5 rounded text-xs font-bold"
                      title="Cancel"
                    >
                      ✕
                    </button>
                  </div>
                );
              }

              return (
                <div
                  key={chat.id}
                  onClick={() => {
                    onSelectChat(chat.id);
                    if (onCloseMobile) onCloseMobile();
                  }}
                  onDoubleClick={(e) => handleStartRename(chat, e)}
                  className={`
                    group flex items-center justify-between px-3 py-2 rounded-xl text-xs cursor-pointer transition-all duration-150
                    ${isActive
                      ? 'bg-gray-100 text-gray-900 font-semibold border border-gray-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <span className="truncate pr-2">{chat.title || 'New Conversation'}</span>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => handleStartRename(chat, e)}
                      className="text-gray-400 hover:text-[#FF6B00] p-0.5 rounded"
                      title="Rename"
                    >
                      <IconEdit />
                    </button>
                    <button
                      onClick={(e) => onDeleteChat(chat.id, e)}
                      className="text-gray-400 hover:text-rose-500 p-0.5 rounded"
                      title="Delete"
                    >
                      <IconX />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Bottom User Card */}
        <div className="p-3 m-3 bg-white border border-gray-200 rounded-2xl flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-amber-500 flex items-center justify-center text-white flex-shrink-0">
              <IconUser />
            </div>
            <div className="text-xs">
              <p className="font-bold text-gray-900 leading-tight">Citizen User</p>
              <p className="text-[10px] text-gray-400 flex items-center gap-1">
                <span className={`w-1.5 h-1.5 rounded-full ${healthy ? 'bg-emerald-500' : 'bg-gray-400'}`} />
                {healthy ? 'Online' : 'Offline'}
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
