import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Upload, Edit, Trash, Database, Loader2 } from 'lucide-react';
import axios from 'axios';

const AddEntryForm = ({ onSuccess, onError }) => {
  const [entries, setEntries] = useState([{ text: '', image_path: '', file_path: '' }]);
  const [loading, setLoading] = useState(false);

  const handleAddEntry = async (e) => {
    e.preventDefault();
    if (entries.every(entry => !entry.text.trim())) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8008/db/add', entries);
      onSuccess(response.data.message);
      setEntries([{ text: '', image_path: '', file_path: '' }]);
    } catch (err) {
      onError('Failed to add entries. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleEntryChange = (index, field, value) => {
    const newEntries = [...entries];
    newEntries[index][field] = value;
    setEntries(newEntries);
  };

  const addEntryField = () => {
    setEntries([...entries, { text: '', image_path: '', file_path: '' }]);
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md"
    >
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <Upload size={24} className="text-blue-600 dark:text-blue-400 mr-2" /> Add Entries
      </h3>
      <form onSubmit={handleAddEntry}>
        {entries.map((entry, index) => (
          <div key={index} className="mb-4">
            <input
              type="text"
              value={entry.text}
              onChange={(e) => handleEntryChange(index, 'text', e.target.value)}
              placeholder="Text content"
              className="w-full px-4 py-2 mb-2 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <input
              type="text"
              value={entry.image_path}
              onChange={(e) => handleEntryChange(index, 'image_path', e.target.value)}
              placeholder="Image path (optional)"
              className="w-full px-4 py-2 mb-2 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <input
              type="text"
              value={entry.file_path}
              onChange={(e) => handleEntryChange(index, 'file_path', e.target.value)}
              placeholder="File path (optional)"
              className="w-full px-4 py-2 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
        ))}
        <button
          type="button"
          onClick={addEntryField}
          className="text-blue-600 dark:text-blue-400 hover:underline mb-4"
        >
          + Add another entry
        </button>
        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md shadow-md hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
        >
          {loading ? <Loader2 size={20} className="animate-spin mr-2" /> : <Upload size={20} className="mr-2" />}
          Submit Entries
        </button>
      </form>
    </motion.div>
  );
};

const UpdateEntryForm = ({ onSuccess, onError }) => {
  const [where, setWhere] = useState('');
  const [values, setValues] = useState({ text: '' });
  const [loading, setLoading] = useState(false);

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!where.trim() || !values.text.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8008/db/update', { where, values });
      onSuccess(response.data.message);
      setWhere('');
      setValues({ text: '' });
    } catch (err) {
      onError('Failed to update entries. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md"
    >
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <Edit size={24} className="text-blue-600 dark:text-blue-400 mr-2" /> Update Entry
      </h3>
      <form onSubmit={handleUpdate}>
        <input
          type="text"
          value={where}
          onChange={(e) => setWhere(e.target.value)}
          placeholder="Where condition (e.g., text = 'goodbye world')"
          className="w-full px-4 py-2 mb-4 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
        <input
          type="text"
          value={values.text}
          onChange={(e) => setValues({ text: e.target.value })}
          placeholder="New text value"
          className="w-full px-4 py-2 mb-4 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md shadow-md hover:bg-blue-700 transition-colors duration-200 flex items-center justify-center"
        >
          {loading ? <Loader2 size={20} className="animate-spin mr-2" /> : <Edit size={20} className="mr-2" />}
          Update Entry
        </button>
      </form>
    </motion.div>
  );
};

const DeleteEntryForm = ({ onSuccess, onError }) => {
  const [condition, setCondition] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDelete = async (e) => {
    e.preventDefault();
    if (!condition.trim()) return;

    setLoading(true);
    try {
      const response = await axios.delete('http://localhost:8008/db/delete', {
        data: { condition }
      });
      onSuccess(response.data.message);
      setCondition('');
    } catch (err) {
      onError('Failed to delete entries. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md"
    >
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <Trash size={24} className="text-blue-600 dark:text-blue-400 mr-2" /> Delete Entry
      </h3>
      <form onSubmit={handleDelete}>
        <input
          type="text"
          value={condition}
          onChange={(e) => setCondition(e.target.value)}
          placeholder="Condition (e.g., text = 'farewell world')"
          className="w-full px-4 py-2 mb-4 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full px-4 py-2 bg-red-600 text-white rounded-md shadow-md hover:bg-red-700 transition-colors duration-200 flex items-center justify-center"
        >
          {loading ? <Loader2 size={20} className="animate-spin mr-2" /> : <Trash size={20} className="mr-2" />}
          Delete Entry
        </button>
      </form>
    </motion.div>
  );
};

const DropTableButton = ({ onSuccess, onError }) => {
  const [loading, setLoading] = useState(false);

  const handleDrop = async () => {
    if (!window.confirm('Are you sure you want to drop the entire table? This action cannot be undone.')) return;

    setLoading(true);
    try {
      const response = await axios.delete('http://localhost:8008/db/drop');
      onSuccess(response.data.message);
    } catch (err) {
      onError('Failed to drop table. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md"
    >
      <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <Database size={24} className="text-blue-600 dark:text-blue-400 mr-2" /> Drop Table
      </h3>
      <button
        onClick={handleDrop}
        disabled={loading}
        className="w-full px-4 py-2 bg-red-600 text-white rounded-md shadow-md hover:bg-red-700 transition-colors duration-200 flex items-center justify-center"
      >
        {loading ? <Loader2 size={20} className="animate-spin mr-2" /> : <Database size={20} className="mr-2" />}
        Drop Table
      </button>
    </motion.div>
  );
};

export { AddEntryForm, UpdateEntryForm, DeleteEntryForm, DropTableButton };