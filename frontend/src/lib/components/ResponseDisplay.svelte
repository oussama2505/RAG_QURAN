<script lang="ts">
  import { marked } from 'marked';
  import type { Source } from '../stores/appStore';
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
</script>

<div class="card bg-base-100 shadow-lg">
  <div class="card-body">
    <div class="flex justify-between items-start">
      <h2 class="card-title text-xl mb-4">Answer</h2>
      <CopyButton text={response.answer} label="Copy answer" size="sm" />
    </div>
    
    <div class="prose max-w-none">
      {@html formattedAnswer}
    </div>
    
    {#if response.sources && response.sources.length > 0}
      <div class="divider my-6">Sources</div>
      
      <div class="space-y-6">
        {#each Object.entries(groupedSources) as [sourceType, sources]}
          <div>
            <h3 class="text-lg font-semibold mb-2 capitalize">
              {sourceType.replace('_', ' ')}
            </h3>
            
            <div class="space-y-4">
              {#each sources as source}
                <div class="bg-base-200 p-4 rounded-lg">
                  <div class="flex justify-between items-start mb-2">
                    <span class="font-medium">{source.reference}</span>
                    <CopyButton text={source.content} size="sm" />
                  </div>
                  <p class="whitespace-pre-line">{source.content}</p>
                </div>
              {/each}
            </div>
          </div>
        {/each}
      </div>
    {/if}
    
    {#if response.filters_applied && (response.filters_applied.surah_filter || response.filters_applied.verse_filter)}
      <div class="mt-4 text-sm text-neutral-500">
        <p>
          Filters applied: 
          {#if response.filters_applied.surah_filter}
            Surah {response.filters_applied.surah_filter}
          {/if}
          {#if response.filters_applied.verse_filter}
            {#if response.filters_applied.surah_filter}, {/if}
            Verse {response.filters_applied.verse_filter}
          {/if}
        </p>
      </div>
    {/if}
  </div>
</div>