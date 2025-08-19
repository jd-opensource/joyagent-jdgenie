<script lang="ts">
  import { onMount } from 'svelte';
  import GeneralInput from '$lib/components/GeneralInput.svelte';
  import Slogn from '$lib/components/Slogn.svelte';
  import ChatView from '$lib/components/ChatView.svelte';
  import { productList, defaultProduct } from '$lib/utils/constants';
  import { inputInfo, selectedProduct } from '$lib/stores/chat';
  import '$lib/types/chat';
  
  let currentProduct = defaultProduct;
  let videoModalOpen: string | undefined;
  let showChat = false;
  
  selectedProduct.set(defaultProduct);
  
  function changeInputInfo(info: CHAT.TInputInfo) {
    inputInfo.set(info);
    if (info.message) {
      showChat = true;
    }
  }
  
  function selectProduct(product: CHAT.Product) {
    currentProduct = product;
    selectedProduct.set(product);
  }
  
  $: if ($inputInfo.message) {
    showChat = true;
  }
</script>

<div class="h-full overflow-auto bg-gradient-to-b from-white to-gray-50">
  {#if !showChat}
    <div class="pt-120 flex flex-col items-center">
      <Slogn />
      <div class="w-640 rounded-xl shadow-[0_18px_39px_0_rgba(198,202,240,0.1)]">
        <GeneralInput
          placeholder={currentProduct.placeholder}
          showBtn={true}
          size="big"
          disabled={false}
          product={currentProduct}
          send={changeInputInfo}
        />
      </div>
      
      <div class="w-640 flex flex-wrap gap-16 mt-16">
        {#each productList as item}
          <button
            on:click={() => selectProduct(item)}
            class="w-[22%] h-36 cursor-pointer flex items-center justify-center border rounded-[8px] transition-all
              {item.type === currentProduct.type 
                ? 'border-[#4040ff] bg-[rgba(64,64,255,0.02)] text-[#4040ff]' 
                : 'border-[#E9E9F0] text-[#666] hover:border-gray-300'}"
          >
            <i class="font_family {item.img} {item.color}"></i>
            <div class="ml-6">{item.name}</div>
          </button>
        {/each}
      </div>
    </div>
  {:else}
    <ChatView inputInfo={$inputInfo} product={currentProduct} />
  {/if}
</div>