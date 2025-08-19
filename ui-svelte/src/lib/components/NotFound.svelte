<script lang="ts">
  import { goto } from '$app/navigation';
  
  export let className = '';
</script>

<div class="flex flex-col items-center justify-center min-h-screen {className}">
  <div class="text-center">
    <h1 class="text-9xl font-bold text-gray-300">404</h1>
    <h2 class="text-2xl font-semibold text-gray-700 mt-4">Page Not Found</h2>
    <p class="text-gray-500 mt-2">The page you are looking for doesn't exist.</p>
    <button
      on:click={() => goto('/')}
      class="mt-6 px-6 py-3 bg-primary text-white rounded-lg hover:bg-opacity-90 transition-all"
    >
      Go Home
    </button>
  </div>
</div>