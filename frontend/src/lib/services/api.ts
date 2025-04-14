import axios from 'axios';
import type { Source } from '../stores/appStore';

// Base API URL - will be proxied in development
const API_BASE_URL = '';  // Empty string since we're using the proxy

// API client with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Response interface
export interface QueryResponse {
  answer: string;
  sources: Source[];
  filters_applied: {
    surah_filter?: number;
    verse_filter?: number;
  };
}

// API functions
export const api = {
  /**
   * Query the Quran RAG system
   */
  async queryQuran(question: string, surahFilter?: number, verseFilter?: number): Promise<QueryResponse> {
    try {
      // The backend expects a POST to /api/ask with a JSON body
      const response = await apiClient.post('/api/ask', {
        question,
        surah_filter: surahFilter || null,
        verse_filter: verseFilter || null
      });
      
      return response.data;
    } catch (error) {
      console.error('Error querying the API:', error);
      throw error;
    }
  },
  
  /**
   * Check if the API is available
   */
  async checkHealth(): Promise<boolean> {
    try {
      // Use the health endpoint that's defined in the backend
      const response = await apiClient.get('/health');
      return response.status === 200 && response.data?.status === "ok";
    } catch (error) {
      console.error('API health check failed:', error);
      return false;
    }
  }
};