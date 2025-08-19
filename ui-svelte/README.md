# Genie UI - Svelte Version

This is the Svelte/SvelteKit version of the Genie UI application, migrated from React.

## Features

- 🚀 Built with SvelteKit and TypeScript
- 🎨 Styled with Tailwind CSS
- 💬 Real-time chat interface with SSE support
- 📎 File upload and attachment handling
- 🧠 Deep thinking mode
- 📝 Markdown rendering with syntax highlighting
- 🎯 Multiple product/agent types support
- ⚡ Fast and reactive state management with Svelte stores

## Tech Stack

- **Framework**: SvelteKit 2.0
- **Language**: TypeScript
- **Styling**: Tailwind CSS 3.x
- **Build Tool**: Vite 5.x
- **HTTP Client**: Axios
- **SSE**: @microsoft/fetch-event-source
- **Markdown**: Custom markdown parser with highlight.js
- **Animations**: Lottie Web

## Project Structure

```
src/
├── app.css              # Global styles and Tailwind imports
├── app.d.ts            # TypeScript global definitions
├── app.html            # HTML template
├── assets/             # Static assets (icons, fonts, styles)
├── lib/
│   ├── components/     # Svelte components
│   ├── services/       # API services and SSE handling
│   ├── stores/         # Svelte stores for state management
│   ├── types/          # TypeScript type definitions
│   └── utils/          # Utility functions
└── routes/             # SvelteKit routes
    ├── +layout.svelte  # Root layout
    └── +page.svelte    # Home page
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or pnpm

### Installation

1. Clone the repository
2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Update the `SERVICE_BASE_URL` in `.env` to point to your backend service

### Development

Run the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Building for Production

Build the application:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## Key Components

### Core Components
- **ChatView**: Main chat interface with SSE streaming
- **GeneralInput**: Multi-functional input component with file upload
- **Dialogue**: Message display component
- **MarkdownRenderer**: Custom markdown parser and renderer
- **ActionView**: Action panel for task visualization

### Foundation Components
- **Logo**: Application logo
- **Loading**: Loading states (spinner, dots)
- **Toast**: Toast notification system
- **NotFound**: 404 error page

### Stores
- **chat**: Main chat state management
- **message**: Toast notification system
- **constants**: Application constants

## Migration from React

This application was migrated from React following these key changes:

1. **Component Conversion**: React components converted to Svelte components
2. **State Management**: React Context/hooks replaced with Svelte stores
3. **Routing**: React Router replaced with SvelteKit file-based routing
4. **UI Library**: Ant Design components replaced with custom Svelte components
5. **Styling**: Maintained Tailwind CSS with minor adjustments

## Configuration

### Environment Variables

- `SERVICE_BASE_URL`: Backend service URL for API calls

### Vite Configuration

The `vite.config.ts` includes:
- Proxy configuration for `/web` API endpoints
- Path aliases for cleaner imports
- Build optimization settings

## API Integration

The application communicates with the backend through:
- REST API calls via Axios
- Server-Sent Events (SSE) for streaming responses
- File upload support

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[License information]

## Support

For issues or questions, please contact the development team.