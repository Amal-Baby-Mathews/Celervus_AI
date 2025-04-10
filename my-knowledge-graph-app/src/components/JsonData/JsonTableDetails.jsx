import React from 'react';
import { motion } from 'framer-motion';
import LoadingSpinner from '../Common/LoadingSpinner'; // Assuming you have a spinner

function JsonTableDetails({ nodes, isLoading, error }) {
  if (isLoading) {
    return <div className="flex justify-center items-center h-full"><LoadingSpinner /></div>;
  }

  if (error) {
    return <p className="text-red-600 dark:text-red-400 p-4">{error}</p>;
  }

  if (!nodes || nodes.length === 0) {
    return <p className="text-gray-500 dark:text-gray-400 p-4 italic">No nodes found in this table.</p>;
  }

  // Simple list view - could be enhanced with a table or cards
  return (
    <motion.div
      className="space-y-2"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {nodes.map((node, index) => (
        <motion.div
          key={node._id || index} // Use node._id if available, otherwise index
          className="bg-gray-50 dark:bg-gray-700 p-3 rounded-md shadow-sm border border-gray-200 dark:border-gray-600"
          initial={{ x: -10, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: index * 0.03 }} // Stagger entry
        >
          <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words">
            {JSON.stringify(node, null, 2)}
          </pre>
        </motion.div>
      ))}
    </motion.div>
  );
}

export default JsonTableDetails;