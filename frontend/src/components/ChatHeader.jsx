export default function ChatHeader({ title, onOpenMobileSidebar, onGoHome }) {
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
          <h2 className="font-serif-title font-bold text-xl md:text-2xl text-gray-900 tracking-tight">
            {title || 'Scheme Discovery Workspace'}
          </h2>
          <span className="w-7 h-7 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center text-xs text-gray-500 cursor-pointer shadow-sm hover:bg-gray-100">
            ✏️
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onGoHome}
          className="px-4 py-1.5 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 text-xs font-semibold rounded-full shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
        >
          <span>🏠</span> Home
        </button>

        <button
          onClick={() => {
            navigator.clipboard.writeText(window.location.href);
            alert('Workspace URL copied!');
          }}
          className="px-4 py-1.5 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 text-xs font-semibold rounded-full shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
        >
          <span>↗</span> Share
        </button>
      </div>
    </header>
  );
}
