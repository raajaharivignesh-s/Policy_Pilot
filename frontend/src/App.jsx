import { useState, useEffect } from 'react';
import { useQuery } from './hooks/useQuery';
import { useAuth } from './hooks/useAuth';
import LandingPage from './pages/LandingPage';
import ChatPage from './pages/ChatPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  const { user, token, isLoading: authLoading, login, logout } = useAuth();
  const [view, setView] = useState('landing'); // 'landing' | 'chat'
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [loginError, setLoginError] = useState(null);
  const [isLoggingIn, setIsLoggingIn] = useState(false);

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
    targetFolderId,
    setTargetFolderId,
    isLoading: queryLoading,
    activeStep,
    doneSteps,
    stepLabels,
    runQuery,
    addVoiceMessage,
  } = useQuery(token, user);

  useEffect(() => {
    if (user) {
      setView('chat');
    }
  }, [user]);

  if (authLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#FAFAFA]">
        <div className="animate-spin h-8 w-8 text-[#FF6B00] border-4 border-current border-t-transparent rounded-full"></div>
      </div>
    );
  }

  const handleLogin = async (email, name) => {
    setIsLoggingIn(true);
    setLoginError(null);
    const result = await login(email, name);
    if (!result.success) {
      setLoginError(result.error);
    } else {
      createNewChat();
      setView('chat');
    }
    setIsLoggingIn(false);
  };

  if (!user) {
    return <LoginPage onLogin={handleLogin} isLoading={isLoggingIn} error={loginError} />;
  }

  const handleOpenChat = (initialQuery) => {
    setView('chat');
    if (initialQuery) {
      runQuery(initialQuery);
    }
  };

  if (view === 'dashboard') {
    return (
      <DashboardPage 
        user={user}
        token={token}
        onLogout={logout}
        onGoBack={() => setView('chat')}
      />
    );
  }

  if (view === 'landing') {
    return (
      <LandingPage
        onOpenDashboard={() => handleOpenChat()}
        onDomainSelect={(query) => handleOpenChat(query)}
        user={user}
        onLogout={logout}
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
      targetFolderId={targetFolderId}
      setTargetFolderId={setTargetFolderId}
      isLoading={queryLoading}
      activeStep={activeStep}
      doneSteps={doneSteps}
      stepLabels={stepLabels}
      runQuery={runQuery}
      mobileSidebarOpen={mobileSidebarOpen}
      setMobileSidebarOpen={setMobileSidebarOpen}
      onGoToLanding={() => setView('landing')}
      addVoiceMessage={addVoiceMessage}
      user={user}
      token={token}
      onLogout={logout}
      onGoToDashboard={() => setView('dashboard')}
    />
  );
}
