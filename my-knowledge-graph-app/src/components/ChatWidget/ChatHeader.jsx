import React from 'react';
// Consider adding an icon library like react-icons if you don't have one
// import { VscChromeClose } from "react-icons/vsc"; // Example using react-icons

function ChatHeader({ title, onClose }) {
  return (
    <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-900 rounded-t-lg">
      <h3 className="font-semibold text-gray-800 dark:text-gray-100">{title}</h3>
      <button
        onClick={onClose}
        className="text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-100 focus:outline-none"
        aria-label="Close chat"
      >
        {/* Placeholder for Close Icon - Replace with actual icon */}
        {/* <VscChromeClose size={20} /> */}
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
          <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

export default ChatHeader;