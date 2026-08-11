const STATS = [
  { value: '3', label: 'Domains Covered' },
  { value: '110+', label: 'Tests Passed' },
  { value: 'AI', label: 'Multi-Agent System' },
  { value: '100%', label: 'Verified Info' },
];

export default function StatsBar() {
  return (
    <div className="bg-white border-y border-gray-200 py-5 px-6">
      <div className="max-w-7xl mx-auto flex flex-wrap justify-center gap-8 md:gap-16">
        {STATS.map(stat => (
          <div key={stat.label} className="text-center">
            <p className="font-heading font-bold text-2xl text-[#FF6B00]">{stat.value}</p>
            <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
