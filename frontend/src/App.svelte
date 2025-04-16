<script lang="ts">
  import { onMount } from 'svelte';
  import { appStore, type Source } from './lib/stores/appStore';
  import { api } from './lib/services/api';
  
  // Import all components
  import Header from './lib/components/Header.svelte';
  import Sidebar from './lib/components/Sidebar.svelte';
  import QuestionInput from './lib/components/QuestionInput.svelte';
  import ResponseDisplay from './lib/components/ResponseDisplay.svelte';
  import RecentQuestions from './lib/components/RecentQuestions.svelte';
  import StatusIndicator from './lib/components/StatusIndicator.svelte';
  import SurahFilter from './lib/components/SurahFilter.svelte';
  import LoadingSpinner from './lib/components/LoadingSpinner.svelte';
  import ErrorBoundary from './lib/components/ErrorBoundary.svelte';
  import KeyboardShortcuts from './lib/components/KeyboardShortcuts.svelte';
  import Toast from './lib/components/Toast.svelte';
  
  // State management
  let isLoading = false;
  let status: 'idle' | 'loading' | 'success' | 'error' = 'idle';
  let statusMessage = '';
  let question = '';
  
  // Source type is imported from appStore

  // Define response type based on your API response structure
  interface QuranResponse {
    answer?: string;
    verses?: any[];
    sources?: Source[];
    filters_applied: {
      surah_filter?: number;
      verse_filter?: number;
    };
    // Add other fields that match your actual API response
  }
  
  let response: QuranResponse | null = null;
  let showKeyboardShortcuts = false;
  let showSurahFilter = false;
  let selectedSurah: number | null = null;
  type ToastType = 'info' | 'warning' | 'error';
  let toast = { show: false, message: '', type: 'info' as ToastType };
  
  const quranQuote = {
    text: "Indeed, We have sent it down as an Arabic Qur'an that you might understand.",
    author: "Quran 12:2"
  };
  
  onMount(() => {
    // Initialize any data if needed
    const storedQuestion = $appStore.question;
    if (storedQuestion) {
      question = storedQuestion;
    }

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || savedTheme === 'light') {
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    }
  });
  
  // Handle question submission
  async function handleQuestionSubmit(event: CustomEvent) {
    const submittedQuestion = event.detail;
    
    if (!$appStore.apiKey) {
      toast = { 
        show: true, 
        message: 'Please set your API key first', 
        type: 'warning' 
      };
      return;
    }
    
    try {
      isLoading = true;
      status = 'loading';
      statusMessage = 'Searching for relevant Quranic knowledge...';
      
      // Make API call with filters if set
      const params: any = {};
      if (selectedSurah) {
        params.surah_filter = selectedSurah;
      }
      
      response = await api.queryQuran(submittedQuestion, selectedSurah === null ? undefined : selectedSurah);
      
      status = 'success';
      statusMessage = 'Answer generated successfully';
    } catch (error) {
      status = 'error';
      statusMessage = error instanceof Error ? error.message : 'Failed to get answer';
      
      toast = {
        show: true,
        message: statusMessage,
        type: 'error'
      };
    } finally {
      isLoading = false;
    }
  }
  
  function handleSurahChange(event: CustomEvent) {
    selectedSurah = event.detail;
  }
  
  function handleQuestionSelect(selectedQuestion: string) {
    question = selectedQuestion;
    // You might want to auto-submit the question here
  }
  
  function closeToast() {
    toast.show = false;
  }
</script>

<ErrorBoundary>
  <div class="app min-h-screen bg-base-100">
    <Header quote={quranQuote} />
    
    <div class="container mx-auto px-4 py-8">
      <div class="flex flex-col lg:flex-row gap-8">
        <!-- Sidebar with settings, filters, etc. -->
        <aside class="w-full lg:w-1/4">
          <Sidebar />
        </aside>
        
        <!-- Main content area -->
        <main class="w-full lg:w-3/4 space-y-8">
          <!-- Question input and status -->
          <div class="space-y-4">
            <QuestionInput 
              initialQuestion={question}
              isLoading={isLoading}
              on:submit={handleQuestionSubmit}
            />
            
            <StatusIndicator 
              status={status}
              message={statusMessage}
            />
            
            <!-- Surah filter -->
            <div class="flex justify-between items-center">
              <button 
                class="btn btn-sm btn-ghost"
                on:click={() => showSurahFilter = !showSurahFilter}
              >
                {showSurahFilter ? 'Hide Filters' : 'Show Filters'}
              </button>
              
              <!-- Keyboard shortcuts toggle -->
              <button 
                class="btn btn-sm btn-ghost"
                on:click={() => showKeyboardShortcuts = !showKeyboardShortcuts}
              >
                Keyboard Shortcuts
              </button>
            </div>
            
            <SurahFilter 
              showFilter={showSurahFilter}
              selectedSurah={selectedSurah}
              on:change={handleSurahChange}
            />
          </div>
          
          <!-- Loading indicator or Response -->
          {#if isLoading}
            <div class="flex justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          {:else if response && response.answer && response.sources}
            <ResponseDisplay response={{
              answer: response.answer,
              sources: response.sources,
              filters_applied: response.filters_applied
            }} />
          {/if}
          
          <!-- Recent Questions -->
          <RecentQuestions onQuestionSelect={handleQuestionSelect} />
        </main>
      </div>
    </div>
    
    <!-- Keyboard shortcuts panel -->
    <KeyboardShortcuts visible={showKeyboardShortcuts} />
    
    <!-- Toast notifications -->
    {#if toast.show}
      <Toast 
        message={toast.message}
        type={toast.type}
        onClose={closeToast}
        duration={5000}
      />
    {/if}
  </div>
</ErrorBoundary>

<style>
  /* Add global styles here */
  :global(.arabic) {
    font-family: 'Traditional Arabic', 'Scheherazade New', serif;
  }
</style>
