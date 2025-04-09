import React from 'react';

function MessageList({ messages }) {
  return (
    <>
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] p-3 rounded-lg shadow-sm ${
              msg.sender === 'user'
                ? 'bg-blue-500 text-white'
                : msg.error // Style error messages differently
                ? 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 border border-red-300 dark:border-red-700'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-100'
            }`}
          >
            {/* Basic rendering of text, handles newlines */}
            <p className="whitespace-pre-wrap break-words">{msg.text || (msg.sender === 'bot' && <span className="italic opacity-75">Typing...</span>)}</p>
          </div>
        </div>
      ))}
    </>
  );
}

export default MessageList;