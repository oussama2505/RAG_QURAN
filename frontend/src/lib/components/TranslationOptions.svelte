<script lang="ts">
  import { settings } from "../stores/settings";

  let selectedTranslation = "en-sahih";
  let selectedSummarization = "medium";
  let focusTopic = "";

  const availableTranslations = [
    { id: "en-sahih", name: "Sahih International" },
    { id: "en-pickthall", name: "Pickthall" },
    { id: "en-yusufali", name: "Yusuf Ali" },
    { id: "en-shakir", name: "Shakir" },
  ];

  const summarizationOptions = [
    { id: "short", name: "Short Summary" },
    { id: "medium", name: "Medium Summary" },
    { id: "detailed", name: "Detailed Summary" },
  ];

  function handleTranslationChange() {
    // Emit event or update store
    $settings.translation = selectedTranslation;
  }

  function handleSummarizationChange() {
    // Emit event or update store
    $settings.summarization = selectedSummarization;
  }

  function handleFocusTopicChange() {
    // Emit event or update store
    $settings.focusTopic = focusTopic;
  }
</script>

<div class="translation-options">
  <h3>Translation & Summarization Options</h3>

  <div class="option-group">
    <label for="translation">Translation</label>
    <select
      id="translation"
      bind:value={selectedTranslation}
      on:change={handleTranslationChange}
    >
      {#each availableTranslations as translation}
        <option value={translation.id}>{translation.name}</option>
      {/each}
    </select>
  </div>

  <div class="option-group">
    <label for="summarization">Summarization Level</label>
    <select
      id="summarization"
      bind:value={selectedSummarization}
      on:change={handleSummarizationChange}
    >
      {#each summarizationOptions as option}
        <option value={option.id}>{option.name}</option>
      {/each}
    </select>
  </div>

  <div class="option-group">
    <label for="focusTopic">Focus Topic (Optional)</label>
    <input
      type="text"
      id="focusTopic"
      bind:value={focusTopic}
      on:change={handleFocusTopicChange}
      placeholder="Enter a specific topic to focus on"
    />
  </div>
</div>

<style>
  .translation-options {
    padding: 1rem;
    background: var(--surface-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  h3 {
    margin: 0 0 1rem 0;
    color: var(--text-color);
  }

  .option-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--text-color);
  }

  select,
  input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--background-color);
    color: var(--text-color);
  }

  input::placeholder {
    color: var(--text-color-secondary);
  }
</style>
