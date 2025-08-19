<script lang="ts">
  import '../app.css';
  import '../assets/styles/common.css';
  import '../assets/styles/RelayIcon.css';
  import '../assets/styles/github-markdown.css';
  import Toast from '$lib/components/Toast.svelte';
  import { onMount } from 'svelte';
  import { setMessage } from '$lib/utils/utils';
  import { messageApi } from '$lib/stores/message';
  import { constantsStore } from '$lib/stores/constants';
  import { setContext } from 'svelte';
  
  // Set up global message handler
  onMount(() => {
    setMessage(messageApi);
  });
  
  // Provide constants through context
  setContext('constants', constantsStore);
</script>

<Toast />
<div class="h-full">
  <slot />
</div>