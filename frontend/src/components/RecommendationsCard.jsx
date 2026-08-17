import indiaEmblem from '../assets/india emblem.png';

// Government of India National Emblem
const GovEmblem = () => (
  <img
    src={indiaEmblem}
    alt="Government of India Emblem"
    width={44}
    height={44}
    style={{ objectFit: 'contain' }}
  />
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {recommendations.map((scheme, i) => {
          let name = scheme.scheme_name || scheme.name || `Scheme ${i + 1}`;
          // Strip markdown links if present, e.g. "[Link Text](url)" -> "Link Text"
          name = name.replace(/\[(.*?)\]\(.*?\)/g, '$1');
          
          const desc = scheme.description || scheme.benefits || scheme.summary || '';
          const tags = scheme.tags || scheme.categories || [];
          const benefitText = scheme.benefit_amount || scheme.benefit || 'Verified Benefit';
          const officialUrl = scheme.official_url || scheme.source_url || scheme.domain_url || scheme.source || '';
          const hasUrl = !!officialUrl;
          const linkUrl = hasUrl
            ? officialUrl.startsWith('http')
              ? officialUrl
              : `https://${officialUrl}`
            : null;
          const displayUrl = hasUrl
            ? officialUrl.replace(/^https?:\/\//, '')
            : null;
          const bannerColor = bannerColors[i % bannerColors.length];

          const CardWrapper = hasUrl ? 'a' : 'div';
          const cardProps = hasUrl
            ? { href: linkUrl, target: '_blank', rel: 'noopener noreferrer' }
            : {};

          return (
            <CardWrapper
              key={i}
              {...cardProps}
              className={`bg-white border border-[#E6E4DF] rounded-2xl p-4 flex flex-col justify-between hover:shadow-lg hover:shadow-orange-500/5 hover:border-amber-300 transition-all duration-200 group ${hasUrl ? 'cursor-pointer' : ''} no-underline`}
            >
              <div>
                {/* Top Banner — national emblem + label centered */}
                <div className={`w-full h-32 rounded-xl bg-gradient-to-br ${bannerColor} mb-3 group-hover:scale-[1.02] transition-transform duration-200 flex flex-col items-center justify-center gap-1.5`}>
                  <GovEmblem />
                  <span className="text-[10px] font-bold tracking-widest text-gray-600 uppercase text-center">
                    Government of India
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
            </CardWrapper>
          );
        })}
      </div>
    </div>
  );
}
