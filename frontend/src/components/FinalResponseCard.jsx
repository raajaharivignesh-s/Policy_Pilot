import { useState } from 'react';

// SVG icons
const IconCopy = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
  </svg>
);
const IconCheck = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 6 9 17l-5-5"/>
  </svg>
);
const IconRefresh = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
    <path d="M21 3v5h-5"/>
    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
    <path d="M8 16H3v5"/>
  </svg>
);
const IconTarget = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
  </svg>
);
const IconFolder = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>
  </svg>
);

export default function FinalResponseCard({ data, onRerun }) {
  const [copied, setCopied] = useState(false);
  const { final_response, intent, domain, confidence_score } = data;

  const handleCopy = () => {
    if (final_response) {
      navigator.clipboard.writeText(final_response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-white border border-[#E6E4DF] rounded-2xl p-6 shadow-sm animate-fade-up space-y-4 font-sans">
      {/* Verification & Confidence */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[#F1EFEA]">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="text-xs font-bold text-gray-800">Verified Policy Summary</span>
        </div>
        <span className="text-[10px] bg-amber-50 text-amber-800 border border-amber-200 px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1">
          <IconTarget />
          Confidence: {confidence_score ? `${Math.round(confidence_score * 100)}%` : '100% Rule Match'}
        </span>
      </div>

      {/* Response content */}
      <div className="text-sm md:text-base text-gray-800 leading-relaxed whitespace-pre-wrap font-sans">
        {final_response || 'No response generated.'}
      </div>

      {/* Meta tags */}
      {(intent || domain) && (
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#F1EFEA]">
          {intent && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-[#F1EFEA] text-gray-700">
              <IconTarget /> {intent.replace(/_/g, ' ')}
            </span>
          )}
          {domain && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
              <IconFolder /> {domain.charAt(0).toUpperCase() + domain.slice(1)}
            </span>
          )}
        </div>
      )}

      {/* Action buttons: Copy + Re-answer */}
      <div className="flex items-center justify-end gap-2 pt-2 text-xs text-gray-500 font-medium">
        {onRerun && (
          <button
            onClick={onRerun}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-[#F1EFEA] hover:text-gray-900 transition-colors cursor-pointer"
            title="Regenerate answer"
          >
            <IconRefresh /> Re-answer
          </button>
        )}
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-[#F1EFEA] hover:text-gray-900 transition-colors cursor-pointer"
          title="Copy response"
        >
          {copied ? <><IconCheck /> Copied</> : <><IconCopy /> Copy</>}
        </button>
      </div>
    </div>
  );
}
