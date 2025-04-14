const STORAGE_KEYS = {
  API_KEY: 'rag-quran-api-key',
  RECENT_QUESTIONS: 'rag-quran-recent-questions',
} as const;

export function saveApiKey(apiKey: string): void {
  localStorage.setItem(STORAGE_KEYS.API_KEY, apiKey);
}

export function getApiKey(): string {
  return localStorage.getItem(STORAGE_KEYS.API_KEY) || '';
}

export function saveRecentQuestions(questions: string[]): void {
  localStorage.setItem(STORAGE_KEYS.RECENT_QUESTIONS, JSON.stringify(questions));
}

export function getRecentQuestions(): string[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.RECENT_QUESTIONS);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

export function clearStorage(): void {
  Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
}