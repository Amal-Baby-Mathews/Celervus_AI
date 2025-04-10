import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast'; // For feedback messages

import { getJsonTables, getJsonTableNodesById } from '../../services/api'; // Adjust path
import JsonTableList from '../../components/JsonData/JsonTableList';
import JsonIngestionForms from '../../components/JsonData/JsonIngestionForms';
import JsonTableDetails from '../../components/JsonData/JsonTableDetails';
import JsonQueryChat from '../../components/JsonData/JsonQueryChat';
import LoadingSpinner from '../../components/Common/LoadingSpinner'; // Assume you have a spinner

function JsonDataPage() {
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null); // Stores { id, name }
  const [tableNodes, setTableNodes] = useState([]);
  const [isLoadingTables, setIsLoadingTables] = useState(true);
  const [isLoadingNodes, setIsLoadingNodes] = useState(false);
  const [error, setError] = useState(null);

  const fetchTables = useCallback(async () => {
    setIsLoadingTables(true);
    setError(null);
    try {
      const response = await getJsonTables();
      setTables(response.data || []);
    } catch (err) {
      console.error("Error fetching JSON tables:", err);
      setError("Failed to load JSON tables. Please try again.");
      toast.error("Failed to load JSON tables.");
    } finally {
      setIsLoadingTables(false);
    }
  }, []);

  useEffect(() => {
    fetchTables();
  }, [fetchTables]);

  const handleTableSelect = useCallback(async (table) => {
    if (selectedTable?.id === table.id) {
       // Optional: Deselect if clicking the same table again
       // setSelectedTable(null);
       // setTableNodes([]);
       return; // Already selected
    }
    setSelectedTable(table);
    setTableNodes([]); // Clear previous nodes
    setIsLoadingNodes(true);
    setError(null);
    try {
      const response = await getJsonTableNodesById(table.id);
      setTableNodes(response.data || []);
    } catch (err) {
      console.error(`Error fetching nodes for table ${table.id}:`, err);
      setError(`Failed to load data for table "${table.name}".`);
      toast.error(`Failed to load data for table "${table.name}".`);
      setSelectedTable(null); // Deselect on error
    } finally {
      setIsLoadingNodes(false);
    }
  }, [selectedTable?.id]);

  const handleIngestionSuccess = () => {
    toast.success('JSON data ingested successfully!');
    fetchTables(); // Refresh the table list after successful ingestion
    setSelectedTable(null); // Deselect any current table
    setTableNodes([]);
  };

  // Animation variants for the right panel
  const panelVariants = {
    hidden: { x: '100%', opacity: 0 },
    visible: {
        x: 0,
        opacity: 1,
        transition: { type: 'spring', stiffness: 100, damping: 20, duration: 0.5 }
    },
    exit: {
        x: '100%',
        opacity: 0,
        transition: { duration: 0.3, ease: 'easeIn' }
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 md:gap-8 p-4 md:p-6 min-h-[calc(100vh-150px)]"> {/* Adjust min-h based on header/footer */}
      <Toaster position="top-right" />

      {/* Left Panel: Ingestion & Table List */}
      <motion.div
        initial={{ x: -50, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="lg:w-1/3 xl:w-1/4 space-y-6 flex-shrink-0"
      >
        <JsonIngestionForms onIngestionSuccess={handleIngestionSuccess} />

        <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200 border-b pb-2 dark:border-gray-700">
            Available JSON Tables
          </h2>
          {isLoadingTables ? (
             <div className="flex justify-center items-center h-32"> <LoadingSpinner /> </div>
          ) : error && !tables.length ? (
            <p className="text-red-600 dark:text-red-400">{error}</p>
          ) : !tables.length ? (
            <p className="text-gray-500 dark:text-gray-400">No JSON tables found.</p>
          ) : (
            <JsonTableList
              tables={tables}
              selectedTableId={selectedTable?.id}
              onSelectTable={handleTableSelect}
            />
          )}
        </div>
      </motion.div>

      {/* Right Panel: Details & Chat (Animated) */}
      <div className="flex-grow lg:w-2/3 xl:w-3/4 relative overflow-hidden"> {/* Parent for positioning animation */}
        <AnimatePresence mode="wait">
          {selectedTable ? (
            <motion.div
              key={selectedTable.id} // Key ensures animation runs on change
              variants={panelVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="absolute inset-0 flex flex-col md:flex-row gap-4 md:gap-6 bg-white dark:bg-gray-800 shadow-lg rounded-lg p-4 md:p-6 overflow-y-auto" // Added overflow-y-auto
            >
               {/* Table Details Section */}
               <div className="md:w-1/2 h-full flex flex-col">
                 <h2 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200 border-b pb-2 dark:border-gray-700 flex-shrink-0">
                   Details for: <span className="text-blue-600 dark:text-blue-400">{selectedTable.name}</span> (ID: {selectedTable.id})
                 </h2>
                 <div className="flex-grow overflow-y-auto pr-2"> {/* Scrollable node list */}
                    <JsonTableDetails
                        nodes={tableNodes}
                        isLoading={isLoadingNodes}
                        error={error && !isLoadingNodes ? error : null} // Show error only if loading finished
                    />
                 </div>
               </div>

               {/* Chat Section */}
               <div className="md:w-1/2 h-full flex flex-col border-t md:border-t-0 md:border-l border-gray-200 dark:border-gray-700 pt-4 md:pt-0 md:pl-6">
                  <JsonQueryChat
                      tableId={selectedTable.id}
                      tableName={selectedTable.name}
                  />
               </div>

            </motion.div>
          ) : (
            <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 text-lg italic bg-gray-50 dark:bg-gray-800/50 rounded-lg"
            >
                Select a table or ingest JSON data to get started.
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default JsonDataPage;