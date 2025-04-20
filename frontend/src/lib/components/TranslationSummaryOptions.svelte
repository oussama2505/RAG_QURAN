<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { slide } from "svelte/transition";
  import { mcpServices } from "../services/mcpServices";

  export let visible = false;

  // Translation options
  const translations = [
    { id: "en-sahih-international", name: "Sahih International (English)" },
    { id: "en-yusuf-ali", name: "Yusuf Ali (English)" },
    { id: "en-pickthall", name: "Pickthall (English)" },
    { id: "fr-hamidullah", name: "Hamidullah (French)" },
    { id: "tr-diyanet", name: "Diyanet İşleri (Turkish)" },
    { id: "ur-jalandhry", name: "Jalandhry (Urdu)" },
  ];

  // Summarization options
  let useSummarization = false;
  let summaryLength = 200;
  let summaryFocus = "";
  let translationOption = "en-sahih-international";

  // Tafsir options
  let showTafsir = false;
  let tafsirSources = [
    { id: "ibn-kathir", name: "Ibn Kathir" },
    { id: "al-tabari", name: "Al-Tabari" },
    { id: "al-qurtubi", name: "Al-Qurtubi" },
    { id: "al-baghawi", name: "Al-Baghawi" },
    { id: "muyassar", name: "Muyassar" },
  ];
  let selectedTafsirSource = "ibn-kathir";

  const dispatch = createEventDispatcher();

  function applyOptions() {
    const options = {
      translation: {
        enabled: true,
        source: translationOption,
      },
      summarization: {
        enabled: useSummarization,
        length: summaryLength,
        focus: summaryFocus,
      },
      tafsir: {
        enabled: showTafsir,
        source: selectedTafsirSource,
      },
    };

    dispatch("optionsChange", options);
  }

  // Function to get a sample translation
  async function getSampleTranslation() {
    try {
      const sampleVerse =
        "Indeed, We have sent it down as an Arabic Qur'an that you might understand.";
      const result = await mcpServices.translation.translateText(
        sampleVerse,
        translationOption.split("-")[0] // Extract language code
      );

      // In a real implementation, we would display this result
      console.log("Translation result:", result);

      // For now, just dispatch an event to show it was successful
      dispatch("sampleTranslation", result);
    } catch (error) {
      console.error("Error getting sample translation:", error);
    }
  }

  // Function to get a sample summary
  async function getSampleSummary() {
    if (!useSummarization) return;

    try {
      const sampleText =
        "The Quran emphasizes the importance of seeking knowledge and understanding. It encourages believers to reflect on the signs of Allah in the universe and within themselves. The pursuit of knowledge is considered a form of worship, and scholars are highly respected in Islamic tradition. The first word revealed in the Quran was 'Read,' highlighting the significance of literacy and learning.";

      const result = await mcpServices.summarizer.summarizeText(sampleText, {
        length: summaryLength,
        focus: summaryFocus,
      });

      // In a real implementation, we would display this result
      console.log("Summary result:", result);

      // For now, just dispatch an event to show it was successful
      dispatch("sampleSummary", result);
    } catch (error) {
      console.error("Error getting sample summary:", error);
    }
  }
</script>

{#if visible}
  <div
    class="translation-summary-options bg-white dark:bg-base-200 rounded-lg shadow-lg p-6"
    transition:slide
  >
    <h2 class="text-xl font-bold mb-4 dark:text-white">
      Translation & Summarization Options
    </h2>

    <!-- Translation Options -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2 dark:text-white">Translation</h3>
      <select
        bind:value={translationOption}
        class="select select-bordered w-full"
      >
        {#each translations as option}
          <option value={option.id}>{option.name}</option>
        {/each}
      </select>
      <button
        class="btn btn-sm btn-outline mt-2"
        on:click={getSampleTranslation}
      >
        Preview Translation
      </button>
    </div>

    <!-- Summarization Options -->
    <div class="mb-6">
      <div class="flex items-center gap-2 mb-2">
        <input
          type="checkbox"
          bind:checked={useSummarization}
          class="checkbox"
          id="use-summarization"
        />
        <label
          for="use-summarization"
          class="text-lg font-semibold dark:text-white"
          >Enable Summarization</label
        >
      </div>

      {#if useSummarization}
        <div class="pl-6 border-l-2 border-primary">
          <div class="form-control mb-2">
            <label class="label">
              <span class="label-text dark:text-white"
                >Summary Length (characters)</span
              >
            </label>
            <input
              type="range"
              min="50"
              max="500"
              step="50"
              bind:value={summaryLength}
              class="range range-primary"
            />
            <div class="flex justify-between text-xs px-2 dark:text-gray-400">
              <span>50</span>
              <span>200</span>
              <span>350</span>
              <span>500</span>
            </div>
            <p class="text-sm mt-1 dark:text-gray-400">
              Current: {summaryLength} characters
            </p>
          </div>

          <div class="form-control mb-2">
            <label class="label">
              <span class="label-text dark:text-white"
                >Focus Area (optional)</span
              >
            </label>
            <input
              type="text"
              bind:value={summaryFocus}
              placeholder="e.g., historical context, moral lessons"
              class="input input-bordered w-full"
            />
          </div>

          <button
            class="btn btn-sm btn-outline mt-2"
            on:click={getSampleSummary}
          >
            Preview Summary
          </button>
        </div>
      {/if}
    </div>

    <!-- Tafsir Options -->
    <div class="mb-6">
      <div class="flex items-center gap-2 mb-2">
        <input
          type="checkbox"
          bind:checked={showTafsir}
          class="checkbox"
          id="show-tafsir"
        />
        <label for="show-tafsir" class="text-lg font-semibold dark:text-white"
          >Include Tafsir (Exegesis)</label
        >
      </div>

      {#if showTafsir}
        <div class="pl-6 border-l-2 border-primary">
          <select
            bind:value={selectedTafsirSource}
            class="select select-bordered w-full"
          >
            {#each tafsirSources as source}
              <option value={source.id}>{source.name}</option>
            {/each}
          </select>
        </div>
      {/if}
    </div>

    <!-- Apply Button -->
    <button class="btn btn-primary w-full" on:click={applyOptions}>
      Apply Options
    </button>
  </div>
{/if}

<style>
  .translation-summary-options {
    width: 100%;
    max-width: 500px;
    z-index: 50;
  }
</style>