<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { fade } from 'svelte/transition';
  
  export let apiKey: string | null = null;
  export let isVisible = false;
  
  const dispatch = createEventDispatcher();
  
  let inputValue = '';
  let error = '';
  
  // Initialize input value when component is mounted or apiKey changes
  $: {
    // Safely handle null or undefined apiKey
    inputValue = apiKey || '';
  }
  
  function handleSave() {
    // Validate the API key
    if (!inputValue || inputValue.trim() === '') {
      error = 'API key cannot be empty';
      return;
    }
    
    // Dispatch save event with the trimmed API key
    dispatch('save', inputValue.trim());
    error = '';
  }
  
  function handleCancel() {
    // Reset input to current API key and close
    inputValue = apiKey || '';
    error = '';
    dispatch('cancel');
  }
</script>

{#if isVisible}
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    transition:fade={{ duration: 200 }}
  >
    <div class="bg-base-100 rounded-lg shadow-xl p-6 w-full max-w-md">
      <h2 class="text-xl font-bold mb-4">OpenAI API Key</h2>
      
      <p class="mb-4 text-sm">
        Enter your OpenAI API key to use the RAG system. Your key is stored locally in your browser and never sent to our servers.
      </p>
      
      <div class="form-control w-full">
        <label class="label" for="api-key-input">
          <span class="label-text">API Key</span>
        </label>
        <input 
          id="api-key-input"
          type="password" 
          bind:value={inputValue}
          placeholder="sk-..." 
          class="input input-bordered w-full" 
        />
        {#if error}
          <label class="label">
            <span class="label-text-alt text-error">{error}</span>
          </label>
        {/if}
      </div>
      
      <div class="flex justify-end gap-2 mt-6">
        <button class="btn btn-ghost" on:click={handleCancel}>
          Cancel
        </button>
        <button class="btn btn-primary" on:click={handleSave}>
          Save
        </button>
      </div>
    </div>
  </div>
{/if}