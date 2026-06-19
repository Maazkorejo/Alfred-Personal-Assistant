export default function InputBar({ inputValue, setInputValue, onSend, onFocus, onBlur }) {
  const hasText = inputValue.trim().length > 0;

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      onSend(inputValue);
    }
  };

  return (
    <div id="input-area">
      <div id="input-wrap">
        <input
          id="msg-input"
          type="text"
          placeholder="Ask Alfred anything..."
          autoComplete="off"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={onFocus}
          onBlur={onBlur}
        />
        <button
          id="send-btn"
          className={hasText ? 'has-text' : ''}
          onClick={() => onSend(inputValue)}
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>
      </div>
    </div>
  );
}