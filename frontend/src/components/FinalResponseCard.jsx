import { useState, useEffect } from 'react';

// SVG icons
const IconCopy = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>
    <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>
  </svg>
);
const IconCheck = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 6 9 17l-5-5"/>
  </svg>
);
const IconRefresh = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
    <path d="M21 3v5h-5"/>
    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
    <path d="M8 16H3v5"/>
  </svg>
);
const IconTarget = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>
  </svg>
);
const IconFolder = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>
  </svg>
);
const IconSpeaker = ({ isSpeaking }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={isSpeaking ? 'text-[#FF5500] animate-pulse' : ''}>
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>
    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
  </svg>
);

function renderInlineBold(text) {
  const elements = [];
  let lastIndex = 0;
  const boldRegex = /\*\*(.+?)\*\*/g;
  let match;

  while ((match = boldRegex.exec(text)) !== null) {
    const [fullMatch, boldText] = match;
    const start = match.index;

    if (start > lastIndex) {
      elements.push(text.slice(lastIndex, start));
    }

    elements.push(
      <strong key={`bold-${start}`} className="font-bold">
        {boldText}
      </strong>
    );

    lastIndex = start + fullMatch.length;
  }

  if (lastIndex < text.length) {
    elements.push(text.slice(lastIndex));
  }

  return elements.length > 0 ? elements : text;
}

// Remove lines that contain markdown links or bare URLs — these are shown in the Recommendations card
function stripLinkLines(text) {
  if (!text) return text;
  const mdLinkRegex = /\[.+?\]\(https?:\/\/.+?\)/;
  const bareUrlRegex = /https?:\/\/\S+/;
  return text
    .split('\n')
    .filter((line) => !mdLinkRegex.test(line) && !bareUrlRegex.test(line))
    .join('\n')
    // Clean up heading lines that become empty after link removal
    .replace(/^[-*]?\s*$\n/gm, '\n');
}

function formatResponseText(text) {
  if (!text) return null;
  const cleaned = stripLinkLines(text);

  return cleaned.split('\n').map((line, index) => {
    const headingMatch = line.match(/^(#{1,6})\s+(.*)$/);

    if (headingMatch) {
      const level = headingMatch[1].length;
      const content = headingMatch[2];
      const headingStyle =
        level === 1
          ? 'text-xl font-bold'
          : level === 2
          ? 'text-lg font-bold'
          : 'text-base font-bold';

      return (
        <div key={index} className={`${headingStyle} mt-3 mb-1 text-gray-900`}>
          {renderInlineBold(content)}
        </div>
      );
    }

    if (line.trim() === '') {
      return <div key={index} className="h-2" />;
    }

    return (
      <div key={index} className="leading-relaxed text-gray-800">
        {renderInlineBold(line)}
      </div>
    );
  });
}

function getVerificationMeta(data) {
  const verified = Array.isArray(data?.verified_information)
    ? data.verified_information
    : [];
  const supportedCount = verified.filter((item) => item?.supported === true).length;
  const hasVerifiedSources = supportedCount > 0;

  let confidenceLabel = 'Insufficient verification';
  if (typeof data?.confidence_score === 'number') {
    confidenceLabel = `${Math.round(data.confidence_score * 100)}% verified`;
  } else if (verified.length > 0) {
    confidenceLabel = `${Math.round((supportedCount / verified.length) * 100)}% verified`;
  }

  return {
    hasVerifiedSources,
    confidenceLabel,
    summaryTitle: hasVerifiedSources
      ? 'Verified Policy Summary'
      : 'Policy Summary',
  };
}

export default function FinalResponseCard({ data, onRerun }) {
  const [copied, setCopied] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const { final_response, intent, domain, confidence_score } = data || {};
  const { hasVerifiedSources, confidenceLabel, summaryTitle } = getVerificationMeta(data);

  useEffect(() => {
    // Pre-load browser voices array
    if ('speechSynthesis' in window) {
      window.speechSynthesis.getVoices();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = () => {
          window.speechSynthesis.getVoices();
        };
      }
    }
    return () => {
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const handleCopy = () => {
    if (final_response) {
      navigator.clipboard.writeText(final_response);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleToggleSpeak = () => {
    if (!('speechSynthesis' in window) || !final_response) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    } else {
      window.speechSynthesis.cancel(); // Stop any existing speech

      // Clean markdown tags for natural speech
      const plainText = final_response
        .replace(/#{1,6}\s+/g, '')
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/[*_~`]/g, '')
        .replace(/\[(.*?)\]\(.*?\)/g, '$1');

      const utterance = new SpeechSynthesisUtterance(plainText);
      
      // Find a female voice (e.g. Zira, Samantha, Jenny, Google US/UK Female, Natural female)
      const voices = window.speechSynthesis.getVoices();
      const femaleVoice = voices.find(v => {
        const name = v.name.toLowerCase();
        return (
          name.includes('female') ||
          name.includes('zira') ||
          name.includes('samantha') ||
          name.includes('jenny') ||
          name.includes('victoria') ||
          name.includes('karen') ||
          name.includes('fiona') ||
          name.includes('moira') ||
          name.includes('aria') ||
          name.includes('google us english') ||
          name.includes('google uk english female') ||
          name.includes('natural')
        ) && (v.lang.startsWith('en'));
      }) || voices.find(v => v.lang.startsWith('en'));

      if (femaleVoice) {
        utterance.voice = femaleVoice;
      }
      utterance.rate = 1.0;
      utterance.pitch = 1.15; // Pleasant, natural warm female voice pitch

      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      setIsSpeaking(true);
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="bg-white border border-[#E6E4DF] rounded-2xl p-6 shadow-sm animate-fade-up space-y-4 font-sans">
      {/* Verification & Confidence */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[#F1EFEA]">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              hasVerifiedSources ? 'bg-emerald-500' : 'bg-amber-400'
            }`}
          />
          <span className="text-xs font-bold text-gray-800">{summaryTitle}</span>
        </div>
        <span
          className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1 border ${
            hasVerifiedSources
              ? 'bg-amber-50 text-amber-800 border-amber-200'
              : 'bg-gray-50 text-gray-600 border-gray-200'
          }`}
        >
          <IconTarget />
          {hasVerifiedSources ? `Confidence: ${confidenceLabel}` : confidenceLabel}
        </span>
      </div>

      {/* Response content */}
      <div className="text-sm md:text-base leading-relaxed whitespace-pre-wrap font-sans">
        {final_response ? formatResponseText(final_response) : 'No response generated.'}
      </div>

      {/* Meta tags */}
      {(intent || domain) && (
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-[#F1EFEA]">
          {intent && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-[#F1EFEA] text-gray-700">
              <IconTarget /> {intent.replace(/_/g, ' ')}
            </span>
          )}
          {domain && (
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
              <IconFolder /> {domain.charAt(0).toUpperCase() + domain.slice(1)}
            </span>
          )}
        </div>
      )}

      {/* Action buttons: Listen + Copy + Re-answer */}
      <div className="flex items-center justify-end gap-2 pt-2 text-xs text-gray-500 font-medium">
        {final_response && 'speechSynthesis' in window && (
          <button
            onClick={handleToggleSpeak}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors cursor-pointer ${
              isSpeaking
                ? 'bg-orange-50 text-[#FF5500] font-bold border border-orange-200'
                : 'hover:bg-[#F1EFEA] hover:text-gray-900'
            }`}
            title={isSpeaking ? 'Stop listening' : 'Listen to response'}
          >
            <IconSpeaker isSpeaking={isSpeaking} /> {isSpeaking ? 'Stop Voice' : 'Listen'}
          </button>
        )}
        {onRerun && (
          <button
            onClick={onRerun}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-[#F1EFEA] hover:text-gray-900 transition-colors cursor-pointer"
            title="Regenerate answer"
          >
            <IconRefresh /> Re-answer
          </button>
        )}
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-[#F1EFEA] hover:text-gray-900 transition-colors cursor-pointer"
          title="Copy response"
        >
          {copied ? <><IconCheck /> Copied</> : <><IconCopy /> Copy</>}
        </button>
      </div>
    </div>
  );
}
