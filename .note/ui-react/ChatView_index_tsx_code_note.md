# ChatView/index.tsx Code Documentation

## File Summary
The main chat interface component that handles real-time conversation with AI agents. It manages SSE (Server-Sent Events) connections, chat history, task management, and provides an interactive chat experience with support for file attachments, action views, and plan tracking.

## Key Components and Functions

### ChatView Component
```typescript
const ChatView: GenieType.FC<Props> = (props) => {
  const { inputInfo: inputInfoProp, product  } = props;

  const [chatTitle, setChatTitle] = useState("");
  const [taskList, setTaskList] = useState<MESSAGE.Task[]>([]);
  const chatList = useRef<CHAT.ChatItem[]>([]);
  const [activeTask, setActiveTask] = useState<CHAT.Task>();
  const [plan, setPlan] = useState<CHAT.Plan>();
  const [showAction, setShowAction] = useState(false);
  const [loading, setLoading] = useState(false);
  // ... other state and refs
};
```

**Purpose**: Main chat interface component that handles real-time AI conversations with task management and action views.

**Props/Parameters**:
- `inputInfo: CHAT.TInputInfo` - Initial input information from parent
- `product?: CHAT.Product` - Selected AI agent product configuration

**Return Value**: JSX element containing the complete chat interface

**State Management**:
- `chatTitle`: Title of the current chat session
- `taskList`: List of AI agent tasks
- `chatList`: Ref containing complete chat history
- `activeTask`: Currently selected task for action view
- `plan`: AI agent planning information
- `showAction`: Controls action panel visibility
- `loading`: Chat loading state

**React Hooks Used**:
- `useState` - Multiple state variables for chat management
- `useRef` - Chat list and DOM element references
- `useMemo` - Session ID memoization
- `useEffect` - Input handling and lifecycle management
- `useMemoizedFn` - Optimized callback functions from ahooks

### combineCurrentChat Function
```typescript
const combineCurrentChat = (
  inputInfo: CHAT.TInputInfo,
  sessionId: string,
  requestId: string
): CHAT.ChatItem => {
  return {
    query: inputInfo.message!,
    files: inputInfo.files!,
    responseType: "txt",
    sessionId,
    requestId,
    loading: true,
    forceStop: false,
    tasks: [],
    thought: "",
    response: "",
    taskStatus: 0,
    tip: "已接收到你的任务，将立即开始处理...",
    multiAgent: {tasks: []},
  };
};
```

**Purpose**: Creates a new chat item with default values for the current conversation.

**Parameters**:
- `inputInfo: CHAT.TInputInfo` - User input data
- `sessionId: string` - Unique session identifier  
- `requestId: string` - Unique request identifier

**Return Value**: `CHAT.ChatItem` - Formatted chat item object

**Key Logic**: Initializes chat item with loading state and Chinese prompt message

### sendMessage Function
```typescript
const sendMessage = useMemoizedFn((inputInfo: CHAT.TInputInfo) => {
  const {message, deepThink, outputStyle} = inputInfo;
  const requestId = getUniqId();
  let currentChat = combineCurrentChat(inputInfo, sessionId, requestId);
  chatList.current =  [...chatList.current, currentChat];
  
  // Set chat title from first message
  if (!chatTitle) {
    setChatTitle(message!);
  }
  
  setLoading(true);
  const params = {
    sessionId: sessionId,
    requestId: requestId,
    query: message,
    deepThink: deepThink ? 1 : 0,
    outputStyle
  };
  
  // SSE connection and message handling
  querySSE({
    body: params,
    handleMessage,
    handleError,
    handleClose,
  });
});
```

**Purpose**: Sends a message to the AI agent and establishes SSE connection for real-time responses.

**Parameters**:
- `inputInfo: CHAT.TInputInfo` - User input containing message, files, and options

**Return Value**: Void

**Key Logic**:
1. Generates unique request ID
2. Creates new chat item and adds to history
3. Sets chat title from first message
4. Establishes SSE connection with server
5. Handles real-time streaming responses

### handleMessage Function (within sendMessage)
```typescript
const handleMessage = (data: MESSAGE.Answer) => {
  const { finished, resultMap, packageType, status } = data;
  
  if (status === "tokenUseUp") {
    modal.info({
      title: '您的试用次数已用尽',
      content: '如需额外申请，请联系 liyang.1236@jd.com',
    });
    // Handle token limit exceeded
    return;
  }
  
  if (packageType !== "heartbeat") {
    requestAnimationFrame(() => {
      if (resultMap?.eventData) {
        currentChat = combineData(resultMap.eventData || {}, currentChat);
        const taskData = handleTaskData(currentChat, deepThink, currentChat.multiAgent);
        
        setTaskList(taskData.taskList);
        updatePlan(taskData.plan!);
        openAction(taskData.taskList);
        
        if (finished) {
          currentChat.loading = false;
          setLoading(false);
        }
        
        // Update chat list
        const newChatList = [...chatList.current];
        newChatList.splice(newChatList.length - 1, 1, currentChat);
        chatList.current = newChatList;
      }
    });
    scrollToTop(chatRef.current!);
  }
};
```

**Purpose**: Handles incoming SSE messages from the AI agent server.

**Parameters**:
- `data: MESSAGE.Answer` - Server response data

**Key Logic**:
1. Checks for token limit exceeded status
2. Filters out heartbeat packages
3. Updates chat data using combineData utility
4. Processes task data and updates UI state
5. Handles completion state and loading indicators
6. Maintains smooth scrolling experience

### Task and Action Management Functions

#### changeTask Function
```typescript
const changeTask = (task: CHAT.Task) => {
  actionViewRef.current?.changeActionView(ActionViewItemEnum.follow);
  changeActionStatus(true);
  setActiveTask(task);
};
```

**Purpose**: Switches the active task in the action view panel.

#### changeFile Function  
```typescript
const changeFile = (file: CHAT.TFile) => {
  changeActionStatus(true);
  actionViewRef.current?.setFilePreview(file);
};
```

**Purpose**: Opens file preview in the action view panel.

#### changePlan Function
```typescript
const changePlan = () => {
  changeActionStatus(true);
  actionViewRef.current?.openPlanView();
};
```

**Purpose**: Opens the AI agent's plan view in the action panel.

## Component Structure

### Header Section
- Logo and chat title display
- Deep research indicator badge
- Responsive layout with proper spacing

### Chat Messages Area
```typescript
<div className="w-full flex-1 overflow-auto no-scrollbar mb-[36px]" ref={chatRef}>
  {chatList.current.map((chat) => {
    return <div key={chat.requestId}>
      <Dialogue
        chat={chat}
        deepThink={inputInfoProp.deepThink}
        changeTask={changeTask}
        changeFile={changeFile}
        changePlan={changePlan}
      />
    </div>;
  })}
</div>
```

**Features**:
- Scrollable chat history
- Individual Dialogue components for each chat item
- Callback functions for interaction handling

### Input Section
```typescript
<GeneralInput
  placeholder={loading ? "任务进行中" : "希望 Genie 为你做哪些任务呢？"}
  showBtn={false}
  size="medium"
  disabled={loading}
  product={product}
  send={(info) => sendMessage({
    ...info,
    deepThink: inputInfoProp.deepThink
  })}
/>
```

**Features**:
- Dynamic placeholder based on loading state
- Disabled state during processing
- Maintains deepThink setting from initial input

### Action View Panel
```typescript
<div className={classNames('transition-all w-0', {
  'opacity-0 overflow-hidden': !showAction,
  'flex-1': showAction,
})}>
  <ActionView
    activeTask={activeTask}
    taskList={taskList}
    plan={plan}
    ref={actionViewRef}
    onClose={() => changeActionStatus(false)}
  />
</div>
```

**Features**:
- Animated slide-in/slide-out transitions
- Conditional rendering based on showAction state
- Integration with task and plan data

## Real-time Features

**SSE Integration**:
- Server-Sent Events for real-time responses
- Streaming message handling
- Token usage monitoring
- Error handling and recovery

**Dynamic UI Updates**:
- Real-time task list updates
- Plan progression tracking
- Loading states and indicators
- Smooth scrolling and animations

**State Synchronization**:
- Consistent state between components
- Proper cleanup and memory management
- Optimistic UI updates

## Dependencies
- `react` - Core hooks and functionality
- `antd` - Modal component for notifications
- `ahooks` - useMemoizedFn for optimized callbacks
- Various internal components and utilities
- SSE utilities for real-time communication

**Performance Optimizations**:
- useMemoizedFn for callback optimization
- requestAnimationFrame for smooth updates
- Ref-based chat history to avoid re-renders
- Efficient state updates and batch processing

**Notes**:
- Comprehensive real-time chat experience
- Support for multiple AI agent types
- Rich interaction with files and tasks
- Chinese language interface elements
- Robust error handling and user feedback