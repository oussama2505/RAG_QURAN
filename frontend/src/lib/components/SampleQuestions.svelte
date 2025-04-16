<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { slide } from 'svelte/transition';

  const dispatch = createEventDispatcher();

  const questions = [
    "What does the Quran say about seeking knowledge?",
    "How does the Quran describe Paradise?",
    "What is the importance of patience in Islam?",
    "What does the Quran say about kindness to parents?",
    "How does the Quran describe the creation of the universe?"
  ];

  function handleQuestionClick(question: string) {
    dispatch('select', { question });
  }
</script>

<div class="sample-questions bg-white/50 dark:bg-base-200/50 backdrop-blur-sm rounded-lg p-6 shadow-sm" transition:slide>
  <h3 class="text-lg font-semibold text-neutral dark:text-neutral-content mb-4">Sample Questions</h3>
  <div class="space-y-2">
    {#each questions as question}
      <button
        class="w-full text-left p-3 rounded-lg bg-white dark:bg-base-300 text-neutral-700 dark:text-neutral-200 
               hover:bg-primary/5 dark:hover:bg-primary/20 transition-colors
               border border-base-200 dark:border-base-300 hover:border-primary/20"
        on:click={() => handleQuestionClick(question)}
      >
        {question}
      </button>
    {/each}
  </div>
</div>

<style>
  button {
    font-size: 0.95rem;
    line-height: 1.4;
  }
</style>