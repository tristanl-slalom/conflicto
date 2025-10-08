# Component Documentation

## Overview

This document provides detailed information about all React components in the Caja frontend
application, their props, usage patterns, and examples.

## Layout Components

### PersonaLayout

A high-level layout component that provides consistent styling and structure across all persona
interfaces.

**Props:**

```typescript
interface PersonaLayoutProps {
  persona: 'admin' | 'viewer' | 'participant';
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}
```

**Usage:**

```tsx
import { PersonaLayout } from '@/components/layouts/PersonaLayout';

<PersonaLayout
  persona="admin"
  title="Session Management"
  subtitle="Configure and control your sessions"
>
  {/* Admin interface content */}
</PersonaLayout>;
```

**Persona Styling:**

- **Admin**: Blue gradient (`from-blue-500 to-purple-500`)
- **Viewer**: Green gradient (`from-green-500 to-emerald-500`)
- **Participant**: Purple gradient (`from-purple-500 to-pink-500`)

### Card

A flexible container component for grouping related content with consistent styling.

**Props:**

```typescript
interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
}
```

**Usage:**

```tsx
import { Card } from '@/components/layouts/PersonaLayout';

<Card title="Session Configuration">
  <p>Configure your session settings here.</p>
</Card>;
```

## Form Components

### Button

A customizable button component with multiple variants and sizes.

**Props:**

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}
```

**Variants:**
- **Primary**: Blue background, used for main actions
- **Secondary**: Gray background, used for secondary actions
- **Success**: Green background, used for positive actions
- **Danger**: Red background, used for destructive actions

**Usage:**

```tsx
import { Button } from '@/components/layouts/PersonaLayout';

<Button variant="primary" size="lg" onClick={handleSubmit}>
  Create Session
</Button>;
```

### Input

A form input component with optional labels and consistent styling.

**Props:**

```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}
```

**Usage:**

```tsx
import { Input } from '@/components/layouts/PersonaLayout';

<Input
  label="Session Name"
  placeholder="Enter session name..."
  value={sessionName}
  onChange={e => setSessionName(e.target.value)}
/>;
```

### Select

A dropdown select component with label support.

**Props:**

```typescript
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  children: React.ReactNode;
}
```

**Usage:**

```tsx
import { Select } from '@/components/layouts/PersonaLayout';

<Select label="Session Type" value={sessionType} onChange={handleTypeChange}>
  <option value="poll">Live Polling</option>
  <option value="quiz">Quiz/Trivia</option>
  <option value="poker">Planning Poker</option>
</Select>;
```

## Page Components

### HomePage

The main landing page component that displays the Caja branding and persona selection interface.

**Features:**
- Responsive hero section with branding
- Three persona cards with navigation links
- Platform feature highlights
- Mobile-optimized layout

**Usage:**
```tsx
// Automatically rendered at '/' route
export const Route = createFileRoute('/')({
  component: HomePage,
});
```

### AdminInterface

The administrative interface for session management and configuration.

**Features:**
- Session creation and configuration forms
- Real-time participant monitoring
- Content management tools
- Session lifecycle controls

**Key Sections:**
- **Session Configuration**: Create and modify session settings
- **Content Management**: Set questions and response options
- **Session Status**: Monitor active session metrics
- **Quick Actions**: Start/stop sessions and export results

### ViewerDisplay

The large screen display interface optimized for projectors and shared viewing.

**Features:**
- Full-screen session information display
- QR code for participant joining
- Real-time result visualization
- High contrast design for distance viewing

**Key Sections:**
- **Header**: Session name and participant count
- **QR Code Section**: Join instructions and session code
- **Results Section**: Live voting results with animated progress bars

### ParticipantInterface

The mobile-optimized interface for event attendees to join and interact with sessions.

**Features:**
- Quick session joining via code or QR scan
- Touch-optimized voting interface
- Vote confirmation and status updates
- Offline-capable with sync when reconnected

**Key Sections:**
- **Session Join**: Enter session code or scan QR
- **Voting Interface**: Select options with large touch targets
- **Confirmation Screen**: Vote submitted status and next actions

## Component Styling Guidelines

### Color Schemes

Each persona has a dedicated color scheme to maintain visual consistency and help users understand
their current context:

```css
/* Admin - Blue/Purple */
--admin-primary: rgb(59 130 246)
  --admin-gradient: linear-gradient(to right, rgb(59 130 246), rgb(147 51 234)) /* Viewer - Green */
  --viewer-primary: rgb(34 197 94)
  --viewer-gradient: linear-gradient(to right, rgb(34 197 94), rgb(16 185 129))
  /* Participant - Purple/Pink */ --participant-primary: rgb(147 51 234)
  --participant-gradient: linear-gradient(to right, rgb(147 51 234), rgb(236 72 153));
```

### Responsive Breakpoints

Components follow mobile-first responsive design:

```css
/* Mobile (default) */
/* 375px and up */

/* Tablet */
@media (min-width: 768px) {
  /* md: */
}

/* Desktop */
@media (min-width: 1024px) {
  /* lg: */
}

/* Large Desktop */
@media (min-width: 1280px) {
  /* xl: */
}
```

### Typography Scale

```css
/* Headings */
.text-6xl {
  font-size: 3.75rem;
} /* Hero titles */
.text-4xl {
  font-size: 2.25rem;
} /* Section titles */
.text-2xl {
  font-size: 1.5rem;
} /* Card titles */
.text-lg {
  font-size: 1.125rem;
} /* Button text */

/* Body text */
.text-base {
  font-size: 1rem;
} /* Default body */
.text-sm {
  font-size: 0.875rem;
} /* Helper text */
.text-xs {
  font-size: 0.75rem;
} /* Fine print */
```

### Spacing System

Consistent spacing using Tailwind's scale:

```css
.p-1 {
  padding: 0.25rem;
} /* 4px */
.p-2 {
  padding: 0.5rem;
} /* 8px */
.p-3 {
  padding: 0.75rem;
} /* 12px */
.p-4 {
  padding: 1rem;
} /* 16px */
.p-6 {
  padding: 1.5rem;
} /* 24px */
.p-8 {
  padding: 2rem;
} /* 32px */
```

## Accessibility Guidelines

### Keyboard Navigation

All interactive components support keyboard navigation:

- **Tab**: Move to next focusable element
- **Shift + Tab**: Move to previous focusable element
- **Enter/Space**: Activate buttons and links
- **Arrow Keys**: Navigate within option groups

### Screen Reader Support

Components include proper ARIA attributes:

```tsx
// Button example
<button
  aria-label="Create new session"
  aria-describedby="session-help-text"
>
  Create Session
</button>

// Form input example
<input
  aria-label="Session name"
  aria-required="true"
  aria-invalid={hasError}
/>
```

### Focus Management

Clear focus indicators for all interactive elements:

```css
.focus\:ring-2:focus {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width)
    var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width))
    var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}
```

## Animation Guidelines

### Transitions

Smooth transitions for state changes:

```css
.transition-all {
  transition-property: all;
}
.duration-200 {
  transition-duration: 200ms;
}
.duration-300 {
  transition-duration: 300ms;
}
.ease-out {
  transition-timing-function: cubic-bezier(0, 0, 0.2, 1);
}
```

### Hover Effects

Subtle hover effects for interactive elements:

```css
.hover\:scale-105:hover {
  transform: scale(1.05);
}
.hover\:bg-blue-700:hover {
  background-color: rgb(29 78 216);
}
.hover\:shadow-lg:hover {
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```

### Loading States

Skeleton loaders and progress indicators:

```tsx
// Loading skeleton
<div className="animate-pulse">
  <div className="h-4 bg-slate-700 rounded w-3/4 mb-2"></div>
  <div className="h-4 bg-slate-700 rounded w-1/2"></div>
</div>
```

## Error Handling

### Error Boundaries

Components handle errors gracefully:

```tsx
function ErrorFallback({ error }: { error: Error }) {
  return (
    <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
      <h2 className="text-lg font-semibold text-red-400 mb-2">Something went wrong</h2>
      <p className="text-red-300">{error.message}</p>
    </div>
  );
}
```

### Validation States

Form components show validation feedback:

```tsx
<Input
  label="Session Name"
  error={errors.sessionName}
  className={errors.sessionName ? 'border-red-500' : ''}
/>;
{
  errors.sessionName && <p className="text-red-400 text-sm mt-1">{errors.sessionName}</p>;
}
```

This component documentation provides comprehensive guidance for using, customizing, and maintaining
the Caja frontend component library.
