/**
 * MCP Services - TypeScript modules to communicate with MCP servers
 * 
 * This file contains client implementations for all MCP servers:
 * - Retriever
 * - Generator
 * - Translation
 * - Summarizer
 * - Tafsir
 */

import axios from 'axios';

// MCP Server ports (from backend/mcp_servers/run_servers.py)
const MCP_PORTS = {
  RETRIEVER: 5000,
  GENERATOR: 5001,
  TAFSIR: 5002,
  SUMMARIZER: 5003,
  TRANSLATION: 5004
};

// Base URLs for each MCP server
const BASE_URLS = {
  retriever: `http://localhost:${MCP_PORTS.RETRIEVER}`,
  generator: `http://localhost:${MCP_PORTS.GENERATOR}`,
  tafsir: `http://localhost:${MCP_PORTS.TAFSIR}`,
  summarizer: `http://localhost:${MCP_PORTS.SUMMARIZER}`,
  translation: `http://localhost:${MCP_PORTS.TRANSLATION}`
};

// Create API clients for each MCP server
const createApiClient = (baseURL: string) => {
  return axios.create({
    baseURL,
    headers: {
      'Content-Type': 'application/json'
    }
  });
};

// General interface for MCP server responses
interface MCPResponse<T> {
  result: T;
  error?: string;
}

// Retriever interfaces
export interface RetrieverRequest {
  query: string;
  surah_filter?: number;
  verse_filter?: number;
  end_verse_filter?: number;
  top_k?: number;
}

export interface RetrieverResult {
  verses: Array<{
    surah: number;
    verse: number;
    text: string;
    score: number;
  }>;
  filters_applied: {
    surah_filter?: number;
    verse_filter?: number;
    end_verse_filter?: number;
  };
}

// Generator interfaces
export interface GeneratorRequest {
  query: string;
  context: string;
  model_name?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface GeneratorResult {
  answer: string;
  sources: Array<{
    source_type: string;
    reference: string;
    content: string;
  }>;
  metadata: {
    query: string;
    model: string;
  };
}

// Translation interfaces
export interface TranslationRequest {
  surah: number;
  verse: number;
  end_verse?: number;
  translation_name?: string;
}

export interface TranslationResult {
  arabic_text: string;
  translated_text: string;
  translation_name: string;
  reference: string;
  metadata: {
    surah: number;
    verse: number;
    end_verse?: number;
    translation: string;
  };
}

// Summarizer interfaces
export interface SummarizerRequest {
  content: string;
  max_length?: number;
  focus?: string;
  model_name?: string;
  temperature?: number;
}

export interface SummarizerResult {
  summary: string;
  original_length: number;
  summary_length: number;
  metadata: {
    original_length: number;
    summary_length: number;
    focus?: string;
    model: string;
  };
}

// Tafsir interfaces
export interface TafsirRequest {
  surah: number;
  verse: number;
  tafsir_sources?: string[];
}

export interface TafsirResult {
  tafsir: Array<{
    source: string;
    text: string;
    reference: string;
    metadata?: any;
  }>;
  verse_text: string;
  reference: string;
  metadata: {
    surah: number;
    verse: number;
    sources_queried: string[];
  };
}

/**
 * Generic function to execute a tool on any MCP server
 */
async function executeMcpTool<T, R>(
  baseUrl: string, 
  toolName: string, 
  parameters: T
): Promise<R> {
  const client = createApiClient(baseUrl);
  
  try {
    const response = await client.post('/tools/execute', {
      name: toolName,
      parameters
    });
    
    const result = response.data as MCPResponse<R>;
    
    if (result.error) {
      throw new Error(result.error);
    }
    
    return result.result;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error(`Error executing MCP tool ${toolName}:`, error.message);
      throw new Error(`Failed to execute ${toolName}: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Retriever MCP Client
 */
export const retrieverClient = {
  async retrieveVerses(
    query: string, 
    filters?: { 
      surahFilter?: number, 
      verseFilter?: number,
      endVerseFilter?: number,
      topK?: number
    }
  ): Promise<RetrieverResult> {
    const parameters: RetrieverRequest = {
      query
    };
    
    if (filters?.surahFilter) {
      parameters.surah_filter = filters.surahFilter;
    }
    
    if (filters?.verseFilter) {
      parameters.verse_filter = filters.verseFilter;
    }
    
    if (filters?.endVerseFilter) {
      parameters.end_verse_filter = filters.endVerseFilter;
    }
    
    if (filters?.topK) {
      parameters.top_k = filters.topK;
    }
    
    return executeMcpTool<RetrieverRequest, RetrieverResult>(
      BASE_URLS.retriever,
      'retrieve_verses',
      parameters
    );
  },
  
  async listSurahs(): Promise<{ surahs: Array<{ number: number, name: string, verses_count: number }> }> {
    return executeMcpTool(
      BASE_URLS.retriever,
      'list_surahs',
      {}
    );
  }
};

/**
 * Generator MCP Client
 */
export const generatorClient = {
  async generateAnswer(
    query: string, 
    context: string, 
    options?: {
      model?: string,
      temperature?: number,
      maxTokens?: number
    }
  ): Promise<GeneratorResult> {
    const parameters: GeneratorRequest = {
      query,
      context
    };
    
    if (options?.model) {
      parameters.model_name = options.model;
    }
    
    if (options?.temperature !== undefined) {
      parameters.temperature = options.temperature;
    }
    
    if (options?.maxTokens) {
      parameters.max_tokens = options.maxTokens;
    }
    
    return executeMcpTool<GeneratorRequest, GeneratorResult>(
      BASE_URLS.generator,
      'generate_answer',
      parameters
    );
  },
  
  async listModels(): Promise<{ models: Array<{ id: string, name: string, provider: string, description: string }> }> {
    return executeMcpTool(
      BASE_URLS.generator,
      'list_models',
      {}
    );
  }
};

/**
 * Translation MCP Client
 */
export const translationClient = {
  async translateVerse(
    surah: number, 
    verse: number, 
    options?: {
      endVerse?: number,
      translationName?: string
    }
  ): Promise<TranslationResult> {
    const parameters: TranslationRequest = {
      surah,
      verse
    };
    
    if (options?.endVerse) {
      parameters.end_verse = options.endVerse;
    }
    
    if (options?.translationName) {
      parameters.translation_name = options.translationName;
    }
    
    return executeMcpTool<TranslationRequest, TranslationResult>(
      BASE_URLS.translation,
      'translate_verse',
      parameters
    );
  },
  
  async listTranslations(): Promise<{ translations: Array<{ id: string, name: string }> }> {
    return executeMcpTool(
      BASE_URLS.translation,
      'list_translations',
      {}
    );
  }
};

/**
 * Summarizer MCP Client
 */
export const summarizerClient = {
  async summarizeContent(
    content: string, 
    options?: { 
      maxLength?: number, 
      focus?: string,
      modelName?: string,
      temperature?: number
    }
  ): Promise<SummarizerResult> {
    const parameters: SummarizerRequest = {
      content
    };
    
    if (options?.maxLength) {
      parameters.max_length = options.maxLength;
    }
    
    if (options?.focus) {
      parameters.focus = options.focus;
    }
    
    if (options?.modelName) {
      parameters.model_name = options.modelName;
    }
    
    if (options?.temperature !== undefined) {
      parameters.temperature = options.temperature;
    }
    
    return executeMcpTool<SummarizerRequest, SummarizerResult>(
      BASE_URLS.summarizer,
      'summarize_content',
      parameters
    );
  },
  
  async listModels(): Promise<{ models: Array<{ id: string, name: string, provider: string, description: string }> }> {
    return executeMcpTool(
      BASE_URLS.summarizer,
      'list_models',
      {}
    );
  }
};

/**
 * Tafsir MCP Client
 */
export const tafsirClient = {
  async getTafsir(
    surah: number, 
    verse: number, 
    options?: {
      tafsirSources?: string[]
    }
  ): Promise<TafsirResult> {
    const parameters: TafsirRequest = {
      surah,
      verse
    };
    
    if (options?.tafsirSources) {
      parameters.tafsir_sources = options.tafsirSources;
    }
    
    return executeMcpTool<TafsirRequest, TafsirResult>(
      BASE_URLS.tafsir,
      'get_tafsir',
      parameters
    );
  },
  
  async listTafsirSources(): Promise<{ sources: Array<{ id: string, name: string, language: string }> }> {
    return executeMcpTool(
      BASE_URLS.tafsir,
      'list_tafsir_sources',
      {}
    );
  }
};

// Export a combined service for easier imports
export const mcpServices = {
  retriever: retrieverClient,
  generator: generatorClient,
  translation: translationClient,
  summarizer: summarizerClient,
  tafsir: tafsirClient
};