import LogoMark from './LogoMark';

// SVG icon helpers (outline/skeleton style, no colors)
const SvgLeaf = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/>
    <path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>
  </svg>
);
const SvgGraduate = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
    <path d="M6 12v5c3 3 9 3 12 0v-5"/>
  </svg>
);
const SvgHeart = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
  </svg>
);

const DOMAIN_PILLS = [
  { key: 'agri',   label: 'Agriculture', Icon: SvgLeaf,
    query: 'What financial assistance is available for farmers?',
    classes: 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50' },
  { key: 'edu',    label: 'Education',   Icon: SvgGraduate,
    query: 'What government schemes are available for students?',
    classes: 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50' },
  { key: 'health', label: 'Healthcare',  Icon: SvgHeart,
    query: 'What government schemes provide financial assistance for healthcare?',
    classes: 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50' },
];

// Arrow right SVG
const SvgArrow = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
  </svg>
);

export default function HeroSection({ onOpenDashboard, onDomainSelect }) {
  return (
    <section
      className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-6 text-center"
      style={{
        background: 'linear-gradient(135deg, #fff8f5 0%, #fff4ee 40%, #fff 100%)',
      }}
    >
      {/* Subtle decorative blobs */}
      <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-orange-100/30 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-32 -left-32 w-[500px] h-[500px] rounded-full bg-amber-100/25 blur-3xl pointer-events-none" />

      <div className="relative max-w-3xl mx-auto w-full space-y-8">
        {/* Logo mark + brand name */}
        <div className="flex flex-col items-center gap-3">
          <div className="flex items-center gap-3">
            <LogoMark size={38} />
            <span className="font-sans font-bold text-3xl text-gray-900 tracking-tight">
              PolicyPilot <span className="text-[#FF5500]">AI</span>
            </span>
          </div>
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-[#FFEFEA] border border-[#FFD8CC] rounded-full text-[11px] font-semibold text-[#FF6B00]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF5500] animate-pulse" />
            Multi-Agent AI Platform · Government Scheme Discovery
          </div>
        </div>

        {/* Headline — consistent Inter font */}
        <h1 className="font-sans font-extrabold text-5xl md:text-6xl lg:text-7xl text-gray-900 leading-tight">
          Find Government{' '}
          <span className="text-[#FF6B00]">Schemes</span>{' '}
          Made for You
        </h1>

        <p className="font-sans text-gray-500 text-lg md:text-xl max-w-xl mx-auto leading-relaxed">
          Ask in plain language. PolicyPilot AI searches, verifies, and
          checks eligibility across Agriculture, Education &amp; Healthcare schemes.
        </p>

        {/* Domain Pills — outline style, no colored backgrounds */}
        <div className="flex flex-wrap justify-center gap-3">
          {DOMAIN_PILLS.map(d => (
            <button
              key={d.key}
              onClick={() => onDomainSelect(d.query)}
              className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium border transition-all duration-200 cursor-pointer ${d.classes}`}
            >
              <d.Icon /> {d.label}
            </button>
          ))}
        </div>

        {/* CTA */}
        <div className="flex flex-wrap justify-center gap-4 pt-2">
          <button
            onClick={onOpenDashboard}
            className="inline-flex items-center gap-2 bg-[#FF5500] hover:bg-[#E64D00] text-white font-semibold text-base px-8 py-3.5 rounded-xl transition-all duration-200 shadow-lg shadow-orange-500/25 cursor-pointer"
          >
            Ask Your Question <SvgArrow />
          </button>
        </div>

        {/* Trust badge */}
        <p className="text-xs text-gray-400 font-sans">
          Based on official government data · No login required
        </p>
      </div>
    </section>
  );
}
