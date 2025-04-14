<script lang="ts">
  import { onDestroy } from 'svelte';
  import Toast from './Toast.svelte';

  export let text: string;
  export let label = 'Copy to clipboard';
  export let size: 'sm' | 'md' | 'lg' = 'md';
  
  let copied = false;
  let timeout: ReturnType<typeof setTimeout>;
  let toast = { show: false, message: '', type: 'info' as const };
  
  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(text);
      copied = true;
      
      // Show toast
      toast = {
        show: true,
        message: 'Copied to clipboard',
        type: 'success'
      };
      
      // Reset copied state after 2 seconds
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        copied = false;
      }, 2000);
    } catch (error) {
      console.error('Failed to copy text:', error);
      toast = {
        show: true,
        message: 'Failed to copy to clipboard',
        type: 'error'
      };
    }
  }
  
  function closeToast() {
    toast.show = false;
  }
  
  // Clean up timeout on component destruction
  onDestroy(() => {
    clearTimeout(timeout);
  });
  
  // Determine button size classes
  $: sizeClass = {
    sm: 'btn-xs',
    md: 'btn-sm',
    lg: 'btn-md'
  }[size];
</script>

<div class="inline-block">
  <button
    class="btn btn-ghost {sizeClass} gap-2 text-neutral hover:text-primary"
    on:click={copyToClipboard}
    aria-label={label}
    title={label}
  >
    {#if copied}
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
      </svg>
    {:else}
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
      </svg>
    {/if}
    Copy
  </button>

  {#if toast.show}
    <Toast 
      message={toast.message}
      type={toast.type}
      onClose={closeToast}
    />
  {/if}
</div>

<style>
  button {
    transition: all 0.2s ease;
  }
  
  button:hover {
    transform: translateY(-1px);
  }
</style>