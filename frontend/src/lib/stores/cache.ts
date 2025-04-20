import { writable } from 'svelte/store';

export interface CachedResult {
    query: string;
    filters: {
        surah?: number;
        verse?: number;
    };
    results: any[];
    timestamp: number;
}

export interface CacheState {
    results: CachedResult[];
    maxSize: number;
    ttl: number; // Time to live in milliseconds
}

const defaultState: CacheState = {
    results: [],
    maxSize: 100, // Maximum number of cached results
    ttl: 24 * 60 * 60 * 1000 // 24 hours in milliseconds
};

export const cacheStore = writable<CacheState>(defaultState);

export function addToCache(result: CachedResult) {
    cacheStore.update(state => {
        // Remove expired results
        const now = Date.now();
        const validResults = state.results.filter(r => now - r.timestamp < state.ttl);

        // Add new result
        validResults.unshift(result);

        // Trim to max size
        if (validResults.length > state.maxSize) {
            validResults.length = state.maxSize;
        }

        return {
            ...state,
            results: validResults
        };
    });
}

export function getFromCache(query: string, filters: { surah?: number; verse?: number } = {}): CachedResult | null {
    let cachedResult: CachedResult | null = null;
    
    cacheStore.subscribe(state => {
        const now = Date.now();
        cachedResult = state.results.find(r => 
            r.query === query && 
            JSON.stringify(r.filters) === JSON.stringify(filters) &&
            now - r.timestamp < state.ttl
        ) || null;
    })();

    return cachedResult;
}

export function clearCache() {
    cacheStore.update(state => ({
        ...state,
        results: []
    }));
} 