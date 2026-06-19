export default function TopBar({ alfredState, toggleMic }) {
  const isListening = alfredState === 'listening';

  return (
    <div id="topbar">
      <button
        className={`icon-btn${isListening ? ' active' : ''}`}
        title="Toggle voice"
        onClick={toggleMic}
      >
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <rect x="9" y="2" width="6" height="12" rx="3"/>
          <path d="M5 10a7 7 0 0014 0M12 19v3M8 22h8"/>
        </svg>
      </button>
      <button className="icon-btn" title="Minimize">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M5 12h14"/>
        </svg>
      </button>
    </div>
  );
}