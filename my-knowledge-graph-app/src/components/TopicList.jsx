import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getAllTopics } from '../services/api';
import { ChevronRight, Loader, AlertCircle, FileText, List, Network } from 'lucide-react';

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
            <p>{subtopic.full_text || 'No full text available.'}</p>
            {subtopic.bullet_points && subtopic.bullet_points.length > 0 && (
              <div className="mt-2">
                <h5 className="text-xs sm:text-sm font-semibold text-gray-600 dark:text-gray-400 mb-1 flex items-center">
                  <List size={14} className="mr-1.5" /> Key Points:
                </h5>
                <ul className="list-disc list-inside text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1">
                  {subtopic.bullet_points.map((point, index) => (
                    <li key={index}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const TopicList = () => {
  const [topics, setTopics] = useState([]);
  const [selectedTopicId, setSelectedTopicId] = useState(null);
  const [selectedTopicDetails, setSelectedTopicDetails] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState('loading');
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTopics = async () => {
      setLoadingStatus('loading');
      setError('');
      try {
        const response = await getAllTopics();
        setTopics(response.data || []);
        setLoadingStatus('success');
      } catch (err) {
        console.error('Error fetching topics:', err);
        setError(err.response?.data?.detail || 'Failed to load topics.');
        setLoadingStatus('error');
      }
    };
    fetchTopics();
  }, []);

  const handleSelectTopic = async (topicId) => {
    if (selectedTopicId === topicId) {
      setSelectedTopicId(null);
      setSelectedTopicDetails(null);
    } else {
      setSelectedTopicId(topicId);
      setSelectedTopicDetails(null);
      setDetailLoading(true);
      setError('');
      try {
        const topic = topics.find(t => t.id === topicId);
        setSelectedTopicDetails(topic || {});
      } catch (err) {
        console.error(`Error setting details for topic ${topicId}:`, err);
        setError(`Failed to load details for topic ${topicId}.`);
        setSelectedTopicId(null);
      } finally {
        setDetailLoading(false);
      }
    }
  };

  return (
    <div className="grid md:grid-cols-3 gap-6 sm:gap-8">
      <div className="md:col-span-1">
        <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-700">
          Available Topics
        </h2>
        <AnimatePresence>
          {loadingStatus === 'loading' && (
            <motion.div key="loader" className="flex justify-center items-center h-40" exit={{ opacity: 0 }}>
              <Loader size={32} className="text-blue-600 dark:text-blue-400 animate-spin" />
            </motion.div>
          )}
          {loadingStatus === 'error' && error && (
            <motion.div
              key="error"
              className="p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-md flex items-center"
              exit={{ opacity: 0 }}
            >
              <AlertCircle size={20} className="mr-2" /> {error}
            </motion.div>
          )}
          {loadingStatus === 'success' && topics.length === 0 && (
            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-gray-600 dark:text-gray-400">
              No topics found. Upload a PDF to create one.
            </motion.div>
          )}
          {loadingStatus === 'success' && topics.length > 0 && (
            <motion.div layout className="space-y-2">
              <AnimatePresence initial={false}>
                {topics.map((topic) => (
                  <TopicItem key={topic.id} topic={topic} onSelect={handleSelectTopic} isSelected={selectedTopicId === topic.id} />
                ))}
              </AnimatePresence>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <div className="md:col-span-2">
        <AnimatePresence mode="wait">
          {selectedTopicId ? (
            <motion.div
              key={selectedTopicId}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.4, ease: 'easeInOut' }}
              className="sticky top-24"
            >
              <h2 className="text-xl sm:text-2xl font-semibold mb-4 text-gray-900 dark:text-white border-b pb-2 border-gray-200 dark:border-gray-700">
                {detailLoading ? 'Loading Details...' : selectedTopicDetails?.name || 'Details'}
              </h2>
              {detailLoading && (
                <div className="flex justify-center items-center h-40">
                  <Loader size={32} className="text-blue-600 dark:text-blue-400 animate-spin" />
                </div>
              )}
              {!detailLoading && error && (
                <div className="p-4 bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-md flex items-center">
                  <AlertCircle size={20} className="mr-2" /> {error}
                </div>
              )}
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