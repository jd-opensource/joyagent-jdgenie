# React to Svelte Migration Technical Plan

## Executive Summary

This document outlines a comprehensive plan to migrate the existing React-based Genie UI application to Svelte/SvelteKit. The application is a chat/AI assistant interface with real-time streaming capabilities, file handling, and complex state management.

## Current React Application Analysis

### Project Overview
- **Name**: genie-ui
- **Version**: 0.1.0
- **Build Tool**: Vite 6.1.0
- **Framework**: React 19.0.0 with TypeScript
- **Styling**: Tailwind CSS v4 + Ant Design (antd)
- **Routing**: React Router DOM v7.6.2
- **State Management**: React Context API + Local State + ahooks

### Key Dependencies to Replace

| React Dependency | Purpose | Svelte Alternative |
|-----------------|---------|-------------------|
| react, react-dom | Core framework | svelte, @sveltejs/kit |
| react-router-dom | Routing | SvelteKit routing (file-based) |
| antd | UI components | Custom components / shadcn-svelte / Carbon Components Svelte |
| ahooks | React hooks utilities | Custom stores / svelte utilities |
| react-markdown | Markdown rendering | svelte-markdown / marked + svelte |
| react-syntax-highlighter | Code highlighting | svelte-highlight / prism-svelte |
| react-frame-component | iframe wrapper | Custom Svelte component |
| react-lottie | Lottie animations | lottie-web + svelte wrapper |
| @microsoft/fetch-event-source | SSE handling | Same library (framework agnostic) |

### Application Structure

```
ui/
├── src/
│   ├── components/          # React components
│   │   ├── ActionPanel/     # Action display panel
│   │   ├── ActionView/      # Action viewer with frames
│   │   ├── AttachmentList/  # File attachments
│   │   ├── ChatView/        # Main chat interface
│   │   ├── Dialogue/        # Chat messages
│   │   ├── GeneralInput/    # Input component
│   │   ├── PlanView/        # Task planning view
│   │   └── ...             # Other UI components
│   ├── hooks/              # Custom React hooks
│   ├── layout/             # Layout components
│   ├── pages/              # Page components
│   ├── router/             # Routing configuration
│   ├── services/           # API services
│   ├── types/              # TypeScript definitions
│   └── utils/              # Utility functions
```

## Migration Strategy

### Phase 1: Project Setup and Foundation (Week 1)

#### 1.1 Initialize SvelteKit Project
```bash
npm create svelte@latest ui-svelte -- --template skeleton-typescript
```

#### 1.2 Configure Development Environment
- Set up TypeScript configuration matching React project
- Configure Vite settings for compatibility
- Set up path aliases (@/* -> src/*)
- Configure environment variables handling

#### 1.3 Set Up Styling System
- Install and configure Tailwind CSS v4
- Migrate global styles and CSS variables
- Set up custom fonts (RelayIcon)
- Configure PostCSS

#### 1.4 Install Core Dependencies
```json
{
  "dependencies": {
    "@sveltejs/kit": "^2.0.0",
    "svelte": "^4.0.0",
    "@microsoft/fetch-event-source": "^2.0.1",
    "axios": "^1.10.0",
    "dayjs": "^1.11.13",
    "lodash": "^4.17.21",
    "mermaid": "^11.8.1",
    "svelte-markdown": "^0.4.0",
    "highlight.js": "^11.0.0",
    "lottie-web": "^5.12.0"
  }
}
```

### Phase 2: Core Infrastructure (Week 2)

#### 2.1 TypeScript Types Migration
- Convert global type definitions to Svelte-compatible format
- Create type definition files for:
  - `$types/global.ts` - Global types
  - `$types/chat.ts` - Chat-related types
  - `$types/message.ts` - Message types

#### 2.2 Utility Functions
- Direct migration (framework-agnostic):
  - `/utils/constants.ts`
  - `/utils/enums.ts`
  - `/utils/utils.ts`
  - `/utils/chat.ts`
- Adapt for Svelte:
  - `/utils/querySSE.ts` - Ensure compatibility with Svelte stores

#### 2.3 API Services Layer
- Migrate `/services/index.ts` - Base API client
- Migrate `/services/agent.ts` - Agent-specific APIs
- Create Svelte stores for API state management

#### 2.4 State Management Architecture
Replace React Context with Svelte stores:

```typescript
// stores/constants.ts
import { writable } from 'svelte/store';
import * as constants from '$lib/utils/constants';

export const constantsStore = writable(constants);

// stores/chat.ts
import { writable, derived } from 'svelte/store';

export const chatList = writable<CHAT.ChatItem[]>([]);
export const activeTask = writable<CHAT.Task>();
export const plan = writable<CHAT.Plan>();
```

### Phase 3: Component Migration (Weeks 3-4)

#### 3.1 Component Conversion Priority

**Tier 1 - Foundation Components** (Week 3, Day 1-2):
- `Logo` - Simple static component
- `LoadingDot` - CSS animation component
- `LoadingSpinner` - Loading indicator
- `NotFound` - 404 page

**Tier 2 - Input/Display Components** (Week 3, Day 3-5):
- `GeneralInput` - Main input component with file handling
- `AttachmentList` - File attachment display
- `Tabs` - Tab navigation component
- `Slogn` - Animated slogan component

**Tier 3 - Complex Components** (Week 4, Day 1-3):
- `Dialogue` - Message display component
- `ActionPanel` - Action result display
- `ActionView` - Action viewer with multiple renderers
- `PlanView` - Task planning interface

**Tier 4 - Container Components** (Week 4, Day 4-5):
- `ChatView` - Main chat interface with SSE handling
- `Layout` - Application layout wrapper
- `Home` - Home page component

#### 3.2 Component Conversion Patterns

**React to Svelte Hook Mappings:**

| React Hook | Svelte Equivalent |
|-----------|------------------|
| useState | let variable + reactive statements |
| useEffect | onMount, afterUpdate, reactive statements |
| useContext | getContext/setContext or stores |
| useRef | bind:this or variable reference |
| useMemo | $: derived value |
| useCallback | Regular function (Svelte handles efficiently) |
| useImperativeHandle | Export functions/variables |

**Example Conversion Pattern:**

React Component:
```tsx
const MyComponent: React.FC<Props> = ({ value, onChange }) => {
  const [localState, setLocalState] = useState(0);
  
  useEffect(() => {
    // side effect
  }, [value]);
  
  const computed = useMemo(() => value * 2, [value]);
  
  return <div>{computed}</div>;
};
```

Svelte Component:
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  
  export let value: number;
  export let onChange: (val: number) => void;
  
  let localState = 0;
  
  $: computed = value * 2;
  
  $: if (value) {
    // reactive side effect
  }
</script>

<div>{computed}</div>
```

### Phase 4: Routing Implementation (Week 5, Day 1-2)

#### 4.1 SvelteKit File-Based Routing Structure
```
src/routes/
├── +layout.svelte        # Root layout (replaces Layout component)
├── +page.svelte          # Home page
├── +error.svelte         # Error page (404, etc.)
└── api/                  # API routes if needed
    └── [...path]/
        └── +server.ts
```

#### 4.2 Route Configuration
- Implement route guards if needed
- Set up preloading strategies
- Configure SSR/CSR preferences

### Phase 5: Advanced Features (Week 5, Day 3-5)

#### 5.1 Server-Sent Events (SSE) Integration
```typescript
// lib/sse/client.ts
import { readable } from 'svelte/store';
import { fetchEventSource } from '@microsoft/fetch-event-source';

export function createSSEStore(url: string, params: any) {
  return readable(null, (set) => {
    const controller = new AbortController();
    
    fetchEventSource(url, {
      method: 'POST',
      body: JSON.stringify(params),
      signal: controller.signal,
      onmessage(event) {
        set(JSON.parse(event.data));
      }
    });
    
    return () => controller.abort();
  });
}
```

#### 5.2 File Upload Handling
- Implement drag-and-drop with Svelte actions
- Create file preview components
- Handle multiple file types (PDF, images, etc.)

#### 5.3 Markdown and Code Rendering
- Integrate svelte-markdown
- Set up syntax highlighting
- Handle mermaid diagrams

### Phase 6: UI Component Library Replacement (Week 6)

#### 6.1 Ant Design Component Replacements

| Ant Design Component | Svelte Alternative | Implementation Priority |
|---------------------|-------------------|------------------------|
| ConfigProvider | Context/stores | High |
| message | Toast notifications (custom/library) | High |
| Modal | Custom modal or svelte-french-toast | High |
| Timeline | Custom component | Medium |
| Image | Native img with preview modal | Medium |
| Tabs | Custom tabs component | Medium |
| Button | Custom button component | High |
| Input | Native input with styling | High |

#### 6.2 Custom Component Development
- Create base component library in `$lib/components/ui/`
- Implement consistent theming system
- Ensure accessibility standards

### Phase 7: Testing and Optimization (Week 7)

#### 7.1 Testing Strategy
- Unit tests with Vitest
- Component testing with Svelte Testing Library
- E2E tests with Playwright
- SSE connection testing

#### 7.2 Performance Optimization
- Implement code splitting
- Optimize bundle size
- Set up lazy loading for routes
- Configure preloading strategies

#### 7.3 Build Configuration
```javascript
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    port: 3000,
    proxy: {
      '/web': {
        target: process.env.SERVICE_BASE_URL,
        changeOrigin: true
      }
    }
  }
});
```

### Phase 8: Migration Completion (Week 8)

#### 8.1 Feature Parity Checklist
- [ ] Chat interface functionality
- [ ] File upload and preview
- [ ] SSE streaming responses
- [ ] Markdown rendering
- [ ] Code syntax highlighting
- [ ] Task planning view
- [ ] Action panels and viewers
- [ ] Deep thinking mode
- [ ] Multi-agent support

#### 8.2 Final Steps
- Performance benchmarking
- Accessibility audit
- Cross-browser testing
- Documentation update
- Deployment configuration

## Migration Risks and Mitigation

### Technical Risks

1. **SSE Compatibility**
   - Risk: SSE implementation differences
   - Mitigation: Use same library (@microsoft/fetch-event-source)

2. **Complex State Management**
   - Risk: Store complexity for real-time updates
   - Mitigation: Careful store architecture design, use derived stores

3. **UI Component Library**
   - Risk: No direct Ant Design equivalent
   - Mitigation: Build custom components or use alternative libraries

4. **TypeScript Integration**
   - Risk: Type inference differences
   - Mitigation: Comprehensive type definitions, strict typing

### Business Risks

1. **Development Timeline**
   - Risk: 8-week timeline may extend
   - Mitigation: Prioritize core features, implement incrementally

2. **Feature Regression**
   - Risk: Missing functionality
   - Mitigation: Comprehensive testing, feature parity checklist

## Success Metrics

- **Performance**: 20% improvement in initial load time
- **Bundle Size**: 30% reduction in JavaScript bundle
- **Developer Experience**: Simplified component structure
- **Maintainability**: Reduced boilerplate code
- **User Experience**: Maintained or improved interaction responsiveness

## Recommended Tools and Libraries

### Core Dependencies
```json
{
  "@sveltejs/kit": "^2.0.0",
  "svelte": "^4.0.0",
  "vite": "^5.0.0",
  "@sveltejs/adapter-node": "^4.0.0"
}
```

### UI and Styling
```json
{
  "tailwindcss": "^3.4.0",
  "postcss": "^8.4.0",
  "autoprefixer": "^10.4.0",
  "@tailwindcss/forms": "^0.5.0",
  "@tailwindcss/typography": "^0.5.0"
}
```

### Utilities and Features
```json
{
  "svelte-markdown": "^0.4.0",
  "highlight.js": "^11.9.0",
  "lottie-web": "^5.12.0",
  "mermaid": "^10.6.0",
  "@microsoft/fetch-event-source": "^2.0.1",
  "axios": "^1.6.0",
  "dayjs": "^1.11.0",
  "lodash-es": "^4.17.0"
}
```

### Development Tools
```json
{
  "typescript": "^5.3.0",
  "eslint": "^8.56.0",
  "prettier": "^3.2.0",
  "vitest": "^1.2.0",
  "@testing-library/svelte": "^4.0.0",
  "playwright": "^1.41.0"
}
```

## Conclusion

This migration plan provides a structured approach to converting the React-based Genie UI to Svelte/SvelteKit. The 8-week timeline allows for systematic migration while maintaining feature parity and improving performance. Key success factors include:

1. Maintaining the existing application's functionality
2. Leveraging Svelte's reactive paradigm for cleaner code
3. Utilizing SvelteKit's features for better performance
4. Creating a maintainable and scalable architecture

The migration should result in a more performant, maintainable, and developer-friendly application while preserving all existing features and user experience.