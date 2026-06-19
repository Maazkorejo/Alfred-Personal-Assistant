import { useEffect, useRef } from 'react';

export default function ChatLog({ messages }) {
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [messages]);

  if (messages.length === 0) return null;

  return (
    <div id="chat-log" ref={logRef}>
      {messages.map((msg, i) => (
        <div key={i} className={`chat-row ${msg.role === 'user' ? 'chat-row-user' : 'chat-row-alfred'}`}>
          <div className="chat-avatar">{msg.role === 'user' ? 'YOU' : 'AL'}</div>
          <div className="chat-bubble">{msg.content}</div>
        </div>
      ))}
    </div>
  );
}