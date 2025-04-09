import React, { useState, useCallback, useRef, useEffect } from 'react';
import { streamQuery } from '../../services/api'; // Adjust path if needed
import ChatWindow from './ChatWindow';
import ChatTriggerButton from './ChatTriggerButton';

function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    // Optional: Initial greeting
    // { id: Date.now(), sender: 'bot', text: 'Hi there! I am Celerbud. Ask me anything about your documents.' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const toggleChat = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  const handleInputChange = useCallback((event) => {
    setInputValue(event.target.value);
  }, []);

  const handleSend = useCallback(async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isStreaming) return;

    const userMessage = { id: Date.now(), sender: 'user', text: trimmedInput };
    const botMessagePlaceholder = { id: Date.now() + 1, sender: 'bot', text: '' };

    // Add user message and bot placeholder immediately
    setMessages(prev => [...prev, userMessage, botMessagePlaceholder]);
    setInputValue('');
    setIsStreaming(true);

    let accumulatedBotResponse = '';

    try {
      await streamQuery(
        trimmedInput,
        (chunk) => {
          // Update the text of the *last* message (the bot placeholder)
          accumulatedBotResponse += chunk;
          setMessages(prev => {
            const updatedMessages = [...prev];
            const lastMessageIndex = updatedMessages.length - 1;
            if (lastMessageIndex >= 0 && updatedMessages[lastMessageIndex].sender === 'bot') {
               updatedMessages[lastMessageIndex] = {
                 ...updatedMessages[lastMessageIndex],
                 text: accumulatedBotResponse, // Append chunk to existing text
               };
            }
            return updatedMessages;
          });
        },
        () => {
          // Stream finished
          setIsStreaming(false);
          // Optional: Final state update if needed, though chunk updates should cover it
        },
        (error) => {
           // Handle stream error - update the bot message with an error
           console.error("Streaming failed:", error);
           setMessages(prev => {
                const updatedMessages = [...prev];
                const lastMessageIndex = updatedMessages.length - 1;
                if (lastMessageIndex >= 0 && updatedMessages[lastMessageIndex].sender === 'bot') {
                    updatedMessages[lastMessageIndex] = {
                        ...updatedMessages[lastMessageIndex],
                        text: `Sorry, I encountered an error: ${error.message}`,
                        error: true, // Add an error flag for potential styling
                    };
                } else {
                    // If placeholder wasn't added correctly, add a new error message
                    updatedMessages.push({ id: Date.now(), sender: 'bot', text: `Error: ${error.message}`, error: true });
                }
                return updatedMessages;
           });
           setIsStreaming(false);
        }
      );
    } catch (error) {
        // Catch potential errors *before* calling streamQuery (e.g., network issues)
        console.error("Failed to initiate stream:", error);
         setMessages(prev => [
             ...prev,
             { id: Date.now(), sender: 'bot', text: `Failed to connect: ${error.message}`, error: true }
         ]);
        setIsStreaming(false); // Ensure streaming is marked as false
    }

  }, [inputValue, isStreaming]);

  const handleKeyPress = useCallback((event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Prevent newline in input
      handleSend();
    }
  }, [handleSend]);

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {isOpen ? (
        <ChatWindow
          messages={messages}
          inputValue={inputValue}
          isStreaming={isStreaming}
          onInputChange={handleInputChange}
          onSendMessage={handleSend}
          onClose={toggleChat}
          onKeyPress={handleKeyPress}
        />
      ) : (
        <ChatTriggerButton onClick={toggleChat} />
      )}
    </div>
  );
}

export default ChatWidget;