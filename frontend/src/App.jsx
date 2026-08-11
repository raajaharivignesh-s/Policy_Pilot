import { useState } from 'react';
import { useQuery } from './hooks/useQuery';
import LandingPage from './pages/LandingPage';
import ChatPage from './pages/ChatPage';

export default function App() {
  const [view, setView] = useState('landing'); // 'landing' | 'chat'
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const {
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
    stepLabels,
    runQuery,
    addVoiceMessage,
  } = useQuery();

  const handleOpenChat = (initialQuery) => {
    setView('chat');
    if (initialQuery) {
      runQuery(initialQuery);
    }
  };

  if (view === 'landing') {
    return (
      <LandingPage
        onOpenDashboard={() => handleOpenChat()}
        onDomainSelect={(query) => handleOpenChat(query)}
      />
    );
  }

  return (
    <ChatPage
      chats={chats}
      activeChat={activeChat}
      activeChatId={activeChatId}
      selectChat={selectChat}
      createNewChat={createNewChat}
      renameChat={renameChat}
      deleteChat={deleteChat}
      clearAllChats={clearAllChats}
      queryText={queryText}
      setQueryText={setQueryText}
      isLoading={isLoading}
      activeStep={activeStep}
      doneSteps={doneSteps}
      stepLabels={stepLabels}
      runQuery={runQuery}
      mobileSidebarOpen={mobileSidebarOpen}
      setMobileSidebarOpen={setMobileSidebarOpen}
      onGoToLanding={() => setView('landing')}
      addVoiceMessage={addVoiceMessage}
    />
  );
}
