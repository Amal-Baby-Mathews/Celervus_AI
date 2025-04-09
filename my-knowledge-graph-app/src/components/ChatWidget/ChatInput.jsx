import React from 'react';
// import { IoSend } from "react-icons/io5"; // Example using react-icons

function ChatInput({ value, onChange, onSend, onKeyPress, disabled }) {
  return (
    <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-b-lg flex items-center space-x-2">
      <input
        type="text"
        placeholder="Ask Celerbud..."
        value={value}
        onChange={onChange}
        onKeyPress={onKeyPress}
        disabled={disabled}
        className="flex-grow p-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100 disabled:opacity-50"
      />
      <button
        onClick={onSend}
        disabled={disabled || !value.trim()}
        className="p-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Send message"
      >
        {/* Placeholder for Send Icon - Replace with actual icon */}
        {/* <IoSend size={20} /> */}
         <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
         </svg>
      </button>
    </div>
  );
}

export default ChatInput;