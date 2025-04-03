import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_BASE_URL, getAllTopics,getTopicDetails } from '../services/api';
import { ChevronRight, Loader, AlertCircle, FileText, List, Network } from 'lucide-react';

// --- TopicItem Component (No changes needed) ---
const TopicItem = ({ topic, onSelect, isSelected }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className={`p-4 rounded-lg cursor-pointer border-l-4 ${
        isSelected ? 'border-blue-600 bg-blue-500/5' : 'border-transparent hover:border-blue-500/50 hover:bg-gray-50 dark:hover:bg-gray-700'
      }`}
      onClick={() => onSelect(topic.id)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex justify-between items-center">
        <span className="font-medium text-base sm:text-lg text-gray-900 dark:text-white">{topic.name}</span>
        <motion.div animate={{ x: isHovered || isSelected ? 5 : 0 }}>
          <ChevronRight size={20} className={`text-gray-400 dark:text-gray-500 ${isSelected ? 'text-blue-600 dark:text-blue-400' : ''}`} />
        </motion.div>
      </div>
    </motion.div>
  );
};

const SubtopicItem = ({ subtopic }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [enlargedImage, setEnlargedImage] = useState(null);

  // Ensure bullet_points is always an array
  const bulletPoints = Array.isArray(subtopic.bullet_points) ? subtopic.bullet_points : [];

  const handleImageClick = (imgUrl) => {
    setEnlargedImage(imgUrl);
  };

  const handleCloseEnlarged = () => {
    setEnlargedImage(null);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="ml-4 sm:ml-6 mb-3 bg-white dark:bg-gray-800 rounded-md shadow-sm border border-gray-200 dark:border-gray-700"
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full text-left p-3 sm:p-4 flex items-center justify-between text-sm sm:text-base font-medium text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
      >
        <div className="flex items-center">
          <FileText size={16} className="mr-2 text-blue-600 dark:text-blue-400 flex-shrink-0" />
          {subtopic.name}
        </div>
        <ChevronRight size={16} className={`transform transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
      </button>
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="px-3 sm:px-4 pb-3 sm:pb-4 text-sm text-gray-700 dark:text-gray-300 overflow-hidden"
          >
            {/* Display Full Text */}
            <p className="mb-2">{subtopic.full_text || 'No full text available.'}</p>

            {/* Display Bullet Points */}
            {bulletPoints.length > 0 && (
              <div className="mt-2">
                <h5 className="text-xs sm:text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1 flex items-center">
                  <List size={14} className="mr-1.5" /> Key Points:
                </h5>
                <ul className="list-disc list-inside text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  {bulletPoints.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Display Images */}
            {subtopic.image_metadata && subtopic.image_metadata.length > 0 && (
              <div className="mt-3 pt-2 border-t border-gray-200 dark:border-gray-700">
                <h5 className="text-xs sm:text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Related Images:</h5>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {subtopic.image_metadata.map((img, index) => (
                    <motion.button
                      key={img.url || index}
                      onClick={() => handleImageClick(`${API_BASE_URL}${img.url}`)}
                      className="w-full h-auto rounded border border-gray-300 dark:border-gray-600 focus:outline-none"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <img
                        src={`${API_BASE_URL}${img.url}`}
                        alt={img.image_name || `Image ${index + 1}`}
                        className="w-full h-auto object-cover rounded mb-1"
                        loading="lazy"
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate" title={img.image_name}>
                        {img.image_name || `Image ${index + 1}`} (Pg: {img.page_number})
                      </p>
                    </motion.button>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Enlarged Image Overlay */}
      <AnimatePresence>
        {enlargedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={handleCloseEnlarged}
          >
            <motion.img
              src={enlargedImage}
              alt="Enlarged Image"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ duration: 0.4, ease: 'easeInOut' }}
              className="max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-lg"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};


// --- TopicList Component (Main changes here) ---
const TopicList = () => {
  // State for the list of topics (id, name)
  const [topics, setTopics] = useState([]);
  // State for the currently selected topic ID
  const [selectedTopicId, setSelectedTopicId] = useState(null);
  // State for the *details* of the selected topic (fetched separately)
  const [selectedTopicDetails, setSelectedTopicDetails] = useState(null);
  // Loading state specifically for the initial topic list fetch
  const [listLoading, setListLoading] = useState(true); // Start loading initially
  // Loading state specifically for fetching topic details
  const [detailLoading, setDetailLoading] = useState(false);
  // General error state
  const [error, setError] = useState('');

  // Fetch the list of all topics on component mount
  useEffect(() => {
    const fetchTopics = async () => {
      setListLoading(true);
      setError(''); // Clear previous errors
      setTopics([]); // Clear previous topics
      try {
        const response = await getAllTopics();
        // Ensure response.data is an array, default to empty array if not
        setTopics(Array.isArray(response.data) ? response.data : []);
      } catch (err) {
        console.error('Error fetching topics:', err);
        setError(err.response?.data?.detail || 'Failed to load topics list.');
        setTopics([]); // Ensure topics is empty on error
      } finally {
        setListLoading(false); // Stop list loading indicator
      }
    };
    fetchTopics();
  }, []); // Empty dependency array means run once on mount

  // Handle selecting a topic from the list
  const handleSelectTopic = async (topicId) => {
    // If the clicked topic is already selected, deselect it
    if (selectedTopicId === topicId) {
      setSelectedTopicId(null);
      setSelectedTopicDetails(null);
      setError(''); // Clear any detail error
    } else {
      // Select a new topic
      setSelectedTopicId(topicId);
      setSelectedTopicDetails(null); // Clear previous details immediately
      setDetailLoading(true); // Show loading indicator for details pane
      setError(''); // Clear previous errors

      try {
        // Fetch the details for the *selected* topic using its ID
        const response = await getTopicDetails(topicId);
        setSelectedTopicDetails(response.data); // Store the fetched details
      } catch (err) {
        console.error(`Error fetching details for topic ${topicId}:`, err);
        setError(err.response?.data?.detail || `Failed to load details for the selected topic.`);
        // Keep topic selected in the list, but clear details and show error
        setSelectedTopicDetails(null);
      } finally {
        setDetailLoading(false); // Stop detail loading indicator
      }
    }
  };

  // Find the name of the selected topic from the initial list for the header
  // (Handles case where details are loading/failed but we still know the name)
  const selectedTopicName = topics.find(t => t.id === selectedTopicId)?.name || 'Topic Details';

  return (
    <div className="grid md:grid-cols-3 gap-6 sm:gap-8">
      {/* Left Panel: List of Topics */}
      <div className="md:col-span-1">
        <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-700">
          Available Topics
        </h2>
        <AnimatePresence>
          {/* List Loading State */}
          {listLoading && (
            <motion.div key="list-loader" className="flex justify-center items-center h-40" exit={{ opacity: 0 }}>
              <Loader size={32} className="text-blue-600 dark:text-blue-400 animate-spin" />
            </motion.div>
          )}
          {/* List Error State (only show if not loading and list is empty) */}
          {!listLoading && error && topics.length === 0 && (
            <motion.div
              key="list-error"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-md flex items-center"
            >
              <AlertCircle size={20} className="mr-2" /> {error}
            </motion.div>
          )}
          {/* Empty State (No topics found after successful load) */}
          {!listLoading && !error && topics.length === 0 && (
            <motion.div key="list-empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-gray-600 dark:text-gray-400">
              No topics found. Upload a PDF to create knowledge graph topics.
            </motion.div>
          )}
          {/* Success State: Display Topic List */}
          {!listLoading && topics.length > 0 && (
            <motion.div layout className="space-y-2">
              <AnimatePresence initial={false}>
                {topics.map((topic) => (
                  <TopicItem
                    key={topic.id}
                    topic={topic}
                    onSelect={handleSelectTopic}
                    isSelected={selectedTopicId === topic.id}
                  />
                ))}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Right Panel: Selected Topic Details */}
      <div className="md:col-span-2">
        <AnimatePresence mode="wait">
          {/* Show details or placeholder */}
          {selectedTopicId ? (
            // Details View (when a topic is selected)
            <motion.div
              key={selectedTopicId} // Key change triggers animation
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.4, ease: 'easeInOut' }}
              className="sticky top-24" // Make details sticky on scroll
            >
              <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-700">
                {/* Show Topic Name - Use fetched details name if available, otherwise fallback */}
                {detailLoading ? 'Loading Details...' : (selectedTopicDetails?.name || selectedTopicName)}
              </h2>

              {/* Detail Loading State */}
              {detailLoading && (
                <div className="flex justify-center items-center h-40">
                  <Loader size={32} className="text-blue-600 dark:text-blue-400 animate-spin" />
                </div>
              )}

              {/* Detail Error State */}
              {!detailLoading && error && !selectedTopicDetails && ( // Show error only if not loading and details failed
                <div className="p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-md flex items-center">
                  <AlertCircle size={20} className="mr-2" /> {error}
                </div>
              )}

              {/* Success State: Display Subtopics from fetched details */}
              {!detailLoading && !error && selectedTopicDetails && (
                <div>
                  <h3 className="text-lg sm:text-xl font-medium mb-3 text-blue-600 dark:text-blue-400">Subtopics</h3>
                  {selectedTopicDetails.subtopics && selectedTopicDetails.subtopics.length > 0 ? (
                    <motion.div layout className="space-y-2">
                      <AnimatePresence>
                        {selectedTopicDetails.subtopics.map((subtopic) => (
                          <SubtopicItem key={subtopic.id} subtopic={subtopic} />
                        ))}
                      </AnimatePresence>
                    </motion.div>
                  ) : (
                    <p className="text-gray-600 dark:text-gray-400 italic">No subtopics found for this topic.</p>
                  )}
                </div>
              )}
            </motion.div>
          ) : (
            // Placeholder View (when no topic is selected)
            <motion.div
              key="placeholder"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="flex flex-col items-center justify-center h-full text-center text-gray-600 dark:text-gray-400 p-6 sm:p-10 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg sticky top-24"
            >
              <Network size={48} className="mb-4 text-gray-400 dark:text-gray-500" />
              <p className="text-base sm:text-lg font-medium">Select a topic on the left</p>
              <p>to view its details and subtopics here.</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
export default TopicList;