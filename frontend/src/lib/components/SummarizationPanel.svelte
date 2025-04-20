<script lang="ts">
  import { settings } from "../stores/settings";

  const lengthOptions = [
    {
      id: "short",
      name: "Short Summary",
      description: "Brief overview of key points",
    },
    {
      id: "medium",
      name: "Medium Summary",
      description: "Balanced coverage of main points",
    },
    {
      id: "detailed",
      name: "Detailed Summary",
      description: "Comprehensive analysis with context",
    },
  ];

  const focusOptions = [
    {
      id: "thematic",
      name: "Thematic Focus",
      description: "Focus on themes and concepts",
    },
    {
      id: "linguistic",
      name: "Linguistic Focus",
      description: "Focus on language and structure",
    },
    {
      id: "historical",
      name: "Historical Focus",
      description: "Focus on historical context",
    },
    {
      id: "practical",
      name: "Practical Focus",
      description: "Focus on practical applications",
    },
  ];

  function handleLengthChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    $settings.summarization = select.value;
  }

  function handleFocusChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    $settings.focusTopic = select.value;
  }
</script>

<div class="summarization-panel">
  <h3>Summarization Options</h3>

  <div class="option-group">
    <label for="length">Summary Length</label>
    <select
      id="length"
      value={$settings.summarization}
      on:change={handleLengthChange}
    >
      {#each lengthOptions as option}
        <option value={option.id}>
          {option.name} - {option.description}
        </option>
      {/each}
    </select>
  </div>

  <div class="option-group">
    <label for="focus">Focus Area</label>
    <select
      id="focus"
      value={$settings.focusTopic}
      on:change={handleFocusChange}
    >
      <option value="">No Specific Focus</option>
      {#each focusOptions as option}
        <option value={option.id}>
          {option.name} - {option.description}
        </option>
      {/each}
    </select>
  </div>

  <div class="option-group">
    <label for="customFocus">Custom Focus (Optional)</label>
    <input
      type="text"
      id="customFocus"
      bind:value={$settings.focusTopic}
      placeholder="Enter a specific topic or theme to focus on"
    />
  </div>
</div>

<style>
  .summarization-panel {
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
