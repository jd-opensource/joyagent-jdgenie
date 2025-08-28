# main.tsx Code Documentation

## File Summary
The main entry point file for the React application. This file handles the application bootstrapping, DOM rendering, and initial React setup using React 18's new createRoot API.

## Key Components and Functions

### Application Bootstrap
```typescript
const root = document.getElementById('root');

if (root) {
  createRoot(root).render(
    <App />
  );
} else {
  console.error('Root element not found');
}
```

**Purpose**: Initializes the React application and renders the root App component into the DOM.

**Key Features**:
- Uses React 18's `createRoot` API instead of the legacy `ReactDOM.render`
- Includes error handling for missing root DOM element
- Strict mode is commented out (Chinese comment indicates temporary removal)
- Imports global CSS styles

**Props/Parameters**: None (entry point file)

**Return Value**: Void - renders the application to DOM

**Key Logic**: 
1. Locates the root DOM element with id 'root'
2. Creates a React root using the new concurrent rendering API
3. Renders the App component without StrictMode wrapper
4. Provides error logging if root element is not found

**React Hooks Used**: None (this is the bootstrap file)

**Dependencies**:
- `react-dom/client` - For React 18's createRoot API
- `./App` - The main application component
- `./global.css` - Global styling

**Notes**:
- StrictMode is intentionally disabled (commented out with Chinese explanation)
- Uses modern React 18 rendering patterns
- Simple error handling for DOM mounting failures