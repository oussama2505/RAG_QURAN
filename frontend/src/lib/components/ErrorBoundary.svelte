<script lang="ts">
  import { onError } from 'svelte';
  import { slide } from 'svelte/transition';
  
  let error: Error | null = null;
  
  onError((e) => {
    error = e.error;
    console.error('Caught error:', e.error);
  });
</script>

{#if error}
  <div 
    class="alert alert-error shadow-lg mb-4"
    transition:slide
    role="alert"
  >
    <div class="flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div class="ml-2">
        <h3 class="font-bold">Error</h3>
        <p class="text-sm">{error.message}</p>
      </div>
      <button 
        class="btn btn-ghost btn-sm ml-auto"
        on:click={() => error = null}
      >
        Dismiss
      </button>
    </div>
  </div>
{/if}

<slot />

<style>
  .alert {
    background-color: theme('colors.error.100');
    color: theme('colors.error.800');
    border: 1px solid theme('colors.error.200');
  }
</style>