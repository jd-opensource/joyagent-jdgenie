<script lang="ts">
  import LoadingSpinner from './LoadingSpinner.svelte';
  
  export let loading = false;
  export let className = '';
  export let text = 'Loading...';
  export let size: 'small' | 'medium' | 'large' = 'medium';
</script>

{#if loading}
  <div class="flex flex-col items-center justify-center gap-4 {className}">
    <LoadingSpinner {size} />
    {#if text}
      <span class="text-gray-600 text-sm">{text}</span>
    {/if}
  </div>
{/if}