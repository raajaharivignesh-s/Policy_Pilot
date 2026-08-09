import { useEffect, useState } from 'react';
import { checkHealth } from '../api/query';

export default function Navbar({ onOpenDashboard }) {
  const [healthy, setHealthy] = useState(null);

  useEffect(() => {
    checkHealth().then(setHealthy);
  }, []);

  return (
    <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Brand */}
        <a href="#" className="flex items-center gap-2.5 no-underline">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-600 to-accent-500 flex items-center justify-center text-white text-lg flex-shrink-0">
            🏛️
          </div>
          <span className="font-heading font-bold text-xl text-gray-900">
            Policy<span className="text-brand-600">Pilot</span>
          </span>
          <span className="hidden sm:inline-flex ml-1 text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200 px-2 py-0.5 rounded-full">
            AI
          </span>
        </a>

        {/* Nav links */}
        <div className="flex items-center gap-3">
          <a href="#how-it-works" className="hidden md:block px-4 py-2 text-sm font-medium text-gray-600 rounded-full hover:bg-gray-100 hover:text-gray-900 transition-colors">
            How it works
          </a>

          {/* Backend status */}
          <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
            healthy === null
              ? 'bg-gray-50 text-gray-500 border-gray-200'
              : healthy
              ? 'bg-green-50 text-green-700 border-green-200'
              : 'bg-red-50 text-red-700 border-red-200'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${
              healthy === null ? 'bg-gray-400' : healthy ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`} />
            {healthy === null ? 'Checking…' : healthy ? 'Backend Online' : 'Backend Offline'}
          </span>

          <button
            onClick={onOpenDashboard}
            className="btn-primary text-xs px-5 py-2 cursor-pointer"
          >
            💬 Open Dashboard
          </button>
        </div>
      </div>
    </nav>
  );
}
