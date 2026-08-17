import { useState, useEffect, useRef } from 'react';
import LogoMark from './LogoMark';

// ─── SVG icons ────────────────────────────────────────────────────────────────

const IconMic = ({ size = 22 }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" x2="12" y1="19" y2="22"/>
  </svg>
);

const IconStop = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
    fill="currentColor" stroke="none">
    <rect x="4" y="4" width="16" height="16" rx="2"/>
  </svg>
);

const IconSend = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="m22 2-7 20-4-9-9-4Z"/>
    <path d="M22 2 11 13"/>
  </svg>
);

const IconShield = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
);

export default function ChatInput({
  queryText,
  setQueryText,
  isLoading,
  onSubmit,
  voice,
}) {
  const [internalIsRecording, setInternalIsRecording] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  const recognitionRef = useRef(null);
  const shouldAutoSubmitRef = useRef(false);

  // Active state: prefer voice prop (WebSocket) if available, otherwise local state
  const isRecording = voice ? voice.isRecording : internalIsRecording;
  const isProcessing = voice?.isProcessing;
  const isPlaying = voice?.isPlaying;
  const activeVoiceError = voice?.error || voiceError;

  useEffect(() => {
    if (voice) return; // Skip local WebSpeech setup if WebSocket voice prop provided

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setInternalIsRecording(true);
        setVoiceError(null);
      };

      recognition.onresult = (event) => {
        let currentTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        if (currentTranscript.trim()) {
          setQueryText(currentTranscript);
          shouldAutoSubmitRef.current = true;
        }
      };

      recognition.onerror = (event) => {
        if (event.error !== 'no-speech') {
          setVoiceError(`Voice recognition: ${event.error}`);
        }
        setInternalIsRecording(false);
      };

      recognition.onend = () => {
        setInternalIsRecording(false);
        if (shouldAutoSubmitRef.current && queryText.trim() && !isLoading) {
          shouldAutoSubmitRef.current = false;
          onSubmit();
        }
      };

      recognitionRef.current = recognition;
    }
  }, [voice, setQueryText, onSubmit, isLoading, queryText]);

  const toggleRecording = () => {
    if (voice) {
      if (voice.isRecording) {
        voice.stopRecording();
      } else {
        voice.startRecording();
      }
      return;
    }

    if (!recognitionRef.current) {
      setVoiceError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (internalIsRecording) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        setInternalIsRecording(false);
      }
    } else {
      setVoiceError(null);
      shouldAutoSubmitRef.current = false;
      try {
        recognitionRef.current.start();
      } catch (err) {
        try {
          recognitionRef.current.stop();
          setTimeout(() => recognitionRef.current.start(), 100);
        } catch (e) {
          setInternalIsRecording(false);
        }
      }
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isRecording) {
      if (voice) voice.stopRecording();
      else if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (err) {}
      }
    }
    if (queryText.trim() && !isLoading) {
      onSubmit();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="sticky bottom-0 bg-gradient-to-t from-[#FAFAFA] via-[#FAFAFA]/90 to-transparent pt-3 pb-6 px-4 md:px-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-2">

        {/* ── Voice recording / processing active banner ───────────────────── */}
        {(isRecording || isProcessing || isPlaying) && (
          <div className="px-4 py-2.5 rounded-2xl bg-[#1A1A1A] text-white border border-rose-500/30 shadow-lg flex items-center justify-between animate-fade-up">
            <div className="flex items-center gap-3">
              <span className="flex h-3 w-3 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"/>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"/>
              </span>
              <span className="text-xs font-semibold">
                {isRecording && '🎙 Streaming Voice AI listening… Speak clearly into microphone'}
                {isProcessing && '⚡ Transcribing & generating streaming response…'}
                {isPlaying && '🔊 Playing AI voice response…'}
              </span>
            </div>

            <div className="flex items-center gap-1 h-4 px-3">
              {[0, 150, 300, 450].map((d) => (
                <span key={d} className="w-1 bg-rose-400 rounded-full animate-bounce"
                  style={{ animationDelay: `${d}ms`, height: '60%' }} />
              ))}
            </div>

            <button
              type="button"
              onClick={toggleRecording}
              className="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded-full transition-colors flex items-center gap-1 cursor-pointer"
            >
              <IconStop /> {isRecording ? 'Stop & Process' : 'Stop'}
            </button>
          </div>
        )}

        {/* ── Voice error banner ──────────────────────────────────────────── */}
        {activeVoiceError && !isRecording && (
          <div className="px-4 py-2 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-medium flex items-center gap-2">
            ⚠ {activeVoiceError}
          </div>
        )}

        {/* ── Main input form ─────────────────────────────────────────────── */}
        <form
          onSubmit={handleSubmit}
          className={`bg-white/95 backdrop-blur-xs rounded-3xl border shadow-xl p-4 space-y-3 transition-all duration-200 ${
            isRecording
              ? 'border-rose-400 ring-2 ring-rose-100'
              : 'border-gray-300 focus-within:border-[#FF5500] focus-within:ring-2 focus-within:ring-orange-100'
          }`}
        >
          <div className="flex items-start gap-2">
            <span className="text-orange-500 text-lg mt-0.5 select-none">
              <LogoMark size={24} />
            </span>
            <textarea
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
              placeholder={
                isRecording
                  ? 'Listening… speak your query live…'
                  : 'Ask anything about government schemes, eligibility, farmer assistance…'
              }
              className="w-full text-sm md:text-base text-gray-900 bg-transparent outline-none resize-none placeholder-gray-400 leading-relaxed font-sans"
            />
          </div>

          <div className="flex items-center justify-between pt-1 border-t border-gray-100">
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400 font-medium hidden md:inline">
                Multi-Agent RAG &amp; Streaming Voice AI Engine
              </span>
            </div>

            <div className="flex items-center gap-2">
              {/* Mic button */}
              <button
                type="button"
                id="voice-mic-btn"
                onClick={toggleRecording}
                className={`p-2.5 rounded-full transition-colors cursor-pointer ${
                  isRecording
                    ? 'text-rose-600 bg-rose-50 border border-rose-200 animate-pulse'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
                title={isRecording ? 'Stop voice recording' : 'Voice input (Whisper STT & TTS)'}
              >
                {isRecording ? <IconStop /> : <IconMic size={22} />}
              </button>

              {/* Send button */}
              <button
                id="text-send-btn"
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
          <IconShield /> Information based on official government sources. Verify at official portals.
        </p>
      </div>
    </div>
  );
}

