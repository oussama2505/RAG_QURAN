<script lang="ts">
  import { settings } from "../stores/settings";

  const translations = [
    { id: "en-sahih", name: "Sahih International", language: "English" },
    { id: "en-pickthall", name: "Pickthall", language: "English" },
    { id: "en-yusufali", name: "Yusuf Ali", language: "English" },
    { id: "en-shakir", name: "Shakir", language: "English" },
    { id: "ar", name: "Arabic", language: "Arabic" },
    { id: "fr-hamidullah", name: "Hamidullah", language: "French" },
    { id: "es-cortes", name: "Cortes", language: "Spanish" },
    { id: "ur-ahmedali", name: "Ahmed Ali", language: "Urdu" },
  ];

  function handleTranslationChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    $settings.translation = select.value;
  }
</script>

<div class="translation-selector">
  <label for="translation">Select Translation</label>
  <select
    id="translation"
    value={$settings.translation}
    on:change={handleTranslationChange}
  >
    {#each translations as translation}
      <option value={translation.id}>
        {translation.name} ({translation.language})
      </option>
    {/each}
  </select>
</div>

<style>
  .translation-selector {
    margin-bottom: 1rem;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--text-color);
  }

  select {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border-color);
    border-radius: 4px;
    background: var(--background-color);
    color: var(--text-color);
  }
</style>
