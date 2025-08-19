<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import hljs from 'highlight.js';
  import 'highlight.js/styles/github.css';
  
  export let content = '';
  
  let container: HTMLDivElement;
  
  // Simple markdown parser
  function parseMarkdown(text: string): string {
    // Code blocks
    text = text.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      const highlighted = lang ? hljs.highlight(code.trim(), { language: lang }).value : hljs.highlightAuto(code.trim()).value;
      return `<pre><code class="hljs language-${lang || 'plaintext'}">${highlighted}</code></pre>`;
    });
    
    // Inline code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Headers
    text = text.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    text = text.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    text = text.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Links
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    
    // Lists
    text = text.replace(/^\* (.+)$/gim, '<li>$1</li>');
    text = text.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Line breaks
    text = text.replace(/\n\n/g, '</p><p>');
    text = '<p>' + text + '</p>';
    
    // Clean up empty paragraphs
    text = text.replace(/<p><\/p>/g, '');
    
    return text;
  }
  
  function addCopyButtons() {
    if (!container) return;
    
    const codeBlocks = container.querySelectorAll('pre');
    codeBlocks.forEach(block => {
      if (block.querySelector('.copy-button')) return;
      
      const button = document.createElement('button');
      button.className = 'copy-button';
      button.textContent = '复制';
      button.onclick = () => {
        const code = block.querySelector('code')?.textContent || '';
        navigator.clipboard.writeText(code).then(() => {
          button.textContent = '已复制!';
          setTimeout(() => {
            button.textContent = '复制';
          }, 2000);
        });
      };
      
      block.style.position = 'relative';
      block.appendChild(button);
    });
  }
  
  $: htmlContent = parseMarkdown(content);
  
  afterUpdate(() => {
    addCopyButtons();
  });
</script>

<div bind:this={container} class="markdown-content">
  {@html htmlContent}
</div>

<style>
  :global(.markdown-content) {
    line-height: 1.6;
    color: #333;
  }
  
  :global(.markdown-content h1) {
    font-size: 2em;
    margin: 0.67em 0;
    font-weight: bold;
  }
  
  :global(.markdown-content h2) {
    font-size: 1.5em;
    margin: 0.75em 0;
    font-weight: bold;
  }
  
  :global(.markdown-content h3) {
    font-size: 1.17em;
    margin: 0.83em 0;
    font-weight: bold;
  }
  
  :global(.markdown-content p) {
    margin: 1em 0;
  }
  
  :global(.markdown-content code) {
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 85%;
  }
  
  :global(.markdown-content pre) {
    background-color: #f6f8fa;
    padding: 16px;
    overflow: auto;
    border-radius: 6px;
    position: relative;
  }
  
  :global(.markdown-content pre code) {
    background-color: transparent;
    padding: 0;
  }
  
  :global(.markdown-content ul) {
    list-style-type: disc;
    padding-left: 2em;
    margin: 1em 0;
  }
  
  :global(.markdown-content li) {
    margin: 0.25em 0;
  }
  
  :global(.markdown-content a) {
    color: #0366d6;
    text-decoration: none;
  }
  
  :global(.markdown-content a:hover) {
    text-decoration: underline;
  }
  
  :global(.markdown-content .copy-button) {
    position: absolute;
    top: 8px;
    right: 8px;
    padding: 4px 8px;
    font-size: 12px;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s;
  }
  
  :global(.markdown-content pre:hover .copy-button) {
    opacity: 1;
  }
  
  :global(.markdown-content .copy-button:hover) {
    background: #f3f4f6;
  }
</style>