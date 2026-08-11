import ProcessingStepper from './ProcessingStepper';
import FinalResponseCard from './FinalResponseCard';
import RecommendationsCard from './RecommendationsCard';
import EligibilityCard from './EligibilityCard';
import DocumentsCard from './DocumentsCard';

export default function ResultsSection({ result, error, isLoading, activeStep, doneSteps, stepLabels }) {
  if (!isLoading && !result && !error) return null;

  return (
    <section id="results-section" className="py-12 px-6 max-w-5xl mx-auto space-y-6 scroll-mt-20">
      <div className="flex items-center justify-between">
        <h2 className="font-heading font-bold text-2xl text-gray-900 flex items-center gap-2">
          🔍 Results & Analysis
        </h2>
      </div>

      {/* Stepper while loading or step overview */}
      {(isLoading || doneSteps.length > 0) && (
        <ProcessingStepper stepLabels={stepLabels} activeStep={activeStep} doneSteps={doneSteps} />
      )}

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-start gap-3 animate-fade-up">
          <span className="text-lg">⚠️</span>
          <div>
            <h4 className="font-bold mb-1">Execution Error</h4>
            <p className="text-xs text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Clarification Needed Alert */}
      {result && result.needs_clarification && result.clarification_question && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-sm flex items-start gap-3 animate-fade-up">
          <span className="text-lg">❓</span>
          <div>
            <h4 className="font-bold mb-1">Clarification Requested</h4>
            <p className="text-xs text-amber-800">{result.clarification_question}</p>
          </div>
        </div>
      )}

      {/* Results grid */}
      {result && (
        <div className="space-y-6">
          <FinalResponseCard data={result} />
          <RecommendationsCard recommendations={result.recommendations} />
          <EligibilityCard eligibilityResults={result.eligibility_results} />
          <DocumentsCard requiredDocuments={result.required_documents} />
        </div>
      )}
    </section>
  );
}
