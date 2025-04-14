<script lang="ts">
  import { slide } from 'svelte/transition';
  import { appStore } from '../stores/appStore';
  import Toast from './Toast.svelte';

  export let visible = false;
  
  let toast = { show: false, message: '', type: 'info' as const };
  let confirmClearVisible = false;

  function clearRecentQuestions() {
    appStore.clearRecentQuestions();
    toast = {
      show: true,
      message: 'Recent questions cleared',
      type: 'success'
    };
    confirmClearVisible = false;
  }

  function clearAPIKey() {
    appStore.setApiKey('');
    toast = {
      show: true,
      message: 'API key removed',
      type: 'success'
    };
  }

  function closeToast() {
    toast.show = false;
  }
</script>

{#if visible}
  <div 
    class="settings bg-white rounded-lg shadow-lg p-6"
    transition:slide
  >
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-neutral">Settings</h3>
      <div class="space-x-2">
        {#if $appStore.apiKey}
          <button
            class="btn btn-ghost btn-sm text-error"
            on:click={clearAPIKey}
          >
            Remove API Key
          </button>
        {/if}
        {#if $appStore.recentQuestions.length > 0}
          <button
            class="btn btn-ghost btn-sm"
            on:click={() => confirmClearVisible = true}
          >
            Clear History
          </button>
        {/if}
      </div>
    </div>

    <!-- Confirmation Dialog -->
    {#if confirmClearVisible}
      <div class="confirmation-dialog bg-base-200 rounded-lg p-4 mb-4">
        <p class="text-sm mb-4">Are you sure you want to clear all recent questions?</p>
        <div class="flex justify-end space-x-2">
          <button
            class="btn btn-ghost btn-sm"
            on:click={() => confirmClearVisible = false}
          >
            Cancel
          </button>
          <button
            class="btn btn-error btn-sm"
            on:click={clearRecentQuestions}
          >
            Clear
          </button>
        </div>
      </div>
    {/if}

    <!-- Settings Content -->
    <div class="space-y-4">
      <!-- API Key Status -->
      <div class="flex items-center justify-between p-3 bg-base-100 rounded-lg">
        <div>
          <h4 class="font-medium text-neutral">API Key Status</h4>
          <p class="text-sm text-neutral-600">
            {$appStore.apiKey ? 'API key is set' : 'No API key set'}
          </p>
        </div>
        <div class="badge {$appStore.apiKey ? 'badge-success' : 'badge-warning'}">
          {$appStore.apiKey ? 'Active' : 'Missing'}
        </div>
      </div>

      <!-- Recent Questions Stats -->
      <div class="flex items-center justify-between p-3 bg-base-100 rounded-lg">
        <div>
          <h4 class="font-medium text-neutral">Question History</h4>
          <p class="text-sm text-neutral-600">
            {$appStore.recentQuestions.length} recent questions
          </p>
        </div>
      </div>
    </div>
  </div>
{/if}

{#if toast.show}
  <Toast 
    message={toast.message}
    type={toast.type}
    onClose={closeToast}
  />
{/if}