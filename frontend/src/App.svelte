<script lang="ts">
  import { onMount } from 'svelte';
  import { appStore } from './lib/stores/appStore';
  import { api } from './lib/services/api';
  import QuestionInput from './lib/components/QuestionInput.svelte';
  import ResponseDisplay from './lib/components/ResponseDisplay.svelte';
  import RecentQuestions from './lib/components/RecentQuestions.svelte';
  import SurahFilter from './lib/components/SurahFilter.svelte';
  import StatusIndicator from './lib/components/StatusIndicator.svelte';
  import APIKeyManager from './lib/components/APIKeyManager.svelte';
  
  let isLoading = false;
  let currentQuestion = '';
  let currentResponse = null;
  let showApiKeyManager = false;
  let showFilters = false;
  let error = null;
  let apiAvailable = true;
  
  // Check API availability on mount
  onMount(async () => {
    try {
      apiAvailable = await api.checkHealth();
    } catch (e) {
      apiAvailable = false;
      console.error('API health check failed:', e);
    }
  });
  
  async function handleQuestionSubmit(event) {
    const question = event.detail;
    currentQuestion = question;
    isLoading = true;
    error = null;
    
    try {
      // Call the API service
      const response = await api.queryQuran(
        question, 
        $appStore.selectedSurah
      );
      
      currentResponse = response;
      
      // Add to recent questions
      appStore.addRecentQuestion(question);
    } catch (err) {
      error = err.message || 'An error occurred';
      console.error('Error querying:', err);
    } finally {
      isLoading = false;
    }
  }
  
  function handleQuestionSelect(question) {
    currentQuestion = question;
  }
  
  function toggleApiKeyManager() {
    showApiKeyManager = !showApiKeyManager;
  }
  
  function toggleFilters() {
    showFilters = !showFilters;
  }
  
  function handleApiKeySave(event) {
    const apiKey = event.detail;
    appStore.setApiKey(apiKey);
    showApiKeyManager = false;
  }
</script>

<main class="container mx-auto px-4 py-8 max-w-4xl">
  <header class="mb-8 text-center">
    <h1 class="text-3xl font-bold mb-2">Quran RAG Explorer</h1>
    <p class="text-lg text-neutral-600">Ask questions about the Quran and receive AI-powered answers with sources</p>
    
    {#if !apiAvailable}
      <div class="alert alert-warning mt-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>Backend API is not available. Make sure the backend server is running.</span>
      </div>
    {/if}
  </header>
  
  <div class="flex flex-col md:flex-row gap-6">
    <!-- Sidebar -->
    <aside class="w-full md:w-1/3 space-y-6">
      <div class="card bg-base-100 shadow-lg">
        <div class="card-body">
          <RecentQuestions onQuestionSelect={handleQuestionSelect} />
        </div>
      </div>
      
      <div class="card bg-base-100 shadow-lg">
        <div class="card-body">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold text-neutral">Settings</h3>
          </div>
          
          <div class="space-y-4">
            <button 
              class="btn btn-outline btn-block"
              on:click={toggleApiKeyManager}
            >
              {$appStore.apiKey ? 'Change API Key' : 'Set API Key'}
            </button>
            
            <button 
              class="btn btn-outline btn-block"
              on:click={toggleFilters}
            >
              {showFilters ? 'Hide Filters' : 'Show Filters'}
            </button>
          </div>
        </div>
      </div>
    </aside>
    
    <!-- Main content -->
    <div class="w-full md:w-2/3 space-y-6">
      <SurahFilter 
        selectedSurah={$appStore.selectedSurah} 
        showFilter={showFilters}
      />
      
      <div class="card bg-base-100 shadow-lg">
        <div class="card-body">
          <QuestionInput 
            initialQuestion={currentQuestion}
            isLoading={isLoading}
            on:submit={handleQuestionSubmit}
          />
          
          {#if error}
            <div class="alert alert-error mt-4">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          {/if}
          
          {#if isLoading}
            <div class="flex justify-center items-center py-8">
              <div class="loading loading-spinner loading-lg"></div>
            </div>
          {/if}
        </div>
      </div>
      
      {#if currentResponse}
        <ResponseDisplay response={currentResponse} />
      {/if}
    </div>
  </div>
  
  <APIKeyManager 
    apiKey={$appStore.apiKey}
    isVisible={showApiKeyManager}
    on:save={handleApiKeySave}
    on:cancel={() => showApiKeyManager = false}
  />
</main>

<style>
  :global(body) {
    background-color: #f8f9fa;
  }
</style>
