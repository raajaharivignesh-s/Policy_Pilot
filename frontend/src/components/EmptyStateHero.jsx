// Outline SVG icons for each category — no colors, no backgrounds
const IconLeaf = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
  </svg>
);
const IconGraduate = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
    <path d="M6 12v5c3 3 9 3 12 0v-5"/>
  </svg>
);
const IconHeart = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
  </svg>
);
const IconShield = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
);
const IconArrow = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
  </svg>
);

const CARDS = [
  {
    category: 'AGRICULTURE',
    title: 'Farmer Financial Relief',
    query: 'What financial assistance is available for farmers under PM-KISAN?',
    borderColor: 'border-l-emerald-400',
    Icon: IconLeaf,
  },
  {
    category: 'EDUCATION',
    title: 'Student Scholarships',
    query: 'What government schemes and scholarships are available for students?',
    borderColor: 'border-l-blue-400',
    Icon: IconGraduate,
  },
  {
    category: 'HEALTHCARE',
    title: 'Medical Insurance Relief',
    query: 'What government schemes provide financial assistance for healthcare?',
    borderColor: 'border-l-purple-400',
    Icon: IconHeart,
  },
  {
    category: 'ELIGIBILITY',
    title: 'Rule Eligibility Check',
    query: 'Am I eligible for small farmer loan and subsidy schemes?',
    borderColor: 'border-l-orange-400',
    Icon: IconShield,
  },
];

export default function EmptyStateHero({ onCardClick }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 md:p-10 max-w-4xl mx-auto text-center space-y-8 animate-fade-up">
      {/* Title & Tagline — consistent sans font */}
      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-center gap-2 mb-1">
          <span className="text-3xl text-[#FF6B00] leading-none">✴️</span>
        </div>
        <h2 className="font-sans text-4xl md:text-5xl font-bold text-gray-900 tracking-tight">
          PolicyPilot <span className="text-[#FF6B00]">AI</span>
        </h2>
        <p className="text-gray-500 text-sm max-w-xl mx-auto leading-relaxed font-sans">
          Explore government schemes across Agriculture, Education, and Healthcare.
          Verified details and deterministic eligibility evaluation.
        </p>
      </div>

      {/* 4 Suggestion Cards — outline icons, no colored backgrounds */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full text-left">
        {CARDS.map((card, i) => (
          <button
            key={i}
            onClick={() => onCardClick(card.query)}
            className={`bg-white/90 backdrop-blur-xs rounded-2xl border border-gray-200 border-l-4 ${card.borderColor} p-5 shadow-sm hover:shadow-md transition-all duration-200 flex items-center justify-between gap-4 group cursor-pointer`}
          >
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                {/* Outline icon — no colored container */}
                <span className="text-gray-500 group-hover:text-[#FF5500] transition-colors">
                  <card.Icon />
                </span>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-gray-500">
                  {card.category}
                </span>
              </div>

              <h3 className="font-sans font-semibold text-base text-gray-900 group-hover:text-[#FF5500] transition-colors leading-snug">
                {card.title}
              </h3>

              <p className="text-xs text-gray-400 leading-relaxed italic">
                "{card.query}"
              </p>
            </div>

            {/* Arrow — no colored background */}
            <span className="text-gray-400 group-hover:text-[#FF5500] transition-colors flex-shrink-0">
              <IconArrow />
            </span>
          </button>
        ))}
      </div>
    </div>
  );
}
