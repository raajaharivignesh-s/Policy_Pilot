import { useState } from 'react';

export default function ChatHeader({
  title,
  activeChatId,
  onRenameChat,
  onOpenMobileSidebar,
  onGoHome,
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(title);

  const handleStartEditing = () => {
    setEditTitle(title || 'Scheme Discovery Workspace');
    setIsEditing(true);
  };

  const handleSave = () => {
    if (editTitle.trim() && activeChatId && onRenameChat) {
      onRenameChat(activeChatId, editTitle.trim());
    }
    setIsEditing(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-30 font-sans shadow-sm">
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="lg:hidden p-2 text-gray-700 hover:bg-gray-100 rounded-xl"
        >
          ☰
        </button>

        <div className="flex items-center gap-2">
          {isEditing ? (
            <div className="flex items-center gap-1.5">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSave();
                  if (e.key === 'Escape') setIsEditing(false);
                }}
                autoFocus
                className="font-serif-title font-bold text-lg md:text-xl text-gray-900 border border-[#FF5500] rounded-lg px-2.5 py-0.5 outline-none bg-orange-50/50"
              />
              <button
                onClick={handleSave}
                className="px-2.5 py-1 bg-[#FF5500] text-white text-xs font-semibold rounded-lg hover:bg-[#E64D00]"
              >
                Save
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-semibold rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <h2 className="font-serif-title font-bold text-xl md:text-2xl text-gray-900 tracking-tight">
                {title || 'Scheme Discovery Workspace'}
              </h2>
              {activeChatId && (
                <button
                  onClick={handleStartEditing}
                  className="w-7 h-7 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-xs text-gray-500 cursor-pointer shadow-sm hover:bg-gray-100 transition-colors"
                  title="Rename workspace"
                >
                  ✏️
                </button>
              )}
            </div>
          )}
        </div>
      </div>

    </header>
  );
}
