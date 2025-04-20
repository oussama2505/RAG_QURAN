<script lang="ts">
  import { onMount } from "svelte";
  import { settings } from "../stores/settings";

  let apiKey = "";
  let selectedModel = "gpt-3.5-turbo";
  let availableModels = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"];
  let showApiKey = false;

  onMount(() => {
    // Load saved settings
    const savedSettings = localStorage.getItem("quranRagSettings");
    if (savedSettings) {
      const parsed = JSON.parse(savedSettings);
      apiKey = parsed.apiKey || "";
      selectedModel = parsed.model || "gpt-3.5-turbo";
    }
  });

  function saveSettings() {
    const newSettings = {
      apiKey,
      model: selectedModel,
    };
    localStorage.setItem("quranRagSettings", JSON.stringify(newSettings));
    settings.set(newSettings);
  }
</script>

<div class="settings-panel">
  <h2>Settings</h2>

  <div class="setting-group">
    <label for="apiKey">OpenAI API Key</label>
    <div class="input-group">
      {#if showApiKey}
        <input
          type="text"
          id="apiKey"
          bind:value={apiKey}
          placeholder="Enter your OpenAI API key"
        />
      {:else}
        <input
          type="password"
          id="apiKey"
          bind:value={apiKey}
          placeholder="Enter your OpenAI API key"
        />
      {/if}
      <button on:click={() => (showApiKey = !showApiKey)}>
        {showApiKey ? "Hide" : "Show"}
      </button>
    </div>
  </div>

  <div class="setting-group">
    <label for="model">Model Selection</label>
    <select id="model" bind:value={selectedModel}>
      {#each availableModels as model}
        <option value={model}>{model}</option>
      {/each}
    </select>
  </div>

  <button class="save-button" on:click={saveSettings}> Save Settings </button>
</div>

<style>
  .settings-panel {
    padding: 1rem;
    background: var(--surface-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  h2 {
    margin: 0 0 1rem 0;
    color: var(--text-color);
  }

  .setting-group {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--text-color);
  }

  .input-group {
    display: flex;
    gap: 0.5rem;
  }

  input,
  select {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--background-color);
    color: var(--text-color);
  }

  button {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    background: var(--primary-color);
    color: white;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  button:hover {
    background: var(--primary-color-dark);
  }

  .save-button {
    width: 100%;
    margin-top: 1rem;
  }
</style>
