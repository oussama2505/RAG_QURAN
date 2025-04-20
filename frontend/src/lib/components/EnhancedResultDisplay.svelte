<script lang="ts">
  import { marked } from 'marked';
  import { fade, slide } from 'svelte/transition';
  import type { Source } from '../stores/appStore';
  import { languageStore } from '../stores/languageStore';
  import CopyButton from './CopyButton.svelte';
  
  export let response: {
    answer: string;
    sources: Source[];
    filters_applied: {
      surah_filter?: number;
      verse_filter?: number;
      end_verse_filter?: number;
    };
    translation?: {
      translated_text: string;
      arabic_text: string;
      translation_name: string;
      reference: string;
    };
    summary?: {
      summary: string;
      original_length: number;
      summary_length: number;
      focus?: string;
    };
  };
  
  // Local state
  let activeTab = 'answer';
  let showAllSources = false;
  let expandedSourceIndex: number | null = null;
  
  // Format the answer with markdown
  $: formattedAnswer = marked.parse(response.answer);
  
  // Group sources by type
  $: groupedSources = response.sources.reduce((acc, source) => {
    const type = source.source_type;
    if (!acc[type]) {
      acc[type] = [];
    }
    acc[type].push(source);
    return acc;
  }, {} as Record<string, Source[]>);
  
  // Translation strings
  $: answerTitle = $languageStore === 'en' 
    ? 'Answer' 
    : $languageStore === 'ar' 
    ? 'الإجابة' 
    : 'Respuesta';
    
  $: copyAnswerLabel = $languageStore === 'en' 
    ? 'Copy answer' 
    : $languageStore === 'ar' 
    ? 'نسخ الإجابة' 
    : 'Copiar respuesta';
    
  $: sourcesTitle = $languageStore === 'en' 
    ? 'Sources' 
    : $languageStore === 'ar' 
    ? 'المصادر' 
    : 'Fuentes';
    
  $: filtersApplied = $languageStore === 'en' 
    ? 'Filters applied:' 
    : $languageStore === 'ar' 
    ? 'الفلاتر المطبقة:' 
    : 'Filtros aplicados:';
    
  $: surahLabel = $languageStore === 'en' 
    ? 'Surah' 
    : $languageStore === 'ar' 
    ? 'سورة' 
    : 'Sura';
    
  $: verseLabel = $languageStore === 'en' 
    ? 'Verse' 
    : $languageStore === 'ar' 
    ? 'آية' 
    : 'Versículo';
    
  $: translationTitle = $languageStore === 'en'
    ? 'Translation'
    : $languageStore === 'ar'
    ? 'ترجمة'
    : 'Traducción';
    
  $: summaryTitle = $languageStore === 'en'
    ? 'Summary'
    : $languageStore === 'ar'
    ? 'ملخص'
    : 'Resumen';
    
  $: originalTextTitle = $languageStore === 'en'
    ? 'Original Arabic'
    : $languageStore === 'ar'
    ? 'النص العربي الأصلي'
    : 'Árabe Original';
    
  $: translatedTextTitle = $languageStore === 'en'
    ? 'Translation'
    : $languageStore === 'ar'
    ? 'الترجمة'
    : 'Traducción';
    
  $: showAllSourcesText = $languageStore === 'en'
    ? showAllSources ? 'Show fewer sources' : 'Show all sources'
    : $languageStore === 'ar'
    ? showAllSources ? 'عرض مصادر أقل' : 'عرض كل المصادر'
    : showAllSources ? 'Mostrar menos fuentes' : 'Mostrar todas las fuentes';
    
  $: summaryInfoText = $languageStore === 'en'
    ? `Summarized from ${response.summary?.original_length} to ${response.summary?.summary_length} words`
    : $languageStore === 'ar'
    ? `تم تلخيصه من ${response.summary?.original_length} إلى ${response.summary?.summary_length} كلمة`
    : `Resumido de ${response.summary?.original_length} a ${response.summary?.summary_length} palabras`;
  
  $: summaryFocusText = $languageStore === 'en'
    ? `Focus: ${response.summary?.focus}`
    : $languageStore === 'ar'
    ? `التركيز: ${response.summary?.focus}`
    : `Enfoque: ${response.summary?.focus}`;
  
  $: tabs = [
    { id: 'answer', label: answerTitle, show: true },
    { id: 'translation', label: translationTitle, show: !!response.translation },
    { id: 'summary', label: summaryTitle, show: !!response.summary }
  ].filter(tab => tab.show);
  
  function toggleSource(index: number) {
    expandedSourceIndex = expandedSourceIndex === index ? null : index;
  }
  
  function toggleShowAllSources() {
    showAllSources = !showAllSources;
  }
</script>

<div class="card bg-base-100 shadow-lg" class:rtl={$languageStore === 'ar'}>
  <div class="card-body">
    <!-- Tab Navigation -->
    {#if tabs.length > 1}
      <div class="tabs tabs-boxed mb-4">
        {#each tabs as tab}
          <button 
            class="tab" 
            class:tab-active={activeTab === tab.id}
            on:click={() => activeTab = tab.id}
            class:arabic={$languageStore === 'ar'}
          >
            {tab.label}
          </button>
        {/each}
      </div>
    {/if}
    
    <!-- Answer Tab -->
    {#if activeTab === 'answer'}
      <div transition:fade>
        <div class="flex justify-between items-start">
          <h2 class="card-title text-xl mb-4" class:arabic={$languageStore === 'ar'}>
            {answerTitle}
          </h2>
          <CopyButton text={response.answer} label={copyAnswerLabel} size="sm" />
        </div>
        
        <div class="prose max-w-none quran-container">
          {@html formattedAnswer}
        </div>
      </div>
    {/if}
    
    <!-- Translation Tab -->
    {#if activeTab === 'translation' && response.translation}
      <div transition:fade>
        <div class="flex justify-between items-start">
          <h2 class="card-title text-xl mb-4" class:arabic={$languageStore === 'ar'}>
            {translationTitle} - {response.translation.reference}
          </h2>
          <CopyButton text={response.translation.translated_text} size="sm" />
        </div>
        
        <div class="space-y-6">
          <div class="bg-base-200 p-4 rounded-lg">
            <h3 class="font-semibold mb-2" class:arabic={$languageStore === 'ar'}>
              {originalTextTitle}
            </h3>
            <p class="whitespace-pre-line arabic" dir="rtl">
              {response.translation.arabic_text}
            </p>
          </div>
          
          <div class="bg-base-200 p-4 rounded-lg">
            <h3 class="font-semibold mb-2" class:arabic={$languageStore === 'ar'}>
              {translatedTextTitle} ({response.translation.translation_name})
            </h3>
            <p class="whitespace-pre-line" dir={$languageStore === 'ar' ? 'rtl' : 'ltr'} 
               class:arabic={$languageStore === 'ar'}>
              {response.translation.translated_text}
            </p>
          </div>
        </div>
      </div>
    {/if}
    
    <!-- Summary Tab -->
    {#if activeTab === 'summary' && response.summary}
      <div transition:fade>
        <div class="flex justify-between items-start">
          <h2 class="card-title text-xl mb-4" class:arabic={$languageStore === 'ar'}>
            {summaryTitle}
          </h2>
          <CopyButton text={response.summary.summary} size="sm" />
        </div>
        
        <div class="prose max-w-none">
          <p class="whitespace-pre-line" dir={$languageStore === 'ar' ? 'rtl' : 'ltr'} 
             class:arabic={$languageStore === 'ar'}>
            {response.summary.summary}
          </p>
        </div>
        
        <div class="mt-4 text-sm text-neutral-500">
          <p class:arabic={$languageStore === 'ar'}>
            {summaryInfoText}
          </p>
          {#if response.summary.focus}
            <p class:arabic={$languageStore === 'ar'}>
              {summaryFocusText}
            </p>
          {/if}
        </div>
      </div>
    {/if}
    
    <!-- Sources Section (shown with all tabs) -->
    {#if response.sources && response.sources.length > 0}
      <div class="divider my-6">
        <span class:arabic={$languageStore === 'ar'}>
          {sourcesTitle}
        </span>
      </div>
      
      <!-- Sources Display -->
      <div class="space-y-6">
        {#each Object.entries(groupedSources) as [sourceType, sources], i}
          {@const displaySources = showAllSources ? sources : sources.slice(0, 2)}
          
          <div>
            <h3 class="text-lg font-semibold mb-2 capitalize" class:arabic={$languageStore === 'ar'}>
              {$languageStore === 'en' 
                ? sourceType.replace('_', ' ')
                : $languageStore === 'ar'
                ? (sourceType === 'quran_verse' ? 'آيات القرآن' : 
                   sourceType === 'tafsir' ? 'التفسير' : sourceType.replace('_', ' '))
                : (sourceType === 'quran_verse' ? 'Versículos del Corán' : 
                   sourceType === 'tafsir' ? 'Interpretación' : sourceType.replace('_', ' '))}
            </h3>
            
            <div class="space-y-4">
              {#each displaySources as source, j}
                {@const isExpanded = expandedSourceIndex === sources.indexOf(source)}
                
                <div class="bg-base-200 dark:bg-base-300 p-4 rounded-lg">
                  <div class="flex justify-between items-start mb-2">
                    <button class="font-medium hover:underline" on:click={() => toggleSource(sources.indexOf(source))}
                            class:arabic={$languageStore === 'ar'}>
                      {source.reference}
                      <span class="text-sm opacity-70">
                        {isExpanded ? '(collapse)' : '(expand)'}
                      </span>
                    </button>
                    <CopyButton text={source.content} size="sm" />
                  </div>
                  
                  {#if isExpanded}
                    <p class="whitespace-pre-line" dir={source.source_type === 'tafsir' && source.reference.includes('ar-') ? 'rtl' : ($languageStore === 'ar' ? 'rtl' : 'ltr')} 
                       class:arabic={source.source_type === 'tafsir' && source.reference.includes('ar-') || $languageStore === 'ar'}>
                      {source.content}
                    </p>
                  {:else}
                    <p class="whitespace-pre-line line-clamp-2" dir={source.source_type === 'tafsir' && source.reference.includes('ar-') ? 'rtl' : ($languageStore === 'ar' ? 'rtl' : 'ltr')} 
                       class:arabic={source.source_type === 'tafsir' && source.reference.includes('ar-') || $languageStore === 'ar'}>
                      {source.content}
                    </p>
                  {/if}
                </div>
              {/each}
              
              {#if sources.length > 2}
                <button 
                  class="btn btn-sm btn-ghost w-full" 
                  on:click={toggleShowAllSources}
                  class:arabic={$languageStore === 'ar'}
                >
                  {showAllSourcesText}
                </button>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
    
    <!-- Filters Applied Section -->
    {#if response.filters_applied && (response.filters_applied.surah_filter || response.filters_applied.verse_filter)}
      <div class="mt-4 text-sm text-neutral-500 dark:text-neutral-400">
        <p class:arabic={$languageStore === 'ar'}>
          {filtersApplied}
          {#if response.filters_applied.surah_filter}
            {surahLabel} {response.filters_applied.surah_filter}
          {/if}
          {#if response.filters_applied.verse_filter}
            {#if response.filters_applied.surah_filter}, {/if}
            {verseLabel} {response.filters_applied.verse_filter}
            {#if response.filters_applied.end_verse_filter}
              - {response.filters_applied.end_verse_filter}
            {/if}
          {/if}
        </p>
      </div>
    {/if}
  </div>
</div>

<style>
  .rtl {
    direction: rtl;
    text-align: right;
  }
  
  :global(.arabic) {
    font-family: 'Traditional Arabic', 'Scheherazade New', serif;
  }
  
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>