<script lang="ts">
  import { slide } from "svelte/transition";
  import { appStore } from "../stores/appStore";
  import Toast from "./Toast.svelte";
  import { mcpServices } from "../services/mcpServices";

  export let visible = false;

  // Toast notification state
  let toast = { show: false, message: "", type: "info" as const };

  // API configuration state
  let apiKey = $appStore.apiKey || "";
  let mcpServerStatus = {
    retriever: false,
    generator: false,
    translation: false,
    summarizer: false,
    tafsir: false,
  };

  // Model selection options
  let modelOptions = [
    { id: "gpt-4", name: "GPT-4 (Recommended)" },
    { id: "gpt-3.5-turbo", name: "GPT-3.5 Turbo" },
    { id: "llama-3", name: "Llama 3" },
    { id: "claude-3", name: "Claude 3" },
  ];

  let selectedModel = "gpt-4";

  // Check MCP server status on component mount
  async function checkMcpServerStatus() {
    try {
      // Check retriever server
      try {
        await mcpServices.retriever.retrieveVerses("test", {});
        mcpServerStatus.retriever = true;
      } catch (error) {
        mcpServerStatus.retriever = false;
      }

      // Check generator server
      try {
        await mcpServices.generator.generateAnswer("test", ["test context"]);
        mcpServerStatus.generator = true;
      } catch (error) {
        mcpServerStatus.generator = false;
      }

      // Check other servers similarly
      // Note: In a production app, we would implement proper health check endpoints
    } catch (error) {
      console.error("Error checking MCP server status:", error);
    }
  }

  function saveApiKey() {
    if (apiKey) {
      appStore.setApiKey(apiKey);
      toast = {
        show: true,
        message: "API key saved successfully",
        type: "success",
      };
    } else {
      toast = {
        show: true,
        message: "Please enter a valid API key",
        type: "error",
      };
    }
  }

  function saveModelSelection() {
    // In a real implementation, this would update a model selection store
    toast = {
      show: true,
      message: `Model set to ${selectedModel}`,
      type: "success",
    };
  }

  function closeToast() {
    toast.show = false;
  }
</script>

{#if visible}
  <div
    class="api-config-panel bg-white dark:bg-base-200 rounded-lg shadow-lg p-6"
    transition:slide
  >
    <h2 class="text-xl font-bold mb-4 dark:text-white">API Configuration</h2>

    <!-- API Key Configuration -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2 dark:text-white">OpenAI API Key</h3>
      <div class="flex gap-2">
        <input
          type="password"
          bind:value={apiKey}
          placeholder="Enter your OpenAI API key"
          class="input input-bordered w-full"
        />
        <button class="btn btn-primary" on:click={saveApiKey}> Save </button>
      </div>
      <p class="text-sm mt-1 text-gray-600 dark:text-gray-400">
        Your API key is stored locally and never sent to our servers.
      </p>
    </div>

    <!-- Model Selection -->
    <div class="mb-6">
      <h3 class="text-lg font-semibold mb-2 dark:text-white">
        Model Selection
      </h3>
      <select bind:value={selectedModel} class="select select-bordered w-full">
        {#each modelOptions as option}
          <option value={option.id}>{option.name}</option>
        {/each}
      </select>
      <button class="btn btn-primary mt-2" on:click={saveModelSelection}>
        Apply
      </button>
    </div>

    <!-- MCP Server Status -->
    <div class="mb-4">
      <h3 class="text-lg font-semibold mb-2 dark:text-white">Server Status</h3>
      <div class="grid grid-cols-2 gap-2">
        <div class="flex items-center gap-2">
          <div
            class={`w-3 h-3 rounded-full ${mcpServerStatus.retriever ? "bg-green-500" : "bg-red-500"}`}
          ></div>
          <span class="dark:text-white">Retriever</span>
        </div>
        <div class="flex items-center gap-2">
          <div
            class={`w-3 h-3 rounded-full ${mcpServerStatus.generator ? "bg-green-500" : "bg-red-500"}`}
          ></div>
          <span class="dark:text-white">Generator</span>
        </div>
        <div class="flex items-center gap-2">
          <div
            class={`w-3 h-3 rounded-full ${mcpServerStatus.translation ? "bg-green-500" : "bg-red-500"}`}
          ></div>
          <span class="dark:text-white">Translation</span>
        </div>
        <div class="flex items-center gap-2">
          <div
            class={`w-3 h-3 rounded-full ${mcpServerStatus.summarizer ? "bg-green-500" : "bg-red-500"}`}
          ></div>
          <span class="dark:text-white">Summarizer</span>
        </div>
        <div class="flex items-center gap-2">
          <div
            class={`w-3 h-3 rounded-full ${mcpServerStatus.tafsir ? "bg-green-500" : "bg-red-500"}`}
          ></div>
          <span class="dark:text-white">Tafsir</span>
        </div>
      </div>
      <button
        class="btn btn-sm btn-outline mt-2"
        on:click={checkMcpServerStatus}
      >
        Refresh Status
      </button>
    </div>
  </div>
{/if}

{#if toast.show}
  <Toast message={toast.message} type={toast.type} on:close={closeToast} />
{/if}

<style>
  .api-config-panel {
    width: 100%;
    max-width: 500px;
    z-index: 50;
  }
</style>