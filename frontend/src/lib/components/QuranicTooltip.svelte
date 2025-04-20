<script lang="ts">
  import { onMount } from "svelte";

  export let term: string;
  export let definition: string;
  export let position: "top" | "bottom" | "left" | "right" = "top";

  let tooltipElement: HTMLElement;
  let isVisible = false;

  const quranicTerms: Record<string, string> = {
    Allah: "The One and Only God in Islam",
    Rahman: "The Most Gracious",
    Raheem: "The Most Merciful",
    Surah: "A chapter of the Quran",
    Ayah: "A verse of the Quran",
    Tafsir: "Explanation or interpretation of the Quran",
    Hadith: "Sayings and actions of the Prophet Muhammad",
    Sunnah: "The way of life prescribed as normative for Muslims",
    Iman: "Faith or belief in Islamic theology",
    Taqwa: "God-consciousness or piety",
    Zakat: "Charitable giving in Islam",
    Salah: "Islamic prayer",
    Sawm: "Fasting during Ramadan",
    Hajj: "Pilgrimage to Mecca",
    Shahada: "Islamic declaration of faith",
    Jannah: "Paradise in Islam",
    Jahannam: "Hell in Islam",
    Qiyamah: "The Day of Resurrection",
    Malaikah: "Angels in Islam",
    Jinn: "Supernatural creatures in Islamic mythology",
  };

  function showTooltip() {
    isVisible = true;
  }

  function hideTooltip() {
    isVisible = false;
  }

  function getDefinition(term: string): string {
    return quranicTerms[term] || "No definition available";
  }
</script>

<div
  class="tooltip-container"
  on:mouseenter={showTooltip}
  on:mouseleave={hideTooltip}
>
  <slot />
  {#if isVisible}
    <div class="tooltip {position}" bind:this={tooltipElement}>
      <div class="term">{term}</div>
      <div class="definition">{getDefinition(term)}</div>
    </div>
  {/if}
</div>

<style>
  .tooltip-container {
    position: relative;
    display: inline-block;
  }

  .tooltip {
    position: absolute;
    padding: 0.5rem;
    background: var(--surface-color);
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    max-width: 200px;
    z-index: 1000;
  }

  .tooltip.top {
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    margin-bottom: 0.5rem;
  }

  .tooltip.bottom {
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    margin-top: 0.5rem;
  }

  .tooltip.left {
    right: 100%;
    top: 50%;
    transform: translateY(-50%);
    margin-right: 0.5rem;
  }

  .tooltip.right {
    left: 100%;
    top: 50%;
    transform: translateY(-50%);
    margin-left: 0.5rem;
  }

  .term {
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: 0.25rem;
  }

  .definition {
    font-size: 0.875rem;
    color: var(--text-color);
    line-height: 1.4;
  }
</style>
