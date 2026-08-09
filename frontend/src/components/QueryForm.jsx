import { useState } from 'react';

const MAX_CHARS = 500;

const DOMAINS = [
  {
    key: 'agri',
    emoji: '🌾',
    title: 'Agriculture & Farming',
    desc: 'Financial support, crop loans, subsidies & PM-KISAN details',
    query: 'What financial assistance is available for farmers?',
    bg: 'bg-green-50/80 hover:bg-green-100/80',
    border: 'border-green-200 hover:border-green-400',
    activeBorder: 'border-green-500 bg-green-100/90',
    iconBg: 'bg-green-200/60 text-green-800',
  },
  {
    key: 'edu',
    emoji: '🎓',
    title: 'Education & Student Support',
    desc: 'Scholarships, higher education funding & student welfare',
    query: 'What government schemes are available for students?',
    bg: 'bg-blue-50/80 hover:bg-blue-100/80',
    border: 'border-blue-200 hover:border-blue-400',
    activeBorder: 'border-blue-500 bg-blue-100/90',
    iconBg: 'bg-blue-200/60 text-blue-800',
  },
  {
    key: 'health',
    emoji: '🏥',
    title: 'Healthcare & Insurance',
    desc: 'Medical relief, Ayushman Bharat & healthcare assistance',
    query: 'What government schemes provide financial assistance for healthcare?',
    bg: 'bg-rose-50/80 hover:bg-rose-100/80',
    border: 'border-rose-200 hover:border-rose-400',
    activeBorder: 'border-rose-500 bg-rose-100/90',
    iconBg: 'bg-rose-200/60 text-rose-800',
  },
];

const QUICK_SUGGESTIONS = [
  'Am I eligible for PM-KISAN scheme?',
  'Scholarships for college students',
  'Government health insurance schemes',
  'Crop loan assistance for small farmers',
];

export default function QueryForm({ queryText, setQueryText, isLoading, onSubmit }) {
  const [selectedDomain, setSelectedDomain] = useState(null);

  const handleDomainSelect = (domain) => {
    setSelectedDomain(domain.key);
    setQueryText(domain.query);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (queryText.trim() && !isLoading) {
      onSubmit(queryText.trim());
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Domain Quick Select */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {DOMAINS.map((d) => (
          <button
            key={d.key}
            onClick={() => handleDomainSelect(d)}
            className={`text-left p-4 rounded-2xl border transition-all duration-200 hover:-translate-y-1 hover:shadow-md cursor-pointer ${
              selectedDomain === d.key
                ? `${d.activeBorder} shadow-sm`
                : `${d.bg} ${d.border}`
            }`}
          >
            <div className={`w-10 h-10 rounded-xl ${d.iconBg} flex items-center justify-center text-xl mb-3`}>
              {d.emoji}
            </div>
            <h3 className="font-heading font-bold text-sm text-gray-900 mb-1">{d.title}</h3>
            <p className="text-xs text-gray-600 leading-relaxed">{d.desc}</p>
          </button>
        ))}
      </div>

      {/* Main Form Box */}
      <div className="bg-white rounded-2xl border border-gray-200 p-6 md:p-8 shadow-md space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="font-heading font-bold text-xl text-gray-900 flex items-center gap-2">
              <span>💬</span> Ask PolicyPilot AI
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Enter your scheme question in natural language below
            </p>
          </div>
          <span className="text-xs font-semibold text-brand-600 bg-brand-50 border border-brand-200 px-3 py-1 rounded-full self-start sm:self-auto">
            Multi-Agent AI Ready
          </span>
        </div>

        {/* Suggestion Chips */}
        <div className="flex flex-wrap gap-2 pt-1">
          {QUICK_SUGGESTIONS.map((chip) => (
            <button
              key={chip}
              onClick={() => setQueryText(chip)}
              className="px-3 py-1.5 bg-gray-100 hover:bg-brand-50 border border-gray-200 hover:border-brand-200 text-gray-700 hover:text-brand-700 rounded-full text-xs font-medium transition-colors cursor-pointer"
            >
              {chip}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <textarea
              value={queryText}
              onChange={(e) => {
                if (e.target.value.length <= MAX_CHARS) setQueryText(e.target.value);
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleSubmit(e);
              }}
              rows={4}
              placeholder="e.g. What financial assistance is available for farmers in Tamil Nadu?"
              className="w-full p-4 text-sm text-gray-800 bg-gray-50 border border-gray-200 rounded-xl outline-none transition-all duration-200 focus:border-brand-400 focus:bg-white focus:ring-2 focus:ring-brand-100 placeholder-gray-400 leading-relaxed resize-y"
            />
            <span
              className={`absolute bottom-3 right-3 text-xs pointer-events-none ${
                queryText.length > 450 ? 'text-red-500 font-bold' : 'text-gray-400'
              }`}
            >
              {queryText.length}/{MAX_CHARS}
            </span>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
            <div className="text-xs text-gray-400 flex items-center gap-1.5">
              <span>⌨️</span> Press <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-200 rounded text-[10px] font-mono">Ctrl + Enter</kbd> to execute
            </div>

            <button
              type="submit"
              disabled={isLoading || !queryText.trim()}
              className="btn-primary w-full sm:w-auto px-8 py-3 text-base justify-center"
            >
              {isLoading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                  Analyzing Query…
                </>
              ) : (
                <>
                  <span>🚀</span> Submit Query
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
