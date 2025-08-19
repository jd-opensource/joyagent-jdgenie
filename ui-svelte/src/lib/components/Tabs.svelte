<script lang="ts">
  export let tabs: Array<{ key: string; label: string }> = [];
  export let activeKey = '';
  export let className = '';
  export let onChange: (key: string) => void = () => {};
</script>

<div class="flex border-b border-gray-200 {className}">
  {#each tabs as tab}
    <button
      class="px-4 py-2 text-sm font-medium transition-colors
        {activeKey === tab.key 
          ? 'text-primary border-b-2 border-primary' 
          : 'text-gray-600 hover:text-gray-800'}"
      on:click={() => {
        activeKey = tab.key;
        onChange(tab.key);
      }}
    >
      {tab.label}
    </button>
  {/each}
</div>