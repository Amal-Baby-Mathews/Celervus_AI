import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate
import { motion, AnimatePresence } from 'framer-motion';
import { createGraphFromPDF } from '../services/api';
import { UploadCloud, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, success, error
  const [message, setMessage] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const [subtopicLimit, setSubtopicLimit] = useState(10); // Default limit
  const navigate = useNavigate(); // Hook for navigation

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setStatus('idle');
      setMessage('');
    } else {
      setSelectedFile(null);
      setStatus('error');
      setMessage('Please select a PDF file.');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setStatus('error');
      setMessage('No file selected.');
      return;
    }

    setStatus('uploading');
    setMessage('Uploading and processing PDF...');

    try {
      const response = await createGraphFromPDF(selectedFile, subtopicLimit); // Pass subtopic limit
      setStatus('success');
      setMessage(response.data.message || 'Graph created successfully!');
      setSelectedFile(null);

      const topics = response.data.topics || [];
      if (topics.length > 0) {
        const firstTopicId = topics[0].id;
        setTimeout(() => {
          navigate('/topics', { state: { selectedTopicId: firstTopicId } });
        }, 1000);
      } else {
        setTimeout(() => {
          navigate('/topics');
        }, 1000);
      }
    } catch (error) {
      setStatus('error');
      setMessage(error.response?.data?.detail || error.message || 'An error occurred during upload.');
      console.error("Upload error:", error);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(false);
    const file = event.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setStatus('idle');
      setMessage('');
    } else {
      setSelectedFile(null);
      setStatus('error');
      setMessage('Please drop a PDF file.');
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setDragOver(false);
  };

  return (
    <motion.div
      className="card space-y-6"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
          dragOver ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-primary'
        }`}
        onClick={() => document.getElementById('fileInput').click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          type="file"
          id="fileInput"
          accept=".pdf"
          onChange={handleFileChange}
          className="hidden"
          disabled={status === 'uploading'}
        />
        <UploadCloud size={48} className={`mx-auto mb-4 ${dragOver ? 'text-primary' : 'text-gray-400'}`} />
        {selectedFile ? (
          <div className="text-text-main font-medium flex items-center justify-center">
            <FileText size={20} className="mr-2 text-secondary" /> {selectedFile.name}
          </div>
        ) : (
          <p className="text-text-muted">
            {dragOver ? 'Drop the PDF file here' : 'Drag & drop a PDF file here, or click to select'}
          </p>
        )}
      </div>

      {/* Subtopic Limit Slider */}
      <div className="space-y-2">
        <label htmlFor="subtopic-limit" className="text-text-main font-medium">
          Maximum Subtopics: {subtopicLimit}
        </label>
        <input
          type="range"
          id="subtopic-limit"
          min="1"
          max="50" // Adjust max as needed
          value={subtopicLimit}
          onChange={(e) => setSubtopicLimit(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary"
          disabled={status === 'uploading'}
        />
        <p className="text-text-muted text-sm">
          Adjust the number of subtopics to extract (1-50).
        </p>
      </div>

      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className={`p-3 rounded-md text-sm flex items-center ${
              status === 'success' ? 'bg-green-100 text-green-800' :
              status === 'error' ? 'bg-red-100 text-red-800' :
              'bg-blue-100 text-blue-800'
            }`}
          >
            {status === 'success' && <CheckCircle size={20} className="mr-2 flex-shrink-0" />}
            {status === 'error' && <AlertCircle size={20} className="mr-2 flex-shrink-0" />}
            {status === 'uploading' && <Loader size={20} className="mr-2 flex-shrink-0 animate-spin" />}
            {message}
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        onClick={handleUpload}
        disabled={!selectedFile || status === 'uploading'}
        className="btn-primary w-full flex items-center justify-center"
        whileHover={{ scale: status !== 'uploading' ? 1.03 : 1 }}
        whileTap={{ scale: status !== 'uploading' ? 0.98 : 1 }}
      >
        {status === 'uploading' ? (
          <>
            <Loader size={20} className="mr-2 animate-spin" /> Processing...
          </>
        ) : (
          <>
            <UploadCloud size={20} className="mr-2" /> Upload & Create Graph
          </>
        )}
      </motion.button>
    </motion.div>
  );
};
export default FileUpload;