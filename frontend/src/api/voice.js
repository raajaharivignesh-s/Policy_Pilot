/**
 * VoiceWSClient — manages the WebSocket connection to /ws/voice.
 *
 * Usage:
 *   const client = new VoiceWSClient({ onEvent, onAudio, onClose });
 *   await client.connect();
 *   client.sendAudioChunk(bytes);
 *   client.endOfSpeech();
 *   client.disconnect();
 */
export class VoiceWSClient {
  /** @param {{ onEvent: (evt:object)=>void, onAudio: (chunk:ArrayBuffer)=>void, onClose: ()=>void }} opts */
  constructor({ onEvent, onAudio, onClose }) {
    this._onEvent = onEvent;
    this._onAudio = onAudio;
    this._onClose = onClose;
    this._ws = null;
    this._ready = false;
  }

  connect() {
    return new Promise((resolve, reject) => {
      // Use relative ws path — Vite proxy forwards /ws → ws://127.0.0.1:8000
      const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
      const ws = new WebSocket(`${protocol}://${location.host}/ws/voice`);
      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        this._ws = ws;
        this._ready = true;
        resolve();
      };

      ws.onerror = (err) => {
        reject(new Error('Voice WebSocket connection failed'));
      };

      ws.onclose = () => {
        this._ready = false;
        this._ws = null;
        this._onClose?.();
      };

      ws.onmessage = (evt) => {
        if (evt.data instanceof ArrayBuffer) {
          this._onAudio?.(evt.data);
        } else {
          try {
            const json = JSON.parse(evt.data);
            this._onEvent?.(json);
          } catch {
            // ignore malformed frames
          }
        }
      };
    });
  }

  get isReady() {
    return this._ready && this._ws?.readyState === WebSocket.OPEN;
  }

  _send(data) {
    if (!this.isReady) return;
    if (typeof data === 'string') {
      this._ws.send(data);
    } else {
      this._ws.send(data);
    }
  }

  /** Send raw audio bytes from MediaRecorder */
  sendAudioChunk(arrayBuffer) {
    this._send(arrayBuffer);
  }

  /** Trigger STT → LLM → TTS pipeline for the buffered audio */
  endOfSpeech() {
    this._send(JSON.stringify({ type: 'end_of_speech' }));
  }

  /** Send text directly (bypasses STT) */
  sendTextQuery(text) {
    this._send(JSON.stringify({ type: 'text_query', text }));
  }

  /** Cancel current in-flight response */
  interrupt() {
    this._send(JSON.stringify({ type: 'interrupt' }));
  }

  /** Configure voice/language for this session */
  configure(voice = 'alloy', language = null) {
    this._send(JSON.stringify({ type: 'config', voice, language }));
  }

  disconnect() {
    this._ready = false;
    try { this._ws?.close(); } catch { /* ignore */ }
    this._ws = null;
  }
}
