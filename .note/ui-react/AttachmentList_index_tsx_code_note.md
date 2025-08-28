# AttachmentList/index.tsx Code Documentation

## File Summary
The AttachmentList component displays a grid of file attachments with preview capabilities. It handles different file types, shows file metadata (name, size), provides visual icons, and supports both preview and removal modes. The component is used throughout the chat interface for displaying user uploads and AI-generated files.

## Key Components and Functions

### AttachmentList Component (GeneralInput)
```typescript
const GeneralInput: GenieType.FC<Props> = (props) => {
  const { files, preview, remove, review } = props;
  
  // Component implementation
};
```

**Note**: The component is incorrectly named `GeneralInput` but functions as `AttachmentList`. This appears to be a naming inconsistency.

**Purpose**: Renders a list of file attachments with appropriate icons, metadata, and interaction capabilities.

**Props/Parameters**:
- `files: CHAT.TFile[]` - Array of file objects to display
- `preview?: boolean` - Whether files are clickable for preview
- `remove?: (index: number) => void` - Callback for file removal (edit mode)
- `review?: (file: CHAT.TFile) => void` - Callback for file preview (view mode)

**Return Value**: JSX element containing the file attachment grid

### formatSize Function
```typescript
const formatSize = (size: number) => {
  const units = ["B", "KB", "MB", "GB"];
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  return `${size?.toFixed(2)} ${units[unitIndex]}`;
};
```

**Purpose**: Converts file size from bytes to human-readable format with appropriate units.

**Parameters**:
- `size: number` - File size in bytes

**Return Value**: String - Formatted size with units (e.g., "2.45 MB")

**Key Logic**:
1. Iterates through unit array [B, KB, MB, GB]
2. Divides size by 1024 until below threshold
3. Returns size with two decimal places and appropriate unit

### combinIcon Function
```typescript
const combinIcon = (f: CHAT.TFile) => {
  const imgType = ["jpg", "png", "jpeg"];
  if (imgType.includes(f.type)) {
    return f.url;
  } else {
    return iconType[f.type] || docxIcon;
  }
};
```

**Purpose**: Determines the appropriate icon or thumbnail for a file based on its type.

**Parameters**:
- `f: CHAT.TFile` - File object with type and URL properties

**Return Value**: String - URL or icon path

**Key Logic**:
1. **Image Files**: Returns actual file URL for thumbnail display
   - Supported types: jpg, png, jpeg
2. **Other Files**: Returns type-specific icon from iconType mapping
   - Fallback to docxIcon for unknown types

### removeFile Function
```typescript
const removeFile = (index: number) => {
  remove?.(index);
};
```

**Purpose**: Handles file removal by calling the provided remove callback.

**Parameters**:
- `index: number` - Index of file to remove

**Return Value**: Void

### reviewFile Function
```typescript
const reviewFile = (f: CHAT.TFile) => {
  review?.(f);
};
```

**Purpose**: Handles file preview by calling the provided review callback.

**Parameters**:
- `f: CHAT.TFile` - File object to preview

**Return Value**: Void

### renderFile Function
```typescript
const renderFile = (f: CHAT.TFile, index: number) => {
  return (
    <div
      key={index}
      className={`group w-200 h-56 rounded-xl border border-[#E9E9F0] p-[8px] box-border flex items-center relative ${preview ? "cursor-pointer" : "cursor-default"}`}
      onClick={() => reviewFile(f)}
    >
      <img src={combinIcon(f)} alt={f.name} className="w-32 h-32 shrink" />
      <div className="flex-1 ml-[4px] overflow-hidden">
        <Tooltip title={f.name}>
          <div className="w-full overflow-hidden whitespace-nowrap text-ellipsis text-[14px] text-[#27272A] leading-[20px]">
            {f.name}
          </div>
        </Tooltip>
        <div className="w-full text-[12px] text-[#9E9FA3] leading-[18px]">
          {formatSize(f.size)}
        </div>
      </div>
      {!preview ? (
        <i
          className="font_family icon-jia-1 absolute top-[10px] right-[8px] cursor-pointer hidden group-hover:block"
          onClick={() => removeFile(index)}
        ></i>
      ) : null}
    </div>
  );
};
```

**Purpose**: Renders an individual file attachment with icon, metadata, and interactive elements.

**Parameters**:
- `f: CHAT.TFile` - File object to render
- `index: number` - File index for removal handling

**Return Value**: JSX element representing the file attachment

**Key Features**:

#### Layout Structure
- Fixed dimensions: 200px width, 56px height
- Rounded corners with border
- Flexbox layout for icon and content alignment

#### File Icon/Thumbnail
- 32x32px image display
- Uses combinIcon for appropriate visual representation
- Alt text for accessibility

#### File Information
- **File Name**: Truncated with ellipsis for overflow
- **Tooltip**: Shows full filename on hover
- **File Size**: Formatted using formatSize function
- **Typography**: Different sizes and colors for hierarchy

#### Interactive Elements
- **Conditional Cursor**: Pointer for preview mode, default for display mode
- **Click Behavior**: Calls reviewFile for preview functionality
- **Remove Button**: 
  - Only visible in non-preview mode
  - Appears on hover (group-hover)
  - Positioned absolutely in top-right corner

## Main Render Structure
```typescript
return (
  <div className="w-full flex gap-8 flex-wrap">
    {files.map((f, index) => renderFile(f, index))}
  </div>
);
```

**Layout Features**:
- Full width container
- Flexbox with wrapping for responsive grid
- 8px gap between items
- Accommodates varying numbers of files

## Supported File Types

### Image Files
- jpg, png, jpeg
- Display actual file as thumbnail
- Direct URL usage for preview

### Document Files
- Uses iconType mapping for visual representation
- Fallback to docxIcon (Word document icon)
- Common types likely include: pdf, txt, docx, xlsx, etc.

## Interaction Modes

### Preview Mode (`preview: true`)
- Files are clickable for preview
- Pointer cursor indicates interactivity
- No removal capability
- Used for displaying AI-generated files or completed uploads

### Edit Mode (`preview: false`)
- Files show remove button on hover
- Default cursor (not clickable for preview)
- Removal functionality available
- Used during file upload/selection process

## Visual Design

### Card Styling
- Clean white background with subtle border
- Rounded corners (12px border-radius)
- Consistent padding and spacing
- Group hover effects for interactive elements

### Typography Hierarchy
- File name: 14px, dark color (#27272A)
- File size: 12px, muted color (#9E9FA3)
- Proper line heights for readability

### Responsive Behavior
- Flexible width containers
- Wrapping grid layout
- Consistent sizing regardless of content

## Dependencies
- `react` - Core React functionality
- `antd` - Tooltip component for enhanced UX
- File type constants and icons from utils
- Custom styling with Tailwind CSS classes

**Accessibility Features**:
- Alt text on images
- Tooltips for truncated text
- Semantic HTML structure
- Keyboard navigation support through proper elements

**Performance Considerations**:
- Efficient rendering with proper key usage
- Image optimization for thumbnails
- Minimal DOM manipulation

**Notes**:
- Component naming inconsistency (GeneralInput vs AttachmentList)
- Flexible design supports various file types
- Clean separation between preview and edit modes
- Responsive grid layout for various screen sizes
- Chinese language elements in some parts of the codebase