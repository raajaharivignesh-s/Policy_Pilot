import { useState } from 'react';

const DOMAIN_EMOJI = { agriculture: '🌾', education: '🎓', healthcare: '🏥' };

export default function FinalResponseCard({ data }) {
  const [copied, setCopied] = useState(false);
  const { final_response, intent, domain } = data;

  const handleCopy = () => {
    if (final_response) {
      navigator.clipboard.writeText(final_response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="bg-white border border-[#E6E4DF] rounded-2xl p-6 shadow-xs animate-fade-up space-y-4 font-sans">
      {/* Response content */}
      <div className="text-sm md:text-base text-gray-800 leading-relaxed whitespace-pre-wrap font-sans">
        {final_response || 'No response generated.'}
      </div>

      {/* Meta tags */}
      {(intent || domain) && (
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#F1EFEA]">
          {intent && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-[#F1EFEA] text-gray-700">
              🎯 {intent.replace(/_/g, ' ')}
            </span>
          )}
          {domain && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
              {DOMAIN_EMOJI[domain] || '📂'} {domain.charAt(0).toUpperCase() + domain.slice(1)}
            </span>
          )}
        </div>
      )}

      {/* Nomi AI Action buttons: Copy & Try again */}
      <div className="flex items-center justify-end gap-3 pt-2 text-xs text-gray-500 font-medium">
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-[#F1EFEA] hover:text-gray-900 transition-colors cursor-pointer"
        >
          <span>{copied ? '✓ Copied' : '📋 Copy'}</span>
        </button>
        <button
          onClick={() => window.location.reload()}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-[#F1EFEA] hover:text-gray-900 transition-colors cursor-pointer"
        >
          <span>🔄 Try again</span>
        </button>
      </div>
    </div>
  );
}
