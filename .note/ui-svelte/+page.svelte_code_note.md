# +page.svelte Code Documentation

## File Summary
This is the main homepage component of the Svelte application. It serves as the entry point for users and handles the initial UI state, product selection, and the transition from the landing page to the chat interface. The component provides a gradient background with a centered logo, input field, and product selection buttons before switching to the chat view once a message is submitted.

## Component Structure

### Imports and Dependencies
- **Svelte imports**: `onMount` for lifecycle management
- **Component imports**: 
  - `GeneralInput`: Main input component for user messages
  - `Slogn`: Logo/slogan component 
  - `ChatView`: Chat interface component
- **Utility imports**: `productList`, `defaultProduct` from constants
- **Store imports**: `inputInfo`, `selectedProduct` for state management
- **Type imports**: Chat type definitions

### State Variables

#### `currentProduct: CHAT.Product`
- **Purpose**: Tracks the currently selected product type
- **Initial value**: `defaultProduct`
- **Usage**: Determines placeholder text and styling for input field

#### `videoModalOpen: string | undefined`
- **Purpose**: Controls video modal visibility state (unused in current implementation)
- **Initial value**: `undefined`

#### `showChat: boolean`
- **Purpose**: Controls conditional rendering between landing page and chat interface
- **Initial value**: `false`
- **Trigger**: Set to `true` when user submits a message

## Functions

### `changeInputInfo(info: CHAT.TInputInfo): void`
- **Purpose**: Handles input information changes and triggers chat mode
- **Parameters**:
  - `info`: Object containing message, files, output style, and deep think flag
- **Functionality**: 
  - Updates the `inputInfo` store with the provided information
  - Switches to chat mode (`showChat = true`) if message exists
- **Side effects**: Triggers reactive statement and UI state change

### `selectProduct(product: CHAT.Product): void`
- **Purpose**: Handles product selection from the product grid
- **Parameters**:
  - `product`: Product object containing name, type, placeholder, etc.
- **Functionality**:
  - Updates local `currentProduct` state
  - Updates the `selectedProduct` store
- **UI Impact**: Changes button styling and input placeholder

## Reactive Statements

### `$: if ($inputInfo.message) { showChat = true; }`
- **Purpose**: Reactive listener that automatically shows chat when input message exists
- **Trigger**: Any change to the `inputInfo` store's message property  
- **Effect**: Switches UI from landing page to chat interface

## Template Structure

### Landing Page Mode (`!showChat`)
The initial state renders a centered layout with:

#### Header Section
- **Container**: `pt-120 flex flex-col items-center` - Top padding with centered flex column
- **Components**: `<Slogn />` component for logo/branding

#### Input Section
- **Container**: `w-640 rounded-xl shadow-[0_18px_39px_0_rgba(198,202,240,0.1)]` - Fixed width with rounded corners and subtle shadow
- **Component**: `GeneralInput` with properties:
  - `placeholder`: Dynamic based on selected product
  - `showBtn={true}`: Displays send button
  - `size="big"`: Large input styling
  - `disabled={false}`: Input is always enabled on landing page
  - `product={currentProduct}`: Current product context
  - `send={changeInputInfo}`: Callback for handling submission

#### Product Grid
- **Container**: `w-640 flex flex-wrap gap-16 mt-16` - Fixed width flex container with gaps
- **Items**: Loops through `productList` array
- **Button Styling**: Dynamic classes based on selection state:
  - **Selected**: `border-[#4040ff] bg-[rgba(64,64,255,0.02)] text-[#4040ff]`
  - **Unselected**: `border-[#E9E9F0] text-[#666] hover:border-gray-300`
- **Content**: Icon (`i` element with font family classes) and product name

### Chat Mode (`showChat`)
When a message is submitted, renders:
- **Component**: `<ChatView>` with props:
  - `inputInfo={$inputInfo}`: Current input information from store
  - `product={currentProduct}`: Selected product context

## Styling and Layout

### Background
- **Classes**: `h-full overflow-auto bg-gradient-to-b from-white to-gray-50`
- **Effect**: Full height with subtle gradient background

### Product Button Styling
- **Base classes**: `w-[22%] h-36 cursor-pointer flex items-center justify-center border rounded-[8px] transition-all`
- **Responsive**: Buttons are 22% width allowing ~4 per row with gaps
- **Interactive**: Hover and selection state styling with smooth transitions

## State Management Integration

### Store Usage
- **inputInfo store**: Manages user input data across components
- **selectedProduct store**: Tracks current product selection globally

### Store Initialization
- Immediately sets default product: `selectedProduct.set(defaultProduct)`

## Key Svelte Patterns

### Conditional Rendering
Uses `{#if !showChat}...{:else}...{/if}` for main UI state switching

### Event Handling  
- Button clicks handled with `on:click` directive
- Function calls passed as props for child component communication

### Reactive Data Flow
- Store subscriptions with `$` prefix for automatic reactivity
- Reactive statements for derived state management

### Component Communication
- Parent-to-child: Props passing
- Child-to-parent: Callback functions (`send` prop)

This component effectively serves as the application's entry point, managing the user's journey from product selection to active chat conversation while maintaining clean separation of concerns through Svelte's component and store architecture.