<script lang="ts">
  import { marked } from 'marked';
  import type { Source } from '../stores/appStore';
  import { languageStore } from '../stores/languageStore';
  import CopyButton from './CopyButton.svelte';
  
  export let response: {
    answer: string;
    sources: Source[];
    filters_applied: {
      surah_filter?: number;
      verse_filter?: number;
    };
  };
  
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
</script>

<div class="card bg-base-100 shadow-lg" class:rtl={$languageStore === 'ar'}>
  <div class="card-body">
    <div class="flex justify-between items-start">
      <h2 class="card-title text-xl mb-4" class:arabic={$languageStore === 'ar'}>
        {answerTitle}
      </h2>
      <CopyButton text={response.answer} label={copyAnswerLabel} size="sm" />
    </div>
    
    <div class="prose max-w-none quran-container">
      {@html formattedAnswer}
    </div>
    
    {#if response.sources && response.sources.length > 0}
      <div class="divider my-6">
        <span class:arabic={$languageStore === 'ar'}>
          {sourcesTitle}
        </span>
      </div>
      
      <div class="space-y-6">
        {#each Object.entries(groupedSources) as [sourceType, sources]}
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
              {#each sources as source}
                <div class="bg-base-200 dark:bg-base-300 p-4 rounded-lg">
                  <div class="flex justify-between items-start mb-2">
                    <span class="font-medium" class:arabic={$languageStore === 'ar'}>
                      {source.reference}
                    </span>
                    <CopyButton text={source.content} size="sm" />
                  </div>
                  <p class="whitespace-pre-line" dir={source.source_type === 'tafsir' && source.reference.includes('ar-') ? 'rtl' : ($languageStore === 'ar' ? 'rtl' : 'ltr')} 
                     class:arabic={source.source_type === 'tafsir' && source.reference.includes('ar-') || $languageStore === 'ar'}>
                    {source.content}
                  </p>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    {/if}
    
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
</style>