<script lang="ts">
  export let size = 'md';
  
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };
</script>

<div class="loading-container" role="status">
  <div class={`spinner ${sizeClasses[size]}`}>
    <div class="inner-spinner"></div>
  </div>
  <span class="sr-only">Loading...</span>
</div>

<style>
  .loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .spinner {
    position: relative;
    border: 4px solid theme('colors.primary');
    border-radius: 50%;
    animation: spin 3s linear infinite;
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .inner-spinner {
    position: absolute;
    width: 70%;
    height: 70%;
    border: 4px solid theme('colors.secondary');
    border-radius: 50%;
    animation: spin-reverse 2s linear infinite;
  }

  .inner-spinner::after {
    content: '☪️';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  @keyframes spin-reverse {
    0% { transform: rotate(360deg); }
    100% { transform: rotate(0deg); }
  }
</style>