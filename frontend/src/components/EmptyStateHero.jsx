const CARDS = [
  {
    category: 'AGRICULTURE',
    title: 'Farmer Financial Relief',
    query: 'What financial assistance is available for farmers under PM-KISAN?',
    borderColor: 'border-l-emerald-500',
    tagColor: 'text-emerald-600',
    iconBg: 'bg-emerald-50 text-emerald-600',
    arrowBg: 'bg-emerald-50 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white',
    icon: '🌱',
  },
  {
    category: 'EDUCATION',
    title: 'Student Scholarships',
    query: 'What government schemes and scholarships are available for students?',
    borderColor: 'border-l-blue-500',
    tagColor: 'text-blue-600',
    iconBg: 'bg-blue-50 text-blue-600',
    arrowBg: 'bg-blue-50 text-blue-600 group-hover:bg-blue-600 group-hover:text-white',
    icon: '🎓',
  },
  {
    category: 'HEALTHCARE',
    title: 'Medical Insurance Relief',
    query: 'What government schemes provide financial assistance for healthcare?',
    borderColor: 'border-l-purple-500',
    tagColor: 'text-purple-600',
    iconBg: 'bg-purple-50 text-purple-600',
    arrowBg: 'bg-purple-50 text-purple-600 group-hover:bg-purple-600 group-hover:text-white',
    icon: '💜',
  },
  {
    category: 'ELIGIBILITY',
    title: 'Rule Eligibility Check',
    query: 'Am I eligible for small farmer loan and subsidy schemes?',
    borderColor: 'border-l-orange-500',
    tagColor: 'text-orange-600',
    iconBg: 'bg-orange-50 text-orange-600',
    arrowBg: 'bg-orange-50 text-orange-600 group-hover:bg-orange-600 group-hover:text-white',
    icon: '🛡️',
  },
];

export default function EmptyStateHero({ onCardClick }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 md:p-10 max-w-4xl mx-auto text-center space-y-8 animate-fade-up">
      {/* Title & Tagline matching screenshot */}
      <div className="space-y-3 pt-2">
        <h2 className="font-serif-title text-4xl md:text-5xl font-bold text-gray-900 tracking-tight">
          PolicyPilot <span className="text-[#FF6B00] relative inline-block">AI<span className="absolute -bottom-1 left-0 right-0 h-1 bg-[#FF6B00] rounded-full" /></span>
        </h2>

        <p className="text-gray-600 text-xs md:text-sm max-w-xl mx-auto leading-relaxed">
          Explore government schemes across Agriculture, Education, and Healthcare. Verified details and deterministic eligibility evaluation.
        </p>
      </div>

      {/* 4 Big Colored Left-Border Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full text-left">
        {CARDS.map((card, i) => (
          <button
            key={i}
            onClick={() => onCardClick(card.query)}
            className={`bg-white/90 backdrop-blur-xs rounded-2xl border border-gray-200 border-l-4 ${card.borderColor} p-5 shadow-sm hover:shadow-md transition-all duration-200 flex items-center justify-between gap-4 group cursor-pointer`}
          >
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className={`w-8 h-8 rounded-xl ${card.iconBg} flex items-center justify-center text-sm font-bold flex-shrink-0`}>
                  {card.icon}
                </span>
                <span className={`text-[10px] font-extrabold uppercase tracking-wider ${card.tagColor}`}>
                  {card.category}
                </span>
              </div>

              <h3 className="font-serif-title font-bold text-base text-gray-900 group-hover:text-[#FF5500] transition-colors leading-snug">
                {card.title}
              </h3>

              <p className="text-xs text-gray-500 leading-relaxed italic">
                "{card.query}"
              </p>
            </div>

            {/* Right arrow button */}
            <span className={`w-8 h-8 rounded-full ${card.arrowBg} flex items-center justify-center text-sm transition-all duration-200 flex-shrink-0`}>
              →
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
