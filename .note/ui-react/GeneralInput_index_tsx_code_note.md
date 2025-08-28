# GeneralInput/index.tsx Code Documentation

## File Summary
The GeneralInput component provides a sophisticated text input interface for chat interactions. It features auto-resizing textarea, keyboard shortcuts, product type indicators, deep research toggle, and send functionality. The component handles composition events for internationalization and provides smooth UX for message input.

## Key Components and Functions

### GeneralInput Component
```typescript
const GeneralInput: GenieType.FC<Props> = (props) => {
  const { placeholder, showBtn, disabled, product, send } = props;
  const [question, setQuestion] = useState<string>("");
  const [deepThink, setDeepThink] = useState<boolean>(false);
  const textareaRef = useRef<TextAreaRef>(null);
  const tempData = useRef<{
    cmdPress?: boolean;
    compositing?: boolean;
  }>({});
  // ... component logic
};
```

**Purpose**: Provides a rich text input interface with keyboard shortcuts, product selection, and advanced input handling.

**Props/Parameters**:
- `placeholder: string` - Placeholder text for the input field
- `showBtn: boolean` - Whether to show additional UI buttons and features
- `disabled: boolean` - Whether the input is disabled
- `size: string` - Size variant of the input
- `product?: CHAT.Product` - Current product/agent type configuration
- `send: (p: CHAT.TInputInfo) => void` - Callback function to send message

**Return Value**: JSX element containing the complete input interface

**State Management**:
- `question: string` - Current input text value
- `deepThink: boolean` - Toggle state for deep research mode
- `textareaRef` - Reference to the textarea element for direct DOM manipulation
- `tempData` - Temporary state for keyboard and composition handling

**React Hooks Used**:
- `useState` - For managing input text and deep think state
- `useRef` - For textarea reference and temporary data storage
- `useMemo` - For computing enter key help text

### questionChange Function
```typescript
const questionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  setQuestion(e.target.value);
};
```

**Purpose**: Handles input text changes and updates state.

**Parameters**:
- `e: React.ChangeEvent<HTMLTextAreaElement>` - Input change event

**Return Value**: Void

**Key Logic**: Simple state update for controlled input

### changeThinkStatus Function
```typescript
const changeThinkStatus = () => {
  setDeepThink(!deepThink);
};
```

**Purpose**: Toggles the deep research mode on/off.

**Parameters**: None

**Return Value**: Void

**Key Logic**: Toggles boolean state for deep thinking feature

### pressEnter Function
```typescript
const pressEnter: React.KeyboardEventHandler<HTMLTextAreaElement> = () => {
  if (tempData.current.compositing) {
    return;
  }
  // 按住command 回车换行逻辑
  if (tempData.current.cmdPress) {
    const textareaDom = textareaRef.current?.resizableTextArea?.textArea;
    if (!textareaDom) {
      return;
    }
    const { selectionStart, selectionEnd } = textareaDom || {};
    const newValue =
      question.substring(0, selectionStart) +
      '\n' + // 插入换行符
      question.substring(selectionEnd!);

    setQuestion(newValue);
    setTimeout(() => {
      textareaDom.selectionStart = selectionStart! + 1;
      textareaDom.selectionEnd = selectionStart! + 1;
      textareaDom.focus();
    }, 20);
    return;
  }
  // 屏蔽状态，不发
  if (!question || disabled) {
    return;
  }
  send({
    message: question,
    outputStyle: product?.type,
    deepThink,
  });
  setQuestion("");
};
```

**Purpose**: Handles Enter key press with support for line breaks (Cmd/Ctrl+Enter) and message sending.

**Parameters**: Implicit keyboard event handler

**Return Value**: Void

**Key Logic**:
1. **Composition Check**: Prevents action during IME composition (important for Asian languages)
2. **Line Break Mode**: Cmd/Ctrl+Enter inserts newline at cursor position
3. **Send Mode**: Plain Enter sends message if not empty/disabled
4. **Cursor Management**: Maintains cursor position after newline insertion
5. **State Cleanup**: Clears input after sending

### sendMessage Function
```typescript
const sendMessage = () => {
  send({
    message: question,
    outputStyle: product?.type,
    deepThink,
  });
  setQuestion("");
};
```

**Purpose**: Sends the current message via button click.

**Parameters**: None

**Return Value**: Void

**Key Logic**: Creates message object with current state and clears input

### enterTip Computed Value
```typescript
const enterTip = useMemo(() => {
  return `⏎发送，${getOS() === 'Mac' ? '⌘' : '^'} + ⏎ 换行`;
}, []);
```

**Purpose**: Generates platform-specific keyboard shortcut hint text.

**Parameters**: None (dependencies: empty array)

**Return Value**: String with appropriate keyboard symbols

**Key Logic**: Detects OS and shows Mac (⌘) or Windows/Linux (^) modifier keys

## Keyboard Event Handling

### Key Down Handler
```typescript
onKeyDown={(event) => {
  tempData.current.cmdPress = event.metaKey || event.ctrlKey;
}}
```

**Purpose**: Tracks modifier key state for line break functionality.

### Key Up Handler
```typescript
onKeyUp={() => {
  tempData.current.cmdPress = false;
}}
```

**Purpose**: Resets modifier key state when keys are released.

### Composition Event Handlers
```typescript
onCompositionStart={() => {
  tempData.current.compositing = true;
}}
onCompositionEnd={() => {
  tempData.current.compositing = false;
}}
```

**Purpose**: Handles IME (Input Method Editor) composition for international text input.

**Key Features**:
- Prevents premature Enter key handling during character composition
- Essential for Chinese, Japanese, Korean text input
- Ensures proper character formation before processing

## UI Structure

### Container with Gradient Border (Conditional)
```typescript
<div
  className={
    showBtn
      ? "rounded-[12px] bg-[linear-gradient(to_bottom_right,#4040ff,#ff49fd,#d763fc,#3cc4fa)] p-1"
      : ""
  }
>
```

**Purpose**: Provides attractive gradient border when showBtn is true.

### Input Container
```typescript
<div className="rounded-[12px] border border-[#E9E9F0] overflow-hidden p-[12px] bg-[#fff]">
```

**Purpose**: Main input area with consistent styling and padding.

### TextArea Element
```typescript
<TextArea
  ref={textareaRef}
  value={question}
  placeholder={placeholder}
  className={classNames(
    "h-62 no-border-textarea border-0 resize-none p-[0px] focus:border-0 bg-[#fff]",
    showBtn && product ? "indent-86" : ""
  )}
  onChange={questionChange}
  onPressEnter={pressEnter}
  // ... event handlers
/>
```

**Features**:
- Auto-resizing textarea (height: 62px base)
- No border styling for seamless integration
- Conditional indentation when product selector is shown
- Comprehensive event handling

### Product Type Indicator (Conditional)
```typescript
{showBtn && product ? (
  <div className="h-[24px] w-[80px] absolute top-0 left-0 flex items-center justify-center rounded-[6px] bg-[#f4f4f9] text-[12px] ">
    <i className={`font_family ${product.img} ${product.color} text-14`}></i>
    <div className="ml-[6px]">{product.name}</div>
  </div>
) : null}
```

**Purpose**: Shows current AI agent type with icon and name.

### Bottom Controls Bar
```typescript
<div className="h-30 flex justify-between items-center mt-[6px]">
  {showBtn ? (
    <Button
      color={deepThink ? "primary" : "default"}
      variant="outlined"
      className={...}
      onClick={changeThinkStatus}
    >
      <i className="font_family icon-shendusikao"></i>
      <span className="ml-[-4px]">深度研究</span>
    </Button>
  ) : (
    <div></div>
  )}
  <div className="flex items-center">
    <span className="text-[12px] text-gray-300 mr-8 flex items-center">
      {enterTip}
    </span>
    <Tooltip title="发送">
      <i
        className={`font_family icon-fasongtianchong ${!question || disabled ? "cursor-not-allowed text-[#ccc] pointer-events-none" : "cursor-pointer"}`}
        onClick={sendMessage}
      />
    </Tooltip>
  </div>
</div>
```

**Features**:
- Deep research toggle button (when showBtn is true)
- Keyboard shortcut hint
- Send button with disabled state styling
- Tooltip for accessibility

## Styling and UX Features

**Responsive Design**:
- Flexible height with auto-resize
- Proper spacing and padding
- Consistent border radius (12px)

**Interactive States**:
- Focus states for accessibility
- Disabled states with visual feedback
- Hover effects on clickable elements

**Visual Hierarchy**:
- Gradient borders for emphasis
- Product type indicators
- Clear send button with tooltip

**Internationalization Support**:
- Composition event handling for IME
- Platform-specific keyboard shortcuts
- Flexible text rendering

## Dependencies
- `react` - Core hooks and types
- `antd` - Input.TextArea, Button, Tooltip components
- `classnames` - Conditional CSS class handling
- Internal utilities (getOS for platform detection)

**Performance Optimizations**:
- useMemo for computed values
- Ref-based temporary data to avoid re-renders
- Efficient event handling

**Notes**:
- Sophisticated keyboard handling for power users
- Full internationalization support with composition events
- Rich visual design with gradient effects
- Accessible with tooltips and proper states
- Chinese language UI elements ("深度研究" = Deep Research)