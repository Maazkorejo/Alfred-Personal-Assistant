import { useRef, useCallback, useState } from 'react';

export function useSpeechRecognition({ onResult, onStart, onEnd }) {
  const recognitionRef = useRef(null);
  const [isListening, setIsListening] = useState(false);
  const [isSupported] = useState(
    'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
  );

  const startListening = useCallback(() => {
    if (!isSupported) {
      console.warn('Speech recognition not supported in this browser.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      if (onStart) onStart();
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (onResult) onResult(transcript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (onEnd) onEnd();
    };

    recognition.onend = () => {
      setIsListening(false);
      if (onEnd) onEnd();
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [isSupported, onResult, onStart, onEnd]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  return { startListening, stopListening, isListening, isSupported };
}