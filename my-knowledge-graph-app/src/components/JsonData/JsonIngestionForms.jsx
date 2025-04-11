import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ingestJsonFile, ingestJsonString } from '../../services/api';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../Common/LoadingSpinner';

function JsonIngestionForms({ onIngestionSuccess }) {
  const [file, setFile] = useState(null);
  const [jsonString, setJsonString] = useState('');
  const [fileNodeTable, setFileNodeTable] = useState('Node'); // Separate state for file form
  const [fileRelTable, setFileRelTable] = useState('');
  const [stringNodeTable, setStringNodeTable] = useState('Node'); // Separate state for string form
  const [stringRelTable, setStringRelTable] = useState('');
  const [isIngestingFile, setIsIngestingFile] = useState(false);
  const [isIngestingString, setIsIngestingString] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files ? event.target.files[0] : null);
  };

  const handleIngestFile = async (event) => {
    event.preventDefault();
    if (!file) {
      toast.error('Please select a JSON file.');
      return;
    }
    if (!fileNodeTable.trim()) {
      toast.error('Please provide a Node Table name for the file.');
      return;
    }

    setIsIngestingFile(true);
    try {
      await ingestJsonFile(file, fileNodeTable.trim(), fileRelTable.trim() || null);
      setFile(null);
      event.target.reset(); // Reset form fields
      setFileNodeTable('Node'); // Reset to default
      setFileRelTable('');
      toast.success('File ingested successfully!');
      onIngestionSuccess();
    } catch (err) {
      console.error('Error ingesting file:', err);
      const errorDetail = err.response?.data?.detail || err.message || 'Failed to ingest file.';
      toast.error(`Ingestion failed: ${errorDetail}`);
    } finally {
      setIsIngestingFile(false);
    }
  };

  const handleIngestString = async (event) => {
    event.preventDefault();
    if (!jsonString.trim()) {
      toast.error('Please enter a JSON string.');
      return;
    }
    if (!stringNodeTable.trim()) {
      toast.error('Please provide a Node Table name for the string.');
      return;
    }

    // Validate JSON and convert to string
    let jsonStringToSend;
    try {
      const parsedJson = JSON.parse(jsonString); // Validate the input
      jsonStringToSend = JSON.stringify(parsedJson); // Convert back to string
      console.log('JSON string to send:', jsonStringToSend); // Debug payload
    } catch (e) {
      toast.error('Invalid JSON string format.');
      return;
    }

    setIsIngestingString(true);
    try {
      await ingestJsonString(jsonStringToSend, stringNodeTable.trim(), stringRelTable.trim() || null);
      setJsonString('');
      setStringNodeTable('Node');
      setStringRelTable('');
      toast.success('JSON string ingested successfully!');
      onIngestionSuccess();
    } catch (err) {
      console.error('Error ingesting string:', err);
      const errorDetail = err.response?.data?.detail || err.message || 'Failed to ingest JSON string.';
      toast.error(`Ingestion failed: ${errorDetail}`);
    } finally {
      setIsIngestingString(false);
    }
  };

  const inputStyle = "mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm text-gray-900 dark:text-gray-100 disabled:opacity-50";
  const labelStyle = "block text-sm font-medium text-gray-700 dark:text-gray-300";
  const buttonStyle = "w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed";

  return (
    <motion.div
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.1 }}
      className="space-y-6 bg-white dark:bg-gray-800 shadow-md rounded-lg p-4"
    >
      <h2 className="text-xl font-semibold text-gray-700 dark:text-gray-200 border-b pb-2 dark:border-gray-700">Ingest JSON Data</h2>

      {/* File Ingestion Form */}
      <form onSubmit={handleIngestFile} className="space-y-3">
        <h3 className="text-md font-medium text-gray-600 dark:text-gray-300">Ingest from File</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="fileNodeTable" className={labelStyle}>Node Table Name *</label>
            <input
              type="text"
              id="fileNodeTable"
              value={fileNodeTable}
              onChange={(e) => setFileNodeTable(e.target.value)}
              required
              className={inputStyle}
              disabled={isIngestingFile}
            />
          </div>
          <div>
            <label htmlFor="fileRelTable" className={labelStyle}>Relationship Table Name (Optional)</label>
            <input
              type="text"
              id="fileRelTable"
              value={fileRelTable}
              onChange={(e) => setFileRelTable(e.target.value)}
              placeholder="e.g., HAS_CONDITION"
              className={inputStyle}
              disabled={isIngestingFile}
            />
          </div>
        </div>
        <div>
          <label htmlFor="jsonFile" className={labelStyle}>JSON File</label>
          <input
            type="file"
            id="jsonFile"
            accept=".json"
            onChange={handleFileChange}
            className={`${inputStyle} file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 dark:file:bg-indigo-900/50 file:text-indigo-700 dark:file:text-indigo-300 hover:file:bg-indigo-100 dark:hover:file:bg-indigo-900`}
            disabled={isIngestingFile}
          />
        </div>
        <button type="submit" className={buttonStyle} disabled={isIngestingFile}>
          {isIngestingFile ? <LoadingSpinner size="sm" /> : 'Ingest File'}
        </button>
      </form>

      {/* String Ingestion Form */}
      <form onSubmit={handleIngestString} className="space-y-3 border-t pt-4 dark:border-gray-700">
        <h3 className="text-md font-medium text-gray-600 dark:text-gray-300">Ingest from Text</h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label htmlFor="stringNodeTable" className={labelStyle}>Node Table Name *</label>
            <input
              type="text"
              id="stringNodeTable"
              value={stringNodeTable}
              onChange={(e) => setStringNodeTable(e.target.value)}
              required
              className={inputStyle}
              disabled={isIngestingString}
            />
          </div>
          <div>
            <label htmlFor="stringRelTable" className={labelStyle}>Relationship Table Name (Optional)</label>
            <input
              type="text"
              id="stringRelTable"
              value={stringRelTable}
              onChange={(e) => setStringRelTable(e.target.value)}
              placeholder="e.g., HAS_CONDITION"
              className={inputStyle}
              disabled={isIngestingString}
            />
          </div>
        </div>
        <div>
          <label htmlFor="jsonString" className={labelStyle}>JSON String</label>
          <textarea
            id="jsonString"
            rows="5"
            value={jsonString}
            onChange={(e) => setJsonString(e.target.value)}
            placeholder='[{"id": "p1", "name": "Gregory"}]'
            className={`${inputStyle} font-mono`}
            disabled={isIngestingString}
          />
        </div>
        <button type="submit" className={buttonStyle} disabled={isIngestingString}>
          {isIngestingString ? <LoadingSpinner size="sm" /> : 'Ingest String'}
        </button>
      </form>
    </motion.div>
  );
}

export default JsonIngestionForms;