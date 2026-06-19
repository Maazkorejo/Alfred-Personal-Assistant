import { useState, useRef, useCallback } from 'react';

const STATE_CONFIG = {
  idle:       { label: 'IDLE',         pillColor: 'rgba(232,213,163,0.45)', bg: 'rgba(255,200,80,0.10)',  dot: 'rgba(232,213,163,0.45)', nameRgb: '232,213,163' },
  listening:  { label: 'LISTENING...', pillColor: 'rgba(255,210,100,0.8)',  bg: 'rgba(255,210,100,0.20)', dot: 'rgba(255,210,100,0.9)',  nameRgb: '255,210,100' },
  processing: { label: 'PROCESSING',   pillColor: 'rgba(255,150,50,0.9)',   bg: 'rgba(255,140,40,0.25)',  dot: 'rgba(255,130,40,1)',     nameRgb: '255,160,60'  },
  responding: { label: 'RESPONDING',   pillColor: 'rgba(200,170,100,0.7)',  bg: 'rgba(200,170,80,0.16)',  dot: 'rgba(200,170,100,0.8)',  nameRgb: '232,200,120' },
};

export function useAlfred() {
  const [alfredState, setAlfredState] = useState('idle');
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [activeNav, setActiveNav] = useState('New Chat');
  const timerRef = useRef(null);

  const setState = useCallback((s) => {
    setAlfredState(s);
  }, []);

  const speak = useCallback((text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utt = new SpeechSynthesisUtterance(text);
      utt.rate = 0.95;
      utt.pitch = 0.9;
      window.speechSynthesis.speak(utt);
    }
  }, []);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim()) return;

    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInputValue('');
    setState('processing');

    try {
      const res = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      const data = await res.json();
      const reply = data.response || 'I apologize, I encountered an issue.';

      setState('responding');
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
      speak(reply);

      clearTimeout(timerRef.current);
      timerRef.current = setTimeout(() => setState('idle'), Math.min(reply.length * 60, 8000));

    } catch (err) {
      setState('idle');
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection to Alfred backend failed. Ensure the Flask server is running on port 5000.' }]);
    }
  }, [setState, speak]);

  const toggleMic = useCallback(() => {
    setState(alfredState === 'listening' ? 'idle' : 'listening');
  }, [alfredState, setState]);

  return {
    alfredState,
    setState,
    stateConfig: STATE_CONFIG,
    messages,
    inputValue,
    setInputValue,
    activeNav,
    setActiveNav,
    sendMessage,
    toggleMic,
  };
}