<script lang="ts">
  import { onMount } from 'svelte';
  import MarkdownRenderer from './MarkdownRenderer.svelte';
  import LoadingDot from './LoadingDot.svelte';
  import '$lib/types/chat';
  
  export let chat: CHAT.ChatItem;
  
  let expanded = false;
  
  function toggleExpand() {
    expanded = !expanded;
  }
  
  function copyToClipboard(text: string) {
    navigator.clipboard.writeText(text).then(() => {
      // Show success message
      const event = new CustomEvent('toast', { 
        detail: { type: 'success', message: '复制成功' } 
      });
      window.dispatchEvent(event);
    });
  }
</script>

<div class="mb-24">
  <!-- User Message -->
  <div class="flex gap-12 mb-16">
    <div class="w-32 h-32 rounded-full bg-blue-500 flex items-center justify-center text-white font-semibold">
      U
    </div>
    <div class="flex-1">
      <div class="text-gray-800 whitespace-pre-wrap">{chat.query}</div>
      {#if chat.files && chat.files.length > 0}
        <div class="mt-8 flex flex-wrap gap-8">
          {#each chat.files as file}
            <div class="px-8 py-4 bg-gray-100 rounded text-sm text-gray-600">
              📎 {file.name}
            </div>
          {/each}
        </div>
      {/if}
    </div>
  </div>
  
  <!-- Assistant Response -->
  <div class="flex gap-12">
    <div class="w-32 h-32 rounded-full bg-primary flex items-center justify-center text-white font-semibold">
      AI
    </div>
    <div class="flex-1">
      {#if chat.loading}
        <div class="flex items-center gap-8">
          <LoadingDot />
          <span class="text-gray-500 text-sm">{chat.tip || '正在思考...'}</span>
        </div>
      {:else if chat.forceStop}
        <div class="text-gray-500 italic">生成已停止</div>
      {:else if chat.response}
        <div class="relative group">
          <div class="markdown-body">
            <MarkdownRenderer content={chat.response} />
          </div>
          
          <!-- Copy Button -->
          <button
            on:click={() => copyToClipboard(chat.response)}
            class="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity
              p-2 bg-white rounded shadow-md hover:shadow-lg"
            title="复制"
          >
            📋
          </button>
        </div>
        
        <!-- Thought Process -->
        {#if chat.thought}
          <div class="mt-12">
            <button
              on:click={toggleExpand}
              class="flex items-center gap-4 text-sm text-gray-500 hover:text-gray-700"
            >
              <span class="transform transition-transform {expanded ? 'rotate-90' : ''}">
                ▶
              </span>
              思考过程
            </button>
            {#if expanded}
              <div class="mt-8 p-12 bg-gray-50 rounded-lg text-sm text-gray-600 whitespace-pre-wrap">
                {chat.thought}
              </div>
            {/if}
          </div>
        {/if}
        
        <!-- Tasks -->
        {#if chat.tasks && chat.tasks.length > 0}
          <div class="mt-12">
            <h4 class="text-sm font-semibold text-gray-700 mb-8">执行任务</h4>
            <div class="space-y-4">
              {#each chat.tasks as task}
                <div class="flex items-center gap-8 text-sm">
                  <span class="{task.status === 'completed' ? 'text-green-500' : task.status === 'failed' ? 'text-red-500' : 'text-gray-400'}">
                    {task.status === 'completed' ? '✓' : task.status === 'failed' ? '✗' : '○'}
                  </span>
                  <span class="{task.status === 'completed' ? 'line-through text-gray-400' : ''}">
                    {task.name}
                  </span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      {:else}
        <div class="text-gray-400 italic">无响应内容</div>
      {/if}
    </div>
  </div>
</div>