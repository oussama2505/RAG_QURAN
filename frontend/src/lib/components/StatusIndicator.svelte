<script lang="ts">
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
</script>

{#if status !== 'idle' || message}
  <div class="status-indicator {statusClass} text-sm p-3 rounded-lg shadow-sm flex items-center gap-2 my-2">
    <span class="status-icon">{statusIcon}</span>
    <span class="status-message">{message || getDefaultMessage(status)}</span>
    
    {#if status === 'loading'}
      <span class="loading loading-dots loading-sm ml-auto"></span>
    {/if}
  </div>
{/if}

<script context="module" lang="ts">
  function getDefaultMessage(status: string): string {
    switch (status) {
      case 'loading':
        return 'Processing your request...';
      case 'success':
        return 'Request completed successfully';
      case 'error':
        return 'An error occurred';
      default:
        return '';
    }
  }
</script>

<style>
  .status-indicator {
    transition: all 0.3s ease;
  }
  
  .status-message {
    flex: 1;
  }
</style>