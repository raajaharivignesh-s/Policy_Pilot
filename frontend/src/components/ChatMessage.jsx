import FinalResponseCard from './FinalResponseCard';
import RecommendationsCard from './RecommendationsCard';
import EligibilityCard from './EligibilityCard';
import DocumentsCard from './DocumentsCard';

export default function ChatMessage({ message }) {
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
      <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white flex items-center justify-center text-base shadow-sm flex-shrink-0 mt-1">
        🧭
      </div>

      <div className="flex-1 space-y-4 min-w-0">
        {/* Error message */}
        {error && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-start gap-3">
            <span className="text-base">⚠️</span>
            <div>
              <h4 className="font-bold mb-1">Execution Error</h4>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* AI Result Cards */}
        {data && (
          <div className="space-y-4">
            <FinalResponseCard data={data} />
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
