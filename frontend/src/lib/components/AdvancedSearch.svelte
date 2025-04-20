<script lang="ts">
  import { createEventDispatcher, onMount } from "svelte";
  import { appStore } from "../stores/appStore";
  import { languageStore } from "../stores/languageStore";
  import { settings } from "../stores/settings";
  import { searchState } from "../stores/search";

  // Props with default values
  export let initialQuestion = "";
  export let isLoading = false;

  // Local state
  let question = initialQuestion;
  let showAdvancedOptions = false;
  let surahFilter: number | null = null;
  let verseFilter: number | null = null;
  let endVerseFilter: number | null = null;
  let translationOption: string = "en-sahih-international";
  let useSummarization = false;
  let summaryLength = 200;
  let summaryFocus = "";

  // Available translation options
  const translations = [
    { id: "en-sahih-international", name: "Sahih International (English)" },
    { id: "en-yusuf-ali", name: "Yusuf Ali (English)" },
    { id: "en-pickthall", name: "Pickthall (English)" },
    { id: "fr-hamidullah", name: "Hamidullah (French)" },
    { id: "tr-diyanet", name: "Diyanet İşleri (Turkish)" },
    { id: "ur-jalandhry", name: "Jalandhry (Urdu)" },
  ];

  const dispatch = createEventDispatcher();

  // Subscribe to store changes
  onMount(() => {
    const unsubscribe = appStore.subscribe((state) => {
      if (state.question !== question) {
        question = state.question;
      }
      if (state.surahFilter !== surahFilter) {
        surahFilter = state.surahFilter;
      }
    });

    return unsubscribe;
  });

  function handleSubmit() {
    if (!question?.trim()) return;

    // Create search parameters object
    const searchParams = {
      question,
      filters: {
        surah: surahFilter,
        verse: verseFilter,
        endVerse: endVerseFilter,
      },
      options: {
        translation: translationOption,
        summarize: useSummarization,
        summaryLength: summaryLength,
        summaryFocus: summaryFocus,
      },
    };

    // Dispatch event with search parameters
    dispatch("advancedSearch", searchParams);

    // Add to recent questions if not already there
    if (!$appStore.recentQuestions.includes(question)) {
      appStore.addRecentQuestion(question);
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey && !isLoading) {
      event.preventDefault();
      handleSubmit();
    }
  }

  function toggleAdvancedOptions() {
    showAdvancedOptions = !showAdvancedOptions;
  }

  // Get placeholder text based on language
  $: placeholder =
    $languageStore === "en"
      ? "Enter your question about the Quran..."
      : $languageStore === "ar"
        ? "أدخل سؤالك حول القرآن الكريم..."
        : "Ingrese su pregunta sobre el Corán...";

  // Get label text based on language
  $: labelText =
    $languageStore === "en"
      ? "Advanced Search"
      : $languageStore === "ar"
        ? "بحث متقدم"
        : "Búsqueda avanzada";

  // Get advanced options text based on language
  $: advancedOptionsText =
    $languageStore === "en"
      ? "Advanced Options"
      : $languageStore === "ar"
        ? "خيارات متقدمة"
        : "Opciones avanzadas";

  // Get translation text based on language
  $: translationText =
    $languageStore === "en"
      ? "Translation"
      : $languageStore === "ar"
        ? "ترجمة"
        : "Traducción";

  // Get summarization text based on language
  $: summarizationText =
    $languageStore === "en"
      ? "Summarize Results"
      : $languageStore === "ar"
        ? "تلخيص النتائج"
        : "Resumir resultados";

  // Get summary length text based on language
  $: summaryLengthText =
    $languageStore === "en"
      ? "Summary Length (words)"
      : $languageStore === "ar"
        ? "طول الملخص (كلمات)"
        : "Longitud del resumen (palabras)";

  // Get summary focus text based on language
  $: summaryFocusText =
    $languageStore === "en"
      ? "Focus on (optional)"
      : $languageStore === "ar"
        ? "التركيز على (اختياري)"
        : "Enfoque en (opcional)";

  // Get verse range text based on language
  $: verseRangeText =
    $languageStore === "en"
      ? "Verse Range"
      : $languageStore === "ar"
        ? "نطاق الآيات"
        : "Rango de versos";

  let searchQuery = "";
  let selectedSurah = "";
  let selectedVerse = "";
  let isSearching = false;

  const surahs = [
    { number: 1, name: "Al-Fatihah" },
    { number: 2, name: "Al-Baqarah" },
    { number: 3, name: "Ali 'Imran" },
    { number: 4, name: "An-Nisa" },
    { number: 5, name: "Al-Ma'idah" },
    // Add more surahs as needed
  ];

  async function handleSearch() {
    if (!searchQuery.trim()) return;

    isSearching = true;
    $searchState.isLoading = true;

    try {
      // TODO: Implement search logic using MCP servers
      const response = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: searchQuery,
          surah: selectedSurah,
          verse: selectedVerse,
          translation: $settings.translation,
          summarization: $settings.summarization,
          focusTopic: $settings.focusTopic,
        }),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();
      $searchState.results = data.results;
      $searchState.error = null;
    } catch (error) {
      $searchState.error =
        error instanceof Error ? error.message : "An unknown error occurred";
    } finally {
      isSearching = false;
      $searchState.isLoading = false;
    }
  }

  function handleKeyPress(event: KeyboardEvent) {
    if (event.key === "Enter") {
      handleSearch();
    }
  }
</script>

<div class="advanced-search-container" class:rtl={$languageStore === "ar"}>
  <form on:submit|preventDefault={handleSubmit} class="flex flex-col space-y-4">
    <div class="form-control">
      <label for="question" class="label">
        <span
          class="label-text text-lg font-medium"
          class:arabic={$languageStore === "ar"}
        >
          {labelText}
        </span>
        <button
          type="button"
          class="btn btn-sm btn-ghost"
          on:click={toggleAdvancedOptions}
          aria-expanded={showAdvancedOptions}
        >
          <span class:arabic={$languageStore === "ar"}>
            {advancedOptionsText}
          </span>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            class="w-5 h-5 transition-transform"
            class:rotate-180={showAdvancedOptions}
          >
            <path
              fill-rule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </label>
      <div class="relative">
        <textarea
          id="question"
          bind:value={question}
          on:keydown={handleKeydown}
          {placeholder}
          class="textarea textarea-bordered w-full h-24 resize-none"
          class:arabic={$languageStore === "ar"}
          class:pr-12={$languageStore !== "ar"}
          class:pl-12={$languageStore === "ar"}
          disabled={isLoading}
          dir={$languageStore === "ar" ? "rtl" : "ltr"}
        ></textarea>
        <button
          type="submit"
          class="btn btn-primary absolute bottom-2"
          class:right-2={$languageStore !== "ar"}
          class:left-2={$languageStore === "ar"}
          disabled={!question?.trim() || isLoading}
        >
          {#if isLoading}
            <span class="loading loading-spinner loading-sm"></span>
          {:else}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          {/if}
        </button>
      </div>
    </div>

    {#if showAdvancedOptions}
      <div
        class="advanced-options-panel bg-base-200 p-4 rounded-lg shadow"
        transition:slide
      >
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Surah & Verse Filters -->
          <div class="form-control">
            <label class="label">
              <span class="label-text" class:arabic={$languageStore === "ar"}
                >Surah</span
              >
            </label>
            <input
              type="number"
              bind:value={surahFilter}
              min="1"
              max="114"
              class="input input-bordered w-full"
              placeholder="1-114"
            />
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text" class:arabic={$languageStore === "ar"}
                >{verseRangeText}</span
              >
            </label>
            <div class="flex space-x-2">
              <input
                type="number"
                bind:value={verseFilter}
                min="1"
                class="input input-bordered w-full"
                placeholder="Verse"
              />
              <span class="self-center">-</span>
              <input
                type="number"
                bind:value={endVerseFilter}
                min="1"
                class="input input-bordered w-full"
                placeholder="End (optional)"
              />
            </div>
          </div>

          <!-- Translation Options -->
          <div class="form-control">
            <label class="label">
              <span class="label-text" class:arabic={$languageStore === "ar"}
                >{translationText}</span
              >
            </label>
            <select
              bind:value={translationOption}
              class="select select-bordered w-full"
            >
              {#each translations as translation}
                <option value={translation.id}>{translation.name}</option>
              {/each}
            </select>
          </div>

          <!-- Summarization Options -->
          <div class="form-control">
            <label class="label cursor-pointer">
              <span class="label-text" class:arabic={$languageStore === "ar"}
                >{summarizationText}</span
              >
              <input
                type="checkbox"
                bind:checked={useSummarization}
                class="toggle toggle-primary"
              />
            </label>
          </div>

          {#if useSummarization}
            <div class="form-control">
              <label class="label">
                <span class="label-text" class:arabic={$languageStore === "ar"}
                  >{summaryLengthText}</span
                >
              </label>
              <input
                type="number"
                bind:value={summaryLength}
                min="50"
                max="500"
                step="50"
                class="input input-bordered w-full"
              />
            </div>

            <div class="form-control">
              <label class="label">
                <span class="label-text" class:arabic={$languageStore === "ar"}
                  >{summaryFocusText}</span
                >
              </label>
              <input
                type="text"
                bind:value={summaryFocus}
                class="input input-bordered w-full"
                placeholder="e.g., theological concepts, historical context"
              />
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </form>
</div>

<div class="advanced-search">
  <h3>Advanced Search</h3>

  <div class="search-group">
    <label for="searchQuery">Search Query</label>
    <input
      type="text"
      id="searchQuery"
      bind:value={searchQuery}
      on:keypress={handleKeyPress}
      placeholder="Enter your question about the Quran"
      disabled={isSearching}
    />
  </div>

  <div class="filters">
    <div class="filter-group">
      <label for="surah">Surah</label>
      <select id="surah" bind:value={selectedSurah} disabled={isSearching}>
        <option value="">All Surahs</option>
        {#each surahs as surah}
          <option value={surah.number}>{surah.number}. {surah.name}</option>
        {/each}
      </select>
    </div>

    <div class="filter-group">
      <label for="verse">Verse</label>
      <input
        type="text"
        id="verse"
        bind:value={selectedVerse}
        placeholder="Verse number (optional)"
        disabled={isSearching}
      />
    </div>
  </div>

  <button
    class="search-button"
    on:click={handleSearch}
    disabled={isSearching || !searchQuery.trim()}
  >
    {isSearching ? "Searching..." : "Search"}
  </button>

  {#if $searchState.error}
    <div class="error-message">
      {$searchState.error}
    </div>
  {/if}
</div>

<style>
  .advanced-search-container {
    width: 100%;
  }

  .rtl {
    direction: rtl;
    text-align: right;
  }

  :global(.arabic) {
    font-family: "Traditional Arabic", "Scheherazade New", serif;
  }

  .advanced-options-panel {
    border: 1px solid var(--color-border, #e2e8f0);
  }

  .advanced-search {
    padding: 1rem;
    background: var(--surface-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  h3 {
    margin: 0 0 1rem 0;
    color: var(--text-color);
  }

  .search-group,
  .filter-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--text-color);
  }

  input,
  select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--background-color);
    color: var(--text-color);
  }

  input:disabled,
  select:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .filters {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .search-button {
    width: 100%;
    padding: 0.75rem;
    border: none;
    border-radius: 4px;
    background: var(--primary-color);
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .search-button:hover:not(:disabled) {
    background: var(--primary-color-dark);
  }

  .search-button:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .error-message {
    margin-top: 1rem;
    padding: 0.5rem;
    background: var(--error-color);
    color: white;
    border-radius: 4px;
    text-align: center;
  }
</style>
