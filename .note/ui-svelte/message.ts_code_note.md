# message.ts Store Code Documentation

## File Summary
This module provides a comprehensive toast notification system using Svelte stores, implementing message queuing, automatic dismissal, and a unified API for displaying user feedback messages. It bridges the gap between utility functions and UI components, offering both store-based and utility-style interfaces for maximum flexibility.

## Module Structure

### Imports and Dependencies
- **Svelte Stores**: `writable`, `get` for reactive state management
- **Type Imports**: `MessageApi` type from utils for interface compatibility

## Type Definitions

### `ToastMessage` Type
```typescript
export type ToastMessage = {
  id: string;
  type: 'info' | 'success' | 'error' | 'warning';
  message: string;
  duration?: number;
};
```

#### Properties:
- **`id: string`**: Unique identifier for each toast message
- **`type`**: Categorizes the message for styling and behavior
  - `'info'`: Informational messages (blue styling typically)
  - `'success'`: Success confirmations (green styling)
  - `'error'`: Error notifications (red styling)  
  - `'warning'`: Warning alerts (yellow/orange styling)
- **`message: string`**: The actual text content to display
- **`duration?: number`**: Optional auto-dismiss time in milliseconds

## Core Store

### `toastMessages: writable<ToastMessage[]>`
- **Purpose**: Maintains the queue of active toast messages
- **Initial Value**: Empty array `[]`
- **Content**: Array of toast message objects currently displayed
- **Reactivity**: Updates trigger UI re-renders in toast components

## Core Functions

### `addToast(type, message, duration): string`
- **Purpose**: Creates and adds a new toast message to the queue
- **Parameters**:
  - `type: ToastMessage['type']` - Message category (info/success/error/warning)
  - `message: string` - Text content to display
  - `duration: number = 3000` - Auto-dismiss time (default 3 seconds)
- **ID Generation**: `toast-${Date.now()}-${Math.random()}`
  - Uses timestamp and random number for uniqueness
  - Prevents collisions in rapid-fire messaging scenarios
- **Process**:
  1. Generates unique ID
  2. Creates toast object with provided properties
  3. Adds to store using `toastMessages.update()`
  4. Sets up auto-removal timer if duration > 0
  5. Returns ID for manual removal if needed

#### Auto-Removal Logic:
```typescript
if (duration > 0) {
  setTimeout(() => {
    removeToast(id);
  }, duration);
}
```
- **Conditional**: Only sets timer if duration is positive
- **Zero Duration**: Messages persist until manually removed
- **Cleanup**: Automatically removes message after specified time

### `removeToast(id: string): void`
- **Purpose**: Removes a specific toast message from the queue
- **Parameters**: `id` - Unique identifier of the toast to remove
- **Implementation**: `toastMessages.update(messages => messages.filter(m => m.id !== id))`
- **Usage**: Manual dismissal or automatic cleanup
- **Reactivity**: Update triggers UI re-render to hide the toast

## API Implementations

### `messageApi: MessageApi`
- **Purpose**: Provides utility-compatible interface for message operations
- **Pattern**: Object with methods matching the MessageApi interface
- **Implementation**:
  ```typescript
  export const messageApi: MessageApi = {
    info: (msg: string) => addToast('info', msg),
    success: (msg: string) => addToast('success', msg),
    error: (msg: string) => addToast('error', msg),
    warning: (msg: string) => addToast('warning', msg),
  };
  ```

#### Method Details:
- **`info(msg: string)`**: Creates informational toast with default 3s duration
- **`success(msg: string)`**: Creates success toast with default 3s duration  
- **`error(msg: string)`**: Creates error toast with default 3s duration
- **`warning(msg: string)`**: Creates warning toast with default 3s duration

### `message` Export Object
- **Purpose**: Enhanced API with additional functionality
- **Structure**:
  ```typescript
  export const message = {
    info: messageApi.info,
    success: messageApi.success,
    error: messageApi.error,
    warning: messageApi.warning,
    remove: removeToast
  };
  ```
- **Enhancement**: Includes `remove` function for manual toast dismissal
- **Compatibility**: Maintains compatibility with messageApi interface

## Usage Patterns

### Basic Toast Creation
```typescript
// Using messageApi
messageApi.success('Operation completed successfully!');
messageApi.error('Something went wrong');

// Using enhanced message object
message.info('Loading data...');
message.warning('Please save your work');
```

### Manual Toast Management
```typescript
// Create toast and get ID for later removal
const toastId = addToast('info', 'Processing...', 0); // 0 = no auto-remove

// Later, manually remove
message.remove(toastId);
```

### Custom Duration
```typescript
// Long-duration error message
addToast('error', 'Critical system error', 10000); // 10 seconds

// Persistent message (manual removal only)
addToast('info', 'Connection status: Online', 0); // No auto-dismiss
```

### Store Subscription (in components)
```typescript
// Subscribe to toast messages
$: messages = $toastMessages;

// React to changes
$: if (messages.length > 0) {
  // Handle toast display
}
```

## Integration Points

### Utility Integration
- **setMessage()**: Utils can use `messageApi` for consistent messaging
- **Global Access**: Available throughout application via utils
- **Type Compatibility**: Matches expected MessageApi interface

### Component Integration
- **Toast Component**: Subscribes to `toastMessages` store
- **Reactive Display**: Automatically shows/hides based on store state
- **Event Handling**: Components can trigger removal via `message.remove()`

### Layout Integration
- **Global Placement**: Toast component included in layout
- **Z-index Management**: Toasts appear above all other content
- **Positioning**: Fixed positioning for consistent placement

## Key Features

### Automatic Management
- **Auto-dismiss**: Configurable timeout for automatic removal
- **Unique IDs**: Prevents duplicate or conflicting messages
- **Queue Management**: Handles multiple simultaneous messages

### Type Safety
- **TypeScript**: Full type safety for message properties
- **Interface Compliance**: Matches utility interface requirements
- **Compile-time Validation**: Catches type errors during development

### Flexible API
- **Multiple Interfaces**: Store-based and utility-style access
- **Custom Durations**: Override default auto-dismiss timing
- **Manual Control**: Option to remove messages programmatically

### Performance Considerations
- **Efficient Updates**: Uses filter for removal to create new array
- **Memory Management**: Auto-removal prevents message accumulation
- **Reactive Updates**: Only affected components re-render

## Architecture Benefits

### Separation of Concerns
- **Store Layer**: Pure state management
- **API Layer**: Business logic and convenience methods
- **UI Layer**: Display and interaction handling

### Extensibility
- **New Message Types**: Easy to add additional toast types
- **Custom Styling**: Type-based styling in UI components
- **Enhanced Features**: Additional methods can be added to message object

### Testing
- **Unit Testable**: Core functions can be tested independently
- **Store Testing**: Svelte testing utilities can validate store behavior
- **Mock Friendly**: MessageApi interface enables easy mocking

This message store provides a robust, type-safe foundation for user notifications with flexible APIs, automatic management, and seamless integration with both utility functions and UI components.