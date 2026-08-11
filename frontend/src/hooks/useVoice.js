import { useState, useRef, useCallback, useEffect } from 'react';
import { VoiceWSClient } from '../api/voice';

/**
 * useVoice — manages the full backend voice pipeline:
 *   mic → MediaRecorder → WebSocket → STT → LLM → TTS audio
 *
 * Returns:
 *   isRecording, isProcessing, isPlaying
 *   transcript       — what STT heard
 *   responseText     — LLM text as it streams in
 *   startRecording() — begin capturing mic audio
 *   stopRecording()  — stop mic, trigger pipeline
 *   cancelVoice()    — interrupt any in-flight response
 *   onVoiceDone      — callback(transcript, fullResponseText) called when complete
 */
export function useVoice({ onVoiceDone } = {}) {
  const [isRecording, setIsRecording]   = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlaying, setIsPlaying]       = useState(false);
  const [transcript, setTranscript]     = useState('');
  const [responseText, setResponseText] = useState('');
  const [error, setError]               = useState(null);

  const clientRef      = useRef(null);
  const recorderRef    = useRef(null);
  const audioCtxRef    = useRef(null);
  const responseAccRef = useRef('');   // accumulate full response text
  const audioQueueRef  = useRef([]);   // pending MP3 chunks
  const playingRef     = useRef(false);

  // ---------------------------------------------------------------------------
  // Audio playback — queue MP3 ArrayBuffer chunks → decode → play sequentially
  // ---------------------------------------------------------------------------
  const getAudioCtx = () => {
    if (!audioCtxRef.current || audioCtxRef.current.state === 'closed') {
      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    return audioCtxRef.current;
  };

  const playNextChunk = useCallback(async () => {
    if (playingRef.current) return;
    if (audioQueueRef.current.length === 0) {
      setIsPlaying(false);
      return;
    }

    playingRef.current = true;
    setIsPlaying(true);

    const chunk = audioQueueRef.current.shift();
    try {
      const ctx    = getAudioCtx();
      const buffer = await ctx.decodeAudioData(chunk.slice(0)); // slice = copy
      const src    = ctx.createBufferSource();
      src.buffer   = buffer;
      src.connect(ctx.destination);
      src.onended  = () => {
        playingRef.current = false;
        playNextChunk();
      };
      src.start();
    } catch {
      // Chunk may be partial / incomplete MP3 — skip it
      playingRef.current = false;
      playNextChunk();
    }
  }, []);

  const enqueueAudio = useCallback((arrayBuffer) => {
    audioQueueRef.current.push(arrayBuffer);
    playNextChunk();
  }, [playNextChunk]);

  // ---------------------------------------------------------------------------
  // WS event handler
  // ---------------------------------------------------------------------------
  const handleEvent = useCallback((evt) => {
    switch (evt.type) {
      case 'connected':
        // Session established — configure voice
        clientRef.current?.configure('alloy');
        break;

      case 'transcript':
        setTranscript(evt.text || '');
        setIsProcessing(true);
        break;

      case 'response_start':
        responseAccRef.current = '';
        setResponseText('');
        break;

      case 'response':
        responseAccRef.current += evt.text || '';
        setResponseText(responseAccRef.current);
        break;

      case 'audio_start':
        audioQueueRef.current = [];
        break;

      case 'complete':
        setIsProcessing(false);
        onVoiceDone?.(
          evt.transcript || transcript,
          responseAccRef.current,
        );
        break;

      case 'error':
        setError(evt.message || 'Voice pipeline error');
        setIsProcessing(false);
        setIsPlaying(false);
        break;

      default:
        break;
    }
  }, [transcript, onVoiceDone]);

  // ---------------------------------------------------------------------------
  // Connect / disconnect WS lazily
  // ---------------------------------------------------------------------------
  const ensureConnected = useCallback(async () => {
    if (clientRef.current?.isReady) return;
    const client = new VoiceWSClient({
      onEvent: handleEvent,
      onAudio: enqueueAudio,
      onClose: () => {
        setIsProcessing(false);
        setIsRecording(false);
        clientRef.current = null;
      },
    });
    await client.connect();
    clientRef.current = client;
  }, [handleEvent, enqueueAudio]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clientRef.current?.disconnect();
      audioCtxRef.current?.close();
    };
  }, []);

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------
  const startRecording = useCallback(async () => {
    setError(null);
    setTranscript('');
    setResponseText('');
    responseAccRef.current = '';
    audioQueueRef.current  = [];
    playingRef.current     = false;

    try {
      await ensureConnected();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/ogg';

      const recorder = new MediaRecorder(stream, { mimeType });
      recorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          e.data.arrayBuffer().then((buf) => {
            clientRef.current?.sendAudioChunk(buf);
          });
        }
      };

      recorder.onstop = () => {
        stream.getTracks().forEach((t) => t.stop());
        clientRef.current?.endOfSpeech();
        setIsRecording(false);
        setIsProcessing(true);
      };

      recorder.start(250); // send chunks every 250 ms
      setIsRecording(true);
    } catch (err) {
      setError(err.message || 'Microphone access denied');
      setIsRecording(false);
    }
  }, [ensureConnected]);

  const stopRecording = useCallback(() => {
    if (recorderRef.current?.state === 'recording') {
      recorderRef.current.stop();
    } else {
      setIsRecording(false);
    }
  }, []);

  const cancelVoice = useCallback(() => {
    stopRecording();
    clientRef.current?.interrupt();
    audioQueueRef.current = [];
    playingRef.current    = false;
    setIsProcessing(false);
    setIsPlaying(false);
  }, [stopRecording]);

  return {
    isRecording,
    isProcessing,
    isPlaying,
    transcript,
    responseText,
    error,
    startRecording,
    stopRecording,
    cancelVoice,
  };
}
