<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { slide } from 'svelte/transition';
  import { languageStore } from '../stores/languageStore';
  
  export let selectedSurah: number | null = null;
  export let showFilter = false;
  
  const dispatch = createEventDispatcher();
  
  // Multilingual surah data including Arabic and Spanish names
  const surahsByLanguage = {
    en: [
      { number: 1, name: "Al-Fatihah", englishName: "The Opening" },
      { number: 2, name: "Al-Baqarah", englishName: "The Cow" },
      { number: 3, name: "Aal-Imran", englishName: "The Family of Imran" },
      { number: 4, name: "An-Nisa", englishName: "The Women" },
      { number: 5, name: "Al-Ma'idah", englishName: "The Table Spread" }
      // Add more as needed
    ],
    ar: [
      { number: 1, name: "الفاتحة", englishName: "الفاتحة" },
      { number: 2, name: "البقرة", englishName: "البقرة" },
      { number: 3, name: "آل عمران", englishName: "آل عمران" },
      { number: 4, name: "النساء", englishName: "النساء" },
      { number: 5, name: "المائدة", englishName: "المائدة" }
      // Add more as needed
    ],
    es: [
      { number: 1, name: "Al-Fatihah", englishName: "La Apertura" },
      { number: 2, name: "Al-Baqarah", englishName: "La Vaca" },
      { number: 3, name: "Aal-Imran", englishName: "La Familia de Imran" },
      { number: 4, name: "An-Nisa", englishName: "Las Mujeres" },
      { number: 5, name: "Al-Ma'idah", englishName: "La Mesa Servida" }
      // Add more as needed
    ]
  };
  
  // Get the appropriate surah list based on language
  $: surahs = surahsByLanguage[$languageStore];
  
  // Translation strings
  $: filterTitle = $languageStore === 'en' 
    ? 'Filter by Surah' 
    : $languageStore === 'ar' 
    ? 'تصفية حسب السورة' 
    : 'Filtrar por Sura';
  
  $: selectLabel = $languageStore === 'en' 
    ? 'Select Surah' 
    : $languageStore === 'ar' 
    ? 'اختر سورة' 
    : 'Seleccionar Sura';
  
  $: allSurahs = $languageStore === 'en' 
    ? 'All Surahs' 
    : $languageStore === 'ar' 
    ? 'جميع السور' 
    : 'Todas las Suras';
  
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
  <div class="surah-filter" transition:slide class:rtl={$languageStore === 'ar'}>
    <div class="card bg-base-100 dark:bg-base-300 shadow-lg">
      <div class="card-body">
        <h3 class="card-title text-lg font-semibold text-neutral dark:text-neutral-content" class:arabic={$languageStore === 'ar'}>
          {filterTitle}
        </h3>
        
        <div class="form-control w-full">
          <label class="label" for="surah-select">
            <span class="label-text text-neutral dark:text-neutral-content" class:arabic={$languageStore === 'ar'}>
              {selectLabel}
            </span>
          </label>
          <div class="flex gap-2">
            <select 
              id="surah-select"
              class="select select-bordered flex-1" 
              class:arabic={$languageStore === 'ar'}
              value={selectedSurah || ""}
              on:change={handleSurahChange}
              dir={$languageStore === 'ar' ? 'rtl' : 'ltr'}
            >
              <option value="" class:arabic={$languageStore === 'ar'}>
                {allSurahs}
              </option>
              {#each surahs as surah}
                <option value={surah.number} class:arabic={$languageStore === 'ar'}>
                  {$languageStore === 'ar' 
                    ? `${surah.name} - ${surah.number}` 
                    : `${surah.number}. ${surah.name} (${surah.englishName})`}
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
  
  .rtl {
    direction: rtl;
    text-align: right;
  }
</style>