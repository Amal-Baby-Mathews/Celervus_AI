import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Search, Loader2, ChevronDown, ChevronUp, X } from 'lucide-react';
import axios from 'axios';
import { AddEntryForm, UpdateEntryForm, DeleteEntryForm } from '../components/VDBComponents';

const SearchPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showForms, setShowForms] = useState(false);
  // Modal states
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imageSearchResults, setImageSearchResults] = useState([]);
  const [isImageSearchLoading, setIsImageSearchLoading] = useState(false);
  const [imageSearchError, setImageSearchError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.get('http://localhost:8008/db/search', {
        params: { query, top_k: 12 },
      });
      setResults(response.data.results || []);
    } catch (err) {
      setError('Failed to fetch search results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleImageClick = async (clickedResult) => {
    const pk = clickedResult.pk;
  
    if (!pk) {
      setImageSearchError('Invalid image selected for search (missing pk).');
      setError('Invalid image selected for search (missing pk).');
      return;
    }
  
    // Open modal and set selected image
    if (isImageModalOpen && selectedImage?.pk === pk) {
      setIsImageModalOpen(false);
      setSelectedImage(null);
      setImageSearchResults([]);
      setImageSearchError(null);
      return;
    }
    setIsImageModalOpen(true);
    setSelectedImage(clickedResult);
    setIsImageSearchLoading(true);
    setImageSearchError(null);
    setImageSearchResults([]);
  
    try {
      // Send GET request to image_search_by_pk endpoint
      const searchResponse = await axios.get('http://localhost:8008/db/image_search_by_pk', {
        params: { pk, top_k: 3 },
        headers: { 'Accept': 'application/json' },
      });
  
      setImageSearchResults(searchResponse.data.results || []);
    } catch (err) {
      console.error('Image search API call failed:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to perform image search. Please try again.';
      setImageSearchError(errorMessage);
      setError(errorMessage);
    } finally {
      setIsImageSearchLoading(false);
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
          Image Search & Database Management
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
          Search for images or manage the database using our tools.
        </p>
        {error && <p className="text-red-500 dark:text-red-400 mt-4">{error}</p>}
        {success && <p className="text-green-500 dark:text-green-400 mt-4">{success}</p>}
      </motion.div>

      {/* Upload New Images Dropdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-4xl mx-auto mb-8"
      >
        <button
          onClick={() => setShowForms(!showForms)}
          className="w-full flex justify-between items-center px-6 py-3 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition"
        >
          <span className="text-lg font-semibold">Upload New Images</span>
          {showForms ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
        </button>
        {showForms && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md mt-4 p-6 grid md:grid-cols-2 gap-6"
          >
            <AddEntryForm onSuccess={handleSuccess} onError={handleError} />
            <UpdateEntryForm onSuccess={handleSuccess} onError={handleError} />
            <DeleteEntryForm onSuccess={handleSuccess} onError={handleError} />
          </motion.div>
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
          <Search size={24} className="text-blue-600 dark:text-blue-400 mr-2" /> Search Images
        </h2>
        <form onSubmit={handleSearch} className="flex justify-center items-center">
          <div className="relative w-full">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for images..."
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
          className="max-w-6xl mx-auto"
        >
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-6">
            Search Results ({results.length})
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {results.map((result, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition cursor-pointer"
                onClick={() => handleImageClick(result)}
              >
                {(result.image_url || result.image_path) && (
                  <img
                    src={result.image_url || result.image_path}
                    alt={result.text || "Result image"}
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {result.text}
                  </h3>
                </div>
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

      {/* Image Search Modal */}
      {isImageModalOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setIsImageModalOpen(false)}
        >
          <motion.div
            initial={{ y: 50, opacity: 0, scale: 0.9 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 50, opacity: 0, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 200, damping: 25 }}
            className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-900 z-10">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Image Search Results</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Showing images similar to the one you selected</p>
              <button
                onClick={() => setIsImageModalOpen(false)}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            <div className="p-6 flex-grow">
              {selectedImage && (
                <div className="mb-8 text-center">
                  <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">Searching based on:</h3>
                  <div className="flex justify-center">
                    <img
                      src={selectedImage.image_url || selectedImage.image_path}
                      alt={selectedImage.text || "Selected image"}
                      className="max-w-xs max-h-64 rounded-lg shadow-lg object-contain"
                    />
                  </div>
                  {selectedImage.text && (
                    <p className="mt-3 text-gray-600 dark:text-gray-300 italic">"{selectedImage.text}"</p>
                  )}
                </div>
              )}

              <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                {isImageSearchLoading ? (
                  <div className="flex flex-col items-center justify-center h-48">
                    <Loader2 size={40} className="animate-spin text-blue-600" />
                    <p className="mt-4 text-gray-600 dark:text-gray-300">Searching for similar images...</p>
                  </div>
                ) : imageSearchError ? (
                  <p className="text-red-500 text-center py-10">{imageSearchError}</p>
                ) : imageSearchResults.length > 0 ? (
                  <>
                    <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4 text-center">
                      Similar Images Found ({imageSearchResults.length})
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                      {imageSearchResults.map((result, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ duration: 0.3, delay: index * 0.05 }}
                          className="bg-gray-100 dark:bg-gray-800 rounded-lg shadow-md overflow-hidden"
                        >
                          <img
                            src={result.image_url || result.image_path}
                            alt={result.text || "Result image"}
                            className="w-full h-40 object-cover"
                          />
                          {result.text && (
                            <div className="p-3">
                              <p className="text-sm text-gray-700 dark:text-gray-200 truncate">{result.text}</p>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="text-gray-500 text-center py-10">No similar images found.</p>
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default SearchPage;