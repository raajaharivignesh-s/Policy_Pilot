import FinalResponseCard from './FinalResponseCard';
import RecommendationsCard from './RecommendationsCard';
import EligibilityCard from './EligibilityCard';
import DocumentsCard from './DocumentsCard';
import LogoMark from './LogoMark';

const IconWarn = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
    <path d="M12 9v4"/><path d="M12 17h.01"/>
  </svg>
);

export default function ChatMessage({ message, onRerun }) {
  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end animate-fade-up">
        <div className="max-w-2xl bg-blue-600 text-white rounded-2xl rounded-tr-sm px-5 py-3.5 shadow-sm text-sm leading-relaxed">
          <p>{message.text}</p>
          <span className="block text-[10px] text-blue-200 text-right mt-1 opacity-80">
            {message.timestamp}
          </span>
        </div>
      </div>
    );
  }

  // Assistant message
  const { data, error } = message;

  return (
    <div className="flex items-start gap-4 max-w-4xl animate-fade-up">
      {/* AI avatar — orange star to match brand */}
      <div className="w-9 h-9 rounded-2xl  text-white flex items-center justify-center text-base shadow-sm flex-shrink-0 mt-1 select-none">
        <LogoMark size={24} />
      </div>

      <div className="flex-1 space-y-4 min-w-0">
        {/* Error message */}
        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-start gap-3">
            <IconWarn />
            <div>
              <h4 className="font-bold mb-1">Execution Error</h4>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* AI Result Cards */}
        {data && (
          <div className="space-y-4">
            <FinalResponseCard data={data} onRerun={onRerun} />
            <RecommendationsCard recommendations={data.recommendations} />
            <EligibilityCard eligibilityResults={data.eligibility_results} />
            <DocumentsCard requiredDocuments={data.required_documents} />
          </div>
        )}

        <span className="block text-[10px] text-gray-400">
          {message.timestamp}
        </span>
      </div>
    </div>
  );
}
