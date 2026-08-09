import QueryForm from './QueryForm';
import ResultsSection from './ResultsSection';
import HistorySidebar from './HistorySidebar';

export default function DashboardView({
  queryText,
  setQueryText,
  isLoading,
  result,
  error,
  activeStep,
  doneSteps,
  stepLabels,
  history,
  activeHistoryId,
  onSelectHistory,
  onClearHistory,
  onNewQuery,
  onRunQuery,
  onBackToLanding,
}) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* Top Dashboard Navigation Bar */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40 px-6 py-3">
        <div className="max-w-[1600px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBackToLanding}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors cursor-pointer"
            >
              <span>←</span> Back to Home
            </button>
            <div className="h-4 w-px bg-gray-200 hidden sm:block" />
            <div className="flex items-center gap-2">
              <span className="text-xl">🏛️</span>
              <span className="font-heading font-bold text-lg text-gray-900">
                Policy<span className="text-brand-600">Pilot</span> Workspace
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onNewQuery}
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 bg-brand-50 border border-brand-200 text-brand-700 font-semibold text-xs rounded-lg hover:bg-brand-100 transition-colors cursor-pointer"
            >
              <span>+</span> New Query
            </button>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-50 text-green-700 border border-green-200 rounded-full text-xs font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              API Connected
            </span>
          </div>
        </div>
      </header>

      {/* Main Dashboard Layout (Full page view with History on the right) */}
      <div className="flex-1 max-w-[1600px] w-full mx-auto flex flex-col lg:flex-row overflow-hidden">
        {/* Left / Main Workspace Area */}
        <main className="flex-1 p-6 md:p-8 overflow-y-auto space-y-8">
          {/* Query Input Section */}
          <QueryForm
            queryText={queryText}
            setQueryText={setQueryText}
            isLoading={isLoading}
            onSubmit={(query) => onRunQuery(query)}
          />

          {/* Results Display */}
          <ResultsSection
            result={result}
            error={error}
            isLoading={isLoading}
            activeStep={activeStep}
            doneSteps={doneSteps}
            stepLabels={stepLabels}
          />
        </main>

        {/* Right Sidebar: Query History Panel */}
        <HistorySidebar
          history={history}
          activeId={activeHistoryId}
          onSelect={onSelectHistory}
          onClear={onClearHistory}
          onNewQuery={onNewQuery}
        />
      </div>
    </div>
  );
}
