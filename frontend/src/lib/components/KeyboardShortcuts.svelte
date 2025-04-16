<script lang="ts">
  import { getRegisteredShortcuts } from '../services/shortcuts';
  import { slide } from 'svelte/transition';
  
  const shortcuts = getRegisteredShortcuts();
  export let visible = false;
</script>

{#if visible}
  <div 
    class="keyboard-shortcuts fixed bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-4 z-50"
    transition:slide
  >
    <div class="flex justify-between items-center mb-2">
      <h3 class="text-sm font-semibold text-neutral">Keyboard Shortcuts</h3>
      <button 
        class="btn btn-ghost btn-xs"
        on:click={() => visible = false}
      >
        ✕
      </button>
    </div>
    <div class="space-y-2">
      {#each shortcuts as shortcut}
        <div class="flex items-center justify-between text-sm">
          <span class="text-neutral-600">{shortcut.description}</span>
          <kbd class="kbd kbd-sm">{shortcut.key}</kbd>
        </div>
      {/each}
    </div>
  </div>
{/if}