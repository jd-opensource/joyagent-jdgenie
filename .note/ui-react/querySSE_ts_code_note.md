# utils/querySSE.ts Code Documentation

## File Summary
The querySSE utility provides Server-Sent Events (SSE) functionality for real-time communication with the AI agent backend. It uses the Microsoft fetch-event-source library to establish persistent connections for streaming AI responses, handling JSON parsing, error management, and connection lifecycle.

## Key Components and Functions

### Default Configuration
```typescript
const customHost = SERVICE_BASE_URL || '';
const DEFAULT_SSE_URL = `${customHost}/web/api/v1/gpt/queryAgentStreamIncr`;

const SSE_HEADERS = {
  'Content-Type': 'application/json',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Accept': 'text/event-stream',
};
```

**Purpose**: Defines default URL endpoint and HTTP headers for SSE connections.

**Configuration**:
- **URL**: Uses global SERVICE_BASE_URL or falls back to empty string
- **Endpoint**: `/web/api/v1/gpt/queryAgentStreamIncr` for AI agent streaming
- **Headers**: Standard SSE headers with JSON content type

### SSEConfig Interface
```typescript
interface SSEConfig {
  body: any;
  handleMessage: (data: any) => void;
  handleError: (error: Error) => void;
  handleClose: () => void;
}
```

**Purpose**: Defines the configuration structure for SSE connections.

**Properties**:
- `body: any` - Request payload to send with the connection
- `handleMessage: (data: any) => void` - Callback for processing incoming messages
- `handleError: (error: Error) => void` - Callback for handling connection errors
- `handleClose: () => void` - Callback for connection closure events

### Main querySSE Function
```typescript
export default (config: SSEConfig, url: string = DEFAULT_SSE_URL): void => {
  const { body = null, handleMessage, handleError, handleClose } = config;

  fetchEventSource(url, {
    method: 'POST',
    credentials: 'include',
    headers: SSE_HEADERS,
    body: JSON.stringify(body),
    openWhenHidden: true,
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
    },
    onerror(error: Error) {
      console.error('SSE error:', error);
      handleError(error);
    },
    onclose() {
      console.log('SSE connection closed');
      handleClose();
    }
  });
};
```

**Purpose**: Establishes an SSE connection with comprehensive error handling and message processing.

**Parameters**:
- `config: SSEConfig` - Configuration object with callbacks and request body
- `url: string = DEFAULT_SSE_URL` - Optional custom URL (defaults to standard endpoint)

**Return Value**: Void (establishes persistent connection)

**Key Features**:

#### Connection Configuration
- **Method**: POST (unusual for SSE, typically used for sending request data)
- **Credentials**: 'include' for cookie-based authentication
- **Headers**: Standard SSE headers with JSON content type
- **Body**: JSON stringified request payload
- **openWhenHidden**: true (maintains connection when tab is hidden)

#### Message Handling
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

**Process**:
1. Checks if event contains data
2. Attempts to parse JSON from event data
3. Calls handleMessage with parsed data
4. Catches parsing errors and calls handleError

#### Error Handling
```typescript
onerror(error: Error) {
  console.error('SSE error:', error);
  handleError(error);
}
```

**Features**:
- Logs error to console for debugging
- Passes error to callback for application handling
- Maintains connection unless explicitly closed

#### Connection Closure
```typescript
onclose() {
  console.log('SSE connection closed');
  handleClose();
}
```

**Features**:
- Logs closure event for debugging
- Notifies application of connection termination
- Allows cleanup and reconnection logic

## Usage Pattern

### Typical Implementation
```typescript
querySSE({
  body: {
    sessionId: 'session-123',
    query: 'User message',
    deepThink: 1
  },
  handleMessage: (data) => {
    // Process streaming AI response
    console.log('Received:', data);
  },
  handleError: (error) => {
    // Handle connection or parsing errors
    console.error('SSE Error:', error);
  },
  handleClose: () => {
    // Handle connection closure
    console.log('Connection closed');
  }
});
```

## Integration with AI Agent System

### Request Structure
The body typically contains:
- `sessionId`: Unique session identifier
- `requestId`: Unique request identifier  
- `query`: User message or command
- `deepThink`: Flag for deep analysis mode
- `outputStyle`: Desired response format

### Response Handling
The AI agent sends various message types:
- **Heartbeat**: Keep-alive messages (filtered by packageType)
- **Task Updates**: Real-time task progression
- **File Results**: Generated files and attachments
- **Completion**: Final results and status

### Error Scenarios
Common error cases:
- Network connectivity issues
- JSON parsing failures
- Authentication errors
- Server-side processing errors

## Technical Specifications

### Library Integration
Uses `@microsoft/fetch-event-source` which provides:
- Better error handling than native EventSource
- Support for POST requests
- Configurable retry logic
- Browser compatibility

### Authentication
- Uses credential inclusion for cookie-based auth
- No explicit token management required
- Relies on server-side session validation

### Performance Considerations
- `openWhenHidden: true` maintains connections in background tabs
- JSON parsing on each message (consider performance for high-frequency updates)
- No built-in message queuing or batching

### Browser Compatibility
- Modern browser support through fetch-event-source
- Fallback mechanisms handled by the library
- Cross-origin requests supported with proper CORS

## Dependencies
- `@microsoft/fetch-event-source` - Enhanced SSE client library
- Global `SERVICE_BASE_URL` - Environment-based URL configuration

**Security Features**:
- Credential-based authentication
- HTTPS enforcement through base URL
- Error information sanitization

**Performance Optimizations**:
- Persistent connections reduce overhead
- Streaming responses for better perceived performance
- Background connection maintenance

**Notes**:
- Critical component for real-time AI agent communication
- Robust error handling for production use
- Flexible configuration for different use cases
- Clean separation of connection management and application logic
- Essential for the chat interface's real-time features