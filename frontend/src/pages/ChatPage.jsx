import { useRef, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatHeader from '../components/ChatHeader';
import EmptyStateHero from '../components/EmptyStateHero';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import ProcessingStepper from '../components/ProcessingStepper';
import queryBgImage from '../assets/query background image.png';

export default function ChatPage({
  chats,
  activeChat,
  activeChatId,
  selectChat,
  createNewChat,
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
  mobileSidebarOpen,
  setMobileSidebarOpen,
  onGoToLanding,
}) {
  const messagesEndRef = useRef(null);

  const messages = activeChat?.messages || [];
  const activeTitle = activeChat?.title || 'Scheme Discovery Workspace';

  // Scroll to bottom when messages update or loading
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeChat?.messages?.length, isLoading]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#FAFAFA] text-gray-900 font-sans">
      {/* Pure White Crisp Sidebar */}
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={selectChat}
        onNewChat={createNewChat}
        onRenameChat={renameChat}
        onDeleteChat={deleteChat}
        onClearAll={clearAllChats}
        isOpen={mobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
        onGoToLanding={onGoToLanding}
      />

      {/* Main Canvas Workspace */}
      <div className="flex-1 flex flex-col h-full min-w-0 bg-[#FAFAFA]">
        {/* Header Bar */}
        <ChatHeader
          title={activeTitle}
          activeChatId={activeChatId}
          onRenameChat={renameChat}
          onOpenMobileSidebar={() => setMobileSidebarOpen(true)}
          onGoHome={onGoToLanding}
        />

        {/* Chat Stream & Background Image Container */}
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
              {messages.map((msg, idx) => {
                // For assistant messages, find the preceding user message to enable re-run
                let onRerun = null;
                if (msg.sender === 'assistant' && idx > 0) {
                  const prevUser = messages.slice(0, idx).reverse().find(m => m.sender === 'user');
                  if (prevUser?.text) {
                    onRerun = () => runQuery(prevUser.text);
                  }
                }
                return <ChatMessage key={msg.id} message={msg} onRerun={onRerun} />;
              })}

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

        {/* Bottom Floating Input */}
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
