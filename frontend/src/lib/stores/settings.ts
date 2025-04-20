import { writable } from 'svelte/store';

export interface Settings {
  apiKey: string;
  model: string;
  translation: string;
  summarization: string;
  focusTopic: string;
}

const defaultSettings: Settings = {
  apiKey: '',
  model: 'gpt-3.5-turbo',
  translation: 'en-sahih',
  summarization: 'medium',
  focusTopic: ''
};

export const settings = writable<Settings>(defaultSettings); 