# hooks/useTypeWriter.ts Code Documentation

## File Summary
The useTypeWriter hook provides a typewriter animation effect for text display. It creates a progressive character-by-character text reveal animation using a custom TypeWriterCore class. This hook is typically used for creating engaging text animations in the AI agent interface.

## Key Components and Functions

### UseWriterOptions Interface
```typescript
interface UseWriterOptions {
    maxStepSeconds?: number; // 将 maxStepSeconds 定义为可选的
}
```

**Purpose**: Defines configuration options for the typewriter animation.

**Properties**:
- `maxStepSeconds?: number` - Maximum delay between character reveals (optional)

### useTypeWriter Hook
```typescript
export const useTypeWriter = (
  {text, options}:{ text: string, options?: UseWriterOptions }
) => {
  const [typedText, setTypedText] = useState('');

  const typingCore = useMemo(
    () => new TypeWriterCore(
      {
        onConsume: (str: string) => setTypedText(prev => prev + str),
        ...options,
      }
    ),
    [options]
  );

  useEffect(
    () => {
      typingCore.onRendered(); // 渲染完成 => 清空定时器
      typingCore.add(text);
      typingCore.start();

      return () => typingCore.onRendered(); // 渲染完成 => 清空定时器
    },
    [text, typingCore]
  );

  return [typedText];
};
```

**Purpose**: React hook that provides typewriter animation functionality for text display.

**Parameters**:
- `text: string` - The text to animate with typewriter effect
- `options?: UseWriterOptions` - Optional configuration for animation timing

**Return Value**: `[string]` - Array containing the currently typed text

**React Hooks Used**:
- `useState` - For managing the currently displayed text
- `useMemo` - For creating stable TypeWriterCore instance
- `useEffect` - For managing animation lifecycle

### Core State Management
```typescript
const [typedText, setTypedText] = useState('');
```

**Purpose**: Maintains the currently visible text that builds up character by character.

**State Updates**: Updated through the onConsume callback when TypeWriterCore processes characters

### TypeWriterCore Instance Creation
```typescript
const typingCore = useMemo(
  () => new TypeWriterCore(
    {
      onConsume: (str: string) => setTypedText(prev => prev + str),
      ...options,
    }
  ),
  [options]
);
```

**Purpose**: Creates a stable instance of the TypeWriterCore animation engine.

**Configuration**:
- `onConsume` - Callback that appends characters to typedText state
- Spreads user-provided options for customization
- Memoized to prevent recreation on every render

**Key Features**:
- **State Integration**: Connects TypeWriterCore to React state
- **Character Accumulation**: Appends each character to existing text
- **Stable Reference**: useMemo prevents unnecessary recreations

### Animation Lifecycle Management
```typescript
useEffect(
  () => {
    typingCore.onRendered(); // 渲染完成 => 清空定时器
    typingCore.add(text);
    typingCore.start();

    return () => typingCore.onRendered(); // 渲染完成 => 清空定时器
  },
  [text, typingCore]
);
```

**Purpose**: Manages the animation lifecycle including start, cleanup, and restart on text changes.

**Animation Flow**:
1. **Initial Cleanup**: `onRendered()` clears any existing timers
2. **Text Addition**: `add(text)` queues the new text for animation
3. **Animation Start**: `start()` begins the character-by-character reveal
4. **Cleanup**: Return function clears timers on unmount or text change

**Dependencies**:
- `text` - Restarts animation when text changes
- `typingCore` - Restarts if core instance changes

### Hook Usage Pattern

#### Basic Usage
```typescript
const MyComponent = () => {
  const [displayText] = useTypeWriter({
    text: "Hello, World!",
    options: { maxStepSeconds: 100 }
  });

  return <div>{displayText}</div>;
};
```

#### Dynamic Text Updates
```typescript
const ChatMessage = ({ message }) => {
  const [animatedMessage] = useTypeWriter({
    text: message,
    options: { maxStepSeconds: 50 }
  });

  return <div className="chat-message">{animatedMessage}</div>;
};
```

## Integration with TypeWriterCore

### Character Processing Flow
1. **Text Input**: Hook receives text parameter
2. **Queue Addition**: Text is split into character queue
3. **Character Consumption**: Characters are processed one by one
4. **State Updates**: Each character triggers setTypedText update
5. **Progressive Display**: UI shows incremental text build-up

### Animation Control
- **Speed Control**: Configurable through maxStepSeconds option
- **Dynamic Speed**: TypeWriterCore adjusts speed based on queue length
- **Smooth Animation**: Uses setTimeout for consistent timing

### Memory Management
- **Timer Cleanup**: Proper cleanup prevents memory leaks
- **State Reset**: Text changes trigger fresh animation
- **Stable References**: useMemo prevents unnecessary recreations

## Performance Considerations

### Optimization Strategies
- **Memoized Core**: Prevents recreation of animation engine
- **Efficient State Updates**: Single state variable for text
- **Proper Cleanup**: Timers cleared on unmount and changes

### Re-render Behavior
- Hook only re-creates core when options change
- Text changes restart animation without recreation
- Minimal impact on parent component renders

### Animation Performance
- Character-by-character updates may cause frequent re-renders
- Consider debouncing for very long texts
- Animation speed affects user experience and performance

## Use Cases in AI Agent Interface

### Streaming AI Responses
- Animate AI agent responses as they arrive
- Create natural conversation flow
- Enhance user engagement with progressive reveal

### Status Messages
- Animate loading states and progress updates
- Create dynamic feedback for user actions
- Smooth transitions between different states

### Onboarding and Help Text
- Animate introduction messages
- Create engaging tutorial experiences
- Guide users through interface features

## Dependencies
- `react` - useState, useMemo, useEffect hooks
- `./TypeWriterCore` - Core animation engine class

**Customization Options**:
- Animation speed through maxStepSeconds
- Custom onConsume behavior (though not exposed in current API)
- Integration with TypeWriterCore's dynamic speed calculation

**Browser Compatibility**:
- Uses standard React hooks and setTimeout
- No special browser requirements
- Consistent behavior across platforms

**Notes**:
- Simple and focused hook design
- Clean integration between React state and animation engine
- Proper lifecycle management with cleanup
- Flexible configuration through options parameter
- Suitable for various text animation scenarios
- Chinese comments indicate cleanup operations ("渲染完成 => 清空定时器")