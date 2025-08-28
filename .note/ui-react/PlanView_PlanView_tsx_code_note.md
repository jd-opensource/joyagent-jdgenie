# PlanView/PlanView.tsx Code Documentation

## File Summary
The PlanView component displays AI agent task planning information with expandable/collapsible interface. It shows task progress, completion status, and detailed timeline with stages and steps. The component uses dynamic height calculations and smooth animations to provide an engaging user experience for tracking AI agent planning progress.

## Key Components and Functions

### PlanView Component
```typescript
const PlanView: GenieType.FC<{
  plan?: CHAT.Plan;
  ref?: React.Ref<PlanViewAction>;
}> = forwardRef((props, ref) => {
  const { plan } = props;
  
  const { stages, stepStatus, steps } = plan || {};
  
  // Component implementation with refs and state management
});
```

**Purpose**: Displays AI agent planning information with expandable timeline and progress tracking.

**Props/Parameters**:
- `plan?: CHAT.Plan` - AI agent plan data containing stages, steps, and status
- `ref?: React.Ref<PlanViewAction>` - Forward ref for parent component control

**Return Value**: JSX element containing the plan view interface, or null if no plan

**React Hooks Used**:
- `forwardRef` - For exposing imperative methods to parent
- `useToggle` - Custom toggle hook from ahooks for expand/collapse state
- `useRef` - For DOM element reference and height calculations
- `useImperativeHandle` - For exposing control methods through ref
- `useEffect` - For dynamic height adjustments and ResizeObserver

### PlanViewAction Interface
```typescript
export type PlanViewAction = {
  /**
   * 打开任务进度面板
   * @returns
   */
  closePlanView: () => void;
  /**
   * 关闭任务进度面板
   * @returns
   */
  openPlanView: () => void;
  /**
   * 反向任务进度面板
   */
  togglePlanView: () => void;
}
```

**Purpose**: Defines the imperative API for controlling the plan view from parent components.

**Methods**:
- `closePlanView()` - Collapses the plan view
- `openPlanView()` - Expands the plan view
- `togglePlanView()` - Toggles between expanded and collapsed states

### Stage Progress Calculation
```typescript
const showStageIndex = stages?.reduce((pre, _cur, index, arr) => {
  const curStatus = stepStatus?.[index];
  if (curStatus === 'completed') {
    return Math.min(index + 1, arr.length - 1);
  }
  return pre;
}, 0) || 0;

const showStageStatus = stepStatus?.[showStageIndex];
const showStage = stages?.[showStageIndex];
```

**Purpose**: Determines which stage to display based on completion status.

**Key Logic**:
1. Iterates through all stages and their completion status
2. Finds the last completed stage and shows the next one
3. Ensures index doesn't exceed array bounds
4. Extracts the current stage name and status for display

### Toggle State Management
```typescript
const [ showComplete, { toggle, setLeft: closePlanView, setRight: openPlanView} ] = useToggle(false);
```

**Purpose**: Manages the expand/collapse state of the plan view.

**Features**:
- `showComplete` - Boolean state for expanded/collapsed
- `toggle` - Toggles between states
- `closePlanView` - Sets to collapsed (false)
- `openPlanView` - Sets to expanded (true)

### useImperativeHandle Implementation
```typescript
useImperativeHandle(ref, () => ({
  openPlanView,
  closePlanView,
  togglePlanView: toggle,
  // Commented out setPlanView method for dynamic height calculation
}));
```

**Purpose**: Exposes control methods to parent components through forward ref.

**Exposed Methods**: All methods from PlanViewAction interface

### generateItem Function
```typescript
const generateItem = (show?: boolean) => {
  return <>
    <div className="flex items-center h-32">
      任务进度
      <div className="ml-auto flex items-center text-[#848581]">
        <span className="mr-4 text-[12px]">{showStageIndex + 1} / {stages?.length}</span>
        <i className={classNames('transition-all font_family icon-shouqi size-16 flex items-center justify-center hover:bg-gray-300 rounded-[4px] cursor-pointer', { 'rotate-z-180': showComplete })} onClick={toggle} />
      </div>
    </div>
    <PlanItem title={showStage} status={showStageStatus} className={classNames({ 'hidden': !show })} />
  </>;
};
```

**Purpose**: Generates the plan header and current stage item with consistent structure.

**Parameters**:
- `show?: boolean` - Whether to show the PlanItem component

**Return Value**: JSX fragment containing header and plan item

**Key Features**:
- **Header**: Shows "任务进度" (Task Progress) title
- **Progress Counter**: Displays current stage number and total
- **Toggle Button**: Rotating chevron icon with hover effects
- **Current Stage**: Shows active stage with conditional visibility

### Dynamic Height Management
```typescript
useEffect(() => {
  const adjustHeight = throttle(() => {
    if (!wrapRef.current || !plan) {
      return;
    }
    // 计算高度，并设置动画效果
    const itemRef = wrapRef.current?.querySelector('.plan-item');
    let height = (itemRef?.clientHeight || 63) + 32;
    if (showComplete) {
      height = wrapRef.current?.scrollHeight;
    }
    wrapRef.current.style.height = `${height}px`;
  }, 30);
  
  adjustHeight();
  const observer = new ResizeObserver(adjustHeight);
  if (wrapRef.current) {
    observer.observe(wrapRef.current);
  }
  return () => {
    observer.disconnect();
  };
}, [plan, showComplete]);
```

**Purpose**: Dynamically calculates and animates height changes for smooth expand/collapse transitions.

**Key Features**:
1. **Throttled Calculation**: Uses lodash throttle (30ms) for performance
2. **Collapsed Height**: Base plan item height (63px) + padding (32px)
3. **Expanded Height**: Full scroll height of the container
4. **ResizeObserver**: Monitors content changes and adjusts height accordingly
5. **Cleanup**: Properly disconnects observer on unmount

### Timeline Generation
```typescript
{showComplete && <Timeline
  className={classNames(
    "px-12 pb-0 pt-32 bg-[#f9f9fc] rounded-[6px] transition-all duration-300",
  )}
  items={stages?.map((name, index) => {
    const status = stepStatus?.[index];
    const stepDesc = steps?.[index];

    return {
      dot: getStatusIcon(status),
      children: <div>
        <div className="text-[#80d1ee6]">{name}</div>
        <div className="text-gray text-[12px] text-[#2029459e]">{stepDesc}</div>
      </div>,
      key: name,
    };
  })}
/>}
```

**Purpose**: Renders the complete timeline when expanded, showing all stages with status indicators.

**Features**:
- **Conditional Rendering**: Only shown when `showComplete` is true
- **Timeline Component**: Uses Ant Design Timeline for visual progression
- **Status Icons**: Custom icons based on completion status via getStatusIcon
- **Stage Information**: Shows stage name and step description
- **Styling**: Background color and spacing for visual separation

## Component Structure

### Layout Wrapper
```typescript
<div className="w-full border-[#e9e9f0] mt-[16px] p-[16px] relative">
```

**Purpose**: Provides positioning context and spacing for the component.

### Hidden Placeholder
```typescript
<div className="opacity-0">
  {generateItem(true)}
</div>
```

**Purpose**: Creates invisible placeholder to establish baseline dimensions for height calculations.

### Animated Container
```typescript
<div
  className={classNames(
    'w-full rounded-[12px] border-solid border-1 border-[#e9e9f0] mt-[16px] p-[16px] bg-[#fff]',
    'absolute bottom-0 left-0',
    'transition-all duration-300 overflow-hidden',
  )}
  ref={wrapRef}
>
```

**Features**:
- **Absolute Positioning**: Positioned relative to wrapper
- **Smooth Transitions**: 300ms duration for height changes
- **Overflow Hidden**: Enables smooth expand/collapse animations
- **Border and Background**: Clean white card appearance

### Content Areas
1. **Plan Item** (always visible): Current stage with toggle
2. **Timeline** (conditional): Full stage timeline when expanded

## Visual Design

### Progress Indicator
- Stage counter format: "1 / 5"
- Small gray text for subtle presentation
- Clear visual hierarchy

### Toggle Control
- Rotating chevron icon (icon-shouqi)
- Hover background for interactivity
- Smooth rotation animation (rotate-z-180 when expanded)

### Timeline Styling
- Light gray background (#f9f9fc) for distinction
- Rounded corners for modern appearance
- Proper padding and spacing
- Status-based icons for visual feedback

## Status Handling

### Stage Status Types
Based on MESSAGE.PlanStatus:
- `not_started` - Not yet begun
- `in_progress` - Currently active
- `completed` - Successfully finished

### Icon Mapping
Uses getStatusIcon function to map status to appropriate visual indicators.

## Dependencies
- `react` - forwardRef, useEffect, useRef, useImperativeHandle
- `antd` - Timeline component for stage progression
- `ahooks` - useToggle for state management
- `classnames` - Conditional CSS class handling
- `lodash` - throttle for performance optimization
- Custom components (PlanItem) and utilities (getStatusIcon)

**Performance Optimizations**:
- Throttled height calculations (30ms)
- ResizeObserver for efficient resize handling
- Conditional rendering to avoid unnecessary updates
- Smooth CSS transitions for better UX

**Accessibility Features**:
- Keyboard navigation support
- Semantic HTML structure
- Clear visual status indicators
- Proper contrast and sizing

**Notes**:
- Rich interactive planning interface
- Smooth animations and transitions
- Dynamic height management for varying content
- Chinese language UI elements ("任务进度")
- Clean separation between collapsed and expanded states
- Robust handling of optional plan data
- Integration with parent components through imperative API