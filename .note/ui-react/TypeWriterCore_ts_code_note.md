# hooks/TypeWriterCore.ts Code Documentation

## File Summary
The TypeWriterCore class provides the core animation engine for typewriter text effects. It manages character queuing, dynamic timing, and progressive text consumption to create smooth character-by-character text animations. This class handles the low-level animation logic while being framework-agnostic.

## Key Components and Functions

### TypeWriterCoreOptions Interface
```typescript
interface TypeWriterCoreOptions {
  onConsume: (str: string) => void; // 定义一个回调函数，用于消费（处理）字符
  maxStepSeconds?: number; // 可选属性，定义最大步进间隔（毫秒）
}
```

**Purpose**: Defines configuration options for the TypeWriterCore animation engine.

**Properties**:
- `onConsume: (str: string) => void` - Callback function for character processing
- `maxStepSeconds?: number` - Optional maximum delay between characters (milliseconds)

### TypeWriterCore Class
```typescript
export default class TypeWriterCore {
  onConsume: (str: string) => void; // 消费（处理）字符的回调函数
  queueList: string[] = []; // 存储待消费字符的队列
  maxStepSeconds: number = 50; // 默认最大步进间隔为50毫秒
  maxQueueNum: number = 2000; // 队列中最大字符数
  timer: NodeJS.Timeout | number | undefined; // 用于控制下一次消费的定时器，兼容浏览器和Node.js环境

  constructor({onConsume, maxStepSeconds}: TypeWriterCoreOptions) {
    this.onConsume = onConsume; // 初始化消费字符的回调

    if (maxStepSeconds !== undefined) {
      this.maxStepSeconds = maxStepSeconds; // 如果提供了最大步进间隔，则使用提供的值
    }
  }
}
```

**Purpose**: Core animation engine that manages character queuing, timing, and progressive text reveal.

**Properties**:
- `onConsume` - Callback function to process each character
- `queueList` - Array of characters waiting to be processed
- `maxStepSeconds` - Maximum delay between character consumption (default: 50ms)
- `maxQueueNum` - Maximum characters in queue for dynamic speed calculation (2000)
- `timer` - Timer reference for animation control (compatible with both Node.js and browser)

### Constructor
```typescript
constructor({onConsume, maxStepSeconds}: TypeWriterCoreOptions) {
  this.onConsume = onConsume; // 初始化消费字符的回调

  if (maxStepSeconds !== undefined) {
    this.maxStepSeconds = maxStepSeconds; // 如果提供了最大步进间隔，则使用提供的值
  }
}
```

**Purpose**: Initializes the TypeWriterCore with callback function and optional timing configuration.

**Parameters**:
- `onConsume` - Required callback for character processing
- `maxStepSeconds` - Optional timing override (defaults to 50ms if not provided)

### Dynamic Speed Calculation
```typescript
// 动态计算消费字符的速度
dynamicSpeed() {
  const speedQueueNum = this.maxQueueNum / this.queueList.length; // 根据队列长度动态调整速度
  const resNum = +(
    speedQueueNum > this.maxStepSeconds
      ? this.maxStepSeconds : speedQueueNum
  ).toFixed(0); // 确保结果为整数

  return resNum;
}
```

**Purpose**: Calculates dynamic animation speed based on current queue length.

**Return Value**: `number` - Delay in milliseconds for next character

**Key Logic**:
1. **Speed Calculation**: `maxQueueNum / queueList.length`
2. **Upper Bound**: Never exceeds `maxStepSeconds`
3. **Integer Conversion**: Uses `toFixed(0)` and `+` to ensure integer result

**Dynamic Behavior**:
- **Long Queue**: Faster animation (shorter delays) to catch up
- **Short Queue**: Slower animation (longer delays) for readability
- **Empty Queue**: Returns maxStepSeconds for consistent baseline

### Text Queuing Functions

#### onAddQueueList Method
```typescript
// 将字符串添加到队列中
onAddQueueList(str: string) {
  this.queueList = [...this.queueList, ...str.split('')]; // 分解字符串为字符数组并追加到队列
}
```

**Purpose**: Internal method to add characters to the processing queue.

**Parameters**:
- `str: string` - String to be added to queue

**Key Logic**:
1. Splits string into individual characters
2. Appends to existing queue using spread operator
3. Maintains queue order for sequential processing

#### add Method (Public API)
```typescript
// 添加字符串到队列的公共方法
add(str: string) {
  if (!str) return; // 如果字符串为空，则不执行任何操作
  this.onAddQueueList(str); // 调用内部方法添加字符串到队列
}
```

**Purpose**: Public method for adding text to the animation queue.

**Parameters**:
- `str: string` - Text to animate

**Return Value**: Void

**Features**:
- **Null Check**: Prevents processing empty strings
- **Public Interface**: Clean API for external usage
- **Queue Addition**: Delegates to internal queuing method

### Character Processing

#### consume Method
```typescript
// 从队列中消费一个字符
consume() {
  if (this.queueList.length > 0) {
    const str = this.queueList.shift(); // 从队列头部移除一个字符
    // eslint-disable-next-line @typescript-eslint/no-unused-expressions
    str && this.onConsume(str); // 如果字符存在，则调用消费函数处理该字符
  }
}
```

**Purpose**: Processes one character from the queue and calls the consumption callback.

**Key Logic**:
1. **Queue Check**: Only processes if queue has characters
2. **FIFO Processing**: Uses `shift()` to get first character
3. **Safe Callback**: Only calls onConsume if character exists
4. **State Update**: Callback typically updates UI state

### Animation Control

#### next Method
```typescript
// 定时消费队列中的字符
next() {
  this.timer = setTimeout(() => {
    if (this.queueList.length > 0) {
      this.consume(); // 消费一个字符
      this.next(); // 递归调用，继续消费下一个字符
    }
  }, this.dynamicSpeed()); // 根据动态速度设置定时器
}
```

**Purpose**: Schedules the next character consumption with dynamic timing.

**Key Features**:
- **Recursive Scheduling**: Continues until queue is empty
- **Dynamic Timing**: Uses dynamicSpeed() for intelligent delays
- **Self-Managing**: Stops automatically when queue empties
- **Timer Storage**: Stores timer reference for cleanup

#### start Method
```typescript
// 开始消费队列中的字符
start() {
  this.next(); // 调用next方法开始消费字符
}
```

**Purpose**: Public method to begin the typewriter animation.

**Return Value**: Void

**Usage**: Called after adding text to queue to start animation

### Cleanup and Control

#### onRendered Method
```typescript
// 渲染完成后的清理工作
onRendered() {
  if (this.timer) clearTimeout(this.timer); // 清除定时器，防止继续消费字符
}
```

**Purpose**: Cleans up active timers to stop animation and prevent memory leaks.

**Use Cases**:
- Component unmounting
- Text content changes
- Animation interruption
- Manual stop requests

#### onClearQueueList Method
```typescript
// 清空队列并停止当前的消费过程
onClearQueueList() {
  this.queueList = []; // 清空字符队列
  if (this.timer) clearTimeout(this.timer); // 清除定时器
}
```

**Purpose**: Completely resets the animation state by clearing queue and timers.

**Features**:
- **Queue Reset**: Empties all pending characters
- **Timer Cleanup**: Stops current animation
- **Complete Reset**: Returns to initial state

## Animation Flow

### Typical Usage Pattern
1. **Instantiate**: Create TypeWriterCore with callback
2. **Add Text**: Call `add(text)` to queue characters
3. **Start Animation**: Call `start()` to begin processing
4. **Character Processing**: Core consumes characters with dynamic timing
5. **Callback Execution**: Each character triggers onConsume callback
6. **UI Updates**: Callback typically updates React state or DOM
7. **Cleanup**: Call `onRendered()` when done or changing text

### Performance Characteristics

#### Dynamic Speed Benefits
- **Responsive Animation**: Adapts to content length
- **User Experience**: Balances speed with readability
- **Queue Management**: Prevents excessive buildup

#### Memory Management
- **Timer Cleanup**: Prevents memory leaks
- **Queue Limits**: Implicit through speed calculation
- **Efficient Processing**: FIFO queue for optimal performance

### Cross-Platform Compatibility

#### Timer Handling
```typescript
timer: NodeJS.Timeout | number | undefined;
```

**Features**:
- **Node.js Compatibility**: Supports NodeJS.Timeout type
- **Browser Compatibility**: Supports number return type
- **TypeScript Safety**: Proper typing for both environments

## Integration Considerations

### Callback Design
- **Pure Function**: onConsume should be side-effect focused
- **State Updates**: Typically updates external state (React, DOM)
- **Error Handling**: Should handle callback errors gracefully

### Performance Optimization
- **Dynamic Timing**: Reduces unnecessary delays
- **Queue Management**: Efficient character processing
- **Timer Cleanup**: Prevents resource leaks

### Use Cases
- **Typewriter Effects**: Progressive text reveal
- **Loading Messages**: Dynamic status updates
- **Chat Interfaces**: Message streaming simulation
- **Onboarding**: Step-by-step text guidance

## Dependencies
- **None**: Pure TypeScript/JavaScript implementation
- **Browser APIs**: setTimeout/clearTimeout
- **Node.js Compatibility**: Works in both environments

**Design Patterns**:
- **Observer Pattern**: Callback-based character consumption
- **Queue Pattern**: FIFO character processing
- **Strategy Pattern**: Dynamic speed calculation
- **Lifecycle Management**: Start/stop/cleanup methods

**Notes**:
- Framework-agnostic design for maximum reusability
- Intelligent speed adjustment for better user experience
- Comprehensive cleanup methods for proper resource management
- Chinese comments throughout for documentation
- Robust timer handling for cross-platform compatibility
- Efficient character processing with minimal overhead