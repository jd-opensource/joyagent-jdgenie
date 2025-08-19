<script lang="ts">
  import logoImage from './logo.png';
  
  export let className = '';
</script>

<div class="flex items-center {className}">
  <img src={logoImage} alt="Logo" class="w-32 h-32" />
</div>