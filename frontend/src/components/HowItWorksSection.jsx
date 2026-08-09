const STEPS = [
  {
    num: '1',
    emoji: '💬',
    title: 'Ask Naturally',
    desc: 'Enter your question about any government scheme in plain English. Optionally add your citizen profile for precision.',
  },
  {
    num: '2',
    emoji: '⚙️',
    title: 'Multi-Agent Processing',
    desc: 'Our AI pipeline classifies intent, retrieves verified scheme data, checks domain knowledge, and runs rule evaluations.',
  },
  {
    num: '3',
    emoji: '🎯',
    title: 'Get Verified Results',
    desc: 'Receive tailored scheme recommendations, clear eligibility status, required documents, and citizen-friendly answers.',
  },
];

const FEATURES = [
  {
    icon: '🛡️',
    title: 'Source Verification',
    desc: 'Filters out unverified or hallucinated scheme details using trusted knowledge bases.',
  },
  {
    icon: '📊',
    title: 'Deterministic Rules',
    desc: 'Evaluates age, state, land holding, and income against exact scheme rules.',
  },
  {
    icon: '🌾',
    title: '3 Core Domains',
    desc: 'Full support for Agriculture, Education, and Healthcare schemes.',
  },
  {
    icon: '⚡',
    title: 'FastAPI Backend',
    desc: 'Powered by LangGraph multi-agent architecture for robust reasoning.',
  },
];

export default function HowItWorksSection() {
  return (
    <section id="how-it-works" className="py-20 px-6 bg-white border-t border-gray-200">
      <div className="max-w-6xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="section-label mb-2">Architecture</span>
          <h2 className="font-heading font-bold text-3xl md:text-4xl text-gray-900 mb-4">
            How PolicyPilot Works
          </h2>
          <p className="text-gray-500 text-sm md:text-base">
            Combining multi-agent AI orchestration, semantic hybrid retrieval, and rule-based evaluation.
          </p>
        </div>

        {/* 3 Step Flow */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-20">
          {STEPS.map((step) => (
            <div
              key={step.num}
              className="relative card p-8 text-center hover:-translate-y-1.5 transition-all duration-300 hover:shadow-lg border-gray-200"
            >
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 w-7 h-7 rounded-full bg-brand-600 text-white text-xs font-bold flex items-center justify-center">
                {step.num}
              </div>
              <div className="text-4xl mb-4 mt-2">{step.emoji}</div>
              <h3 className="font-heading font-bold text-lg text-gray-900 mb-2">{step.title}</h3>
              <p className="text-xs text-gray-500 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {FEATURES.map((feat) => (
            <div key={feat.title} className="p-4 rounded-xl bg-gray-50 border border-gray-200 flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-lg bg-brand-100 text-brand-600 flex items-center justify-center text-lg flex-shrink-0">
                {feat.icon}
              </div>
              <div>
                <h4 className="font-heading font-semibold text-sm text-gray-900 mb-0.5">{feat.title}</h4>
                <p className="text-xs text-gray-500 leading-relaxed">{feat.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
