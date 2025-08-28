# chat.ts Utils Code Documentation

## File Summary
This utility module provides comprehensive data processing functions for handling real-time chat messages, task execution, and multi-agent communication data. It processes streaming SSE messages, manages complex task hierarchies, builds user interface representations, and transforms raw backend data into structured formats suitable for display in the chat interface.

## Module Structure

### Core Message Processing

#### `combineData(eventData: MESSAGE.EventData, currentChat: CHAT.ChatItem): CHAT.ChatItem`
- **Purpose**: Main dispatcher function for processing different types of SSE messages
- **Parameters**:
  - `eventData`: Raw event data from SSE stream
  - `currentChat`: Current chat item being updated
- **Logic**: Routes messages based on `messageType` to appropriate handlers
- **Message Types Handled**:
  - `"plan"`: Execution plan updates
  - `"plan_thought"`: Planning reasoning process
  - `"task"`: Task execution messages
- **Returns**: Updated chat item with processed data

## Plan Message Processing

#### `handlePlanMessage(eventData: MESSAGE.EventData, currentChat: CHAT.ChatItem): void`
- **Purpose**: Processes plan-type messages from the AI agent
- **Logic**: 
  - Checks for absence of `taskId` (new plan scenario)
  - Creates plan object from `resultMap` data
  - Assigns plan to `currentChat.multiAgent.plan`
- **Effect**: Updates the execution plan in the chat item

#### `handlePlanThoughtMessage(eventData: MESSAGE.EventData, currentChat: CHAT.ChatItem): void`
- **Purpose**: Handles AI's planning thought process messages
- **Functionality**:
  - Initializes `plan_thought` string if not exists
  - Handles both incremental and final thought updates
  - Accumulates thought content for streaming updates
- **Final Updates**: `isFinal` flag indicates complete thought process
- **Incremental Updates**: Appends new content to existing thoughts

## Task Message Processing

#### `handleTaskMessage(eventData: MESSAGE.EventData, currentChat: CHAT.ChatItem): void`
- **Purpose**: Main handler for task-related messages
- **Process**:
  1. Initializes task array if needed
  2. Finds existing task index by `taskId`
  3. Delegates to type-specific handlers based on nested `messageType`
- **Task Structure**: Tasks organized as `Task[][]` (nested arrays)

#### `findTaskIndex(tasks: MESSAGE.Task[][], taskId: string | undefined): number`
- **Purpose**: Locates a task group by taskId in the nested task structure
- **Logic**: Searches for first task in each sub-array matching the taskId
- **Returns**: Index of task group, or -1 if not found
- **Usage**: Used throughout for task identification and updates

#### `findToolIndex(tasks: MESSAGE.Task[][], taskIndex: number, messageId: string | undefined): number`
- **Purpose**: Locates a specific tool within a task by messageId
- **Parameters**: 
  - `tasks`: Nested task array structure
  - `taskIndex`: Index of the task group
  - `messageId`: Unique identifier for the specific tool/message
- **Returns**: Tool index within the task, or -1 if not found

## Task Message Type Handlers

#### `handleTaskMessageByType(eventData, currentChat, taskIndex): void`
- **Purpose**: Routes task messages to appropriate processors based on message type
- **Message Types**:
  - `"tool_thought"`: Tool reasoning process
  - `"html"`, `"markdown"`, `"ppt"`: Content generation
  - `"deep_search"`: Search operations
  - `default`: Generic non-streaming messages

### Tool Thought Processing

#### `handleToolThoughtMessage(eventData, currentChat, taskIndex, toolIndex): void`
- **Purpose**: Processes AI tool reasoning messages
- **Cases**:
  1. **New Task**: Creates first task in new task group
  2. **New Tool**: Adds tool to existing task group  
  3. **Update Tool**: Updates existing tool's thought content
- **Helper Functions**: Uses `createNewTask()` and `updateToolThought()`

#### `createNewTask(taskId: string, resultMap: MESSAGE.Task): MESSAGE.Task`
- **Purpose**: Factory function for creating new task objects
- **Structure**: Combines taskId with resultMap properties
- **Usage**: Standardizes task creation across handlers

#### `updateToolThought(tool: MESSAGE.Task, newThought: string, isFinal: boolean): void`
- **Purpose**: Updates tool thought content with streaming or final data
- **Logic**:
  - **Final**: Replaces entire thought content
  - **Streaming**: Appends to existing thought content
- **Usage**: Handles both incremental and complete thought updates

### Content Message Processing

#### `handleContentMessage(eventData, currentChat, taskIndex, toolIndex): void`
- **Purpose**: Processes content generation messages (HTML, Markdown, PPT)
- **Complex Logic**: Handles nested task/tool creation and updates
- **Data Processing**:
  - Initializes `resultMap` with `initializeResultMap()`
  - Handles both streaming and final content updates
  - Manages `codeOutput` property for content storage

#### `initializeResultMap(originalResultMap: any): any`
- **Purpose**: Standardizes result map structure with required properties
- **Properties Added**:
  - `codeOutput`: Content data (from `data` property if exists)
  - `fileInfo`: Array for file information (defaults to empty array)
- **Returns**: Enhanced result map with consistent structure

### Deep Search Processing

#### `handleDeepSearchMessage(eventData, currentChat, taskIndex, toolIndex): void`
- **Purpose**: Handles search operation messages with complex result structures
- **Process Flow**: Similar to content messages but with search-specific data
- **Helper Functions**: Uses task management utilities for consistent processing

#### Search Result Management Functions

#### `updateSearchResult(target: MESSAGE.ResultMap, source?: MESSAGE.SearchResult): void`
- **Purpose**: Merges search result data from source to target
- **Properties Updated**:
  - `query`: Search queries array
  - `docs`: Search result documents
- **Safety**: Handles undefined source gracefully

#### `ensureSearchResult(resultMap: MESSAGE.ResultMap): void`
- **Purpose**: Initializes search result structure if missing
- **Default Structure**:
  ```typescript
  {
    query: [],
    docs: []
  }
  ```

## Task Data Processing

#### `handleTaskData(currentChat, deepThink?, multiAgent?): Object`
- **Purpose**: Main function for processing complete task data and preparing UI representation
- **Returns**: Object with processed chat, plan, taskList, and chatList
- **Parameters**:
  - `currentChat`: Current chat item to process
  - `deepThink`: Optional deep thinking mode flag
  - `multiAgent`: Complete multi-agent data structure

### Processing Logic

#### Tool Type Classification
```typescript
const TOOL_TYPES = [
  "tool_result", "browser", "code", "html", "file", 
  "knowledge", "result", "deep_search", "task_summary", 
  "markdown", "ppt"
];
```

#### Chat List Construction
- **Deep Think Mode**: Creates empty arrays for each task group
- **Normal Mode**: Single placeholder with empty children
- **Structure**: Hierarchical organization for UI display

#### Task Processing Loop
```typescript
validTasks?.forEach((taskGroup, groupIndex) => {
  taskGroup?.forEach((task, taskIndex) => {
    // Process individual tasks
  });
});
```

#### Special Task Handling
- **Code Output Only**: Tasks with only code output, no source
- **Deep Search Extend**: Search tasks with extension type
- **Plan Updates**: Plan extraction and assignment
- **Conclusion**: Final result task identification

### Deep Search Task Processing

#### `processDeepSearchTask(task: any, baseId: string): any[]`
- **Purpose**: Handles complex deep search task structures
- **Logic**:
  - **Report Type**: Single task return
  - **Search Types**: Multiple tasks for each query
  - **Query Mapping**: Creates separate task for each search query
- **ID Generation**: Unique IDs for each sub-task using base ID + index

## Action Building

#### `buildAction(task: CHAT.Task): Object`
- **Purpose**: Creates user-friendly action descriptions from task data
- **Returns**: Object with `action`, `tool`, and `name` properties
- **Message Types**: Comprehensive switch statement for all task types

### Action Type Mappings
- **Tool Result**: Maps tool names to user actions
- **Code**: "正在执行代码" (Executing code)
- **HTML**: "正在生成web页面" (Generating web page)
- **File**: File operation descriptions
- **Deep Search**: Search or summarization actions

### Tool-Specific Handlers
#### `handleToolResult(task: CHAT.Task): Object`
- **Web Search**: "正在搜索" with query parameter
- **Code Interpreter**: "正在执行代码" action
- **Default**: Generic tool calling action

#### `handleFileTask(task: any): Object`
- **Action**: Extracted from `resultMap.command`
- **Tool**: "文件编辑器" (File Editor)
- **Name**: Filename from `fileInfo`

#### `handleDeepSearchTask(task: any): Object`
- **Report Mode**: "正在总结" (Summarizing)
- **Search Mode**: "正在搜索" (Searching)
- **Dynamic Names**: Based on query or search result

## Icon Management

#### `IconType` Enum
```typescript
enum IconType {
  PLAN = 'plan',
  PLAN_THOUGHT = 'plan_thought',
  TOOL_RESULT = 'tool_result',
  BROWSER = 'browser',
  FILE = 'file',
  DEEP_SEARCH = 'deep_search',
  CODE = 'code',
  HTML = 'html',
}
```

#### `ICON_MAP: Record<IconType, string>`
- **Purpose**: Maps task types to icon font classes
- **Icons**: RelayIcon font classes for consistent UI
- **Default**: Fallback icon for unknown types

#### `getIcon(type: string): string`
- **Purpose**: Retrieves appropriate icon for given task type
- **Fallback**: Returns default icon for unmapped types
- **Usage**: UI components use this for task visualization

## Attachment Processing

#### `buildAttachment(fileList: CHAT.FileList[]): Array`
- **Purpose**: Transforms file information for UI display
- **Mapping**: Extracts essential file properties
- **Properties**: name, url, type (extension), size
- **Returns**: Array of standardized file objects

## Key Features

### Real-time Processing
- **Streaming Updates**: Handles incremental data from SSE
- **State Management**: Maintains complex nested task structures
- **Live Updates**: Processes data as it arrives

### Complex Data Structures
- **Nested Tasks**: Multi-level task and tool organization
- **Dynamic Content**: Handles various content types and formats
- **Search Integration**: Complex search result processing

### UI Preparation
- **Action Descriptions**: Human-readable task descriptions
- **Icon Mapping**: Visual representations for different operations
- **File Handling**: Standardized attachment processing

### Error Resilience
- **Safe Defaults**: Provides fallbacks for missing data
- **Type Checking**: Handles undefined/null values gracefully
- **Flexible Processing**: Adapts to various message formats

This utility module serves as the critical data transformation layer between the raw SSE messages and the user interface, ensuring that complex multi-agent communication data is properly structured, categorized, and prepared for display in the chat interface.