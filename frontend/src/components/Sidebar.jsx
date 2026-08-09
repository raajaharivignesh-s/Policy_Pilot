import { useState, useEffect } from 'react';
import { checkHealth } from '../api/query';

export default function Sidebar({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  onClearAll,
  isOpen,
  onCloseMobile,
  onGoToLanding,
}) {
  const [healthy, setHealthy] = useState(null);

  useEffect(() => {
    checkHealth().then(setHealthy);
  }, []);

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 bg-black/40 z-40 lg:hidden backdrop-blur-xs"
        />
      )}

      {/* Pure White Crisp Sidebar Matching Screenshot */}
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
            <span className="text-2xl text-[#FF6B00]">✴️</span>
            <span className="font-serif-title font-bold text-xl text-gray-900 tracking-tight">
              PolicyPilot <span className="text-[#FF6B00] font-normal">AI</span>
            </span>
          </div>
          <button
            onClick={onGoToLanding}
            className="text-gray-400 hover:text-gray-700 text-xs p-1 rounded-md transition-colors"
            title="Collapse / Home"
          >
            «
          </button>
        </div>

        {/* + New Chat Button (Screenshot styling: white/orange tint with thin orange border) */}
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

        {/* Sidebar Nav Links */}
        <div className="px-3 py-1 space-y-0.5 text-xs font-medium text-gray-700">
          <button
            onClick={() => {
              if (onGoToLanding) onGoToLanding();
              if (onCloseMobile) onCloseMobile();
            }}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer text-left"
          >
            <span className="text-gray-500 text-sm">🔍</span> Explore Schemes
          </button>

          <div className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer text-left">
            <div className="flex items-center gap-3">
              <span className="text-gray-500 text-sm">🌁</span> Categories
            </div>
          </div>

          <div className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer text-left">
            <div className="flex items-center gap-3">
              <span className="text-gray-500 text-sm">🔖</span> Saved Schemes
            </div>
            <span className="text-[10px] bg-[#FFEFEA] text-[#FF6B00] px-2 py-0.5 rounded-full font-bold">
              32
            </span>
          </div>

          <div className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer text-left">
            <span className="text-gray-500 text-sm">⚙️</span> System Settings
          </div>
        </div>

        <div className="px-4 py-2">
          <div className="h-px bg-gray-100 w-full" />
        </div>

        {/* Recent Chats Section */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
          <div className="px-3 pb-2 flex items-center justify-between">
            <span className="text-[11px] font-semibold text-gray-400">
              Recent Chats
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
            <div className="px-3 py-3 text-xs text-gray-400 italic font-serif-title">
              No recent chats
            </div>
          ) : (
            chats.map(chat => {
              const isActive = activeChatId === chat.id;

              return (
                <div
                  key={chat.id}
                  onClick={() => {
                    onSelectChat(chat.id);
                    if (onCloseMobile) onCloseMobile();
                  }}
                  className={`
                    group flex items-center justify-between px-3 py-2 rounded-xl text-xs cursor-pointer transition-all duration-150
                    ${isActive
                      ? 'bg-gray-100 text-gray-900 font-semibold border border-gray-200'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <span className="truncate pr-2">{chat.title || 'New Conversation'}</span>
                  <button
                    onClick={(e) => onDeleteChat(chat.id, e)}
                    className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-rose-500 text-xs transition-opacity p-0.5"
                    title="Delete"
                  >
                    ✕
                  </button>
                </div>
              );
            })
          )}
        </div>

        {/* Citizen User Card matching screenshot bottom left */}
        <div className="p-3 m-3 bg-white border border-gray-200 rounded-2xl flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-amber-500 flex items-center justify-center text-white text-xs font-bold shadow-sm">
              👤
            </div>
            <div className="text-xs">
              <p className="font-bold text-gray-900 leading-tight">Citizen User</p>
              <p className="text-[10px] text-gray-400 flex items-center gap-1">
                <span className={`w-1.5 h-1.5 rounded-full ${healthy ? 'bg-emerald-500' : 'bg-gray-400'}`} />
                {healthy ? 'Online' : 'Offline'}
              </p>
            </div>
          </div>
          <button className="text-gray-400 hover:text-gray-700 text-xs p-1">
            🔔
          </button>
        </div>
      </aside>
    </>
  );
}
