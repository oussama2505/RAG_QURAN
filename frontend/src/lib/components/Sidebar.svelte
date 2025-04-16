<script lang="ts">
  import { appStore } from '../stores/appStore';
  import { languageStore } from '../stores/languageStore';
  import { onMount } from 'svelte';
  import { slide } from 'svelte/transition';
  import { api } from '../services/api';
  import SampleQuestions from './SampleQuestions.svelte';
  import SurahFilter from './SurahFilter.svelte';
  import Settings from './Settings.svelte';
  
  let apiKey = '';
  let saveKey = false;
  let showSettings = false;

  onMount(async () => {
    const status = await api.checkHealth();
    appStore.setApiStatus(status);
  });

  async function handleApiKeySubmit() {
    if (!apiKey.trim()) return;
    
    try {
      appStore.setApiKey(apiKey);
      appStore.setError(null);
      
      if (saveKey) {
        // Storage is now handled by the store
        appStore.setApiKey(apiKey);
      }
    } catch (error) {
      appStore.setError('Failed to save API key');
    }
  }

  function handleSampleQuestionSelect(event: CustomEvent) {
    const { question } = event.detail;
    appStore.setQuestion(question);
  }

  function handleSurahFilter(event: CustomEvent) {
    const { surah } = event.detail;
    appStore.setSurahFilter(surah);
  }

  function toggleSettings() {
    showSettings = !showSettings;
  }
  
  // Translation getters
  $: apiKeySetup = $languageStore === 'en' 
    ? 'API Key Setup' 
    : $languageStore === 'ar' 
    ? 'إعداد مفتاح API' 
    : 'Configuración de clave API';
    
  $: apiKeyLabel = $languageStore === 'en' 
    ? 'OpenAI API Key' 
    : $languageStore === 'ar' 
    ? 'مفتاح API لـ OpenAI' 
    : 'Clave API de OpenAI';
    
  $: apiKeyPlaceholder = $languageStore === 'en' 
    ? 'Enter your API key' 
    : $languageStore === 'ar' 
    ? 'أدخل مفتاح API الخاص بك' 
    : 'Ingrese su clave API';
    
  $: saveForFuture = $languageStore === 'en' 
    ? 'Save for future sessions' 
    : $languageStore === 'ar' 
    ? 'حفظ للجلسات المستقبلية' 
    : 'Guardar para sesiones futuras';
    
  $: saveApiKey = $languageStore === 'en' 
    ? 'Save API Key' 
    : $languageStore === 'ar' 
    ? 'حفظ مفتاح API' 
    : 'Guardar clave API';
    
  $: systemStatus = $languageStore === 'en' 
    ? 'System Status' 
    : $languageStore === 'ar' 
    ? 'حالة النظام' 
    : 'Estado del Sistema';
    
  $: systemOnline = $languageStore === 'en' 
    ? 'System Online' 
    : $languageStore === 'ar' 
    ? 'النظام متصل' 
    : 'Sistema en Línea';
    
  $: systemOffline = $languageStore === 'en' 
    ? 'System Offline' 
    : $languageStore === 'ar' 
    ? 'النظام غير متصل' 
    : 'Sistema Fuera de Línea';
    
  $: aboutTitle = $languageStore === 'en' 
    ? 'About' 
    : $languageStore === 'ar' 
    ? 'حول' 
    : 'Acerca de';
    
  $: aboutText = $languageStore === 'en' 
    ? 'This application uses advanced AI technology to help you explore and understand the Holy Quran through authentic sources including Quranic verses and trusted tafsir (interpretations).' 
    : $languageStore === 'ar' 
    ? 'يستخدم هذا التطبيق تقنية الذكاء الاصطناعي المتقدمة لمساعدتك على استكشاف وفهم القرآن الكريم من خلال مصادر موثوقة بما في ذلك آيات القرآن والتفاسير الموثوقة.' 
    : 'Esta aplicación utiliza tecnología avanzada de IA para ayudarlo a explorar y comprender el Sagrado Corán a través de fuentes auténticas que incluyen versículos coránicos e interpretaciones confiables (tafsir).';
</script>

<aside class="bg-accent/20 dark:bg-base-200 rounded-lg p-6 shadow-lg space-y-8" class:rtl={$languageStore === 'ar'}>
  <!-- Settings Toggle Button -->
  <div class="flex justify-end">
    <button
      class="btn btn-circle btn-ghost btn-sm"
      on:click={toggleSettings}
      aria-label={showSettings ? 'Close Settings' : 'Open Settings'}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        class="w-5 h-5 stroke-current"
        class:rotate-90={showSettings}
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
        />
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
        />
      </svg>
    </button>
  </div>

  <!-- Settings Panel -->
  {#if showSettings}
    <Settings visible={true} />
  {/if}

  <!-- API Key Section -->
  {#if !$appStore.apiKey}
    <div class="space-y-4">
      <h3 class="text-xl font-bold text-neutral dark:text-neutral-content" class:arabic={$languageStore === 'ar'}>
        {apiKeySetup}
      </h3>
      <form on:submit|preventDefault={handleApiKeySubmit} class="space-y-4">
        <div class="form-control">
          <label class="label" for="apiKey">
            <span class="label-text text-neutral dark:text-neutral-content" class:arabic={$languageStore === 'ar'}>
              {apiKeyLabel}
            </span>
          </label>
          <input
            type="password"
            id="apiKey"
            bind:value={apiKey}
            class="input input-bordered w-full"
            class:arabic={$languageStore === 'ar'}
            placeholder={apiKeyPlaceholder}
            dir={$languageStore === 'ar' ? 'rtl' : 'ltr'}
          />
        </div>
        
        <label class="label cursor-pointer">
          <span class="label-text text-neutral dark:text-neutral-content" class:arabic={$languageStore === 'ar'}>
            {saveForFuture}
          </span>
          <input type="checkbox" bind:checked={saveKey} class="checkbox checkbox-primary" />
        </label>
        
        <button type="submit" class="btn btn-primary w-full">
          <span class:arabic={$languageStore === 'ar'}>
            {saveApiKey}
          </span>
        </button>
      </form>
    </div>
  {/if}

  <!-- System Status -->
  <div class="space-y-4">
    <h3 class="text-xl font-bold text-neutral dark:text-neutral-content" class:arabic={$languageStore === 'ar'}>
      {systemStatus}
    </h3>
    <div class="flex items-center space-x-2 bg-white/50 dark:bg-base-300/50 p-3 rounded-lg">
      <div class="w-3 h-3 rounded-full {$appStore.apiStatus ? 'bg-success' : 'bg-error'}"></div>
      <span class="text-neutral dark:text-neutral-content" class:arabic={$languageStore === 'ar'}>
        {$appStore.apiStatus ? systemOnline : systemOffline}
      </span>
    </div>
  </div>

  <!-- Surah Filter -->
  <SurahFilter on:filter={handleSurahFilter} />

  <!-- Sample Questions -->
  <SampleQuestions on:select={handleSampleQuestionSelect} />

  <!-- About Section -->
  <div class="space-y-4">
    <h3 class="text-xl font-bold text-neutral dark:text-neutral-content" class:arabic={$languageStore === 'ar'}>
      {aboutTitle}
    </h3>
    <div class="prose prose-sm dark:prose-invert">
      <p class="text-neutral-700 dark:text-neutral-200" class:arabic={$languageStore === 'ar'}>
        {aboutText}
      </p>
    </div>
  </div>
</aside>

<style>
  svg {
    transition: transform 0.2s ease-in-out;
  }
  
  .rotate-90 {
    transform: rotate(90deg);
  }
  
  .rtl {
    direction: rtl;
    text-align: right;
  }
</style>