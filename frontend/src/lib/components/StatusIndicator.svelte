<script lang="ts">
  import { languageStore } from '../stores/languageStore';
  
  export let status: 'idle' | 'loading' | 'success' | 'error' = 'idle';
  export let message: string = '';
  
  $: statusClass = {
    idle: 'bg-base-200',
    loading: 'bg-info',
    success: 'bg-success',
    error: 'bg-error'
  }[status];
  
  $: statusIcon = {
    idle: '⏸️',
    loading: '⏳',
    success: '✅',
    error: '❌'
  }[status];
  
  // Get default messages in the current language
  function getDefaultMessage(status: string): string {
    const messages = {
      loading: {
        en: 'Processing your request...',
        ar: 'جاري معالجة طلبك...',
        es: 'Procesando su solicitud...'
      },
      success: {
        en: 'Request completed successfully',
        ar: 'تم إكمال الطلب بنجاح',
        es: 'Solicitud completada con éxito'
      },
      error: {
        en: 'An error occurred',
        ar: 'حدث خطأ',
        es: 'Se produjo un error'
      },
      idle: {
        en: '',
        ar: '',
        es: ''
      }
    };
    
    return messages[status as keyof typeof messages][$languageStore];
  }
</script>

{#if status !== 'idle' || message}
  <div class="status-indicator {statusClass} text-sm p-3 rounded-lg shadow-sm flex items-center gap-2 my-2"
       class:rtl={$languageStore === 'ar'}>
    <span class="status-icon">{statusIcon}</span>
    <span class="status-message" class:arabic={$languageStore === 'ar'}>
      {message || getDefaultMessage(status)}
    </span>
    
    {#if status === 'loading'}
      <span class="loading loading-dots loading-sm ml-auto"></span>
    {/if}
  </div>
{/if}

<style>
  .status-indicator {
    transition: all 0.3s ease;
  }
  
  .status-message {
    flex: 1;
  }
  
  .rtl {
    direction: rtl;
    text-align: right;
  }
</style>