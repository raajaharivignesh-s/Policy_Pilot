// Outline SVG icons
const IconGovBuilding = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect width="16" height="20" x="4" y="2" rx="2" ry="2"/>
    <path d="M9 22v-4h6v4"/>
    <path d="M8 6h.01"/><path d="M16 6h.01"/>
    <path d="M12 6h.01"/><path d="M12 10h.01"/>
    <path d="M12 14h.01"/><path d="M16 10h.01"/>
    <path d="M16 14h.01"/><path d="M8 10h.01"/>
    <path d="M8 14h.01"/>
  </svg>
);
const IconGlobe = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
    <path d="M2 12h20"/>
  </svg>
);
const IconArrowUpRight = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M7 7h10v10"/><path d="M7 17 17 7"/>
  </svg>
);

export default function RecommendationsCard({ recommendations }) {
  if (!recommendations || recommendations.length === 0) return null;

  // Subtle banner color pairs (no emojis, no garish colors)
  const bannerColors = [
    'from-amber-50 to-orange-50 text-amber-900',
    'from-blue-50 to-indigo-50 text-blue-900',
    'from-emerald-50 to-teal-50 text-emerald-900',
    'from-rose-50 to-pink-50 text-rose-900',
  ];

  return (
    <div className="my-6 space-y-4 animate-fade-up font-sans">
      <div className="flex items-center justify-between">
        {/* Consistent Inter font — no serif-title */}
        <h3 className="font-sans text-xl text-gray-900 font-semibold">
          Recommended Government Schemes
        </h3>
        <span className="text-xs text-gray-500 font-medium">
          {recommendations.length} scheme{recommendations.length > 1 ? 's' : ''} matched
        </span>
      </div>

      {/* Grid of scheme cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {recommendations.map((scheme, i) => {
          const name = scheme.scheme_name || scheme.name || `Scheme ${i + 1}`;
          const desc = scheme.description || scheme.benefits || scheme.summary || '';
          const tags = scheme.tags || scheme.categories || [];
          const benefitText = scheme.benefit_amount || scheme.benefit || 'Verified Benefit';
          const domainUrl = scheme.domain_url || scheme.source || 'india.gov.in';
          const bannerColor = bannerColors[i % bannerColors.length];

          return (
            <div
              key={i}
              className="bg-white border border-[#E6E4DF] rounded-2xl p-4 flex flex-col justify-between hover:shadow-lg hover:shadow-orange-500/5 hover:border-amber-300 transition-all duration-200 group"
            >
              <div>
                {/* Top Banner — icon + benefit badge */}
                <div className={`w-full h-32 rounded-xl bg-gradient-to-br ${bannerColor} p-4 flex flex-col justify-between mb-3 group-hover:scale-[1.02] transition-transform duration-200`}>
                  <div className="flex justify-between items-start">
                    {/* Outline government building icon */}
                    <span className="text-gray-600 opacity-80">
                      <IconGovBuilding />
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-wider bg-white/80 backdrop-blur-xs px-2 py-0.5 rounded-md text-gray-800">
                      {benefitText}
                    </span>
                  </div>
                  {/* Scheme name in banner — consistent sans font */}
                  <span className="text-xs font-sans font-bold text-gray-900 line-clamp-1">
                    {name}
                  </span>
                </div>

                {/* Title & Description */}
                <h4 className="font-sans font-bold text-base text-gray-900 mb-1 leading-snug group-hover:text-[#FF5500] transition-colors">
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

              {/* Domain Link */}
              <div className="pt-3 border-t border-[#F1EFEA] flex items-center justify-between text-xs text-gray-500">
                <span className="flex items-center gap-1 text-[11px] font-medium text-amber-800">
                  <IconGlobe /> {domainUrl}
                </span>
                <span className="text-gray-400 group-hover:text-gray-700 transition-colors">
                  <IconArrowUpRight />
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
