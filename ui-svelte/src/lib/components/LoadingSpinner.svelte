<script lang="ts">
  export let size: 'small' | 'medium' | 'large' = 'medium';
  export let className = '';
  
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };
</script>

<div class="flex items-center justify-center {className}">
  <div class="
    {sizeClasses[size]}
    border-4
    border-gray-200
    border-t-primary
    rounded-full
    animate-spin
  "></div>
</div>

<style>
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .animate-spin {
    animation: spin 1s linear infinite;
  }
</style>