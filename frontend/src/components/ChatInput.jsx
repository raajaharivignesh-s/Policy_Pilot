import { useState, useEffect, useRef } from 'react';

// Larger mic SVG icon
const IconMic = ({ size = 22 }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" x2="12" y1="19" y2="22"/>
  </svg>
);

// Send arrow SVG
const IconSend = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="m22 2-7 20-4-9-9-4Z"/>
    <path d="M22 2 11 13"/>
  </svg>
);

// Shield SVG for disclaimer
const IconShield = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
);

export default function ChatInput({ queryText, setQueryText, isLoading, onSubmit }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const recognitionRef = useRef(null);
  const timerRef = useRef(null);

  const isRecordingRef = useRef(false);
  isRecordingRef.current = isRecording;

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        if (transcript.trim()) {
          setQueryText((prev) => (prev ? `${prev} ${transcript.trim()}` : transcript.trim()));
        }
      };

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error);
        setIsRecording(false);
      };

      recognition.onend = () => {
        if (isRecordingRef.current) {
          setIsRecording(false);
        }
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [setQueryText]);

  const startRecording = () => {
    setIsRecording(true);
    setRecordingSeconds(0);
    timerRef.current = setInterval(() => {
      setRecordingSeconds((prev) => prev + 1);
    }, 1000);
    if (recognitionRef.current) {
      try { recognitionRef.current.start(); } catch (err) { console.warn(err); }
    }
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    if (recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch (err) { console.warn(err); }
    }
  };

  const toggleRecording = () => {
    if (isRecording) stopRecording(); else startRecording();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isRecording) stopRecording();
    if (queryText.trim() && !isLoading) onSubmit();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(e); }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="sticky bottom-0 bg-gradient-to-t from-[#FAFAFA] via-[#FAFAFA]/90 to-transparent pt-3 pb-6 px-4 md:px-8">
      <div className="max-w-4xl mx-auto space-y-2">
        {/* Voice Recording Banner */}
        {isRecording && (
          <div className="bg-[#1A1A1A] text-white px-4 py-2.5 rounded-2xl border border-rose-500/30 shadow-lg flex items-center justify-between animate-fade-up">
            <div className="flex items-center gap-3">
              <span className="flex h-3 w-3 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
              </span>
              <div className="text-xs">
                <span className="font-bold text-white uppercase tracking-wider">Voice Recording Active</span>
                <span className="mx-2 text-gray-400">•</span>
                <span className="font-mono text-amber-400 font-bold">{formatTime(recordingSeconds)}</span>
              </div>
            </div>
            <div className="flex items-center gap-1 h-4 px-3">
              <span className="w-1 bg-rose-400 rounded-full animate-wave-bar" style={{ animationDelay: '0ms' }} />
              <span className="w-1 bg-rose-400 rounded-full animate-wave-bar" style={{ animationDelay: '150ms' }} />
              <span className="w-1 bg-rose-400 rounded-full animate-wave-bar" style={{ animationDelay: '300ms' }} />
              <span className="w-1 bg-rose-400 rounded-full animate-wave-bar" style={{ animationDelay: '450ms' }} />
            </div>
            <button
              type="button"
              onClick={stopRecording}
              className="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded-full transition-colors flex items-center gap-1 cursor-pointer"
            >
              ⏹ Stop
            </button>
          </div>
        )}

        {/* Input Container */}
        <form
          onSubmit={handleSubmit}
          className={`bg-white/95 backdrop-blur-xs rounded-3xl border shadow-xl p-4 space-y-3 transition-all duration-200 ${
            isRecording
              ? 'border-rose-400 ring-2 ring-rose-100'
              : 'border-gray-300 focus-within:border-[#FF5500] focus-within:ring-2 focus-within:ring-orange-100'
          }`}
        >
          <div className="flex items-start gap-2">
            <span className="text-orange-500 text-lg mt-0.5 select-none">✴️</span>
            <textarea
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
              placeholder={
                isRecording
                  ? 'Listening... Speak your query clearly...'
                  : 'Ask me anything about government schemes, eligibility, farmer assistance...'
              }
              className="w-full text-sm md:text-base text-gray-900 bg-transparent outline-none resize-none placeholder-gray-400 leading-relaxed font-sans"
            />
          </div>

          <div className="flex items-center justify-between pt-1 border-t border-gray-100">
            <span className="text-xs text-gray-400 font-medium">
              Multi-Agent RAG &amp; Deterministic Eligibility Engine
            </span>

            {/* Mic (larger) & Send */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={toggleRecording}
                className={`p-2.5 rounded-full transition-colors ${
                  isRecording
                    ? 'text-rose-600 bg-rose-50 border border-rose-200'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
                title={isRecording ? 'Stop recording' : 'Voice input'}
              >
                <IconMic size={22} />
              </button>
              <button
                type="submit"
                disabled={isLoading || !queryText.trim()}
                className="w-11 h-11 rounded-full bg-[#FF5500] hover:bg-[#E64D00] disabled:bg-gray-300 text-white flex items-center justify-center transition-all duration-200 shadow-md shadow-orange-500/30 disabled:shadow-none cursor-pointer disabled:cursor-not-allowed flex-shrink-0"
                title="Send query"
              >
                {isLoading ? (
                  <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                ) : (
                  <IconSend />
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Disclaimer */}
        <p className="text-[11px] text-gray-400 text-center flex items-center justify-center gap-1">
          <IconShield /> Information provided is based on government sources. Please verify at official portals.
        </p>
      </div>
    </div>
  );
}
