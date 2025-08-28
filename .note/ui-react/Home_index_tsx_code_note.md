# Home/index.tsx Code Documentation

## File Summary
The main home page component that handles the landing page UI and chat interface. It provides a product selection interface, demo cases, and transitions to chat view when user inputs a message. This is the primary user interaction component for starting conversations with the AI agent.

## Key Components and Functions

### Home Component
```typescript
const Home: GenieType.FC<HomeProps> = memo(() => {
  const [inputInfo, setInputInfo] = useState<CHAT.TInputInfo>({
    message: "",
    deepThink: false,
  });
  const [product, setProduct] = useState(defaultProduct);
  const [videoModalOpen, setVideoModalOpen] = useState();
  // ... component logic
});
```

**Purpose**: Main landing page component that provides product selection, demo cases, and input interface for starting AI conversations.

**Props/Parameters**: `HomeProps` (Record<string, never> - no props)

**Return Value**: JSX element containing either the landing page or chat interface

**State Management**:
- `inputInfo`: Stores user input message and deepThink flag
- `product`: Currently selected product/AI agent type
- `videoModalOpen`: Controls demo video modal visibility

**React Hooks Used**:
- `useState` - For managing component state (inputInfo, product, videoModalOpen)
- `useCallback` - For optimizing the changeInputInfo function
- `memo` - HOC for component memoization

### changeInputInfo Function
```typescript
const changeInputInfo = useCallback((info: CHAT.TInputInfo) => {
  setInputInfo(info);
}, []);
```

**Purpose**: Updates the input information state when user submits a message.

**Parameters**: 
- `info: CHAT.TInputInfo` - Object containing message and deepThink settings

**Return Value**: Void

**Key Logic**: Updates the inputInfo state to trigger transition to chat view

### CaseCard Component
```typescript
const CaseCard = ({ title, description, tag, image, url, videoUrl }: any) => {
  return (
    <div className="group flex flex-col rounded-lg bg-white pt-16 px-16 shadow-[0_4px_12px_rgba(0,0,0,0.05)] hover:shadow-[0_8px_20px_rgba(0,0,0,0.1)] hover:-translate-y-[5px] transition-all duration-300 ease-in-out cursor-pointer w-full max-w-xs border border-[rgba(233,233,240,1)]">
      {/* Card content */}
    </div>
  );
};
```

**Purpose**: Renders individual demo case cards with hover effects and video preview functionality.

**Props/Parameters**:
- `title`: Demo case title
- `description`: Demo case description
- `tag`: Category tag
- `image`: Preview image URL
- `url`: External report URL
- `videoUrl`: Demo video URL

**Return Value**: JSX element representing a demo case card

**Key Features**:
- Hover animations with shadow and transform effects
- Video preview modal functionality
- External link navigation
- Responsive design with max-width constraints

### renderContent Function
```typescript
const renderContent = () => {
  if (inputInfo.message.length === 0) {
    return (
      // Landing page with product selection and demo cases
    );
  }
  return <ChatView inputInfo={inputInfo} product={product} />;
};
```

**Purpose**: Conditionally renders either the landing page or chat interface based on user input.

**Parameters**: None

**Return Value**: JSX element - either landing page or ChatView component

**Key Logic**:
1. Checks if user has entered a message
2. Shows landing page if no message
3. Transitions to ChatView when message exists

## Landing Page Structure

### Product Selection
- Displays available AI agent types from `productList`
- Allows switching between different agent types
- Visual indication of selected product
- Each product has icon, name, and styling

### Demo Cases Section
- Shows "优秀案例" (Excellent Cases) section
- Displays demo cards in a grid layout
- Each card includes:
  - Title and category tag
  - Description text
  - Preview image
  - Video modal functionality
  - External report link

### Input Interface
- Large input area with gradient border styling
- Product type indicator
- "深度研究" (Deep Research) toggle option
- Responsive design with centered layout

## Key UI Features

**Responsive Layout**:
- Centered content with max-width constraints
- Flexible grid layout for product selection
- Responsive demo case cards

**Interactive Elements**:
- Hover effects on product selection buttons
- Animated demo case cards
- Video modal previews
- Gradient styling on input container

**State-Driven UI**:
- Conditional rendering based on input state
- Product selection updates
- Modal state management

## Dependencies
- `react` - useState, useCallback, memo
- `antd` - Image component for video preview
- Various internal components (GeneralInput, Slogn, ChatView)
- Constants and utilities for product data and demo content

**Notes**:
- Component uses memo for performance optimization
- Smooth transition from landing to chat interface
- Rich interactive demo section with video previews
- Chinese language UI elements throughout