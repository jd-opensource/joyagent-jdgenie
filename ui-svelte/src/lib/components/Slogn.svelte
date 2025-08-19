<script lang="ts">
  import { onMount } from 'svelte';
  import lottie from 'lottie-web';
  import { animationData } from './animation';
  
  let animationContainer: HTMLDivElement;
  
  onMount(() => {
    const animation = lottie.loadAnimation({
      container: animationContainer,
      renderer: 'svg',
      loop: true,
      autoplay: true,
      animationData: animationData
    });
    
    return () => {
      animation.destroy();
    };
  });
</script>

<div class="mb-54">
  <div 
    bind:this={animationContainer}
    class="lottie"
    style="width: 200px; height: 68px;"
  ></div>
</div>