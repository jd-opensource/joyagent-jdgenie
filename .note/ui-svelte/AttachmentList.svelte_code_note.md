# AttachmentList.svelte Code Documentation

## File Summary
This component displays and manages a list of attached files, providing visual file representation with icons, size information, and removal functionality. It serves as a reusable UI component that can handle various file types with appropriate iconography and user-friendly file management capabilities.

## Component Structure

### Props

#### `files: File[] = []`
- **Purpose**: Array of File objects to display
- **Default**: Empty array
- **Structure**: Standard JavaScript File objects with properties like `name`, `size`, `type`
- **Usage**: Populated from file input selections

#### `onRemove: (index: number) => void = () => {}`
- **Purpose**: Callback function triggered when user removes a file
- **Parameters**: `index` - Array index of the file to remove
- **Default**: Empty function (no-op)
- **Usage**: Parent component handles the actual removal logic

#### `className: string = ''`
- **Purpose**: Additional CSS classes for container customization
- **Default**: Empty string
- **Usage**: Allows parent components to add custom styling

## Utility Functions

### `getFileIcon(file: File): string`
- **Purpose**: Returns appropriate emoji icon based on file type
- **Parameters**: `file` - File object with name property
- **Logic**: 
  1. Extracts file extension using `file.name.split('.').pop()?.toLowerCase()`
  2. Uses switch statement to match extensions to appropriate icons
- **Icon Mapping**:
  - **PDF**: '📄' - Document with text icon
  - **Word Documents** (doc, docx): '📝' - Memo/notepad icon
  - **Excel Spreadsheets** (xls, xlsx): '📊' - Bar chart icon
  - **Images** (png, jpg, jpeg, gif): '🖼️' - Framed picture icon
  - **Text Files** (txt): '📃' - Page with curl icon
  - **CSV Files** (csv): '📈' - Trending up chart icon
  - **HTML Files** (html): '🌐' - Globe icon
  - **Default**: '📎' - Paperclip icon for unknown types
- **Return**: String emoji representing the file type

### `formatFileSize(bytes: number): string`
- **Purpose**: Converts byte count to human-readable file size format
- **Parameters**: `bytes` - File size in bytes
- **Algorithm**:
  1. Handle zero case: returns '0 Bytes'
  2. Define size units: `['Bytes', 'KB', 'MB', 'GB']`
  3. Calculate appropriate unit index using logarithms: `Math.floor(Math.log(bytes) / Math.log(k))`
  4. Calculate size value: `bytes / Math.pow(k, i)`
  5. Round to 2 decimal places and append unit
- **Examples**:
  - 0 → '0 Bytes'
  - 1024 → '1 KB'
  - 1048576 → '1 MB'
  - 2560000 → '2.44 MB'

## Template Structure

### Conditional Rendering
- **Condition**: `{#if files.length > 0}` - Only renders when files exist
- **Purpose**: Prevents empty container from appearing

### Container
- **Base Classes**: `flex flex-wrap gap-2 p-2 border-t border-gray-200`
- **Layout**: Flexible wrapping container with small gaps
- **Styling**: Top border with padding for visual separation
- **Custom Classes**: `{className}` - Appends additional styling from props

### File Item Loop
- **Iterator**: `{#each files as file, index}` - Maps over files array with index
- **Purpose**: Renders individual file representation

#### File Item Structure
##### Container
- **Classes**: `flex items-center gap-2 px-3 py-1 bg-gray-50 rounded-lg`
- **Layout**: Horizontal flex with center alignment and small gaps
- **Styling**: Light gray background with rounded corners and padding

##### File Icon
- **Element**: `<span class="text-lg">`
- **Content**: `{getFileIcon(file)}` - Dynamic emoji based on file type
- **Size**: Large text size for visibility

##### File Information Container
- **Element**: `<div class="flex flex-col">`
- **Layout**: Vertical flex container for name and size

###### File Name Display
- **Element**: `<span>`
- **Classes**: `text-sm font-medium text-gray-700 max-w-[200px] truncate`
- **Content**: `{file.name}` - Original filename
- **Features**:
  - Small, medium-weight text
  - Dark gray color
  - Maximum width constraint (200px)
  - Text truncation with ellipsis for long names

###### File Size Display
- **Element**: `<span>`
- **Classes**: `text-xs text-gray-500`
- **Content**: `{formatFileSize(file.size)}` - Formatted size string
- **Styling**: Extra small, light gray text

##### Remove Button
- **Element**: `<button>`
- **Trigger**: `on:click={() => onRemove(index)}`
- **Classes**: `ml-2 text-gray-400 hover:text-gray-600`
- **Content**: '✕' - X symbol for removal
- **Features**:
  - Left margin for spacing
  - Gray color with darker hover state
  - No explicit styling beyond color

## Key Features

### File Type Recognition
- **Extension-based**: Uses file extension to determine appropriate icon
- **Comprehensive Coverage**: Supports common document, image, and data formats
- **Fallback Handling**: Default paperclip icon for unrecognized types
- **Case Insensitive**: Converts extensions to lowercase for matching

### Size Formatting
- **Human Readable**: Converts raw bytes to understandable units
- **Precision**: Maintains reasonable precision with 2 decimal places
- **International Units**: Uses standard KB, MB, GB progression
- **Zero Handling**: Special case for empty files

### User Interaction
- **Visual Feedback**: Hover states for interactive elements
- **Easy Removal**: Clear X button for each file
- **Index-based Removal**: Passes array index to parent for precise removal

### Layout and Design
- **Responsive Wrapping**: Files wrap to new lines as needed
- **Consistent Spacing**: Uniform gaps and padding throughout
- **Visual Hierarchy**: Clear distinction between file name and metadata
- **Truncation Handling**: Long filenames are truncated with ellipsis

## Styling Approach

### Color Scheme
- **Background**: Light gray (`bg-gray-50`) for file items
- **Text Primary**: Dark gray (`text-gray-700`) for file names
- **Text Secondary**: Medium gray (`text-gray-500`) for file sizes
- **Interactive**: Gray with hover states for remove buttons

### Typography
- **File Names**: Small, medium-weight font for prominence
- **File Sizes**: Extra small font for metadata
- **Icons**: Large text size for visual impact

### Layout Patterns
- **Flexbox Usage**: Consistent flex layouts for alignment
- **Gap Management**: Small, consistent gaps throughout
- **Border Styling**: Top border for visual separation

## Key Svelte Patterns

### Conditional Rendering
- **Empty State**: Component only renders when files exist
- **Clean Markup**: No unnecessary DOM elements when empty

### Event Handling
- **Callback Pattern**: Uses callback props for parent communication
- **Index Passing**: Provides file index for precise removal

### Props-Based Configuration
- **Flexible Styling**: Accepts className prop for customization
- **Event Delegation**: onRemove callback allows parent control
- **Data Binding**: Direct binding to files array

### Pure Display Logic
- **No Internal State**: Component is purely presentational
- **Utility Functions**: Clean separation of display logic
- **Reusable Design**: Can be used in multiple contexts

This component provides a clean, user-friendly way to display and manage file attachments with appropriate visual cues, proper formatting, and intuitive interaction patterns.