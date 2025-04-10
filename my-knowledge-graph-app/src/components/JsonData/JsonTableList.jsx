import React from 'react';
import { motion } from 'framer-motion';

function JsonTableList({ tables, selectedTableId, onSelectTable }) {
  return (
    <motion.ul
        className="space-y-2 max-h-60 overflow-y-auto pr-1" // Added max-h and overflow
        variants={{
            hidden: { opacity: 0 },
            visible: {
                opacity: 1,
                transition: { staggerChildren: 0.05 } // Stagger animation for list items
            }
        }}
        initial="hidden"
        animate="visible"
    >
      {tables.map((table) => (
        <motion.li
          key={table.id}
          variants={{ hidden: { y: 10, opacity: 0 }, visible: { y: 0, opacity: 1 } }}
        >
          <button
            onClick={() => onSelectTable(table)}
            className={`w-full text-left px-3 py-2 rounded-md transition-colors duration-150 ease-in-out ${
              selectedTableId === table.id
                ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 font-semibold'
                : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            {table.name} <span className="text-xs opacity-70">(ID: {table.id})</span>
          </button>
        </motion.li>
      ))}
    </motion.ul>
  );
}

export default JsonTableList;