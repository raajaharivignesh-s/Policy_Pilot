import { useState } from 'react';

const DOMAIN_EMOJI = {
  agriculture: '🌾',
  education: '🎓',
  healthcare: '🏥',
  general: '🏛️',
};

const DOMAIN_BADGE = {
  agriculture: 'bg-green-50 text-green-700 border-green-200',
  education: 'bg-blue-50 text-blue-700 border-blue-200',
  healthcare: 'bg-rose-50 text-rose-700 border-rose-200',
  general: 'bg-gray-100 text-gray-700 border-gray-200',
};

export default function HistorySidebar({ history, activeId, onSelect, onNewQuery, onClear }) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredHistory = history.filter(item =>
    item.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.domain && item.domain.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <aside className="w-full lg:w-80 bg-white border-l border-gray-200 flex flex-col h-full shadow-sm">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">📜</span>
            <h3 className="font-heading font-bold text-sm text-gray-900">Query History</h3>
            <span className="text-xs bg-brand-50 text-brand-700 border border-brand-200 px-2 py-0.5 rounded-full font-semibold">
              {history.length}
            </span>
          </div>
          {history.length > 0 && (
            <button
              onClick={onClear}
              className="text-xs text-gray-400 hover:text-red-600 transition-colors"
              title="Clear history"
            >
              Clear
            </button>
          )}
        </div>

        {/* New Query Button */}
        <button
          onClick={onNewQuery}
          className="w-full py-2.5 px-4 bg-brand-50 border border-brand-200 text-brand-700 font-semibold text-xs rounded-xl flex items-center justify-center gap-2 hover:bg-brand-100 transition-colors cursor-pointer"
        >
          <span>✨</span> Start New Query
        </button>

        {/* Search input */}
        {history.length > 3 && (
          <input
            type="text"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            placeholder="Search past queries…"
            className="w-full px-3 py-1.5 text-xs bg-gray-50 border border-gray-200 rounded-lg outline-none focus:border-brand-400 focus:bg-white"
          />
        )}
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {filteredHistory.length === 0 ? (
          <div className="py-12 text-center text-gray-400 space-y-2">
            <div className="text-3xl opacity-50">📂</div>
            <p className="text-xs font-medium">No history items yet</p>
            <p className="text-[11px] text-gray-400 px-4">
              Your asked queries and AI recommendations will appear here.
            </p>
          </div>
        ) : (
          filteredHistory.map((item) => {
            const isActive = activeId === item.id;
            const emoji = DOMAIN_EMOJI[item.domain] || '🏛️';
            const badgeClass = DOMAIN_BADGE[item.domain] || DOMAIN_BADGE.general;

            return (
              <button
                key={item.id}
                onClick={() => onSelect(item)}
                className={`w-full text-left p-3 rounded-xl border transition-all duration-200 cursor-pointer space-y-2 ${
                  isActive
                    ? 'bg-brand-50/80 border-brand-400 shadow-sm'
                    : 'bg-white border-gray-100 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold border ${badgeClass}`}>
                    {emoji} {item.domain.toUpperCase()}
                  </span>
                  <span className="text-[10px] text-gray-400">{item.timestamp}</span>
                </div>

                <p className="text-xs text-gray-800 font-medium line-clamp-2 leading-relaxed">
                  {item.query}
                </p>

                {item.recommendationsCount > 0 && (
                  <span className="inline-block text-[10px] font-semibold text-brand-600">
                    ★ {item.recommendationsCount} scheme{item.recommendationsCount > 1 ? 's' : ''} found
                  </span>
                )}
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
}
