<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { appStore, type Source } from "../stores/appStore";
  import CopyButton from "./CopyButton.svelte";

  // Props
  export let answer: string = "";
  export let sources: Source[] = [];
  export let isLoading: boolean = false;
  export let filtersApplied: { surah_filter?: number; verse_filter?: number } =
    {};

  const dispatch = createEventDispatcher();

  // Function to format references
  function formatReference(reference: string): string {
    // Handle different reference formats (Surah:Verse, etc.)
    if (reference.includes(":")) {
      const [surah, verse] = reference.split(":");
      return `Surah ${surah}, Verse ${verse}`;
    }
    return reference;
  }

  // Function to handle source click for more details
  function handleSourceClick(source: Source) {
    dispatch("sourceSelect", { source });
  }
</script>

<div class="search-results-container">
  {#if isLoading}
    <div class="loading-container">
      <div class="loading-spinner"></div>
      <p>Searching through Quranic knowledge...</p>
    </div>
  {:else if answer}
    <div class="answer-container">
      <div class="answer-header">
        <h2>Answer</h2>
        <CopyButton text={answer} />
      </div>
      <div class="answer-content">
        {answer}
      </div>

      {#if sources && sources.length > 0}
        <div class="sources-container">
          <h3>Sources</h3>
          <div class="sources-list">
            {#each sources as source, i}
              <div
                class="source-item"
                on:click={() => handleSourceClick(source)}
              >
                <div class="source-header">
                  <span class="source-number">{i + 1}</span>
                  <span class="source-reference"
                    >{formatReference(source.reference)}</span
                  >
                </div>
                <div class="source-content">
                  <p>{source.content}</p>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if filtersApplied.surah_filter || filtersApplied.verse_filter}
        <div class="filters-applied">
          <p>
            Filters applied:
            {#if filtersApplied.surah_filter}
              Surah {filtersApplied.surah_filter}
            {/if}
            {#if filtersApplied.verse_filter}
              {#if filtersApplied.surah_filter},
              {/if}
              Verse {filtersApplied.verse_filter}
            {/if}
          </p>
        </div>
      {/if}
    </div>
  {:else}
    <div class="no-results">
      <p>No results to display. Try searching for Quranic knowledge.</p>
    </div>
  {/if}
</div>

<style>
  .search-results-container {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
  }

  .loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }

  .loading-spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top: 4px solid #3498db;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .answer-container {
    background-color: var(--card-bg, #fff);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .answer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-color, #eee);
  }

  .answer-header h2 {
    margin: 0;
    font-size: 1.25rem;
    color: var(--heading-color, #333);
  }

  .answer-content {
    line-height: 1.6;
    color: var(--text-color, #444);
    margin-bottom: 1.5rem;
    white-space: pre-line;
  }

  .sources-container {
    margin-top: 1.5rem;
  }

  .sources-container h3 {
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
    color: var(--heading-color, #333);
  }

  .sources-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .source-item {
    background-color: var(--source-bg, #f9f9f9);
    border-radius: 6px;
    padding: 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .source-item:hover {
    background-color: var(--source-hover-bg, #f0f0f0);
  }

  .source-header {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
  }

  .source-number {
    background-color: var(--primary-color, #3498db);
    color: white;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    margin-right: 0.75rem;
  }

  .source-reference {
    font-weight: 600;
    color: var(--heading-color, #333);
  }

  .source-content {
    color: var(--text-color, #555);
    font-size: 0.95rem;
    line-height: 1.5;
  }

  .filters-applied {
    margin-top: 1rem;
    font-size: 0.9rem;
    color: var(--muted-color, #777);
    font-style: italic;
  }

  .no-results {
    text-align: center;
    padding: 2rem;
    color: var(--muted-color, #777);
  }

  /* Dark mode adjustments */
  :global([data-theme="dark"]) .source-item {
    background-color: var(--source-bg, #2a2a2a);
  }

  :global([data-theme="dark"]) .source-item:hover {
    background-color: var(--source-hover-bg, #333);
  }
</style>
