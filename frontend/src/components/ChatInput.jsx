import { useState, useEffect, useRef, useCallback } from 'react';
import LogoMark from './LogoMark';

// ─── SVG Icons ───────────────────────────────────────────────────────────────

const IconMic = ({ size = 20 }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
    <line x1="12" x2="12" y1="19" y2="22"/>
  </svg>
);

const IconStop = ({ size = 16 }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24"
    fill="currentColor" stroke="none">
    <rect x="4" y="4" width="16" height="16" rx="2"/>
  </svg>
);

const IconSend = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width={18} height={18} viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="m22 2-7 20-4-9-9-4Z"/>
    <path d="M22 2 11 13"/>
  </svg>
);

const IconShield = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width={12} height={12} viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
);

const IconVolumeOff = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width={16} height={16} viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="1" y1="1" x2="23" y2="23"/>
    <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"/>
    <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"/>
    <line x1="12" y1="19" x2="12" y2="22"/>
  </svg>
);
export default function ChatInput({
  queryText,
  setQueryText,
  isLoading,
  onSubmit,
}) {
  const [isRecording, setIsRecording] = useState(false);
  const [voiceError, setVoiceError] = useState(null);
  const [isSpeakingAi, setIsSpeakingAi] = useState(false);

  const recognitionRef = useRef(null);
  const isRecordingRef = useRef(false);

  const baseTextRef = useRef('');
  const finalTranscriptRef = useRef('');

  // Keep ref in sync
  useEffect(() => {
    isRecordingRef.current = isRecording;
  }, [isRecording]);

  // Monitor browser speech synthesis status for AI response audio
  useEffect(() => {
    const checkSpeech = () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        setIsSpeakingAi(window.speechSynthesis.speaking);
      }
    };
    const interval = setInterval(checkSpeech, 300);
    return () => clearInterval(interval);
  }, []);

  // Stop recording cleanly
  const stopListening = useCallback(() => {
    isRecordingRef.current = false;
    setIsRecording(false);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onend = null;
        recognitionRef.current.onerror = null;
        recognitionRef.current.stop();
      } catch (err) {
        // ignore stop errors
      }
      recognitionRef.current = null;
    }
  }, []);

  // Stop AI audio playback if active
  const stopAiSpeech = useCallback(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeakingAi(false);
    }
  }, []);

  // Start real-time speech recognition
  const startListening = useCallback(() => {
    // Cancel any current speaking audio
    stopAiSpeech();
    setVoiceError(null);

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError('Speech recognition is not supported in this browser. Please use Chrome, Edge, Safari, or Brave.');
      return;
    }

    // Stop any existing instance
    stopListening();

    try {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      // Use user's local language preference, fallback to en-IN / en-US
      recognition.lang = navigator.language || 'en-IN';
      recognition.maxAlternatives = 1;

      // Capture currently existing text as starting baseline
      const initialText = queryText ? queryText.trim() : '';
      baseTextRef.current = initialText ? initialText + ' ' : '';
      finalTranscriptRef.current = '';

      recognition.onstart = () => {
        isRecordingRef.current = true;
        setIsRecording(true);
        setVoiceError(null);
      };

      recognition.onresult = (event) => {
        let interim = '';
        let finalChunk = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const res = event.results[i];
          const transcriptPiece = res[0].transcript;
          if (res.isFinal) {
            finalChunk += transcriptPiece + ' ';
          } else {
            interim += transcriptPiece;
          }
        }

        if (finalChunk) {
          finalTranscriptRef.current += finalChunk;
        }

        const fullText = (baseTextRef.current + finalTranscriptRef.current + interim).trimStart();
        setQueryText(fullText);
      };

      recognition.onerror = (event) => {
        if (event.error === 'no-speech') {
          // Keep listening or ignore minor silence
          return;
        }
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          setVoiceError('Microphone permission denied. Please allow microphone access in your browser settings.');
          stopListening();
          return;
        }
        if (event.error === 'aborted') {
          // Intentionally stopped
          return;
        }
        setVoiceError(`Speech recognition: ${event.error}`);
        stopListening();
      };

      recognition.onend = () => {
        // If recording flag is still true, auto-restart to maintain continuous listening
        if (isRecordingRef.current) {
          try {
            recognition.start();
            return;
          } catch (err) {
            // failed restart
          }
        }
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      setVoiceError('Could not start voice recognition. Please verify microphone access.');
      setIsRecording(false);
    }
  }, [queryText, setQueryText, stopListening, stopAiSpeech]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopListening();
    };
  }, [stopListening]);

  // Toggle voice recording
  const toggleRecording = () => {
    if (isRecording) {
      stopListening();
    } else {
      startListening();
    }
  };

  // Submit handler
  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (isRecording) {
      stopListening();
    }
    stopAiSpeech();
    if (queryText.trim() && !isLoading) {
      onSubmit();
    }
  };

  // Stop recording and immediately submit
  const handleStopAndSubmit = () => {
    stopListening();
    stopAiSpeech();
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

        {/* ── Active Voice Recording Banner ────────────────────────────────── */}
        {isRecording && (
          <div className="px-4 py-2.5 rounded-2xl bg-gray-900/95 backdrop-blur-xs text-white border border-rose-500/40 shadow-xl flex items-center justify-between animate-fade-up">
            <div className="flex items-center gap-3">
              <span className="flex h-3 w-3 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"/>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"/>
              </span>
              <div className="flex flex-col">
                <span className="text-xs font-semibold text-rose-300 flex items-center gap-1.5">
                  🎙 Listening… Speak naturally into your microphone
                </span>
                <span className="text-[11px] text-gray-300">
                  Words are being transcribed in real-time into the text box below
                </span>
              </div>
            </div>

            {/* Audio wave animation */}
            <div className="flex items-center gap-1 h-5 px-3">
              {[0, 150, 300, 450, 200, 350, 100].map((d, i) => (
                <span
                  key={i}
                  className="w-1 bg-rose-400 rounded-full animate-bounce"
                  style={{ animationDelay: `${d}ms`, height: `${35 + (i % 4) * 20}%` }}
                />
              ))}
            </div>
          </div>
        )}

        {/* ── AI Speaking Banner (Audio Playback) ─────────────────────────── */}
        {isSpeakingAi && !isRecording && (
          <div className="px-4 py-2 rounded-2xl bg-amber-950/90 text-amber-100 border border-amber-500/30 shadow-md flex items-center justify-between animate-fade-up">
            <div className="flex items-center gap-2.5">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"/>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"/>
              </span>
              <span className="text-xs font-medium">
                🔊 PolicyPilot voice response is playing…
              </span>
            </div>
            <button
              type="button"
              onClick={stopAiSpeech}
              className="px-2.5 py-1 bg-amber-800/80 hover:bg-amber-800 text-amber-200 text-xs font-semibold rounded-full transition-colors flex items-center gap-1 cursor-pointer"
            >
              <IconVolumeOff /> Stop Audio
            </button>
          </div>
        )}

        {/* ── Voice Error Banner ──────────────────────────────────────────── */}
        {voiceError && !isRecording && (
          <div className="px-4 py-2 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs font-medium flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span>⚠</span>
              <span>{voiceError}</span>
            </div>
            <button
              type="button"
              onClick={() => setVoiceError(null)}
              className="text-red-500 hover:text-red-700 font-bold ml-2 cursor-pointer"
            >
              ✕
            </button>
          </div>
        )}

        {/* ── Main Input Form ─────────────────────────────────────────────── */}
        <form
          onSubmit={handleSubmit}
          className={`bg-white/95 backdrop-blur-xs rounded-3xl border shadow-xl p-4 space-y-3 transition-all duration-200 ${
            isRecording
              ? 'border-rose-400 ring-4 ring-rose-100/80 shadow-rose-200/50'
              : 'border-gray-300 focus-within:border-[#FF5500] focus-within:ring-2 focus-within:ring-orange-100'
          }`}
        >
          <div className="flex items-start gap-2">
            <span className="text-orange-500 text-lg mt-0.5 select-none">
              <LogoMark size={24} />
            </span>
            <textarea
              id="chat-query-textarea"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
              placeholder={
                isRecording
                  ? '🎙 Listening to your voice… speak now…'
                  : 'Ask anything about government schemes, eligibility, farmer assistance…'
              }
              className="w-full text-sm md:text-base text-gray-900 bg-transparent outline-none resize-none placeholder-gray-400 leading-relaxed font-sans"
            />
          </div>

          <div className="flex items-center justify-between pt-1 border-t border-gray-100">
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400 font-medium hidden md:inline">
                {isRecording ? '🔴 Live Speech-to-Text Transcribing' : 'Multi-Agent RAG & Real-Time Voice Engine'}
              </span>
            </div>

            <div className="flex items-center gap-2">
              {/* Mic / Stop recording button */}
              <button
                type="button"
                id="voice-mic-btn"
                onClick={toggleRecording}
                className={`p-2.5 rounded-full transition-all duration-200 cursor-pointer flex items-center justify-center ${
                  isRecording
                    ? 'text-white bg-rose-600 hover:bg-rose-700 ring-4 ring-rose-200 animate-pulse shadow-md scale-105'
                    : 'text-gray-500 hover:text-[#FF5500] hover:bg-orange-50 active:scale-95'
                }`}
                title={isRecording ? 'Stop voice recording' : 'Speak your query (Live Voice STT)'}
              >
                {isRecording ? <IconStop size={18} /> : <IconMic size={20} />}
              </button>

              {/* Send button */}
              <button
                id="text-send-btn"
                type="submit"
                disabled={isLoading || !queryText.trim()}
                className="w-11 h-11 rounded-full bg-[#FF5500] hover:bg-[#E64D00] disabled:bg-gray-300 text-white flex items-center justify-center transition-all duration-200 shadow-md shadow-orange-500/30 disabled:shadow-none cursor-pointer disabled:cursor-not-allowed flex-shrink-0 active:scale-95"
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
