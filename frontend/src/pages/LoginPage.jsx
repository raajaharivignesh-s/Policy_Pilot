import { useState } from 'react';
import LogoMark from '../components/LogoMark';

export default function LoginPage({ onLogin, isLoading, error }) {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (email) {
      onLogin(email, name);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-orange-50 relative overflow-hidden font-sans">
      
      {/* Decorative Blobs */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-brand-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-amber-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-32 left-1/2 w-96 h-96 bg-pink-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-4000"></div>

      <div className="relative z-10 w-full max-w-md p-8 md:p-10 bg-white/80 backdrop-blur-xl rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/20">
        
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-[#FF6B00] to-[#FF8A33] rounded-2xl flex items-center justify-center shadow-lg shadow-orange-500/30 mb-6 transform transition-transform hover:scale-105">
            <LogoMark size={32} color="white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight font-serif-title mb-2">Welcome Back</h1>
          <p className="text-sm text-gray-500 text-center">Enter your details to access your personalized scheme discovery dashboard.</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-100 text-red-600 text-sm flex items-start gap-2">
            <span className="text-lg">⚠️</span>
            <p>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="email" className="block text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">
              Email Address <span className="text-red-500">*</span>
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50/50 border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/50 focus:border-[#FF6B00] transition-all"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="name" className="block text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">
              Full Name (Optional)
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50/50 border border-gray-200 rounded-xl text-gray-900 focus:outline-none focus:ring-2 focus:ring-[#FF6B00]/50 focus:border-[#FF6B00] transition-all"
              placeholder="John Doe"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !email}
            className={`w-full py-3.5 px-4 bg-gradient-to-r from-[#FF6B00] to-[#FF8A33] text-white text-sm font-semibold rounded-xl shadow-lg shadow-orange-500/25 transition-all transform hover:-translate-y-0.5 hover:shadow-orange-500/40 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#FF6B00] ${
              (isLoading || !email) ? 'opacity-70 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Signing In...
              </span>
            ) : (
              'Get Started'
            )}
          </button>
        </form>

        <p className="mt-8 text-center text-xs text-gray-400">
          By signing in, you agree to our Terms of Service and Privacy Policy.
        </p>
      </div>
    </div>
  );
}
