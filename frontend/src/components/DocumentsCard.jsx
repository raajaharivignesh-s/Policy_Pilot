export default function DocumentsCard({ requiredDocuments }) {
  if (!requiredDocuments || requiredDocuments.length === 0) return null;

  return (
    <div className="card p-6 animate-fade-up">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-9 h-9 rounded-xl bg-amber-50 flex items-center justify-center text-lg">
          📄
        </div>
        <div>
          <h3 className="font-heading font-bold text-base text-gray-900">Required Documents</h3>
          <p className="text-xs text-gray-400">Documents needed to apply</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {requiredDocuments.map((doc, i) => (
          <div key={i} className="flex items-center gap-2.5 p-3 rounded-lg bg-gray-50 border border-gray-200 text-xs font-medium text-gray-700">
            <span className="text-brand-500 text-sm">📁</span>
            <span>{doc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
