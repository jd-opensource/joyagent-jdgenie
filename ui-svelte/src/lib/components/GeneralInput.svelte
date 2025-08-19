<script lang="ts">
  import { onMount } from 'svelte';
  import AttachmentList from './AttachmentList.svelte';
  import { getOS } from '$lib/utils/utils';
  import '$lib/types/chat';
  
  export let placeholder = 'Enter your message...';
  export let showBtn = true;
  export let disabled = false;
  export let size: 'small' | 'big' = 'small';
  export let product: CHAT.Product | undefined = undefined;
  export let send: (info: CHAT.TInputInfo) => void = () => {};
  export let className = '';
  
  let question = '';
  let deepThink = false;
  let files: File[] = [];
  let textarea: HTMLTextAreaElement;
  let fileInput: HTMLInputElement;
  let isComposing = false;
  let cmdPressed = false;
  
  const enterTip = `⏎发送，${getOS() === 'Mac' ? '⌘' : '^'} + ⏎ 换行`;
  
  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Meta' || e.key === 'Control') {
      cmdPressed = true;
    }
    
    if (e.key === 'Enter' && !isComposing) {
      if (cmdPressed) {
        // Insert newline
        e.preventDefault();
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const newValue = question.substring(0, start) + '\n' + question.substring(end);
        question = newValue;
        setTimeout(() => {
          textarea.selectionStart = textarea.selectionEnd = start + 1;
          textarea.focus();
        }, 0);
      } else if (question && !disabled) {
        // Send message
        e.preventDefault();
        sendMessage();
      }
    }
  }
  
  function handleKeyUp(e: KeyboardEvent) {
    if (e.key === 'Meta' || e.key === 'Control') {
      cmdPressed = false;
    }
  }
  
  function sendMessage() {
    if (!question || disabled) return;
    
    send({
      message: question,
      outputStyle: product?.type,
      deepThink,
      files
    });
    
    question = '';
    files = [];
    deepThink = false;
  }
  
  function handleFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files) {
      files = [...files, ...Array.from(target.files)];
    }
    target.value = '';
  }
  
  function removeFile(index: number) {
    files = files.filter((_, i) => i !== index);
  }
  
  function toggleDeepThink() {
    deepThink = !deepThink;
  }
  
  onMount(() => {
    textarea?.focus();
  });
</script>

<div class={showBtn ? 'rounded-[12px] bg-gradient-to-br from-[#4040ff] via-[#ff49fd] via-[#d763fc] to-[#3cc4fa] p-1' : ''}>
  <div class="rounded-[12px] border border-[#E9E9F0] overflow-hidden p-12 bg-white {className}">
    <div class="relative">
      <textarea
        bind:this={textarea}
        bind:value={question}
        {placeholder}
        {disabled}
        on:keydown={handleKeyDown}
        on:keyup={handleKeyUp}
        on:compositionstart={() => isComposing = true}
        on:compositionend={() => isComposing = false}
        class="w-full h-62 border-0 resize-none p-0 focus:outline-none bg-white
          {size === 'big' ? 'text-base' : 'text-sm'}
          {disabled ? 'cursor-not-allowed opacity-50' : ''}"
      ></textarea>
      
      <AttachmentList {files} onRemove={removeFile} />
      
      <div class="flex items-center justify-between mt-8">
        <div class="flex items-center gap-4">
          <button
            on:click={() => fileInput?.click()}
            {disabled}
            class="p-2 rounded hover:bg-gray-100 transition-colors
              {disabled ? 'cursor-not-allowed opacity-50' : ''}"
            title="Attach files"
          >
            <i class="font_family icon-paperclip text-[#666]"></i>
          </button>
          
          <button
            on:click={toggleDeepThink}
            {disabled}
            class="flex items-center gap-2 px-3 py-1 rounded-full transition-colors
              {deepThink ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600'}
              {disabled ? 'cursor-not-allowed opacity-50' : ''}"
          >
            <i class="font_family icon-brain"></i>
            <span class="text-xs">深度思考</span>
          </button>
        </div>
        
        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-400">{enterTip}</span>
          {#if showBtn}
            <button
              on:click={sendMessage}
              disabled={!question || disabled}
              class="px-4 py-2 rounded-lg bg-primary text-white transition-all
                {!question || disabled ? 'opacity-50 cursor-not-allowed' : 'hover:opacity-90'}"
            >
              发送
            </button>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>

<input
  bind:this={fileInput}
  type="file"
  multiple
  on:change={handleFileSelect}
  class="hidden"
/>