export default function EligibilityCard({ eligibilityResults }) {
  if (!eligibilityResults || eligibilityResults.length === 0) return null;

  return (
    <div className="card p-6 animate-fade-up">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-9 h-9 rounded-xl bg-green-50 flex items-center justify-center text-lg">
          📋
        </div>
        <div>
          <h3 className="font-heading font-bold text-base text-gray-900">Eligibility Evaluation</h3>
          <p className="text-xs text-gray-400">Rule-based assessment results</p>
        </div>
      </div>

      <div className="space-y-3">
        {eligibilityResults.map((item, i) => {
          const status = item.status || 'insufficient_information';
          const name = item.scheme_name || item.name || `Scheme ${i + 1}`;
          const reason = item.reason || '';

          let badgeClass = 'badge-insufficient';
          let badgeIcon = '⚠️';
          let badgeText = 'Insufficient Info';

          if (status === 'eligible') {
            badgeClass = 'badge-eligible';
            badgeIcon = '✅';
            badgeText = 'Eligible';
          } else if (status === 'ineligible') {
            badgeClass = 'badge-ineligible';
            badgeIcon = '❌';
            badgeText = 'Ineligible';
          }

          return (
            <div key={i} className="p-4 rounded-xl border border-gray-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <h4 className="font-heading font-semibold text-sm text-gray-900">{name}</h4>
                {reason && <p className="text-xs text-gray-500 leading-relaxed">{reason}</p>}
              </div>
              <span className={`${badgeClass} flex-shrink-0`}>
                {badgeIcon} {badgeText}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
