// src/pages/HomePage.jsx
import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

const HomePage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="text-center"
    >
      <h1 className="text-4xl md:text-5xl font-bold text-text-main mb-4">
        Welcome to <span className="text-primary">KnowledgeGraph</span> AI
      </h1>
      <p className="text-lg text-text-muted mb-8 max-w-2xl mx-auto">
        Upload your PDF documents to automatically generate and visualize structured knowledge graphs. Explore topics and subtopics effortlessly.
      </p>
      <div className="flex justify-center space-x-4">
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Link to="/upload" className="btn-primary inline-flex items-center">
            Upload PDF <ArrowRight size={20} className="ml-2" />
          </Link>
        </motion.div>
         <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
           <Link
             to="/topics"
             className="inline-flex items-center px-4 py-2 bg-gray-200 text-text-main rounded-md shadow-sm hover:bg-gray-300 transition-colors duration-200"
           >
             View Existing Topics
           </Link>
         </motion.div>
      </div>
       {/* Add more fancy sections, feature highlights etc. here */}
       <div className="mt-16 grid md:grid-cols-3 gap-8">
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="card hover:shadow-lg transition-shadow"
            >
                <h3 className="text-xl font-semibold mb-2 text-primary">Automatic Extraction</h3>
                <p className="text-text-muted">Leverages AI to identify key topics and subtopics from your documents.</p>
            </motion.div>
             <motion.div
                 initial={{ opacity: 0, scale: 0.9 }}
                 animate={{ opacity: 1, scale: 1 }}
                 transition={{ duration: 0.5, delay: 0.4 }}
                 className="card hover:shadow-lg transition-shadow"
             >
                 <h3 className="text-xl font-semibold mb-2 text-primary">Interactive Visualization</h3>
                 <p className="text-text-muted">Explore the generated graph structure through an intuitive web interface.</p>
             </motion.div>
              <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.6 }}
                  className="card hover:shadow-lg transition-shadow"
              >
                  <h3 className="text-xl font-semibold mb-2 text-primary">API Driven</h3>
                  <p className="text-text-muted">Built with a FastAPI backend for robust data handling.</p>
              </motion.div>
       </div>
    </motion.div>
  );
};

export default HomePage;