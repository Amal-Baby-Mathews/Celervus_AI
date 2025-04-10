import React, { useState, useCallback, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { queryJsonTable } from '../../services/api'; // Adjust path
import MessageList from '../ChatWidget/MessageList'; // Reuse MessageList
import ChatInput from '../ChatWidget/ChatInput'; // Reuse ChatInput
import LoadingSpinner from '../Common/LoadingSpinner'; // Reuse Spinner

function JsonQueryChat({ tableId, tableName }) {
  const [messages, setMessages] = useState([
     // Initial greeting specific to JSON query
     { id: Date.now(), sender: 'bot', text: `Ready to answer questions about the '${tableName}' table.` }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const messagesEndRef = useRef(null);

  // Reset chat when table changes
  useEffect(() => {
    setMessages([{ id: Date.now(), sender: 'bot', text: `Ready to answer questions about the '${tableName}' table.` }]);
    setInputValue('');
    setIsQuerying(false);
  }, [tableId, tableName]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleInputChange = useCallback((event) => {
    setInputValue(event.target.value);
  }, []);

  const handleSend = useCallback(async () => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput || isQuerying || !tableId) return;

    const userMessage = { id: Date.now(), sender: 'user', text: trimmedInput };
    const thinkingMessage = { id: Date.now() + 1, sender: 'bot', text: 'Thinking...' }; // Placeholder

    setMessages(prev => [...prev, userMessage, thinkingMessage]);
    setInputValue('');
    setIsQuerying(true);

    try {
      const response = await queryJsonTable(tableId, trimmedInput);
      const botResponse = response.data?.answer || "Sorry, I couldn't find an answer.";
      const botMessage = { id: Date.now() + 2, sender: 'bot', text: botResponse };

      // Replace the "Thinking..." message with the actual response
      setMessages(prev => {
          const updatedMessages = prev.slice(0, -1); // Remove the thinking message
          return [...updatedMessages, botMessage];
      });

    } catch (error) {
      console.error("JSON Query failed:", error);
      const errorMsg = error.response?.data?.detail || error.message || "An error occurred.";
      const errorMessage = {
          id: Date.now() + 2,
          sender: 'bot',
          text: `Sorry, I encountered an error: ${errorMsg}`,
          error: true
      };
       // Replace the "Thinking..." message with the error message
      setMessages(prev => {
          const updatedMessages = prev.slice(0, -1); // Remove the thinking message
          return [...updatedMessages, errorMessage];
      });
    } finally {
      setIsQuerying(false);
    }

  }, [inputValue, isQuerying, tableId, tableName]); // Include tableName in dependency if used in error/success messages

  const handleKeyPress = useCallback((event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  return (
    // This component takes full height from parent flex container
    <motion.div
        className="flex flex-col h-full" // Ensure it takes full height
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }} // Slight delay after panel animates
    >
      {/* Header */}
      <div className="flex-shrink-0 p-3 border-b border-gray-200 dark:border-gray-700">
         <h3 className="font-semibold text-center text-gray-800 dark:text-gray-100">
            Query: <span className="text-indigo-600 dark:text-indigo-400">{tableName}</span>
        </h3>
      </div>

      {/* Message List */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4 bg-gray-50/50 dark:bg-gray-800/50">
        <MessageList messages={messages} />
        {/* Dummy element to scroll to */}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="flex-shrink-0">
        <ChatInput
            value={inputValue}
            onChange={handleInputChange}
            onSend={handleSend}
            onKeyPress={handleKeyPress}
            disabled={isQuerying || !tableId}
            placeholder={`Ask about ${tableName}...`} // Dynamic placeholder
        />
      </div>
    </motion.div>
  );
}

export default JsonQueryChat;