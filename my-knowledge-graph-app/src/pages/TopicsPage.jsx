// import React from 'react';
// import { motion } from 'framer-motion';
// import TopicList from '../components/TopicList';

// const TopicsPage = () => {
//   return (
//     <motion.div
//       initial={{ opacity: 0, y: 20 }}
//       animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.5, ease: 'easeOut' }}
//       className="min-h-screen"
//     >
//       <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-6 sm:mb-8 text-gray-900 dark:text-white">
//         Explore Topics
//       </h1>
//       <TopicList />
//     </motion.div>
//   );
// };

// export default TopicsPage;
import React from 'react';
import { motion } from 'framer-motion';
import TopicList from '../components/TopicList';

const TopicsPage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="min-h-screen p-4 sm:p-6 md:p-8" // Added padding for better layout
    >
      <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-6 sm:mb-8 text-gray-900 dark:text-white">
        Explore Topics
      </h1>
      <TopicList />
    </motion.div>
  );
};

export default TopicsPage;