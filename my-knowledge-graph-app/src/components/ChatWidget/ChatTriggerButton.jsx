// src/components/ChatWidget/ChatTriggerButton.jsx
import React from 'react';
import { motion } from 'framer-motion'; // Import motion
import { BsChatDotsFill } from "react-icons/bs"; // Use the imported icon

function ChatTriggerButton({ onClick }) {
  return (
    // Use motion.button instead of button
    <motion.button
      onClick={onClick}
      // Base styles (gradient, shape, shadow, etc.) - Removed conflicting Tailwind animations
      className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium rounded-full px-5 py-3 shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 overflow-hidden" // Added overflow-hidden for potential inner effects
      aria-label="Open Celerbud chat"

      // Framer Motion Props for Animation
      initial={{ scale: 0.8, opacity: 0, y: 20 }} // Initial state before entering
      animate={{
          scale: [1, 1.08, 1], // Subtle pulse effect (scale up slightly and back)
          opacity: 1,
          y: 0, // Animate from bottom
          transition: {
              scale: { repeat: Infinity, duration: 2.5, ease: "easeInOut" }, // Loop the pulse
              opacity: { duration: 0.5 },
              y: { duration: 0.5, type: "spring", stiffness: 150, damping: 15 } // Spring effect on entrance
          }
      }}
      whileHover={{
          scale: 1.1, // Scale up more noticeably on hover
          boxShadow: "0 10px 25px -5px rgba(99, 102, 241, 0.4), 0 8px 10px -6px rgba(99, 102, 241, 0.2)", // Enhanced shadow on hover (example indigo-like)
          transition: { type: "spring", stiffness: 300, damping: 10 } // Springy hover effect
      }}
      whileTap={{
          scale: 0.95 // Briefly shrink when clicked
      }}
    >
      {/* Using react-icons now */}
      <BsChatDotsFill size={20} className="flex-shrink-0" />
      {/* Added Text */}
      <span className="ml-2">Celerbud</span> {/* Ensure spacing if needed, though space-x-2 handles it */}
    </motion.button>
  );
}

export default ChatTriggerButton;