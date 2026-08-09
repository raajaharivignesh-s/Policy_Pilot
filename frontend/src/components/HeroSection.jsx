const DOMAIN_PILLS = [
  { key: 'agri',   label: 'Agriculture', emoji: '🌾',
    query: 'What financial assistance is available for farmers?',
    classes: 'bg-green-50 border-green-200 text-green-800 hover:bg-green-100' },
  { key: 'edu',    label: 'Education',   emoji: '🎓',
    query: 'What government schemes are available for students?',
    classes: 'bg-blue-50 border-blue-200 text-blue-800 hover:bg-blue-100' },
  { key: 'health', label: 'Healthcare',  emoji: '🏥',
    query: 'What government schemes provide financial assistance for healthcare?',
    classes: 'bg-rose-50 border-rose-200 text-rose-800 hover:bg-rose-100' },
];

export default function HeroSection({ onOpenDashboard, onDomainSelect }) {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-white via-brand-50 to-orange-50 py-20 md:py-28 px-6 text-center">
      {/* Decorative blobs */}
      <div className="absolute -top-32 -right-32 w-[500px] h-[500px] rounded-full bg-brand-100/40 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-[400px] h-[400px] rounded-full bg-orange-100/40 blur-3xl pointer-events-none" />

      <div className="relative max-w-4xl mx-auto">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-brand-50 border border-brand-200 rounded-full text-xs font-semibold text-brand-700 mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-brand-500 animate-pulse-dot" />
          Multi-Agent AI Platform • Government Scheme Discovery
        </div>

        {/* Headline */}
        <h1 className="font-heading font-extrabold text-5xl md:text-6xl lg:text-7xl text-gray-900 leading-tight mb-5">
          Find Government{' '}
          <span className="bg-gradient-to-r from-brand-600 to-accent-500 bg-clip-text text-transparent">
            Schemes
          </span>{' '}
          Made for You
        </h1>

        <p className="text-gray-500 text-lg md:text-xl max-w-xl mx-auto leading-relaxed mb-10">
          Ask in plain language. PolicyPilot AI searches, verifies, and
          checks eligibility across Agriculture, Education &amp; Healthcare schemes.
        </p>

        {/* Domain Pills */}
        <div className="flex flex-wrap justify-center gap-3 mb-10">
          {DOMAIN_PILLS.map(d => (
            <button
              key={d.key}
              onClick={() => onDomainSelect(d.query)}
              className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold border-1.5 border transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md cursor-pointer ${d.classes}`}
            >
              <span>{d.emoji}</span> {d.label}
            </button>
          ))}
        </div>

        {/* CTA */}
        <div className="flex flex-wrap justify-center gap-4">
          <button onClick={onOpenDashboard} className="btn-primary text-base px-8 py-3.5 cursor-pointer">
            ✨ Ask Your Question
          </button>
          <a href="#how-it-works" className="btn-secondary text-base px-8 py-3.5">
            How it works
          </a>
        </div>
      </div>
    </section>
  );
}
