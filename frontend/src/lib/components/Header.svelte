<script lang="ts">
  import { slide } from 'svelte/transition';
  import ThemeToggle from './ThemeToggle.svelte';
  import { languageStore } from '../stores/languageStore';
  
  export let quote: { text: string; author: string; } | null = null;
</script>

<header class="text-center py-8 bg-gradient-to-b from-accent/20 to-transparent">
  <div class="container mx-auto px-4">
    <div class="flex justify-between items-center mb-4">
      <div class="w-10"></div> <!-- Spacer para mantener el ThemeToggle a la derecha -->
      <div class="flex-1 text-center">
        <h1 class="arabic text-4xl md:text-5xl font-bold text-primary" 
            transition:slide={{ duration: 1000 }}>
          بِسْمِ ٱللَّٰهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
        </h1>
      </div>
      <ThemeToggle />
    </div>
    
    <div class="text-center">
      <h2 class="text-2xl md:text-3xl font-bold text-neutral mb-2" class:arabic={$languageStore === 'ar'}>
        {#if $languageStore === 'en'}
          Quran Knowledge Explorer
        {:else if $languageStore === 'ar'}
          مستكشف معرفة القرآن
        {:else}
          Explorador de Conocimiento del Corán
        {/if}
      </h2>
      
      <p class="text-lg text-neutral-600 dark:text-neutral-300 max-w-2xl mx-auto" class:arabic={$languageStore === 'ar'}>
        {#if $languageStore === 'en'}
          Explore the wisdom of the Holy Quran through AI-assisted research
        {:else if $languageStore === 'ar'}
          استكشف حكمة القرآن الكريم من خلال البحث بمساعدة الذكاء الاصطناعي
        {:else}
          Explore la sabiduría del Sagrado Corán a través de la investigación asistida por IA
        {/if}
      </p>
    </div>
  </div>

  {#if quote}
    <div class="mt-8 max-w-2xl mx-auto bg-white/50 dark:bg-base-200/50 backdrop-blur-sm p-6 rounded-lg shadow-sm"
         transition:slide={{ duration: 800 }}>
      <p class="text-lg text-neutral-700 dark:text-neutral-200 italic" class:arabic={$languageStore === 'ar'}>"{quote.text}"</p>
      <p class="text-sm text-neutral-600 dark:text-neutral-400 mt-2" class:arabic={$languageStore === 'ar'}>— {quote.author}</p>
    </div>
  {/if}
</header>