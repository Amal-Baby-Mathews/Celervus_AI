// src/services/api.js
import axios from 'axios';

// IMPORTANT: Replace with your actual FastAPI backend URL
// Use environment variables for this in a real app
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8008';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// --- Graph Creation ---
export const createGraphFromPDF = (file, limit = 10) => {
  const formData = new FormData();
  formData.append('file', file); // 'file' must match the FastAPI parameter name
  formData.append('limit', limit); // Add the limit parameter

  return apiClient.post('/create_graph', formData, {
    headers: {
      'Content-Type': 'multipart/form-data', // Important for file uploads
    },
  });
};

// --- Topic Endpoints ---
export const getAllTopics = () => {
  return apiClient.get('/topics');
};

export const getTopicDetails = (topicId) => {
  return apiClient.get(`/topics/${topicId}`);
};

// --- Subtopic Endpoints ---
export const getSubtopicDetails = (subtopicId) => {
  return apiClient.get(`/subtopics/${subtopicId}`);
};

// You might want error handling wrappers around these calls later

export default apiClient; // Optional: export the configured client if needed elsewhere