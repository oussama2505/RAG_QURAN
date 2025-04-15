import { writable } from 'svelte/store';

// Define the Source interface to match backend response
export interface Source {
  source_type: string;
  reference: string;
  content: string;
}

// Define the app store state interface
interface AppState {
  apiKey: string | null;
  question: string | null;
  selectedSurah: number | null;
  recentQuestions: string[];
  apiStatus: boolean;
  error: string | null; // Add error state property
}

// Create the initial state
const initialState: AppState = {
  apiKey: localStorage.getItem('quran_rag_api_key'),
  question: null,
  selectedSurah: null,
  recentQuestions: JSON.parse(localStorage.getItem('quran_rag_recent_questions') || '[]'),
  apiStatus: false,
  error: null // Initialize as null
};

// Create the store
const createAppStore = () => {
  const { subscribe, update, set } = writable<AppState>(initialState);

  return {
    subscribe,
    
    setApiKey: (apiKey: string) => {
      localStorage.setItem('quran_rag_api_key', apiKey);
      update(state => ({ ...state, apiKey }));
    },
    
    setQuestion: (question: string) => {
      update(state => ({ ...state, question }));
    },
    
    setSelectedSurah: (surahNumber: number | null) => {
      update(state => ({ ...state, selectedSurah: surahNumber }));
    },
    
    addRecentQuestion: (question: string) => {
      update(state => {
        // Remove if exists and add to beginning
        const filteredQuestions = state.recentQuestions.filter(q => q !== question);
        const newQuestions = [question, ...filteredQuestions].slice(0, 10); // Keep only 10 most recent
        
        // Save to localStorage
        localStorage.setItem('quran_rag_recent_questions', JSON.stringify(newQuestions));
        
        return {
          ...state,
          recentQuestions: newQuestions
        };
      });
    },
    
    clearRecentQuestions: () => {
      localStorage.removeItem('quran_rag_recent_questions');
      update(state => ({ ...state, recentQuestions: [] }));
    },

    setApiStatus: (status: boolean) => {
      update(state => ({ ...state, apiStatus: status }));
    },
    
    setError: (error: string | null) => {
      update(state => ({ ...state, error }));
    },

    setSurahFilter: (surah: number | null) => {
      update(state => ({ ...state, selectedSurah: surah }));
    }
  };
};

export const appStore = createAppStore();