// src/pages/UploadPage.jsx
import React from 'react';
import { motion } from 'framer-motion';
import FileUpload from '../components/FileUpload'; // We'll create this next

const UploadPage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="max-w-xl mx-auto"
    >
      <h1 className="text-3xl font-bold mb-6 text-center text-text-main">Upload PDF</h1>
      <FileUpload />
    </motion.div>
  );
};

export default UploadPage;