<script lang="ts">
  import { slide } from 'svelte/transition';
  
  export let quote: { text: string; author: string; } | null = null;
</script>

<header class="text-center py-8 bg-gradient-to-b from-accent/20 to-transparent">
  <h1 class="arabic text-4xl md:text-5xl font-bold text-primary mb-4" 
      transition:slide={{ duration: 1000 }}>
    بِسْمِ ٱللَّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
  </h1>
  
  <h2 class="text-2xl md:text-3xl font-bold text-neutral mb-2">
    Quran Knowledge Explorer
  </h2>
  
  <p class="text-lg text-neutral-600 max-w-2xl mx-auto">
    Explore the wisdom of the Holy Quran through AI-assisted research
  </p>

  {#if quote}
    <div class="mt-8 max-w-2xl mx-auto bg-white/50 backdrop-blur-sm p-6 rounded-lg shadow-sm"
         transition:slide={{ duration: 800 }}>
      <p class="text-lg text-neutral-700 italic">"{quote.text}"</p>
      <p class="text-sm text-neutral-600 mt-2">— {quote.author}</p>
    </div>
  {/if}
</header>