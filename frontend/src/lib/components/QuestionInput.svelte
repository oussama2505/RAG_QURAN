<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';
  import { appStore } from '../stores/appStore';
  import { languageStore } from '../stores/languageStore';
  
  export let initialQuestion = '';
  export let isLoading = false;
  
  let question = initialQuestion;
  const dispatch = createEventDispatcher();
  
  // Subscribe to question changes in the store
  onMount(() => {
    const unsubscribe = appStore.subscribe(state => {
      if (state.question !== question) {
        question = state.question;
      }
    });
    
    return unsubscribe;
  });
  
  function handleSubmit() {
    if (!question.trim()) return;
    
    dispatch('submit', question);
    
    // Add to recent questions if not already there
    if (!$appStore.recentQuestions.includes(question)) {
      appStore.addRecentQuestion(question);
    }
  }
  
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey && !isLoading) {
      event.preventDefault();
      handleSubmit();
    }
  }
  
  // Get placeholder text based on language
  $: placeholder = $languageStore === 'en' 
    ? 'Enter your question about the Quran...'
    : $languageStore === 'ar' 
    ? 'أدخل سؤالك حول القرآن الكريم...'
    : 'Ingrese su pregunta sobre el Corán...';
  
  // Get label text based on language
  $: labelText = $languageStore === 'en' 
    ? 'Ask about the Quran'
    : $languageStore === 'ar' 
    ? 'اسأل عن القرآن'
    : 'Pregunte sobre el Corán';
</script>

<div class="question-input-container" class:rtl={$languageStore === 'ar'}>
  <form on:submit|preventDefault={handleSubmit} class="flex flex-col space-y-4">
    <div class="form-control">
      <label for="question" class="label">
        <span class="label-text text-lg font-medium" class:arabic={$languageStore === 'ar'}>
          {labelText}
        </span>
      </label>
      <div class="relative">
        <textarea
          id="question"
          bind:value={question}
          on:keydown={handleKeydown}
          placeholder={placeholder}
          class="textarea textarea-bordered w-full h-24 resize-none"
          class:arabic={$languageStore === 'ar'} 
          class:pr-12={$languageStore !== 'ar'} 
          class:pl-12={$languageStore === 'ar'}
          disabled={isLoading}
          dir={$languageStore === 'ar' ? 'rtl' : 'ltr'}
        ></textarea>
        <button
          type="submit"
          class="btn btn-primary absolute bottom-2"
          class:right-2={$languageStore !== 'ar'}
          class:left-2={$languageStore === 'ar'}
          disabled={!question.trim() || isLoading}
        >
          {#if isLoading}
            <span class="loading loading-spinner loading-sm"></span>
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          {/if}
        </button>
      </div>
    </div>
  </form>
</div>

<style>
  .question-input-container {
    width: 100%;
  }
  
  .rtl {
    direction: rtl;
    text-align: right;
  }
  
  :global(.arabic) {
    font-family: 'Traditional Arabic', 'Scheherazade New', serif;
  }
</style>