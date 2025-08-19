export const combineData = (
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem
) => {
  switch (eventData.messageType) {
    case "plan": {
      handlePlanMessage(eventData, currentChat);
      break;
    }
    case "plan_thought": {
      handlePlanThoughtMessage(eventData, currentChat);
      break;
    }
    case "task": {
      handleTaskMessage(eventData, currentChat);
      break;
    }
    default:
      break;
  }
  return currentChat;
};

/**
 * 处理计划类型的消息
 * @param eventData 事件数据
 * @param currentChat 当前聊天对象
 */
function handlePlanMessage(
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem
) {
  if (!eventData.taskId) {
    currentChat.multiAgent.plan = {
      taskId: eventData.taskId,
      ...eventData?.resultMap,
    } as unknown as CHAT.Plan;
  }
}

/**
 * 处理计划思考类型的消息
 * @param eventData 事件数据
 * @param currentChat 当前聊天对象
 */
function handlePlanThoughtMessage(
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem
) {
  if (!currentChat.multiAgent.plan_thought) {
    currentChat.multiAgent.plan_thought = "";
  }
  if (eventData.resultMap.isFinal) {
    currentChat.multiAgent.plan_thought = eventData.resultMap.planThought;
  } else {
    currentChat.multiAgent.plan_thought += eventData.resultMap.planThought;
  }
}

/**
 * 处理任务类型的消息
 * @param eventData 事件数据
 * @param currentChat 当前聊天对象
 */
function handleTaskMessage(
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem
) {
  if (!currentChat.multiAgent.tasks) {
    currentChat.multiAgent.tasks = [];
  }
  const taskIndex = findTaskIndex(currentChat.multiAgent.tasks, eventData.taskId);
  if (eventData.resultMap?.messageType) {
    handleTaskMessageByType(eventData, currentChat, taskIndex);
  }
}

/**
 * 查找工具在指定任务中的索引
 * @param tasks 任务数组
 * @param taskIndex 任务索引
 * @param messageId 消息ID
 * @returns 工具索引，如果未找到则返回-1
 */
function findToolIndex(tasks: MESSAGE.Task[][], taskIndex: number, messageId: string | undefined): number {
  if (taskIndex === -1) return -1;

  return tasks[taskIndex]?.findIndex(
    (item: MESSAGE.Task) => item.messageId === messageId
  );
}

/**
 * 根据消息类型处理任务消息
 * @param eventData 事件数据
 * @param currentChat 当前聊天对象
 * @param taskIndex 任务索引
 */
function handleTaskMessageByType(
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem,
  taskIndex: number
) {
  const messageType = eventData.resultMap.messageType;
  const toolIndex = findToolIndex(
    currentChat.multiAgent.tasks!,
    taskIndex,
    eventData.messageId
  );

  switch (messageType) {
    case "tool_thought":
      handleToolThoughtMessage(eventData, currentChat, taskIndex, toolIndex);
      break;
    case "html":
    case "markdown":
    case "ppt":
      handleContentMessage(eventData, currentChat, taskIndex, toolIndex);
      break;
    case "deep_search":
      handleDeepSearchMessage(eventData, currentChat, taskIndex, toolIndex);
      break;
    default:
      handleNonStreamingMessage(eventData, currentChat, taskIndex);
      break;
  }
}

/**
 * 查找任务在任务数组中的索引
 * @param tasks 任务数组
 * @param taskId 任务ID
 * @returns 任务索引，如果未找到则返回-1
 */
function findTaskIndex(tasks: MESSAGE.Task[][], taskId: string | undefined): number {
  return tasks.findIndex(
    (item: MESSAGE.Task[]) => item[0]?.taskId === taskId
  );
}

/**
 * 处理工具思考消息
 * @param eventData 事件数据
 * @param currentChat 当前聊天项
 * @param taskIndex 任务索引
 * @param toolIndex 工具索引
 */
function handleToolThoughtMessage(
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem,
  taskIndex: number,
  toolIndex: number
) {
  const { tasks } = currentChat.multiAgent;
  const { taskId, resultMap } = eventData;
  const { toolThought, isFinal } = resultMap;

  if (taskIndex === -1) {
    tasks.push([createNewTask(taskId, resultMap)]);
    return;
  }

  if (toolIndex === -1) {
    tasks[taskIndex].push(createNewTask(taskId, resultMap));
    return;
  }

  updateToolThought(tasks[taskIndex][toolIndex], toolThought || '', isFinal);
}

/**
 * 创建新任务对象
 * @param taskId 任务ID
 * @param resultMap 结果映射
 * @returns 新任务对象
 */
function createNewTask(taskId: string, resultMap: MESSAGE.Task): MESSAGE.Task {
  return {
    taskId,
    ...resultMap,
  };
}

/**
 * 更新工具思考内容
 * @param tool 工具对象
 * @param newThought 新的思考内容
 * @param isFinal 是否为最终结果
 */
function updateToolThought(tool: MESSAGE.Task, newThought: string, isFinal: boolean) {
  if (isFinal) {
    tool.toolThought = newThought;
  } else {
    tool.toolThought = (tool.toolThought || '') + newThought;
  }
}

/**
 * 处理内容消息
 * @param eventData 事件数据
 * @param currentChat 当前聊天
 * @param taskIndex 任务索引
 * @param toolIndex 工具索引
 */
function handleContentMessage(
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem,
  taskIndex: number,
  toolIndex: number
) {
  if (taskIndex !== -1) {
    // 更新
    if (toolIndex !== -1) {
      // 已完成
      if (eventData.resultMap.resultMap.isFinal) {
        currentChat.multiAgent.tasks[taskIndex][toolIndex].resultMap =
                    {
                      ...eventData.resultMap.resultMap,
                      codeOutput: eventData.resultMap.resultMap.data,
                    };
      } else {
        // 进行中
        currentChat.multiAgent.tasks[taskIndex][
          toolIndex
        ].resultMap.isFinal = false;

        currentChat.multiAgent.tasks[taskIndex][
          toolIndex
        ].resultMap.codeOutput +=
                    eventData.resultMap.resultMap?.data || "";
      }
    } else {
      eventData.resultMap.resultMap = initializeResultMap(eventData.resultMap.resultMap);

      // 添加tool
      currentChat.multiAgent.tasks[taskIndex].push({
        taskId: eventData.taskId,
        ...eventData.resultMap,
      });
    }
  } else {

    eventData.resultMap.resultMap = initializeResultMap(eventData.resultMap.resultMap);

    // 添加任务及tool
    currentChat.multiAgent.tasks.push([
      {
        taskId: eventData.taskId,
        ...eventData.resultMap,
      },
    ]);
  }
}

/**
 * 初始化结果映射
 * @param originalResultMap 原始结果映射
 * @returns 初始化后的结果映射
 */
export function initializeResultMap(originalResultMap: any) {
  return {
    ...originalResultMap,
    codeOutput: originalResultMap.codeOutput || originalResultMap.data || '',
    fileInfo: originalResultMap.fileInfo || [],
  };
}

/**
 * 处理现有任务
 * @param currentChat 当前聊天
 * @param taskIndex 任务索引
 * @param toolIndex 工具索引
 * @param eventData 事件数据
 * @param resultMap 结果映射
 */
export function handleExistingTask(
  currentChat: CHAT.ChatItem,
  taskIndex: number,
  toolIndex: number,
  eventData: MESSAGE.EventData,
  resultMap: any
) {
  if (toolIndex !== -1) {
    updateExistingTool(currentChat, taskIndex, toolIndex, resultMap);
  } else {
    addNewTool(currentChat, taskIndex, eventData, resultMap);
  }
}

/**
 * 更新现有工具
 * @param currentChat 当前聊天
 * @param taskIndex 任务索引
 * @param toolIndex 工具索引
 * @param resultMap 结果映射
 */
function updateExistingTool(
  currentChat: CHAT.ChatItem,
  taskIndex: number,
  toolIndex: number,
  resultMap: any
) {
  const tool = currentChat.multiAgent.tasks[taskIndex][toolIndex];
  if (resultMap.isFinal) {
    tool.resultMap = {
      ...resultMap,
      codeOutput: resultMap.data
    };
  } else {
    tool.resultMap.isFinal = false;
    tool.resultMap.codeOutput += resultMap.data || '';
  }
}

/**
 * 添加新工具
 * @param currentChat 当前聊天
 * @param taskIndex 任务索引
 * @param eventData 事件数据
 * @param resultMap 结果映射
 */
function addNewTool(
  currentChat: CHAT.ChatItem,
  taskIndex: number,
  eventData: MESSAGE.EventData,
  resultMap: any
) {
  currentChat.multiAgent.tasks[taskIndex].push({
    taskId: eventData.taskId,
    resultMap: resultMap,
  } as MESSAGE.Task);
}

/**
 * 处理新任务
 * @param currentChat 当前聊天
 * @param eventData 事件数据
 * @param resultMap 结果映射
 */
export function handleNewTask(
  currentChat: CHAT.ChatItem,
  eventData: MESSAGE.EventData,
  resultMap: any
) {
  currentChat.multiAgent.tasks.push([
    {
      taskId: eventData.taskId,
      resultMap: resultMap,
    } as MESSAGE.Task,
  ]);
}

/**
 * 处理深度搜索消息
 * @param eventData 事件数据
 * @param currentChat 当前聊天
 * @param taskIndex 任务索引
 * @param toolIndex 工具索引
 */
function handleDeepSearchMessage(
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem,
  taskIndex: number,
  toolIndex: number
) {
  const resultMap = eventData.resultMap.resultMap;

  if (taskIndex !== -1) {
    if (toolIndex !== -1) {
      updateExistingTaskTool(currentChat, taskIndex, toolIndex, resultMap);
    } else {
      addNewToolToExistingTask(currentChat, taskIndex, eventData);
    }
  } else {
    addNewTask(currentChat, eventData);
  }
}

/**
 * 更新现有任务和工具的结果
 */
function updateExistingTaskTool(
  currentChat: CHAT.ChatItem,
  taskIndex: number,
  toolIndex: number,
  resultMap: MESSAGE.ResultMap
) {
  const targetTool = currentChat.multiAgent.tasks[taskIndex][toolIndex];
  targetTool.resultMap.isFinal = resultMap?.isFinal;
  targetTool.resultMap.messageType = resultMap?.messageType;
  updateSearchResult(targetTool.resultMap, resultMap?.searchResult);
  targetTool.resultMap.answer += resultMap?.answer || "";
}

/**
 * 添加新工具到现有任务
 */
function addNewToolToExistingTask(
  currentChat: CHAT.ChatItem,
  taskIndex: number,
  eventData: MESSAGE.EventData
) {
  const resultMap = eventData.resultMap.resultMap;

  resultMap.answer = resultMap?.answer || "";
  ensureSearchResult(resultMap);

  currentChat.multiAgent.tasks[taskIndex].push({
    taskId: eventData.taskId,
    ...eventData.resultMap,
  });
}

/**
 * 添加新任务
 */
function addNewTask(currentChat: CHAT.ChatItem, eventData: MESSAGE.EventData) {
  const resultMap = eventData.resultMap.resultMap;

  resultMap.answer = resultMap?.answer || "";
  ensureSearchResult(resultMap);

  currentChat.multiAgent.tasks.push([
    {
      taskId: eventData.taskId,
      ...eventData.resultMap,
    },
  ]);
}

/**
 * 更新搜索结果
 */
function updateSearchResult(target: MESSAGE.ResultMap, source?: MESSAGE.SearchResult) {
  if (source?.query?.length) {
    target.searchResult!.query = source.query;
  }
  if (source?.docs?.length) {
    target.searchResult!.docs = source.docs;
  }
}

/**
 * 确保搜索结果存在
 */
function ensureSearchResult(resultMap: MESSAGE.ResultMap) {
  if (resultMap.searchResult) {
    resultMap.searchResult.query = resultMap.searchResult?.query || [];
    resultMap.searchResult.docs = resultMap.searchResult?.docs || [];
  } else {
    resultMap.searchResult = {
      query: [],
      docs: []
    };
  }
}

function handleNonStreamingMessage(
  eventData: MESSAGE.EventData,
  currentChat: CHAT.ChatItem,
  taskIndex: number,
) {
  if (taskIndex !== -1) {
    currentChat.multiAgent.tasks[taskIndex].push({
      taskId: eventData.taskId,
      ...eventData.resultMap,
    });
  } else {
    currentChat.multiAgent.tasks.push([
      {
        taskId: eventData.taskId,
        ...eventData.resultMap,
      },
    ]);
  }

}

/**
 * 处理多智能体任务数据，整合聊天、计划和任务信息
 * @param currentChat 当前聊天对象
 * @param deepThink 深度思考
 * @param multiAgent 多智能体数据
 * @returns 处理后的数据对象
 */
export const handleTaskData = (
  currentChat: CHAT.ChatItem,
  deepThink?: boolean,
  multiAgent?: MESSAGE.MultiAgent
) => {
  const {
    plan: fullPlan,
    tasks: fullTasks,
    plan_thought: planThought,
  } = multiAgent ?? {};

  const TOOL_TYPES = [
    "tool_result",
    "browser",
    "code",
    "html",
    "file",
    "knowledge",
    "result",
    "deep_search",
    "task_summary",
    "markdown",
    "ppt",
  ];

  currentChat.thought = planThought || "";

  let conclusion;
  let plan = fullPlan;
  const taskList: MESSAGE.Task[] = [];

  const validTasks: MESSAGE.Task[][] = fullTasks?.filter(
    (item: MESSAGE.Task[]) => item && item?.length > 0
  ) ?? [];

  const chatList: any = !deepThink
    ? [
      [
        {
          hidden: false,
          children: [],
        },
      ],
    ]
    : Array.from({ length: validTasks?.length || 0 }, () => []);

  validTasks?.forEach((taskGroup, groupIndex) => {
    taskGroup?.forEach((task, taskIndex) => {
      const time = task.messageTime;
      const id = time?.concat(String(taskIndex));

      const isCodeOutputOnly =
        task?.messageType === "code" &&
        (task.resultMap?.codeOutput || !task.resultMap?.code);

      const isDeepSearchExtend =
        task?.messageType === "deep_search" &&
        task.resultMap.messageType === "extend";

      let processedInfo: any = [];

      if (task.messageType === "deep_search") {
        processedInfo = processDeepSearchTask(task, id);
      } else {
        processedInfo = [
          {
            ...task,
            id,
          },
        ];
      }

      if (task.messageType === "task") {
        chatList[groupIndex].push({
          ...task,
          task: task.task,
          hidden: false,
          children: [],
        });
      } else if (task?.messageType !== "result" && !isCodeOutputOnly) {
        chatList[groupIndex]?.at(-1)?.children.push(...processedInfo);
      }

      if (TOOL_TYPES.includes(task?.messageType) && !isCodeOutputOnly && !isDeepSearchExtend) {
        taskList.push(...processedInfo);
      }

      if (task?.messageType === "plan") {
        plan = task.plan;
      }

      if (task?.messageType === "result") {
        conclusion = task;
      }
    });
  });

  currentChat.tasks = chatList;
  currentChat.plan = plan;
  currentChat.conclusion = conclusion;
  currentChat.planList = plan?.stages?.reduce(
    (result: CHAT.PlanItem[], stage: string, index: number) => {
      const group = result.find((item) => item.name === stage);
      if (group) {
        group.list.push(plan?.steps[index] || "");
      } else {
        result.push({
          name: stage,
          list: [plan?.steps[index] || ""],
        });
      }
      return result;
    },
    []
  );

  return {
    currentChat,
    plan,
    taskList,
    chatList,
  };
};

/**
 * 处理深度搜索任务的辅助函数
 * @param task 深度搜索任务
 * @param baseId 基础ID
 * @returns 处理后的任务信息数组
 */
function processDeepSearchTask(task: any, baseId: string): any[] {
  const showTypes = ['extend', 'search'];
  if (task.resultMap.messageType === "report") {
    return [
      {
        ...task,
        id: baseId,
      },
    ];
  }

  if (showTypes.includes(task.resultMap.messageType!)) {
    return task.resultMap.searchResult!.query.map((query: string, index: number) => {
      const clonedTask = structuredClone({
        ...task,
        id: baseId.concat(String(index)),
      });

      const searchResult = {
        query: query,
        docs: task.resultMap.searchResult?.docs?.[index] ?? [],
      };

      clonedTask.resultMap.searchResult = searchResult;
      return clonedTask;
    });
  }

  return [
    {
      ...task,
      id: baseId,
    },
  ];
}

/**
 * 构建任务动作信息
 * @param task 任务对象
 * @returns 包含action、tool和name的动作信息对象
 */
export const buildAction = (task: CHAT.Task) => {
  // 定义消息类型常量
  const MESSAGE_TYPES = {
    TOOL_RESULT: "tool_result",
    CODE: "code",
    HTML: "html",
    PLAN_THOUGHT: "plan_thought",
    PLAN: "plan",
    FILE: "file",
    KNOWLEDGE: "knowledge",
    DEEP_SEARCH: "deep_search",
    MARKDOWN: "markdown"
  };

  const TOOL_NAMES = {
    WEB_SEARCH: "web_search",
    INTERNAL_SEARCH: "internal_search",
    CODE_INTERPRETER: "code_interpreter"
  };

  switch (task.messageType) {
    case MESSAGE_TYPES.TOOL_RESULT:
      return handleToolResult(task);

    case MESSAGE_TYPES.CODE:
      return {
        action: "正在执行代码",
        tool: "编辑器",
        name: ""
      };

    case MESSAGE_TYPES.HTML:
      return {
        action: "正在生成web页面",
        tool: "编辑器",
        name: ""
      };

    case MESSAGE_TYPES.PLAN_THOUGHT:
      return {
        action: "正在思考下一步计划",
        tool: "",
        name: ""
      };

    case MESSAGE_TYPES.PLAN:
      return {
        action: "更新任务列表",
        tool: "",
        name: ""
      };

    case MESSAGE_TYPES.FILE:
      return handleFileTask(task);

    case MESSAGE_TYPES.KNOWLEDGE:
      return {
        action: "正在调用知识库",
        tool: "文件编辑器",
        name: "查询知识库"
      };

    case MESSAGE_TYPES.DEEP_SEARCH:
      return handleDeepSearchTask(task);

    case MESSAGE_TYPES.MARKDOWN:
      return {
        action: "正在生成报告",
        tool: "markdown",
        name: ""
      };

    default:
      return {
        action: "正在调用工具",
        tool: task?.messageType || "",
        name: ""
      };
  }

  /**
   * 处理工具结果类型的任务
   * @param task 任务对象
   * @returns 动作信息对象
   */
  function handleToolResult(task: CHAT.Task) {
    const toolName = task?.toolResult?.toolName;

    switch (toolName) {
      case TOOL_NAMES.WEB_SEARCH:
      case TOOL_NAMES.INTERNAL_SEARCH:
        return {
          action: "正在搜索",
          tool: "网络查询",
          name: task?.toolResult?.toolParam?.query || ""
        };

      case TOOL_NAMES.CODE_INTERPRETER:
        return {
          action: "正在执行代码",
          tool: "编辑器",
          name: "执行代码"
        };

      default:
        return {
          action: "正在调用工具",
          tool: toolName || "",
          name: toolName || ""
        };
    }
  }

  /**
   * 处理文件类型的任务
   * @param task 任务对象
   * @returns 动作信息对象
   */
  function handleFileTask(task: any) {
    const fileInfo = task.resultMap?.fileInfo?.[0] || {};
    return {
      action: task?.resultMap?.command || "",
      tool: "文件编辑器",
      name: fileInfo?.fileName || ""
    };
  }

  /**
   * 处理深度搜索类型的任务
   * @param task 任务对象
   * @returns 动作信息对象
   */
  function handleDeepSearchTask(task: any) {
    const isReport = task.resultMap.messageType === "report";
    return {
      action: isReport ? "正在总结" : "正在搜索",
      tool: "深度搜索",
      name: isReport
        ? task?.resultMap?.query || ""
        : task?.resultMap?.searchResult?.query || ""
    };
  }
};

export enum IconType {
  PLAN = 'plan',
  PLAN_THOUGHT = 'plan_thought',
  TOOL_RESULT = 'tool_result',
  BROWSER = 'browser',
  FILE = 'file',
  DEEP_SEARCH = 'deep_search',
  CODE = 'code',
  HTML = 'html',
}

/**
 * 图标映射表
 */
const ICON_MAP: Record<IconType, string> = {
  [IconType.PLAN]: 'icon-renwu',
  [IconType.PLAN_THOUGHT]: 'icon-juli',
  [IconType.TOOL_RESULT]: 'icon-tiaoshi',
  [IconType.BROWSER]: 'icon-sousuo',
  [IconType.FILE]: 'icon-bianji',
  [IconType.DEEP_SEARCH]: 'icon-sousuo',
  [IconType.CODE]: 'icon-daima',
  [IconType.HTML]: 'icon-daima',
};

/**
 * 默认图标
 */
const DEFAULT_ICON = 'icon-tiaoshi';

/**
 * 根据指定的类型获取对应的图标名称
 * @param type - 图标类型，可以是 IconType 枚举中的值或其他字符串
 * @returns 对应的图标名称，如果类型不存在则返回默认图标
 */
export const getIcon = (type: string): string => {
  if (type in ICON_MAP) {
    return ICON_MAP[type as IconType];
  }
  return DEFAULT_ICON;
};

export const buildAttachment = (fileList: CHAT.FileList[]) => {
  const result = fileList?.map((item) => {
    const { domainUrl, fileName, fileSize } = item;
    const extension = fileName?.split(".").pop();
    return {
      name: fileName,
      url: domainUrl,
      type: extension!,
      size: fileSize,
    };
  });
  return result;
};