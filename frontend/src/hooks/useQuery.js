import { useState, useRef, useCallback, useEffect } from 'react';
import { submitQuery } from '../api/query';

const STEPS = ['Intent', 'Domain', 'Research', 'Verify', 'Eligibility', 'Recommend'];
const STORAGE_KEY = 'policypilot_chats_v2';

export function useQuery() {
  const [chats, setChats]               = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [queryText, setQueryText]       = useState('');
  const [isLoading, setIsLoading]       = useState(false);
  const [activeStep, setActiveStep]     = useState(-1);
  const [doneSteps, setDoneSteps]       = useState([]);
  const stepTimerRef                    = useRef(null);

  // Load chat sessions from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        setChats(parsed);
        if (parsed.length > 0) {
          setActiveChatId(parsed[0].id);
        }
      }
    } catch (e) {
      console.error('Failed to load chats', e);
    }
  }, []);

  // Save chats to localStorage
  const saveChatsToStorage = (updatedChats) => {
    setChats(updatedChats);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedChats));
    } catch (e) {
      console.error('Failed to save chats', e);
    }
  };

  // Get current active chat
  const activeChat = chats.find(c => c.id === activeChatId) || null;

  // Create a new empty chat session
  const createNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      title: 'New Conversation',
      createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      messages: [],
    };
    const updated = [newChat, ...chats];
    saveChatsToStorage(updated);
    setActiveChatId(newChat.id);
    setQueryText('');
    setActiveStep(-1);
    setDoneSteps([]);
    return newChat.id;
  };

  // Select a chat from history sidebar
  const selectChat = (id) => {
    setActiveChatId(id);
    setQueryText('');
    setActiveStep(-1);
    setDoneSteps([]);
  };

  // Rename a chat session
  const renameChat = (id, newTitle) => {
    if (!newTitle || !newTitle.trim()) return;
    const updated = chats.map(c => {
      if (c.id === id) {
        return { ...c, title: newTitle.trim() };
      }
      return c;
    });
    saveChatsToStorage(updated);
  };

  // Delete a chat session
  const deleteChat = (id, e) => {
    if (e) e.stopPropagation();
    const updated = chats.filter(c => c.id !== id);
    saveChatsToStorage(updated);
    if (activeChatId === id) {
      if (updated.length > 0) {
        setActiveChatId(updated[0].id);
      } else {
        setActiveChatId(null);
      }
    }
  };

  // Clear all chat history
  const clearAllChats = () => {
    saveChatsToStorage([]);
    setActiveChatId(null);
    setQueryText('');
  };

  // Stepper animation logic
  const startStepper = useCallback(() => {
    setActiveStep(0);
    setDoneSteps([]);
    let idx = 0;

    function advance() {
      idx++;
      if (idx < STEPS.length) {
        setDoneSteps(prev => [...prev, idx - 1]);
        setActiveStep(idx);
        stepTimerRef.current = setTimeout(advance, 900);
      }
    }

    stepTimerRef.current = setTimeout(advance, 900);
  }, []);

  const stopStepper = useCallback((success) => {
    clearTimeout(stepTimerRef.current);
    if (success) {
      setActiveStep(-1);
      setDoneSteps(STEPS.map((_, i) => i));
    }
  }, []);

  // Run query in current active chat (or create new if none)
  const runQuery = useCallback(async (customText) => {
    const textToRun = customText || queryText;
    if (!textToRun.trim() || isLoading) return;

    let targetChatId = activeChatId;
    let currentChats = [...chats];

    // If no active chat, create one
    if (!targetChatId || !currentChats.some(c => c.id === targetChatId)) {
      const newId = Date.now().toString();
      const newChat = {
        id: newId,
        title: textToRun.trim().slice(0, 30) + (textToRun.length > 30 ? '…' : ''),
        createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        messages: [],
      };
      currentChats = [newChat, ...currentChats];
      targetChatId = newId;
      setActiveChatId(newId);
    }

    const userMessage = {
      id: Date.now().toString() + '-u',
      sender: 'user',
      text: textToRun.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    // Update active chat with user message & set title if first message
    currentChats = currentChats.map(c => {
      if (c.id === targetChatId) {
        const isFirst = c.messages.length === 0;
        return {
          ...c,
          title: isFirst ? textToRun.trim().slice(0, 32) + (textToRun.length > 32 ? '…' : '') : c.title,
          messages: [...c.messages, userMessage],
        };
      }
      return c;
    });

    saveChatsToStorage(currentChats);
    setQueryText('');
    setIsLoading(true);
    startStepper();

    try {
      const responseData = await submitQuery(textToRun.trim(), {});
      stopStepper(true);

      const aiMessage = {
        id: Date.now().toString() + '-ai',
        sender: 'assistant',
        data: responseData,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      const finalChats = currentChats.map(c => {
        if (c.id === targetChatId) {
          return { ...c, messages: [...c.messages, aiMessage] };
        }
        return c;
      });
      saveChatsToStorage(finalChats);
    } catch (err) {
      stopStepper(false);
      setActiveStep(-1);
      setDoneSteps([]);

      const errorMessage = {
        id: Date.now().toString() + '-err',
        sender: 'assistant',
        error: err.message || 'Unable to connect to PolicyPilot backend. Ensure server is running.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      const finalChats = currentChats.map(c => {
        if (c.id === targetChatId) {
          return { ...c, messages: [...c.messages, errorMessage] };
        }
        return c;
      });
      saveChatsToStorage(finalChats);
    } finally {
      setIsLoading(false);
    }
  }, [queryText, isLoading, activeChatId, chats, startStepper, stopStepper]);

  // Add a voice exchange (user transcript + AI response) directly to active chat
  const addVoiceMessage = useCallback((transcript, responseText) => {
    if (!transcript && !responseText) return;

    let targetChatId = activeChatId;
    let currentChats = [...chats];

    if (!targetChatId || !currentChats.some(c => c.id === targetChatId)) {
      const newId = Date.now().toString();
      const newChat = {
        id: newId,
        title: (transcript || 'Voice Query').slice(0, 32),
        createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        messages: [],
      };
      currentChats = [newChat, ...currentChats];
      targetChatId = newId;
      setActiveChatId(newId);
    }

    const ts = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const userMsg = {
      id: Date.now().toString() + '-vu',
      sender: 'user',
      text: transcript || '🎤 Voice query',
      timestamp: ts,
      isVoice: true,
    };
    const aiMsg = {
      id: Date.now().toString() + '-vai',
      sender: 'assistant',
      data: {
        final_response: responseText || '',
        intent: 'voice',
        domain: '',
        recommendations: [],
        eligibility_results: [],
        required_documents: [],
      },
      timestamp: ts,
      isVoice: true,
    };

    const updated = currentChats.map(c => {
      if (c.id === targetChatId) {
        const isFirst = c.messages.length === 0;
        return {
          ...c,
          title: isFirst ? (transcript || 'Voice Query').slice(0, 32) : c.title,
          messages: [...c.messages, userMsg, aiMsg],
        };
      }
      return c;
    });
    saveChatsToStorage(updated);
  }, [activeChatId, chats]);

  return {
    chats,
    activeChat,
    activeChatId,
    createNewChat,
    selectChat,
    renameChat,
    deleteChat,
    clearAllChats,
    queryText,
    setQueryText,
    isLoading,
    activeStep,
    doneSteps,
    stepLabels: STEPS,
    runQuery,
    addVoiceMessage,
  };
}
