import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress,
  });
};

export const deleteDocument = (documentId) => {
  return apiClient.delete(`/documents/${documentId}`);
};

export const clearAllData = () => {
  return apiClient.delete('/clear-all');
};

export const postChatMessage = (query, documentId) => {
  return apiClient.post('/chat', { query, document_id: documentId });
};

export const summarizeDocument = (documentId) => {
  return apiClient.post('/tasks/summarize', { document_id: documentId });
};

export const generateQuestions = (documentId, numQuestions) => {
  return apiClient.post('/tasks/generate-questions', {
    document_id: documentId,
    num_questions: numQuestions,
  });
};

export const extractKeywords = (documentId) => {
  return apiClient.post('/tasks/extract-keywords', { document_id: documentId });
};
