<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  
  export let message: string;
  export let type: 'info' | 'success' | 'error' | 'warning' = 'info';
  export let duration = 3000; // Duration in milliseconds
  export let onClose: () => void;
  
  let timer: ReturnType<typeof setTimeout>;
  
  // Set up auto-dismiss timer
  $: {
    if (message) {
      clearTimeout(timer);
      timer = setTimeout(() => {
        onClose();
      }, duration);
    }
  }
  
  // Clean up timer on component destruction
  import { onDestroy } from 'svelte';
  onDestroy(() => {
    clearTimeout(timer);
  });
  
  // Get appropriate icon based on type
  function getIcon(type: string) {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
      default:
        return 'ℹ️';
    }
  }
  
  // Get appropriate color class based on type
  function getColorClass(type: string) {
    switch (type) {
      case 'success':
        return 'bg-success text-success-content';
      case 'error':
        return 'bg-error text-error-content';
      case 'warning':
        return 'bg-warning text-warning-content';
      case 'info':
      default:
        return 'bg-info text-info-content';
    }
  }
</script>

<div 
  class="toast-container"
  in:fly={{ y: 50, duration: 300 }}
  out:fade={{ duration: 200 }}
>
  <div class="toast-content {getColorClass(type)}">
    <span class="toast-icon">{getIcon(type)}</span>
    <span class="toast-message">{message}</span>
    <button 
      class="toast-close"
      on:click={onClose}
      aria-label="Close notification"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
      </svg>
    </button>
  </div>
</div>

<style>
  .toast-container {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    z-index: 50;
    max-width: 24rem;
  }
  
  .toast-content {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }
  
  .toast-icon {
    margin-right: 0.75rem;
  }
  
  .toast-message {
    flex: 1;
    font-size: 0.875rem;
  }
  
  .toast-close {
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    margin-left: 0.75rem;
    opacity: 0.7;
    transition: opacity 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .toast-close:hover {
    opacity: 1;
  }
</style>