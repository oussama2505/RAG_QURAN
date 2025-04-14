<script lang="ts">
  import { fade, slide } from 'svelte/transition';
  import { appStore } from '../stores/appStore';

  export let onQuestionSelect: (question: string) => void;

  function handleQuestionClick(question: string) {
    onQuestionSelect(question);
  }
</script>

<div class="recent-questions space-y-4" transition:slide>
  <h3 class="text-lg font-semibold text-neutral">Recent Questions</h3>
  
  {#if $appStore.recentQuestions.length === 0}
    <p class="text-sm text-neutral-500 italic">
      No recent questions yet
    </p>
  {:else}
    <ul class="space-y-2">
      {#each $appStore.recentQuestions as question (question)}
        <li 
          transition:fade
          class="question-item"
        >
          <button
            class="btn btn-ghost btn-block justify-start text-left normal-case hover:bg-base-200 p-2 rounded-lg"
            on:click={() => handleQuestionClick(question)}
          >
            <span class="truncate">{question}</span>
          </button>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  .question-item {
    max-width: 100%;
  }

  .question-item button {
    width: 100%;
    text-overflow: ellipsis;
    overflow: hidden;
  }
</style>