<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { toastMessages, message } from '$lib/stores/message';
  
  const iconMap = {
    info: 'ℹ️',
    success: '✅',
    error: '❌',
    warning: '⚠️'
  };
  
  const bgColorMap = {
    info: 'bg-blue-500',
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500'
  };
</script>

<div class="fixed top-4 right-4 z-50 space-y-2">
  {#each $toastMessages as toast (toast.id)}
    <div
      transition:fly={{ x: 300, duration: 300 }}
      class="flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg {bgColorMap[toast.type]} text-white min-w-[300px] max-w-[500px]"
    >
      <span class="text-xl">{iconMap[toast.type]}</span>
      <span class="flex-1">{toast.message}</span>
      <button
        on:click={() => message.remove(toast.id)}
        class="ml-2 hover:opacity-80"
      >
        ✕
      </button>
    </div>
  {/each}
</div>