export default function RecommendationsCard({ recommendations }) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="my-6 space-y-4 animate-fade-up">
      <div className="flex items-center justify-between">
        <h3 className="font-serif-title text-xl text-gray-900 font-semibold">
          Recommended Government Schemes
        </h3>
        <span className="text-xs text-gray-500 font-medium">
          {recommendations.length} scheme{recommendations.length > 1 ? 's' : ''} matched
        </span>
      </div>

      {/* Grid of Nomi AI visual cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {recommendations.map((scheme, i) => {
          const name = scheme.scheme_name || scheme.name || `Scheme ${i + 1}`;
          const desc = scheme.description || scheme.benefits || scheme.summary || '';
          const tags = scheme.tags || scheme.categories || [];
          const benefitText = scheme.benefit_amount || scheme.benefit || 'Verified Benefit';
          const domainUrl = scheme.domain_url || scheme.source || 'india.gov.in';

          // Color banners
          const colors = [
            'from-amber-100 to-orange-50 text-amber-900',
            'from-blue-100 to-indigo-50 text-blue-900',
            'from-emerald-100 to-teal-50 text-emerald-900',
            'from-rose-100 to-pink-50 text-rose-900',
          ];
          const bannerColor = colors[i % colors.length];

          return (
            <div
              key={i}
              className="bg-white border border-[#E6E4DF] rounded-2xl p-4 flex flex-col justify-between hover:shadow-lg hover:shadow-orange-500/5 hover:border-amber-300 transition-all duration-200 group"
            >
              <div>
                {/* Visual Top Banner */}
                <div className={`w-full h-36 rounded-xl bg-gradient-to-br ${bannerColor} p-4 flex flex-col justify-between mb-3 group-hover:scale-[1.02] transition-transform duration-200`}>
                  <div className="flex justify-between items-start">
                    <span className="text-2xl">🏛️</span>
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-white/80 backdrop-blur-xs px-2 py-0.5 rounded-md text-gray-800">
                      {benefitText}
                    </span>
                  </div>
                  <span className="text-xs font-serif-title font-bold text-gray-900 line-clamp-1">
                    {name}
                  </span>
                </div>

                {/* Card Title & Desc */}
                <h4 className="font-serif-title font-bold text-base text-gray-900 mb-1 leading-snug group-hover:text-[#E66946] transition-colors">
                  {name}
                </h4>

                <p className="text-xs text-gray-500 line-clamp-3 leading-relaxed mb-3">
                  {desc}
                </p>

                {/* Category tags */}
                {Array.isArray(tags) && tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {tags.slice(0, 2).map((t, idx) => (
                      <span key={idx} className="text-[10px] bg-[#F1EFEA] text-gray-700 px-2 py-0.5 rounded-full font-medium">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Bottom Domain Link matching Nomi AI (e.g. ikea.com ↗) */}
              <div className="pt-3 border-t border-[#F1EFEA] flex items-center justify-between text-xs text-gray-500">
                <span className="flex items-center gap-1 text-[11px] font-medium text-amber-800">
                  <span>🌐</span> {domainUrl}
                </span>
                <span className="text-gray-400 group-hover:text-gray-700 text-xs">↗</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
