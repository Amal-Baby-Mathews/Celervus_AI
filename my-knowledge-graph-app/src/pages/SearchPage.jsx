import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Loader2 } from 'lucide-react';
import axios from 'axios';
import { AddEntryForm, UpdateEntryForm, DeleteEntryForm, DropTableButton } from '../components/VDBComponents';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.get('http://localhost:8008/db/search', {
        params: { query, top_k: 5 },
      });
      setResults(response.data.results || []);
    } catch (err) {
      setError('Failed to fetch search results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSuccess = (message) => {
    setSuccess(message);
    setError(null);
    setResults([]);
    setQuery('');
  };

  const handleError = (message) => {
    setError(message);
    setSuccess(null);
  };

  return (
    <div className="bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800 min-h-screen py-16 px-4 sm:px-6 lg:px-8">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center max-w-4xl mx-auto"
      >
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 dark:text-white mb-6">
          Manage KnowledgeGraph Database
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
          Search, add, update, delete entries, or manage the database with our AI-powered tools.
        </p>
        {error && (
          <p className="text-red-500 dark:text-red-400 mt-4">{error}</p>
        )}
        {success && (
          <p className="text-green-500 dark:text-green-400 mt-4">{success}</p>
        )}
      </motion.div>

      {/* Search Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="max-w-4xl mx-auto mb-12"
      >
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Search size={24} className="text-blue-600 dark:text-blue-400 mr-2" /> Search Entries
        </h2>
        <form onSubmit={handleSearch} className="flex justify-center items-center">
          <div className="relative w-full">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for topics..."
              className="w-full px-4 py-3 pr-12 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600 dark:focus:ring-blue-400"
            />
            <button
              type="submit"
              disabled={loading}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
            >
              {loading ? <Loader2 size={24} className="animate-spin" /> : <Search size={24} />}
            </button>
          </div>
        </form>
      </motion.div>

      {/* Search Results */}
      {results.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="max-w-4xl mx-auto mb-12"
        >
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            Search Results ({results.length})
          </h2>
          <div className="grid gap-6">
            {results.map((result, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {result.text}
                </h3>
                {result.image_path && (
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    Image: <a href={result.image_path} className="text-blue-600 dark:text-blue-400 hover:underline">{result.image_path}</a>
                  </p>
                )}
                {result.file_path && (
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    File: <a href={result.file_path} className="text-blue-600 dark:text-blue-400 hover:underline">{result.file_path}</a>
                  </p>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {query && results.length === 0 && !loading && !error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-4xl mx-auto mb-12"
        >
          <p className="text-gray-600 dark:text-gray-300">No results found for "{query}".</p>
        </motion.div>
      )}

      {/* Database Management Sections */}
      <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
        <AddEntryForm onSuccess={handleSuccess} onError={handleError} />
        <UpdateEntryForm onSuccess={handleSuccess} onError={handleError} />
        <DeleteEntryForm onSuccess={handleSuccess} onError={handleError} />
        <DropTableButton onSuccess={handleSuccess} onError={handleError} />
      </div>
    </div>
  );
};

export default SearchPage;