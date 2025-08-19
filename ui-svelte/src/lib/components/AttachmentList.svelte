<script lang="ts">
  export let files: File[] = [];
  export let onRemove: (index: number) => void = () => {};
  export let className = '';
  
  function getFileIcon(file: File): string {
    const ext = file.name.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf': return '📄';
      case 'doc':
      case 'docx': return '📝';
      case 'xls':
      case 'xlsx': return '📊';
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif': return '🖼️';
      case 'txt': return '📃';
      case 'csv': return '📈';
      case 'html': return '🌐';
      default: return '📎';
    }
  }
  
  function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
</script>

{#if files.length > 0}
  <div class="flex flex-wrap gap-2 p-2 border-t border-gray-200 {className}">
    {#each files as file, index}
      <div class="flex items-center gap-2 px-3 py-1 bg-gray-50 rounded-lg">
        <span class="text-lg">{getFileIcon(file)}</span>
        <div class="flex flex-col">
          <span class="text-sm font-medium text-gray-700 max-w-[200px] truncate">
            {file.name}
          </span>
          <span class="text-xs text-gray-500">
            {formatFileSize(file.size)}
          </span>
        </div>
        <button
          on:click={() => onRemove(index)}
          class="ml-2 text-gray-400 hover:text-gray-600"
        >
          ✕
        </button>
      </div>
    {/each}
  </div>
{/if}