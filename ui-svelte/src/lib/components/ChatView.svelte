<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getUniqId, getSessionId, scrollToTop } from '$lib/utils/utils';
  import querySSE from '$lib/services/querySSE';
  import { handleTaskData, combineData } from '$lib/utils/chat';
  import Dialogue from './Dialogue.svelte';
  import GeneralInput from './GeneralInput.svelte';
  import ActionView from './ActionView.svelte';
  import Logo from './Logo.svelte';
  import { message } from '$lib/stores/message';
  import '$lib/types/chat';
  import '$lib/types/message';
  
  export let inputInfo: CHAT.TInputInfo;
  export let product: CHAT.Product | undefined;
  
  let chatTitle = '';
  let taskList: MESSAGE.Task[] = [];
  let chatList: CHAT.ChatItem[] = [];
  let activeTask: CHAT.Task | undefined;
  let plan: CHAT.Plan | undefined;
  let showAction = false;
  let loading = false;
  let chatContainer: HTMLDivElement;
  let sessionId = getSessionId();
  let sseController: AbortController | null = null;
  
  function combineCurrentChat(
    inputInfo: CHAT.TInputInfo,
    sessionId: string,
    requestId: string
  ): CHAT.ChatItem {
    return {
      query: inputInfo.message!,
      files: inputInfo.files!,
      responseType: 'txt',
      sessionId,
      requestId,
      loading: true,
      forceStop: false,
      tasks: [],
      thought: '',
      response: '',
      taskStatus: 0,
      tip: '已接收到你的任务，将立即开始处理...',
      multiAgent: { tasks: [] },
    };
  }
  
  function sendMessage(inputInfo: CHAT.TInputInfo) {
    const { message: msg, deepThink, outputStyle } = inputInfo;
    const requestId = getUniqId();
    let currentChat = combineCurrentChat(inputInfo, sessionId, requestId);
    chatList = [...chatList, currentChat];
    
    if (!chatTitle) {
      chatTitle = msg!;
    }
    
    loading = true;
    
    const params = {
      sessionId: sessionId,
      requestId: requestId,
      query: msg,
      deepThink: deepThink ? 1 : 0,
      outputStyle
    };
    
    const handleMessage = (data: MESSAGE.Answer) => {
      const { finished, resultMap, packageType, status } = data;
      
      if (status === 'tokenUseUp') {
        message.info('您的试用次数已用尽，如需额外申请，请联系管理员');
        const taskData = handleTaskData(currentChat);
        currentChat = { ...currentChat, ...taskData, loading: false };
        updateCurrentChat(currentChat);
        loading = false;
        return;
      }
      
      if (finished === 1) {
        const taskData = handleTaskData(currentChat);
        currentChat = { ...currentChat, ...taskData, loading: false };
        updateCurrentChat(currentChat);
        loading = false;
        taskList = [];
      } else {
        const eventData = resultMap;
        if (packageType === 'incr') {
          combineData(eventData, currentChat);
          updateCurrentChat(currentChat);
        }
      }
    };
    
    const handleError = (error: Error) => {
      console.error('SSE Error:', error);
      message.error('连接错误，请稍后重试');
      loading = false;
      currentChat.loading = false;
      updateCurrentChat(currentChat);
    };
    
    const handleClose = () => {
      console.log('SSE connection closed');
      loading = false;
    };
    
    sseController = querySSE({
      body: params,
      handleMessage,
      handleError,
      handleClose
    });
  }
  
  function updateCurrentChat(chat: CHAT.ChatItem) {
    const index = chatList.findIndex(c => c.requestId === chat.requestId);
    if (index >= 0) {
      chatList[index] = chat;
      chatList = [...chatList];
    }
  }
  
  function stopGeneration() {
    if (sseController) {
      sseController.abort();
      sseController = null;
    }
    loading = false;
    if (chatList.length > 0) {
      const lastChat = chatList[chatList.length - 1];
      lastChat.loading = false;
      lastChat.forceStop = true;
      updateCurrentChat(lastChat);
    }
  }
  
  // Send initial message if provided
  $: if (inputInfo.message) {
    sendMessage(inputInfo);
  }
  
  onDestroy(() => {
    if (sseController) {
      sseController.abort();
    }
  });
</script>

<div class="flex flex-col h-full bg-gray-50">
  <!-- Header -->
  <div class="flex items-center justify-between px-24 py-16 bg-white border-b border-gray-200">
    <div class="flex items-center gap-12">
      <Logo className="w-32 h-32" />
      <h1 class="text-lg font-semibold text-gray-800">{chatTitle || 'New Chat'}</h1>
    </div>
    {#if showAction}
      <button
        on:click={() => showAction = !showAction}
        class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
      >
        {showAction ? '隐藏' : '显示'}操作面板
      </button>
    {/if}
  </div>
  
  <!-- Chat Container -->
  <div 
    bind:this={chatContainer}
    class="flex-1 overflow-y-auto px-24 py-16"
  >
    {#each chatList as chat}
      <Dialogue {chat} />
    {/each}
    
    {#if loading}
      <div class="flex items-center gap-8 text-gray-500 mt-16">
        <div class="animate-spin w-16 h-16 border-2 border-gray-300 border-t-primary rounded-full"></div>
        <span>正在生成回复...</span>
        <button
          on:click={stopGeneration}
          class="ml-auto px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600"
        >
          停止生成
        </button>
      </div>
    {/if}
  </div>
  
  <!-- Input Area -->
  <div class="px-24 py-16 bg-white border-t border-gray-200">
    <GeneralInput
      placeholder="继续对话..."
      showBtn={true}
      size="small"
      disabled={loading}
      {product}
      send={sendMessage}
    />
  </div>
  
  <!-- Action Panel -->
  {#if showAction}
    <ActionView {activeTask} {plan} />
  {/if}
</div>