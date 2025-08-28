# utils/chat.ts Code Documentation

## File Summary
The chat utility module contains comprehensive message processing logic for handling real-time AI agent communications. It processes different message types (plan, task, tool_thought), manages chat state updates, builds task actions, handles file attachments, and provides icon mapping for various AI agent operations. This is a critical module for the chat interface's real-time functionality.

## Key Components and Functions

### Main Message Processing Functions

#### combineData Function
```typescript
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
```

**Purpose**: Central message router that processes different types of AI agent messages and updates chat state accordingly.

**Parameters**:
- `eventData: MESSAGE.EventData` - Incoming message data from SSE stream
- `currentChat: CHAT.ChatItem` - Current chat session to update

**Return Value**: `CHAT.ChatItem` - Updated chat object

**Key Logic**: Uses message type to route to appropriate handler function

#### handlePlanMessage Function
```typescript
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
```

**Purpose**: Processes plan-type messages and updates the chat's planning information.

**Key Logic**: Only updates plan if taskId is not present (initial plan creation)

#### handlePlanThoughtMessage Function  
```typescript
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
```

**Purpose**: Handles streaming plan thought messages, either replacing or appending content.

**Key Logic**:
- Initializes plan_thought if not present
- Final messages replace entire content
- Non-final messages append to existing content

#### handleTaskMessage Function
```typescript
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
```

**Purpose**: Processes task-related messages and routes them to specific type handlers.

**Key Logic**:
1. Initializes tasks array if not present
2. Finds existing task by ID
3. Routes to type-specific handler based on message type

### Task Management Functions

#### findTaskIndex Function
```typescript
function findTaskIndex(tasks: MESSAGE.Task[][], taskId: string | undefined): number {
  return tasks.findIndex(
    (item: MESSAGE.Task[]) => item[0]?.taskId === taskId
  );
}
```

**Purpose**: Locates a task group by taskId in the nested task structure.

**Parameters**:
- `tasks: MESSAGE.Task[][]` - Nested array of task groups
- `taskId: string | undefined` - Target task identifier

**Return Value**: `number` - Index of task group, or -1 if not found

#### findToolIndex Function
```typescript
function findToolIndex(tasks: MESSAGE.Task[][], taskIndex: number, messageId: string | undefined): number {
  if (taskIndex === -1) return -1;

  return tasks[taskIndex]?.findIndex(
    (item: MESSAGE.Task) => item.messageId === messageId
  );
}
```

**Purpose**: Locates a specific tool within a task group by messageId.

**Parameters**:
- `tasks: MESSAGE.Task[][]` - Nested task array
- `taskIndex: number` - Index of target task group
- `messageId: string | undefined` - Target message identifier

**Return Value**: `number` - Index of tool within task, or -1 if not found

### Message Type Handlers

#### handleToolThoughtMessage Function
```typescript
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
```

**Purpose**: Handles tool thought messages with streaming content updates.

**Key Logic**:
1. Creates new task group if task doesn't exist
2. Adds new tool to existing task if tool doesn't exist
3. Updates existing tool thought content

#### handleContentMessage Function
```typescript
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
```

**Purpose**: Handles content messages (HTML, Markdown, PPT) with streaming or final updates.

**Key Logic**:
- Updates existing tools with streaming content or final results
- Creates new tools and tasks as needed
- Manages codeOutput for streaming content

#### handleDeepSearchMessage Function
```typescript
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
```

**Purpose**: Handles deep search messages with complex search result structures.

**Key Features**:
- Manages search results with queries and documents
- Handles streaming search content
- Updates search progress and results

### Task Data Processing

#### handleTaskData Function  
```typescript
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

  // Process tasks and build UI structure
  // ... complex task processing logic
  
  return {
    currentChat,
    plan,
    taskList,
    chatList,
  };
};
```

**Purpose**: Processes multi-agent task data and transforms it into UI-ready format.

**Parameters**:
- `currentChat: CHAT.ChatItem` - Current chat session
- `deepThink?: boolean` - Whether deep thinking mode is enabled
- `multiAgent?: MESSAGE.MultiAgent` - Multi-agent data structure

**Return Value**: Object containing processed chat data, plan, task list, and chat list

**Key Processing**:
1. Extracts plan, tasks, and thought data
2. Filters and organizes tasks by type
3. Builds UI-appropriate data structures
4. Handles different display modes (deep think vs. reactive)

### Action Building Functions

#### buildAction Function
```typescript
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

  switch (task.messageType) {
    case MESSAGE_TYPES.TOOL_RESULT:
      return handleToolResult(task);
    case MESSAGE_TYPES.CODE:
      return {
        action: "正在执行代码",
        tool: "编辑器",
        name: ""
      };
    // ... other cases
    default:
      return {
        action: "正在调用工具",
        tool: task?.messageType || "",
        name: ""
      };
  }
};
```

**Purpose**: Builds human-readable action descriptions for different task types.

**Parameters**:
- `task: CHAT.Task` - Task object to build action for

**Return Value**: Object with action, tool, and name properties

**Key Features**:
- Comprehensive task type mapping
- Chinese language descriptions
- Tool-specific action descriptions

### Icon Management

#### getIcon Function
```typescript
export const getIcon = (type: string): string => {
  if (type in ICON_MAP) {
    return ICON_MAP[type as IconType];
  }
  return DEFAULT_ICON;
};
```

**Purpose**: Maps message types to appropriate icon class names.

**Parameters**:
- `type: string` - Message or tool type

**Return Value**: `string` - CSS class name for icon

#### Icon Type Definitions
```typescript
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
```

**Purpose**: Provides consistent icon mapping for different AI agent operations.

### File Attachment Utilities

#### buildAttachment Function
```typescript
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
```

**Purpose**: Transforms file list data into attachment format for UI components.

**Parameters**:
- `fileList: CHAT.FileList[]` - Array of file information objects

**Return Value**: Array of formatted file objects with name, url, type, and size

## Deep Search Processing

### processDeepSearchTask Function
```typescript
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
```

**Purpose**: Processes deep search tasks with multiple queries into individual task items.

**Key Features**:
- Handles different search message types
- Splits multi-query searches into separate items
- Maintains proper task structure and IDs

## Performance and Utility Functions

### Helper Functions
- `createNewTask` - Creates new task objects with proper structure
- `updateToolThought` - Updates tool thought content (streaming or final)
- `initializeResultMap` - Initializes result map with default values
- `updateSearchResult` - Updates search result structures
- `ensureSearchResult` - Ensures search result objects exist

### Constants and Enums
- `TOOL_TYPES` - Array of recognized tool message types
- `MESSAGE_TYPES` - Object mapping for message type constants
- `TOOL_NAMES` - Object mapping for tool name constants
- `IconType` - Enum for icon type definitions
- `ICON_MAP` - Mapping of icon types to CSS classes

## Dependencies
- Complex type definitions from global namespaces (MESSAGE, CHAT)
- No external libraries - pure TypeScript utility functions
- Relies on proper data structures from AI agent backend

**Performance Considerations**:
- Efficient array operations and indexing
- Minimal object cloning (uses structuredClone where needed)
- Optimized message routing and processing
- Streaming content handling to avoid memory bloat

**Error Handling**:
- Safe array access with optional chaining
- Fallback values for missing data
- Proper type checking for message processing

**Notes**:
- Critical module for real-time chat functionality
- Complex message processing logic for various AI agent operations
- Comprehensive task and plan management
- Rich icon and action mapping system
- Chinese language action descriptions
- Efficient streaming content handling
- Clean separation of different message type processing logic