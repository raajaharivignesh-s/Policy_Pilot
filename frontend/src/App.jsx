import { useState, useRef, useEffect } from 'react';
import { useQuery } from './hooks/useQuery';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import StatsBar from './components/StatsBar';
import HowItWorksSection from './components/HowItWorksSection';
import Footer from './components/Footer';
import Sidebar from './components/Sidebar';
import ChatHeader from './components/ChatHeader';
import EmptyStateHero from './components/EmptyStateHero';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import ProcessingStepper from './components/ProcessingStepper';
import queryBgImage from './assets/query background image.png';

export default function App() {
  const [view, setView] = useState('landing'); // 'landing' | 'chat'
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const {
    chats,
    activeChat,
    activeChatId,
    createNewChat,
    selectChat,
    deleteChat,
    clearAllChats,
    queryText,
    setQueryText,
    isLoading,
    activeStep,
    doneSteps,
    stepLabels,
    runQuery,
  } = useQuery();

  // Scroll to bottom of chat when new messages arrive
  useEffect(() => {
    if (view === 'chat') {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [activeChat?.messages, isLoading, view]);

  const handleOpenChat = (initialQuery) => {
    setView('chat');
    if (initialQuery) {
      runQuery(initialQuery);
    }
  };

  // Render Landing Page View
  if (view === 'landing') {
    return (
      <div className="min-h-screen bg-[#FAFAFA] text-gray-900 flex flex-col font-sans">
        <Navbar onOpenDashboard={() => handleOpenChat()} />
        <main className="flex-1">
          <HeroSection
            onOpenDashboard={() => handleOpenChat()}
            onDomainSelect={(query) => handleOpenChat(query)}
          />
          <StatsBar />
          <HowItWorksSection />
        </main>
        <Footer />
      </div>
    );
  }

  // Render PolicyPilot Custom Chat Workspace View
  const messages = activeChat?.messages || [];
  const activeTitle = activeChat?.title || 'Scheme Discovery Workspace';

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#FAFAFA] text-gray-900 font-sans">
      {/* Pure White Crisp Sidebar */}
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={selectChat}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
        onClearAll={clearAllChats}
        isOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
        onGoToLanding={() => setView('landing')}
      />

      {/* Main Canvas Workspace */}
      <div className="flex-1 flex flex-col h-full min-w-0 bg-[#FAFAFA]">
        {/* Header Bar */}
        <ChatHeader
          title={activeTitle}
          onOpenMobileSidebar={() => setMobileSidebarOpen(true)}
          onGoHome={() => setView('landing')}
        />

        {/* Chat Stream & Background Image Container (Ensures top of flag is fully visible below header) */}
        <div
          className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6 bg-no-repeat bg-[length:100%_auto] bg-right-top"
          style={{
            backgroundImage: `url(${queryBgImage})`,
            backgroundPosition: 'right 0px top 0px',
            backgroundSize: '100% auto',
          }}
        >
          {messages.length === 0 ? (
            <EmptyStateHero onCardClick={(query) => runQuery(query)} />
          ) : (
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}

              {/* Stepper while AI processes query */}
              {isLoading && (
                <div className="py-2">
                  <ProcessingStepper
                    stepLabels={stepLabels}
                    activeStep={activeStep}
                    doneSteps={doneSteps}
                  />
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Bottom Floating Capsule Input */}
        <ChatInput
          queryText={queryText}
          setQueryText={setQueryText}
          isLoading={isLoading}
          onSubmit={() => runQuery()}
        />
      </div>
    </div>
  );
}
