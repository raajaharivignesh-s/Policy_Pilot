export default function ProcessingStepper({ stepLabels, activeStep, doneSteps }) {
  return (
    <div className="card p-5 mb-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">
        AI Processing Pipeline
      </p>
      <div className="relative flex items-start justify-between">
        {/* Connector line */}
        <div className="absolute top-3.5 left-3.5 right-3.5 h-0.5 bg-gray-200 z-0" />
        {/* Progress fill */}
        {doneSteps.length > 0 && (
          <div
            className="absolute top-3.5 left-3.5 h-0.5 bg-brand-500 z-0 transition-all duration-700"
            style={{ width: `${(doneSteps.length / (stepLabels.length - 1)) * 100}%` }}
          />
        )}

        {stepLabels.map((label, i) => {
          const isDone   = doneSteps.includes(i);
          const isActive = activeStep === i;

          return (
            <div key={label} className="relative z-10 flex flex-col items-center gap-2 flex-1">
              <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all duration-500 ${
                isDone
                  ? 'bg-brand-600 border-brand-600 text-white'
                  : isActive
                  ? 'bg-brand-100 border-brand-500 text-brand-600 animate-step-pulse'
                  : 'bg-white border-gray-200 text-gray-400'
              }`}>
                {isDone ? '✓' : i + 1}
              </div>
              <span className={`text-center leading-tight transition-colors duration-300 ${
                isDone || isActive ? 'text-brand-700 font-medium' : 'text-gray-400'
              }`} style={{ fontSize: '9px' }}>
                {label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
