import { writable } from 'svelte/store';

export interface SearchResult {
  text: string;
  surah: number;
  verse: number;
  score: number;
}

export interface SearchState {
  isLoading: boolean;
  results: SearchResult[];
  error: string | null;
  query: string;
}

const defaultState: SearchState = {
  isLoading: false,
  results: [],
  error: null,
  query: ''
};

export const searchState = writable<SearchState>(defaultState); 