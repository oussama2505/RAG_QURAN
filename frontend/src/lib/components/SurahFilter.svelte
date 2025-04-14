<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { slide } from 'svelte/transition';
  
  export let selectedSurah: number | null = null;
  export let showFilter = false;
  
  const dispatch = createEventDispatcher();
  
  // Surah data - you might want to load this from an API or store
  const surahs = [
    { number: 1, name: "Al-Fatihah", englishName: "The Opening" },
    { number: 2, name: "Al-Baqarah", englishName: "The Cow" },
    { number: 3, name: "Aal-Imran", englishName: "The Family of Imran" },
    // Add more surahs or load them dynamically
  ];
  
  function handleSurahChange(event: Event) {
    const select = event.target as HTMLSelectElement;
    const value = select.value;
    
    if (value === "") {
      selectedSurah = null;
    } else {
      selectedSurah = parseInt(value, 10);
    }
    
    dispatch('change', selectedSurah);
  }
  
  function clearFilter() {
    selectedSurah = null;
    dispatch('change', null);
  }
</script>

{#if showFilter}
  <div class="surah-filter" transition:slide>
    <div class="card bg-base-100 shadow-lg">
      <div class="card-body">
        <h3 class="card-title text-lg font-semibold">Filter by Surah</h3>
        
        <div class="form-control w-full">
          <label class="label" for="surah-select">
            <span class="label-text">Select Surah</span>
          </label>
          <div class="flex gap-2">
            <select 
              id="surah-select"
              class="select select-bordered flex-1" 
              value={selectedSurah || ""}
              on:change={handleSurahChange}
            >
              <option value="">All Surahs</option>
              {#each surahs as surah}
                <option value={surah.number}>
                  {surah.number}. {surah.name} ({surah.englishName})
                </option>
              {/each}
            </select>
            
            {#if selectedSurah}
              <button 
                class="btn btn-ghost" 
                on:click={clearFilter}
                aria-label="Clear filter"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .surah-filter {
    width: 100%;
    margin-bottom: 1rem;
  }
</style>