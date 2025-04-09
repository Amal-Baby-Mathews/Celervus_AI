import React, { useRef, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ChatHeader from './ChatHeader'; // Assuming you create this

function ChatWindow({
  messages,
  inputValue,
  isStreaming,
  onInputChange,
  onSendMessage,
  onClose,
  onKeyPress
}) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]); // Scroll whenever messages change

  return (
    <div className="w-80 sm:w-96 h-[60vh] max-h-[500px] bg-white dark:bg-gray-800 rounded-lg shadow-xl flex flex-col border border-gray-200 dark:border-gray-700">
      {/* Optional Header */}
      <ChatHeader title="Celerbud" onClose={onClose} />

      {/* Message List */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4 bg-gray-50/50 dark:bg-gray-800/50">
        <MessageList messages={messages} />
        {/* Dummy element to scroll to */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput
        value={inputValue}
        onChange={onInputChange}
        onSend={onSendMessage}
        onKeyPress={onKeyPress}
        disabled={isStreaming} // Disable input while streaming
      />
    </div>
  );
}

export default ChatWindow;