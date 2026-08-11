export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 py-12 px-6 border-t border-gray-800">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-8 border-b border-gray-800">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-[#FF5500] text-white flex items-center justify-center text-sm font-bold">
                🏛️
              </div>
              <span className="font-heading font-bold text-lg text-white">PolicyPilot AI</span>
            </div>
            <p className="text-xs text-gray-400 leading-relaxed max-w-sm">
              An intelligent multi-agent AI system empowering citizens to discover government schemes, verify details, and check eligibility deterministically.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-wider mb-3">Supported Domains</h4>
            <ul className="space-y-2 text-xs">
              <li>🌾 Agriculture &amp; Farmers</li>
              <li>🎓 Education &amp; Scholarships</li>
              <li>🏥 Healthcare &amp; Medical Relief</li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-gray-300 uppercase tracking-wider mb-3">Technical Stack</h4>
            <p className="text-xs text-gray-400 leading-relaxed">
              FastAPI • LangGraph • PostgreSQL • ChromaDB Vector RAG • React + Tailwind CSS
            </p>
          </div>
        </div>

        <div className="bg-gray-800/50 p-4 rounded-xl text-xs text-gray-400 leading-relaxed border border-gray-800">
          ⚠️ <strong className="text-gray-300">Disclaimer:</strong> PolicyPilot AI provides automated information and scheme matching based on available government data. Citizens should verify official scheme portals prior to official application submissions.
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500 gap-2">
          <p>© {new Date().getFullYear()} PolicyPilot AI Capstone Project. All rights reserved.</p>
          <div className="flex gap-4">
            <a href="#" className="hover:text-gray-300 transition-colors">Top ▲</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
