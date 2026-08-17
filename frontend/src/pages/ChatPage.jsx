import { useRef, useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatHeader from '../components/ChatHeader';
import EmptyStateHero from '../components/EmptyStateHero';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import ProcessingStepper from '../components/ProcessingStepper';
import queryBgImage from '../assets/query background image.png';

// Import message cards rendered directly in the chat layout
import FinalResponseCard from '../components/FinalResponseCard';
import RecommendationsCard from '../components/RecommendationsCard';
import EligibilityCard from '../components/EligibilityCard';
import DocumentsCard from '../components/DocumentsCard';
import { useVoice } from '../hooks/useVoice';

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
  targetFolderId,
  setTargetFolderId,
  isLoading,
  activeStep,
  doneSteps,
  stepLabels,
  runQuery,
  mobileSidebarOpen,
  setMobileSidebarOpen,
  onGoToLanding,
  addVoiceMessage,
  user,
  token,
  onLogout,
  onGoToDashboard,
}) {
  const voice = useVoice({
    onVoiceDone: (transcript, responseText) => {
      if (addVoiceMessage) {
        addVoiceMessage(transcript, responseText);
      }
    },
  });

  const [folders, setFolders] = useState([]);
  const messagesEndRef = useRef(null);

  const refreshFolders = () => {
    if (token) {
      import('../api/wallet').then(module => {
        module.getFolders(token)
          .then(data => setFolders(data))
          .catch(err => console.error(err));
      });
    }
  };

  // Fetch folders on mount
  useEffect(() => {
    refreshFolders();
  }, [token]);

  const messages = activeChat?.messages || [];
  const activeTitle = activeChat?.title || 'Scheme Discovery Workspace';

  // Find the last user message to pass as query context for verification
  const lastUserMessage = [...messages].reverse().find(m => m.sender === 'user')?.text || '';

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
        user={user}
        onLogout={onLogout}
        onGoToDashboard={onGoToDashboard}
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
                return (
                  <div key={msg.id} className="space-y-4">
                    {msg.sender === 'user' ? (
                      <ChatMessage message={msg} onRerun={onRerun} />
                    ) : (
                      <div className="space-y-4">
                        {/* Assistant message structure */}
                        <div className="flex items-start gap-4 max-w-4xl animate-fade-up">
                          <div className="w-9 h-9 rounded-2xl text-white flex items-center justify-center text-base shadow-sm flex-shrink-0 mt-1 select-none">
                            <LogoMark size={24} />
                          </div>
                          <div className="flex-1 space-y-4 min-w-0">
                            {msg.error && (
                              <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-start gap-3">
                                <span>⚠️</span>
                                <div>
                                  <h4 className="font-bold mb-1">Execution Error</h4>
                                  <p>{msg.error}</p>
                                </div>
                              </div>
                            )}
                            {msg.data && (
                              <div className="space-y-4">
                                <FinalResponseCard data={msg.data} onRerun={onRerun} />
                                <RecommendationsCard recommendations={msg.data.recommendations} />
                                <EligibilityCard eligibilityResults={msg.data.eligibility_results} />
                                <DocumentsCard 
                                  requiredDocuments={msg.data.required_documents}
                                  folders={folders}
                                  token={token}
                                  runQuery={runQuery}
                                  setTargetFolderId={setTargetFolderId}
                                  lastQuery={lastUserMessage}
                                  refreshFolders={refreshFolders}
                                />
                              </div>
                            )}
                            <span className="block text-[10px] text-gray-400">
                              {msg.timestamp}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
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
          voice={voice}
        />
      </div>
    </div>
  );
}
