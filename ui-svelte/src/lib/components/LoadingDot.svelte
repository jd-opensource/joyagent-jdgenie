<script lang="ts">
  export let className = '';
</script>

<div class="flex items-center space-x-2 {className}">
  <span class="w-4 h-4 rounded-full bg-[#acbdff] animate-dot-pulse delay-0ms"></span>
  <span class="w-4 h-4 rounded-full bg-[#acbdff] animate-dot-pulse delay-400ms"></span>
  <span class="w-4 h-4 rounded-full bg-[#acbdff] animate-dot-pulse delay-800ms"></span>
</div>

<style>
  @keyframes dot-pulse {
    0%, 100% {
      transform: scale(1);
      background-color: #acbdff;
    }
    50% {
      transform: scale(1.5);
      background-color: #4040ff;
    }
  }
  
  .animate-dot-pulse {
    animation: dot-pulse 1.5s infinite ease-in-out;
  }
</style>