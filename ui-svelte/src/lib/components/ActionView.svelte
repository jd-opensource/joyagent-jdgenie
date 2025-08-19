<script lang="ts">
  import '$lib/types/chat';
  
  export let activeTask: CHAT.Task | undefined;
  export let plan: CHAT.Plan | undefined;
</script>

<div class="fixed right-0 top-0 h-full w-400 bg-white shadow-lg border-l border-gray-200 overflow-y-auto">
  <div class="p-16">
    <h2 class="text-lg font-semibold mb-16">操作面板</h2>
    
    {#if plan}
      <div class="mb-24">
        <h3 class="text-sm font-semibold text-gray-700 mb-8">执行计划</h3>
        <div class="space-y-8">
          {#each plan.stages || [] as stage, index}
            <div class="flex items-start gap-8">
              <div class="w-24 h-24 rounded-full bg-primary text-white flex items-center justify-center text-xs">
                {index + 1}
              </div>
              <div class="flex-1">
                <div class="text-sm text-gray-800">{stage}</div>
                {#if plan.stepStatus && plan.stepStatus[index]}
                  <div class="text-xs text-gray-500 mt-4">
                    状态: {plan.stepStatus[index]}
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
    
    {#if activeTask}
      <div>
        <h3 class="text-sm font-semibold text-gray-700 mb-8">当前任务</h3>
        <div class="p-12 bg-gray-50 rounded-lg">
          <div class="text-sm text-gray-800 mb-4">{activeTask.name}</div>
          <div class="text-xs text-gray-500">
            状态: {activeTask.status || 'pending'}
          </div>
          {#if activeTask.result}
            <div class="mt-8 text-xs">
              <div class="font-semibold mb-4">结果:</div>
              <pre class="bg-white p-8 rounded overflow-x-auto">{JSON.stringify(activeTask.result, null, 2)}</pre>
            </div>
          {/if}
        </div>
      </div>
    {/if}
    
    {#if !plan && !activeTask}
      <div class="text-gray-400 text-sm">暂无操作信息</div>
    {/if}
  </div>
</div>