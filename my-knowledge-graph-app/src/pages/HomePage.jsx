import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, UploadCloud, Bot, Combine, FileUp, Network, MessageSquare, Database, FunctionSquare, GitBranchPlus, FileJson, FileText } from 'lucide-react'; // Added/changed icons

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
          Welcome to <span className="text-blue-600 dark:text-blue-400">Celervus</span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
          Transform diverse data like JSON and PDFs into a powerful, interconnected knowledge graph. Chat intelligently with your data using **Celerbud**, powered by GraphRAG and BAML.
        </p>
        <div className="flex flex-wrap justify-center gap-4"> {/* Use gap for spacing */}
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              to="/upload" // Assuming /upload handles both PDF/JSON or redirects
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-md shadow-md hover:bg-blue-700 transition-colors duration-200 text-base font-medium"
            >
              Upload Data <UploadCloud size={20} className="ml-2" />
            </Link>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              to="/topics" // Link to explore PDF-derived topics
              className="inline-flex items-center px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-md shadow-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 text-base font-medium"
            >
              Explore Topics <Network size={20} className="ml-2" />
            </Link>
          </motion.div>
          {/* Optional: Add a link to JSON data page if it exists */}
           <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              to="/json-data" // Link to explore JSON data structures/chat
              className="inline-flex items-center px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-md shadow-md hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 text-base font-medium"
            >
              Query JSON Data <FileJson size={20} className="ml-2" />
            </Link>
          </motion.div>
        </div>
      </motion.div>

      {/* Feature Highlights / Use Cases */}
      <div className="py-16 px-4 sm:px-6 lg:px-8">
         <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">Unlock Your Data's Potential</h2>
        <div className="max-w-7xl mx-auto grid md:grid-cols-3 gap-8">
          {/* Use Case 1: Easy KG from JSON / Topic Digestion from PDF */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow flex flex-col items-center text-center"
          >
            <FileUp size={48} className="text-blue-600 dark:text-blue-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">Intelligent Data Ingestion</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Easily create knowledge graphs from JSON structures or digest complex PDFs into explorable topics and subtopics for enhanced understanding.
            </p>
          </motion.div>
          {/* Use Case 2: Unified Knowledge Graph */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow flex flex-col items-center text-center"
          >
            <Combine size={48} className="text-blue-600 dark:text-blue-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">Unified Knowledge Graph</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Leverage KuzuDB to store structured (JSON) and unstructured (PDF) data interconnectedly, revealing hidden relationships and insights.
            </p>
          </motion.div>
          {/* Use Case 3: Conversational AI / Showcasing BAML/GraphRAG */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow flex flex-col items-center text-center"
          >
            <Bot size={48} className="text-blue-600 dark:text-blue-400 mb-4" />
            <h3 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">Conversational AI: Celerbud</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Chat naturally with Celerbud. Powered by BAML orchestration and GraphRAG retrieval, it provides context-aware answers grounded in your unified graph.
            </p>
          </motion.div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-100 dark:bg-gray-900">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">Simple Steps to Insight</h2>
        <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-blue-100 dark:bg-blue-900/50 p-4 rounded-full inline-block mb-4 ring-4 ring-blue-200 dark:ring-blue-800/60">
              <FileUp size={32} className="text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">1. Upload Data</h3>
            <p className="text-gray-600 dark:text-gray-300">Submit your JSON files or PDF documents.</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 dark:bg-blue-900/50 p-4 rounded-full inline-block mb-4 ring-4 ring-blue-200 dark:ring-blue-800/60">
              <Network size={32} className="text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">2. Build Knowledge Graph</h3>
            <p className="text-gray-600 dark:text-gray-300">Celervus AI analyzes, extracts, and structures data in KuzuDB.</p>
          </div>
          <div className="text-center">
            <div className="bg-blue-100 dark:bg-blue-900/50 p-4 rounded-full inline-block mb-4 ring-4 ring-blue-200 dark:ring-blue-800/60">
              <MessageSquare size={32} className="text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">3. Chat & Explore</h3>
            <p className="text-gray-600 dark:text-gray-300">Interact via Celerbud or browse topics to gain insights.</p>
          </div>
        </div>
      </div>

      {/* Key Technology Section (Replacing Testimonials) */}
      <div className="py-16 px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">Powered by Leading Technologies</h2>
        <div className="max-w-5xl mx-auto grid sm:grid-cols-3 gap-8">
          <div className="flex flex-col items-center text-center p-4">
            <Database size={40} className="text-blue-600 dark:text-blue-400 mb-3"/>
            <h3 className="text-xl font-semibold mb-1 text-gray-900 dark:text-white">KuzuDB</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">High-performance, embeddable graph database for efficient storage and complex queries.</p>
          </div>
           <div className="flex flex-col items-center text-center p-4">
            <FunctionSquare size={40} className="text-blue-600 dark:text-blue-400 mb-3"/>
            <h3 className="text-xl font-semibold mb-1 text-gray-900 dark:text-white">BAML</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">Reliably orchestrate LLM interactions and typed function calls for robust AI workflows.</p>
          </div>
           <div className="flex flex-col items-center text-center p-4">
            <GitBranchPlus size={40} className="text-blue-600 dark:text-blue-400 mb-3"/>
            <h3 className="text-xl font-semibold mb-1 text-gray-900 dark:text-white">GraphRAG</h3>
            <p className="text-gray-600 dark:text-gray-300 text-sm">Enhances Retrieval-Augmented Generation by leveraging graph relationships for deeper context.</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">About Celervus</h3>
              <p className="text-sm text-gray-300">
                Celervus empowers users to unlock insights from diverse data sources using knowledge graphs and conversational AI.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/upload" className="hover:text-blue-400 transition-colors">Upload Data</Link>
                </li>
                <li>
                  <Link to="/topics" className="hover:text-blue-400 transition-colors">Explore PDF Topics</Link>
                </li>
                 <li>
                  <Link to="/json-data" className="hover:text-blue-400 transition-colors">Explore JSON Data</Link>
                </li>
                {/* Add other relevant links like Documentation if available */}
                {/* <li>
                  <a href="#" className="hover:text-blue-400 transition-colors">Documentation</a>
                </li> */}
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact / Source</h3>
              <p className="text-sm text-gray-300">Email: [Your Project Email]</p>
              {/* Add link to GitHub repo if public */}
              {/* <p className="text-sm"><a href="[Your Repo Link]" className="hover:text-blue-400 transition-colors">GitHub Repository</a></p> */}
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-700 text-center text-sm text-gray-400">© {new Date().getFullYear()} Celervus. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;