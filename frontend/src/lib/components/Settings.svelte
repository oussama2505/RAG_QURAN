<script lang="ts">
  import { slide } from 'svelte/transition';
  import { appStore } from '../stores/appStore';
  import { languageStore, type Language } from '../stores/languageStore';
  import Toast from './Toast.svelte';

  export let visible = false;
  
  let toast = { show: false, message: '', type: 'info' as const };
  let confirmClearVisible = false;
  
  // Get current language
  let currentLanguage: Language;
  languageStore.subscribe(value => {
    currentLanguage = value;
  });

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
  
  function setLanguage(lang: Language) {
    languageStore.setLanguage(lang);
  }

  function closeToast() {
    toast.show = false;
  }
</script>

{#if visible}
  <div 
    class="settings bg-white dark:bg-base-200 rounded-lg shadow-lg p-6"
    transition:slide
  >
    <div class="flex items-center justify-between mb-6">
      <h3 class="text-lg font-semibold text-neutral dark:text-neutral-content">{$languageStore === 'en' ? 'Settings' : $languageStore === 'ar' ? 'الإعدادات' : 'Configuración'}</h3>
      <div class="space-x-2">
        {#if $appStore.apiKey}
          <button
            class="btn btn-ghost btn-sm text-error"
            on:click={clearAPIKey}
          >
            {$languageStore === 'en' ? 'Remove API Key' : $languageStore === 'ar' ? 'إزالة مفتاح API' : 'Eliminar clave API'}
          </button>
        {/if}
        {#if $appStore.recentQuestions.length > 0}
          <button
            class="btn btn-ghost btn-sm"
            on:click={() => confirmClearVisible = true}
          >
            {$languageStore === 'en' ? 'Clear History' : $languageStore === 'ar' ? 'مسح التاريخ' : 'Borrar historial'}
          </button>
        {/if}
      </div>
    </div>

    <!-- Confirmation Dialog -->
    {#if confirmClearVisible}
      <div class="confirmation-dialog bg-base-200 dark:bg-base-300 rounded-lg p-4 mb-4">
        <p class="text-sm mb-4">
          {$languageStore === 'en' 
            ? 'Are you sure you want to clear all recent questions?' 
            : $languageStore === 'ar' 
            ? 'هل أنت متأكد أنك تريد مسح جميع الأسئلة الأخيرة؟' 
            : '¿Estás seguro de que deseas borrar todas las preguntas recientes?'}
        </p>
        <div class="flex justify-end space-x-2">
          <button
            class="btn btn-ghost btn-sm"
            on:click={() => confirmClearVisible = false}
          >
            {$languageStore === 'en' ? 'Cancel' : $languageStore === 'ar' ? 'إلغاء' : 'Cancelar'}
          </button>
          <button
            class="btn btn-error btn-sm"
            on:click={clearRecentQuestions}
          >
            {$languageStore === 'en' ? 'Clear' : $languageStore === 'ar' ? 'مسح' : 'Borrar'}
          </button>
        </div>
      </div>
    {/if}

    <!-- Settings Content -->
    <div class="space-y-4">
      <!-- Language Selector -->
      <div class="p-3 bg-base-100 dark:bg-base-300 rounded-lg">
        <h4 class="font-medium text-neutral dark:text-neutral-content mb-2">
          {$languageStore === 'en' ? 'Language' : $languageStore === 'ar' ? 'اللغة' : 'Idioma'}
        </h4>
        <div class="flex flex-wrap gap-2">
          <button 
            class="btn btn-sm {$languageStore === 'en' ? 'btn-primary' : 'btn-outline'}"
            on:click={() => setLanguage('en')}
          >
            English
          </button>
          <button 
            class="btn btn-sm {$languageStore === 'ar' ? 'btn-primary' : 'btn-outline'}"
            on:click={() => setLanguage('ar')}
          >
            العربية
          </button>
          <button 
            class="btn btn-sm {$languageStore === 'es' ? 'btn-primary' : 'btn-outline'}"
            on:click={() => setLanguage('es')}
          >
            Español
          </button>
        </div>
      </div>
      
      <!-- API Key Status -->
      <div class="flex items-center justify-between p-3 bg-base-100 dark:bg-base-300 rounded-lg">
        <div>
          <h4 class="font-medium text-neutral dark:text-neutral-content">
            {$languageStore === 'en' ? 'API Key Status' : $languageStore === 'ar' ? 'حالة مفتاح API' : 'Estado de clave API'}
          </h4>
          <p class="text-sm text-neutral-600 dark:text-neutral-300">
            {$appStore.apiKey 
              ? ($languageStore === 'en' ? 'API key is set' : $languageStore === 'ar' ? 'تم تعيين مفتاح API' : 'Clave API configurada') 
              : ($languageStore === 'en' ? 'No API key set' : $languageStore === 'ar' ? 'لم يتم تعيين مفتاح API' : 'No hay clave API configurada')}
          </p>
        </div>
        <div class="badge {$appStore.apiKey ? 'badge-success' : 'badge-warning'}">
          {$appStore.apiKey 
            ? ($languageStore === 'en' ? 'Active' : $languageStore === 'ar' ? 'نشط' : 'Activo') 
            : ($languageStore === 'en' ? 'Missing' : $languageStore === 'ar' ? 'مفقود' : 'Faltante')}
        </div>
      </div>

      <!-- Recent Questions Stats -->
      <div class="flex items-center justify-between p-3 bg-base-100 dark:bg-base-300 rounded-lg">
        <div>
          <h4 class="font-medium text-neutral dark:text-neutral-content">
            {$languageStore === 'en' ? 'Question History' : $languageStore === 'ar' ? 'سجل الأسئلة' : 'Historial de preguntas'}
          </h4>
          <p class="text-sm text-neutral-600 dark:text-neutral-300">
            {$appStore.recentQuestions.length} 
            {$languageStore === 'en' 
              ? 'recent questions' 
              : $languageStore === 'ar' 
              ? 'أسئلة حديثة' 
              : 'preguntas recientes'}
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