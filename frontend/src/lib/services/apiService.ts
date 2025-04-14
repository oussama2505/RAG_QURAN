import { appStore } from '../stores/appStore';
import type { QuestionResponse } from '../stores/appStore';

interface QueryParams {
  question: string;
  surah?: number;
}

export async function queryQuran(params: QueryParams): Promise<QuestionResponse> {
  const { question, surah } = params;
  
  try {
    appStore.setLoading(true);
    appStore.setStatus('loading');
    
    const apiKey = getApiKey();
    if (!apiKey) {
      throw new Error('API key is required');
    }
    
    const queryParams = new URLSearchParams();
    queryParams.append('question', question);
    if (surah) {
      queryParams.append('surah', surah.toString());
    }
    
    const response = await fetch(`/api/query?${queryParams.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to query the Quran');
    }
    
    const data = await response.json();
    appStore.setStatus('success');
    
    return {
      answer: data.answer,
      sources: data.sources.map((source: any) => ({
        source_type: source.source_type,
        reference: source.reference,
        content: source.content,
        surah: source.surah,
        ayah: source.ayah,
        verse: source.verse,
        text: source.text
      }))
    };
  } catch (error) {
    appStore.setStatus('error');
    appStore.setError(error instanceof Error ? error.message : 'An unknown error occurred');
    throw error;
  } finally {
    appStore.setLoading(false);
  }
}

function getApiKey(): string {
  let store: any;
  appStore.subscribe(value => {
    store = value;
  })();
  
  return store.apiKey;
}