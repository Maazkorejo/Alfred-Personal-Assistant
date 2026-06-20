import { useAlfred } from './hooks/useAlfred';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import BlackHole from './components/BlackHole';
import InputBar from './components/InputBar';
import ChatLog from './components/ChatLog';
import EmailPanel from './components/EmailPanel';
import MemoryPanel from './components/MemoryPanel';
import './styles/main.css';

function App() {
  const {
    alfredState,
    setState,
    stateConfig,
    messages,
    inputValue,
    setInputValue,
    activeNav,
    setActiveNav,
    sendMessage,
    toggleMic,
  } = useAlfred();

  const handleInputFocus = () => {
    if (alfredState === 'idle') setState('listening');
  };

  const handleInputBlur = () => {
    if (alfredState === 'listening' && !inputValue) setState('idle');
  };

  const handleSend = (text) => {
    if (!text.trim()) return;
    sendMessage(text);
  };

  const isEmailPanel = activeNav === 'Email';
  const isMemoryPanel = activeNav === 'Memory';

  return (
    <div className="app">
      <Sidebar
        alfredState={alfredState}
        stateConfig={stateConfig}
        activeNav={activeNav}
        setActiveNav={setActiveNav}
      />

      <div id="main">
        <div id="ambient-glow" />

        <TopBar alfredState={alfredState} toggleMic={toggleMic} />

        {isEmailPanel ? (
          <EmailPanel onBack={() => setActiveNav('New Chat')} />
        ) : isMemoryPanel ? (
          <MemoryPanel onBack={() => setActiveNav('New Chat')} />
        ) : (
          <>
            <div id="center">
              <BlackHole alfredState={alfredState} />
              <ChatLog messages={messages} />
              <div id="agent-status">
                Neural core online &middot; memory active &middot; awaiting command
              </div>
            </div>

            <InputBar
              inputValue={inputValue}
              setInputValue={setInputValue}
              onSend={handleSend}
              onFocus={handleInputFocus}
              onBlur={handleInputBlur}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default App;