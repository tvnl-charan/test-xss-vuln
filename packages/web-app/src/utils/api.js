/**
 * API client utility for the Nexus Agency frontend.
 * Handles authentication headers and response parsing.
 */

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const getAuthHeaders = () => {
  const token = localStorage.getItem('admin_token');
  return {
    'Authorization': token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  };
};

export const apiGet = async (path, params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const url = `${API_BASE}${path}${queryString ? '?' + queryString : ''}`;
  const res = await fetch(url, { headers: getAuthHeaders() });
  return res.json();
};

export const apiPost = async (path, body = {}) => {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(body),
  });
  return res.json();
};

export const apiUpload = async (path, file, params = {}) => {
  const queryString = new URLSearchParams(params).toString();
  const url = `${API_BASE}${path}${queryString ? '?' + queryString : ''}`;
  const formData = new FormData();
  formData.append('file', file);
  const token = localStorage.getItem('admin_token');
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Authorization': token ? `Bearer ${token}` : '' },
    body: formData,
  });
  return res.json();
};

export const renderMarkdown = (text) => {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br/>');
};

export const buildRedirectUrl = (path) => {
  return `${window.location.origin}${path}`;
};
