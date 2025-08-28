# querySSE.ts Utils Code Documentation

## File Summary
This utility module provides a simplified, direct interface for Server-Sent Events (SSE) communication, offering a streamlined alternative to the service layer implementation. It uses the Microsoft fetch-event-source library to establish streaming connections with minimal configuration while maintaining the core functionality needed for real-time chat communication.

## Module Structure

### Imports and Dependencies
- **Microsoft Fetch Event Source**: 
  - `fetchEventSource`: Core function for establishing SSE connections
  - `EventSourceMessage`: Type definition for incoming messages
- **Global Configuration**: Uses `SERVICE_BASE_URL` environment variable

### Configuration Constants

#### `customHost: string`
- **Purpose**: Base URL for API endpoints
- **Logic**: `SERVICE_BASE_URL || ''` - Uses environment variable or empty string
- **Fallback**: Empty string when environment variable not defined
- **Usage**: Allows environment-specific API endpoints

#### `DEFAULT_SSE_URL: string`
- **Value**: `${customHost}/web/api/v1/gpt/queryAgentStreamIncr`
- **Purpose**: Default SSE endpoint for chat communication
- **Pattern**: RESTful API path indicating streaming capability

#### `SSE_HEADERS: object`
- **Purpose**: Standard HTTP headers for SSE requests
- **Configuration**:
  ```typescript
  {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Accept': 'text/event-stream'
  }
  ```
- **Headers Explained**:
  - **Content-Type**: JSON payload format
  - **Cache-Control**: Prevents response caching for real-time data
  - **Connection**: Maintains persistent HTTP connection
  - **Accept**: Specifies expected response format as event stream

## Interface Definition

### `SSEConfig` Interface
```typescript
interface SSEConfig {
  body: any;
  handleMessage: (data: any) => void;
  handleError: (error: Error) => void;
  handleClose: () => void;
}
```

#### Interface Properties:
- **`body: any`**: Request payload sent to server (JSON serializable)
- **`handleMessage`**: Callback for processing incoming SSE messages
- **`handleError`**: Error handler for connection and parsing errors
- **`handleClose`**: Callback for connection closure events

## Main Export Function

### `default(config: SSEConfig, url?: string): void`
- **Purpose**: Creates SSE connection with simplified interface
- **Parameters**:
  - `config: SSEConfig` - Configuration with callbacks and payload
  - `url: string = DEFAULT_SSE_URL` - Optional custom endpoint
- **Return Type**: `void` - Fire-and-forget connection establishment
- **Usage**: Direct connection creation without lifecycle management

## Function Implementation

### Parameter Extraction
```typescript
const { body = null, handleMessage, handleError, handleClose } = config;
```
- **Destructuring**: Extracts configuration properties
- **Default Values**: `body` defaults to `null` if not provided
- **Required Callbacks**: Handler functions must be provided

### Connection Establishment
```typescript
fetchEventSource(url, {
  method: 'POST',
  credentials: 'include',
  headers: SSE_HEADERS,
  body: JSON.stringify(body),
  openWhenHidden: true,
  // Event handlers...
});
```

#### Configuration Properties:
- **`method: 'POST'`**: HTTP method for initial handshake
- **`credentials: 'include'`**: Include cookies for authentication
- **`headers: SSE_HEADERS`**: Standardized headers for SSE
- **`body: JSON.stringify(body)`**: Serialized request payload
- **`openWhenHidden: true`**: Maintain connection when tab hidden

## Event Handlers

### `onmessage(event: EventSourceMessage): void`
- **Purpose**: Processes incoming data from the server
- **Process Flow**:
  1. Validates event data existence
  2. Attempts JSON parsing of message content
  3. Calls configured message handler with parsed data
  4. Handles JSON parsing errors gracefully

```typescript
onmessage(event: EventSourceMessage) {
  if (event.data) {
    try {
      const parsedData = JSON.parse(event.data);
      handleMessage(parsedData);
    } catch (error) {
      console.error('Error parsing SSE message:', error);
      handleError(new Error('Failed to parse SSE message'));
    }
  }
}
```

### `onerror(error: Error): void`
- **Purpose**: Handles connection errors and failures
- **Actions**:
  - Logs error details to console
  - Forwards error to configured error handler
- **Error Types**: Network failures, server errors, timeout issues

### `onclose(): void`
- **Purpose**: Handles connection closure events
- **Actions**:
  - Logs closure for debugging
  - Calls configured close handler
- **Triggers**: Normal completion, server shutdown, network interruption

## Key Differences from Service Implementation

### Simplified Interface
- **No Abort Controller**: Doesn't return connection control mechanism
- **Direct Execution**: Immediate connection establishment
- **Minimal Configuration**: Fewer configuration options

### Lifecycle Management
- **Fire-and-Forget**: No external connection control
- **Internal Management**: Connection lifecycle handled internally
- **Automatic Cleanup**: Relies on fetch-event-source library for cleanup

### Error Handling
- **Consistent Pattern**: Same error handling as service implementation
- **JSON Safety**: Safe JSON parsing with error forwarding
- **Logging**: Console logging for debugging purposes

## Usage Patterns

### Basic Connection
```typescript
querySSE({
  body: { query: 'Hello', sessionId: '123' },
  handleMessage: (data) => {
    // Process incoming message
    console.log('Received:', data);
  },
  handleError: (error) => {
    // Handle errors
    console.error('SSE Error:', error);
  },
  handleClose: () => {
    // Handle connection closure
    console.log('Connection closed');
  }
});
```

### Custom Endpoint
```typescript
querySSE(config, 'https://api.example.com/custom-stream');
```

### Real-time Chat Integration
```typescript
querySSE({
  body: {
    sessionId: currentSession,
    requestId: messageId,
    query: userMessage,
    deepThink: isDeepThinkMode ? 1 : 0
  },
  handleMessage: (data) => {
    // Update chat UI with streaming response
    updateChatWithResponse(data);
  },
  handleError: (error) => {
    // Show error toast
    showErrorMessage('Connection failed');
  },
  handleClose: () => {
    // Clean up loading states
    setLoading(false);
  }
});
```

## Integration Points

### Component Usage
- **ChatView**: Primary consumer for real-time chat updates
- **Direct Integration**: Called directly from components without service layer
- **Event-Driven**: Uses callback pattern for decoupled communication

### State Management
- **External State**: Callbacks update external state/stores
- **UI Updates**: Triggers reactive UI updates through handlers
- **Error Propagation**: Errors handled in calling components

## Performance Considerations

### Connection Efficiency
- **Persistent Connection**: Maintains long-lived HTTP connection
- **Minimal Overhead**: Direct connection without additional abstraction
- **Background Operation**: Continues when browser tab not active

### Memory Management
- **No External References**: Doesn't return objects that need cleanup
- **Internal Cleanup**: Relies on library for proper resource management
- **Event Handler Scope**: Callbacks maintain references as needed

## Security Features

### Authentication
- **Cookie Support**: Includes credentials for session-based auth
- **HTTPS Compatibility**: Works with secure connections
- **CORS Handling**: Proper cross-origin request handling

### Data Safety
- **JSON Validation**: Safe parsing prevents injection issues
- **Error Isolation**: Parsing errors don't crash the application
- **Input Sanitization**: Request body should be validated before calling

## Comparison with Service Implementation

### Advantages
- **Simplicity**: Fewer lines of code, direct usage
- **Lower Overhead**: No additional abstraction layer
- **Immediate Connection**: Direct connection establishment

### Trade-offs
- **Less Control**: No external connection lifecycle management
- **No Cancellation**: Cannot abort connections externally
- **Simpler Interface**: Fewer configuration options

### Use Cases
- **Simple Streaming**: When basic SSE functionality is sufficient
- **Prototype Development**: Quick implementation without full control
- **Fire-and-Forget**: When connection lifecycle isn't critical

## TypeScript Benefits

### Type Safety
- **Interface Contracts**: Clear callback signatures
- **Compile-time Checks**: Parameter validation during development
- **IDE Support**: Full autocomplete and error detection

### Documentation
- **Self-Documenting**: Types serve as inline documentation
- **API Clarity**: Clear expectations for function usage
- **Error Prevention**: Type checking prevents common mistakes

This utility provides a streamlined, direct approach to SSE connections that's suitable for simple use cases where connection lifecycle management isn't critical, offering a clean API that abstracts away the complexity of real-time communication while maintaining essential functionality.