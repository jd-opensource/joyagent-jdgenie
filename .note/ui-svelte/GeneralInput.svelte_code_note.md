# GeneralInput.svelte Code Documentation

## File Summary
This is a comprehensive input component that handles user message composition with advanced features including file attachments, deep thinking mode, keyboard shortcuts, and dynamic styling. It provides a rich text input experience with support for multi-line content, file management, and various input modes while maintaining responsive design and accessibility features.

## Component Structure

### Imports and Dependencies
- **Svelte Imports**: `onMount` for component initialization
- **Component Imports**: `AttachmentList` for file display and management
- **Utility Imports**: `getOS` for operating system detection
- **Type Imports**: Chat type definitions

### Props

#### `placeholder: string = 'Enter your message...'`
- **Purpose**: Placeholder text for the textarea
- **Default**: Generic input message
- **Usage**: Customized based on context (landing page vs. chat)

#### `showBtn: boolean = true`
- **Purpose**: Controls visibility of the send button
- **Default**: `true` - button is shown by default
- **Usage**: May be hidden in certain input contexts

#### `disabled: boolean = false`
- **Purpose**: Disables the entire input component
- **Default**: `false` - input is enabled by default
- **Usage**: Disabled during AI response generation

#### `size: 'small' | 'big' = 'small'`
- **Purpose**: Controls the visual size/scale of the input
- **Values**: 
  - `'small'`: Compact input for chat conversations
  - `'big'`: Larger input for the main landing page
- **Default**: `'small'`

#### `product: CHAT.Product | undefined = undefined`
- **Purpose**: Product context for the input
- **Usage**: Provides context for message processing and output style

#### `send: (info: CHAT.TInputInfo) => void = () => {}`
- **Purpose**: Callback function triggered when message is sent
- **Parameters**: `TInputInfo` object containing message, files, and options
- **Default**: Empty function (no-op)

#### `className: string = ''`
- **Purpose**: Additional CSS classes for customization
- **Default**: Empty string

## State Variables

### Input Content
#### `question: string`
- **Purpose**: Main message content from the textarea
- **Binding**: Two-way bound to textarea element
- **Usage**: Core user input text

#### `files: File[]`
- **Purpose**: Array of attached files
- **Management**: Added via file input, removed via attachment list
- **Reset**: Cleared after message send

### Input Modes
#### `deepThink: boolean`
- **Purpose**: Toggle for deep thinking mode
- **UI**: Rendered as toggle button with brain icon
- **Effect**: Changes message processing behavior

### UI State
#### `isComposing: boolean`
- **Purpose**: Tracks IME (Input Method Editor) composition state
- **Usage**: Prevents Enter key handling during text composition
- **Important**: Critical for non-Latin input methods (Chinese, Japanese, etc.)

#### `cmdPressed: boolean`
- **Purpose**: Tracks Command/Ctrl key state
- **Usage**: Enables keyboard shortcuts (Cmd/Ctrl + Enter for newline)

### Element References
#### `textarea: HTMLTextAreaElement`
- **Purpose**: Direct reference to textarea DOM element
- **Usage**: Cursor positioning, focus management, programmatic text insertion

#### `fileInput: HTMLInputElement`
- **Purpose**: Hidden file input element reference
- **Usage**: Triggered programmatically via attachment button

## Utility Variables

#### `enterTip: string`
- **Purpose**: Dynamic help text showing keyboard shortcuts
- **Logic**: `⏎发送，${getOS() === 'Mac' ? '⌘' : '^'} + ⏎ 换行`
- **Translation**: "Enter to send, Cmd/Ctrl + Enter for new line"
- **Adaptation**: Shows appropriate modifier key based on operating system

## Core Functions

### Keyboard Event Handling

#### `handleKeyDown(e: KeyboardEvent): void`
- **Purpose**: Handles keyboard shortcuts and special key combinations
- **Key Logic**:
  - **Command/Ctrl Detection**: Sets `cmdPressed = true` when meta/control keys are pressed
  - **Enter Key Handling** (when not composing):
    - **With Command/Ctrl**: Inserts newline at cursor position
    - **Without Command/Ctrl**: Sends message if content exists and not disabled
- **Newline Insertion Process**:
  1. Prevents default Enter behavior
  2. Gets current cursor position
  3. Inserts newline at cursor location
  4. Restores cursor position after newline
- **Send Logic**: Only sends if `question` has content and component isn't disabled

#### `handleKeyUp(e: KeyboardEvent): void`
- **Purpose**: Resets command/control key state
- **Logic**: Sets `cmdPressed = false` when meta/control keys are released

### Message Management

#### `sendMessage(): void`
- **Purpose**: Processes and sends the complete message with all attachments and options
- **Validation**: Early return if no question or component is disabled
- **Data Collection**: 
  - Message text from `question`
  - Output style from `product.type`
  - Deep think mode from `deepThink`
  - File attachments from `files` array
- **Callback**: Invokes `send()` prop function with formatted `TInputInfo` object
- **Cleanup**: 
  - Clears question text
  - Resets files array
  - Resets deep think mode

### File Management

#### `handleFileSelect(e: Event): void`
- **Purpose**: Processes file selection from file input
- **Process**:
  1. Extracts files from input event
  2. Appends new files to existing files array (preserves previous selections)
  3. Clears input value to allow re-selection of same files
- **File Handling**: Uses spread operator to create new array (maintains reactivity)

#### `removeFile(index: number): void`
- **Purpose**: Removes specific file from attachments
- **Logic**: Uses `filter()` to create new array excluding item at specified index
- **Reactivity**: Creates new array reference for Svelte reactivity

### UI Interactions

#### `toggleDeepThink(): void`
- **Purpose**: Toggles the deep thinking mode state
- **Logic**: Simple boolean toggle: `deepThink = !deepThink`
- **UI Effect**: Changes toggle button appearance and behavior

## Component Lifecycle

### `onMount(() => { textarea?.focus(); })`
- **Purpose**: Sets focus to textarea when component mounts
- **Behavior**: Automatic focus for immediate user input
- **Conditional**: Uses optional chaining to avoid errors if ref isn't ready

## Template Structure

### Container Architecture
#### Outer Container
- **Conditional Gradient**: Applied only when `showBtn` is true
- **Classes**: `rounded-[12px] bg-gradient-to-br from-[#4040ff] via-[#ff49fd] via-[#d763fc] to-[#3cc4fa] p-1`
- **Effect**: Creates colorful gradient border effect

#### Inner Container  
- **Classes**: `rounded-[12px] border border-[#E9E9F0] overflow-hidden p-12 bg-white`
- **Purpose**: White content area with border and padding

### Main Input Area
#### Textarea Element
- **Binding**: `bind:this={textarea}` and `bind:value={question}`
- **Properties**:
  - Dynamic placeholder text
  - Disabled state handling
  - Key event handlers
  - Composition event handlers (for IME support)
- **Styling**:
  - Size-dependent: `text-base` for big, `text-sm` for small
  - Disabled styling: `cursor-not-allowed opacity-50`
  - Full width and height: `w-full h-62`
  - No resize: `resize-none`

#### Attachment Display
- **Component**: `<AttachmentList {files} onRemove={removeFile} />`
- **Purpose**: Shows selected files with remove functionality

### Control Bar
#### Left Side Controls
- **File Attachment Button**:
  - Trigger: `on:click={() => fileInput?.click()}`
  - Icon: Paperclip icon (`icon-paperclip`)
  - Disabled state handling
  
- **Deep Think Toggle**:
  - Toggle: `on:click={toggleDeepThink}`
  - Dynamic styling: Primary color when active, gray when inactive
  - Icon: Brain icon (`icon-brain`)
  - Text: "深度思考" (Deep thinking)

#### Right Side Controls
- **Help Text**: Shows keyboard shortcuts (`enterTip`)
- **Send Button** (conditional on `showBtn`):
  - Trigger: `on:click={sendMessage}`
  - Disabled when: No question content or component disabled
  - Styling: Primary color with disabled state handling
  - Text: "发送" (Send)

### Hidden Elements
#### File Input
- **Element**: `<input type="file" multiple />`
- **Visibility**: `class="hidden"` - Completely hidden
- **Trigger**: Activated via attachment button click
- **Handler**: `on:change={handleFileSelect}`

## Styling and Design

### Size Variations
- **Big**: Larger text (`text-base`) for prominence on landing page
- **Small**: Smaller text (`text-sm`) for compact chat interface

### State-Based Styling
- **Disabled**: Reduced opacity and cursor changes
- **Deep Think Active**: Primary color background and white text
- **Deep Think Inactive**: Gray background and text
- **Gradient Border**: Applied conditionally based on `showBtn` prop

### Interactive Feedback
- **Hover Effects**: Subtle background changes on buttons
- **Focus States**: Textarea focus outline
- **Transition Effects**: Smooth color transitions on interactive elements

## Accessibility Features

### Keyboard Support
- **Enter/Cmd+Enter**: Standard and alternate send methods
- **Tab Navigation**: Proper tab order through controls
- **Focus Management**: Auto-focus and manual focus control

### Screen Reader Support
- **Labels**: Title attributes for icon buttons
- **State Information**: Visual and semantic state indicators
- **File Information**: Accessible file attachment display

## Key Svelte Patterns

### Two-Way Data Binding
- **Textarea**: `bind:value={question}` for automatic content synchronization
- **Element References**: `bind:this={textarea}` for DOM access

### Event Handling
- **Keyboard Events**: `on:keydown`, `on:keyup` with custom logic
- **Composition Events**: `on:compositionstart/end` for IME support
- **Click Events**: Button interactions with state changes

### Conditional Rendering
- **Send Button**: Based on `showBtn` prop
- **Gradient Border**: Based on button visibility
- **Disabled States**: Dynamic styling based on disabled prop

### Component Communication
- **Props Down**: Configuration and context from parent
- **Events Up**: Send callback with structured data
- **Child Components**: File attachment list integration

This component provides a comprehensive, accessible, and feature-rich input experience that handles the complexity of modern message composition while maintaining clean code architecture and excellent user experience.