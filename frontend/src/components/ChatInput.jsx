export default function ChatInput({ queryText, setQueryText, isLoading, onSubmit }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (queryText.trim() && !isLoading) {
      onSubmit();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="sticky bottom-0 bg-gradient-to-t from-[#FAFAFA] via-[#FAFAFA]/90 to-transparent pt-3 pb-6 px-4 md:px-8">
      <div className="max-w-4xl mx-auto space-y-2">
        {/* Rounded Input Container */}
        <form onSubmit={handleSubmit} className="bg-white/95 backdrop-blur-xs rounded-3xl border border-gray-300 shadow-xl p-4 space-y-3 transition-all duration-200 focus-within:border-[#FF5500] focus-within:ring-2 focus-within:ring-orange-100">
          <div className="flex items-start gap-2">
            <span className="text-orange-500 text-lg mt-0.5">✨</span>
            <textarea
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
              placeholder="Ask me anything about government schemes, eligibility, farmer assistance..."
              className="w-full text-sm md:text-base text-gray-900 bg-transparent outline-none resize-none placeholder-gray-400 leading-relaxed font-sans"
            />
          </div>

          <div className="flex items-center justify-between pt-1 border-t border-gray-100">
            <span className="text-xs text-gray-400 font-medium">
              Multi-Agent RAG &amp; Deterministic Eligibility Engine
            </span>

            {/* Mic & Solid Orange Circular Submit Button */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                className="text-gray-400 hover:text-gray-600 p-2 text-sm"
                title="Voice input"
              >
                🎙️
              </button>
              <button
                type="submit"
                disabled={isLoading || !queryText.trim()}
                className="w-10 h-10 rounded-full bg-[#FF5500] hover:bg-[#E64D00] disabled:bg-gray-300 text-white flex items-center justify-center transition-all duration-200 shadow-md shadow-orange-500/30 disabled:shadow-none cursor-pointer disabled:cursor-not-allowed flex-shrink-0"
                title="Send query"
              >
                {isLoading ? (
                  <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                ) : (
                  <span className="text-base font-bold">➢</span>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Footer Disclaimer Note */}
        <p className="text-[11px] text-gray-400 text-center flex items-center justify-center gap-1">
          <span>🛡️</span> Information provided is based on government sources. Please verify at official portals.
        </p>
      </div>
    </div>
  );
}
