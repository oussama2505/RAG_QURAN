import { searchState } from '../stores/search';
import { settings } from '../stores/settings';
import { addToCache, getFromCache } from '../stores/cache';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function performSearch(query: string, filters: { surah?: number; verse?: number } = {}) {
    try {
        // Check cache first
        const cachedResult = getFromCache(query, filters);
        if (cachedResult) {
            searchState.update(state => ({
                ...state,
                loading: false,
                results: cachedResult.results,
                totalResults: cachedResult.results.length
            }));
            return;
        }

        // Update search state to loading
        searchState.update(state => ({
            ...state,
            loading: true,
            error: null,
            query
        }));

        // Prepare request body
        const requestBody = {
            query,
            filters,
            model: settings.get().model,
            api_key: settings.get().api_key
        };

        // Make API request
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }

        const data = await response.json();

        // Cache the result
        addToCache({
            query,
            filters,
            results: data.results,
            timestamp: Date.now()
        });

        // Update search state with results
        searchState.update(state => ({
            ...state,
            loading: false,
            results: data.results,
            totalResults: data.total_results
        }));
    } catch (error) {
        // Update search state with error
        searchState.update(state => ({
            ...state,
            loading: false,
            error: error instanceof Error ? error.message : 'An unknown error occurred'
        }));
    }
}

export async function getTranslation(surah: number, verse: number) {
    try {
        // Update search state to loading
        searchState.update(state => ({
            ...state,
            loading: true,
            error: null
        }));

        // Prepare request body
        const requestBody = {
            surah,
            verse,
            translation: settings.get().translation,
            model: settings.get().model,
            api_key: settings.get().api_key
        };

        // Make API request
        const response = await fetch(`${API_BASE_URL}/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`Translation failed: ${response.statusText}`);
        }

        const data = await response.json();

        // Update search state with translation
        searchState.update(state => ({
            ...state,
            loading: false,
            translation: data.translation
        }));
    } catch (error) {
        // Update search state with error
        searchState.update(state => ({
            ...state,
            loading: false,
            error: error instanceof Error ? error.message : 'An unknown error occurred'
        }));
    }
}

export async function getSummary(surah: number, verse: number) {
    try {
        // Update search state to loading
        searchState.update(state => ({
            ...state,
            loading: true,
            error: null
        }));

        // Prepare request body
        const requestBody = {
            surah,
            verse,
            length: settings.get().summary_length,
            focus: settings.get().summary_focus,
            model: settings.get().model,
            api_key: settings.get().api_key
        };

        // Make API request
        const response = await fetch(`${API_BASE_URL}/summarize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`Summary failed: ${response.statusText}`);
        }

        const data = await response.json();

        // Update search state with summary
        searchState.update(state => ({
            ...state,
            loading: false,
            summary: data.summary
        }));
    } catch (error) {
        // Update search state with error
        searchState.update(state => ({
            ...state,
            loading: false,
            error: error instanceof Error ? error.message : 'An unknown error occurred'
        }));
    }
} 