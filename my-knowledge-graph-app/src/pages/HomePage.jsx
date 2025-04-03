import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Upload, Eye, Code } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800 min-h-screen">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center py-16 px-4 sm:px-6 lg:px-8"
      >
        <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 dark:text-white mb-4">
          Welcome to <span className="text-blue-600 dark:text-blue-400">KnowledgeGraph</span> AI
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          Upload your PDF documents to automatically generate and visualize structured knowledge graphs. Explore topics and subtopics effortlessly with cutting-edge AI technology.
        </p>
        <div className="flex justify-center space-x-4">
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              to="/upload"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-md shadow-md hover:bg-blue-700 transition-colors duration-200"
            >
              Upload PDF <ArrowRight size={20} className="ml-2" />
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              to="/topics"
              className="inline-flex items-center px-6 py-3 bg-gray-200 text-gray-700 rounded-md shadow-md hover:bg-gray-300 transition-colors duration-200"
            >
              View Existing Topics
            </Link>
          </motion.div>
        </div>
      </motion.div>

      {/* Feature Highlights */}
      <div className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <Upload size={48} className="text-blue-600 dark:text-blue-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">Automatic Extraction</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Leverages advanced AI to extract key topics and subtopics from your documents seamlessly.
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <Eye size={48} className="text-blue-600 dark:text-blue-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">Interactive Visualization</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Navigate and explore your knowledge graphs with an intuitive, interactive web interface.
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
          >
            <Code size={48} className="text-blue-600 dark:text-blue-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">API Driven</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Powered by a robust FastAPI backend for efficient and scalable data processing.
            </p>
          </motion.div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-100 dark:bg-gray-900">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">How It Works</h2>
        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 dark:bg-blue-900 p-4 rounded-full inline-block mb-4">
              <Upload size={32} className="text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Upload PDF</h3>
            <p className="text-gray-600 dark:text-gray-300">Simply upload your PDF document to get started.</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 dark:bg-blue-900 p-4 rounded-full inline-block mb-4">
              <Eye size={32} className="text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Generate Graph</h3>
            <p className="text-gray-600 dark:text-gray-300">Our AI processes the document to create a knowledge graph.</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 dark:bg-blue-900 p-4 rounded-full inline-block mb-4">
              <Code size={32} className="text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Explore & Interact</h3>
            <p className="text-gray-600 dark:text-gray-300">Dive into the graph with an easy-to-use interface.</p>
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-8">What Our Users Say</h2>
        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              "This tool has revolutionized how I manage my research papers. The automatic extraction is incredibly accurate!"
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">- Dr. Jane Doe, Researcher</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              "The interactive visualizations are a game-changer for understanding complex documents."
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">- John Smith, Data Analyst</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">About Us</h3>
              <p className="text-sm">
                KnowledgeGraph AI empowers users to unlock insights from documents with advanced AI-driven tools.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2">
                <li>
                  <Link to="/upload" className="hover:text-blue-400">Upload PDF</Link>
                </li>
                <li>
                  <Link to="/topics" className="hover:text-blue-400">View Topics</Link>
                </li>
                <li>
                  <a href="#" className="hover:text-blue-400">Documentation</a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <p className="text-sm">Email: support@knowledgegraph.ai</p>
              <p className="text-sm">Twitter: @KnowledgeGraphAI</p>
            </div>
          </div>
          <div className="mt-8 text-center text-sm">&copy; 2023 KnowledgeGraph AI. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;