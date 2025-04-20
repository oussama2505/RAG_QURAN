<script lang="ts">
  import { searchState } from "../stores/search";

  export let highlightColor = "#ffeb3b";
  export let highlightOpacity = 0.3;

  function highlightText(text: string, query: string) {
    if (!query) return text;

    const regex = new RegExp(`(${query})`, "gi");
    return text.replace(regex, "<mark>$1</mark>");
  }

  function formatReference(surah: number, verse: number) {
    return `Surah ${surah}:${verse}`;
  }
</script>

<div class="source-display">
  {#if $searchState.isLoading}
    <div class="loading">Loading sources...</div>
  {:else if $searchState.results.length === 0}
    <div class="no-results">No sources found</div>
  {:else}
    <div class="sources-list">
      {#each $searchState.results as result}
        <div class="source-item">
          <div class="reference">
            {formatReference(result.surah, result.verse)}
          </div>
          <div class="text">
            {@html highlightText(result.text, $searchState.query)}
          </div>
          <div class="score">
            Relevance: {(result.score * 100).toFixed(1)}%
          </div>
        </div>
      {/each}
    </div>
  {/if}

  {#if $searchState.error}
    <div class="error">
      {$searchState.error}
    </div>
  {/if}
</div>

<style>
  .source-display {
    margin-top: 1rem;
  }

  .loading,
  .no-results,
  .error {
    padding: 1rem;
    text-align: center;
    color: var(--text-color);
  }

  .error {
    color: var(--error-color);
  }

  .sources-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .source-item {
    padding: 1rem;
    background: var(--surface-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .reference {
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: 0.5rem;
  }

  .text {
    line-height: 1.6;
    margin-bottom: 0.5rem;
  }

  .score {
    font-size: 0.875rem;
    color: var(--text-color-secondary);
  }

  mark {
    background-color: v-bind(highlightColor);
    opacity: v-bind(highlightOpacity);
    padding: 0.1em 0.2em;
    border-radius: 2px;
  }
</style>
