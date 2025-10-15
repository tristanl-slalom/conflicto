# Implementation Plan: Adjust color scheme to Halloween theme

**GitHub Issue:** [#87](https://github.com/tristanl-slalom/conflicto/issues/87)
**Generated:** 2025-10-15T20:45:00Z

## Implementation Strategy

### Approach
Systematic replacement of the existing color scheme with Halloween-themed colors using a two-phase approach:
1. **CSS Custom Properties Update**: Replace root color variables with Halloween palette
2. **Component Color Class Updates**: Replace hardcoded Tailwind classes with Halloween equivalents

### Architecture Alignment
This implementation aligns with Caja's existing CSS custom property system and maintains the multi-persona design consistency across admin, viewer, and participant interfaces.

## File Structure Changes

### Files to Modify
```
frontend/src/styles.css                    # Primary CSS custom properties
frontend/src/routes/admin/index.tsx        # Admin interface colors
frontend/src/components/Header.tsx         # Navigation colors
frontend/src/components/admin/            # Admin component colors
frontend/src/routes/viewer/index.tsx       # Viewer interface colors
frontend/src/routes/participant/index.tsx  # Participant interface colors
```

### No New Files Required
This is a pure styling update that leverages existing architecture.

## Implementation Steps

### Step 1: Update CSS Custom Properties (/frontend/src/styles.css)
**Estimated Time: 30 minutes**

#### Light Theme Variables (`:root`)
```css
:root {
  --background: oklch(0.95 0.02 40);        /* Warm off-white */
  --foreground: oklch(0.15 0.02 350);       /* Dark purple-black */
  --card: oklch(0.98 0.01 40);              /* Light cream */
  --card-foreground: oklch(0.15 0.02 350);
  --primary: oklch(0.65 0.25 35);           /* Pumpkin orange */
  --primary-foreground: oklch(0.98 0.01 40);
  --secondary: oklch(0.45 0.15 300);        /* Deep purple */
  --secondary-foreground: oklch(0.98 0.01 40);
  --accent: oklch(0.75 0.20 50);            /* Bright orange */
  --destructive: oklch(0.55 0.22 25);       /* Dark red-orange */
  --border: oklch(0.85 0.03 35);            /* Light orange border */
}
```

#### Dark Theme Variables (`.dark`)
```css
.dark {
  --background: oklch(0.15 0.02 350);       /* Dark charcoal */
  --foreground: oklch(0.95 0.02 40);        /* Light orange-white */
  --card: oklch(0.20 0.03 340);             /* Dark card background */
  --card-foreground: oklch(0.95 0.02 40);
  --primary: oklch(0.65 0.25 35);           /* Pumpkin orange */
  --primary-foreground: oklch(0.15 0.02 350);
  --secondary: oklch(0.35 0.12 300);        /* Darker purple */
  --border: oklch(0.30 0.05 340);           /* Dark border */
}
```

### Step 2: Update Admin Interface (/frontend/src/routes/admin/index.tsx)
**Estimated Time: 45 minutes**

#### Color Class Replacements
- `bg-slate-900` → `bg-background` (use CSS custom property)
- `bg-slate-800` → `bg-card`
- `border-slate-700` → `border-border`
- `text-white` → `text-foreground`
- `text-gray-400` → `text-muted-foreground`
- `bg-slate-600 hover:bg-slate-500` → `bg-secondary hover:bg-secondary/90`
- `from-blue-500 to-purple-500` → `from-primary to-secondary`

#### Specific Changes
```tsx
// Header background
<div className="bg-card border-b border-border">

// Logo gradient
<div className="w-8 h-8 bg-gradient-to-r from-primary to-secondary rounded-lg">

// Button styling
<button className="w-full bg-secondary hover:bg-secondary/90 text-secondary-foreground">
```

### Step 3: Update Navigation Component (/frontend/src/components/Header.tsx)
**Estimated Time: 30 minutes**

#### Color Class Replacements
- `bg-gray-800` → `bg-card`
- `text-white` → `text-foreground`
- `hover:bg-gray-700` → `hover:bg-accent/10`
- `bg-gray-900` → `bg-background`
- `border-gray-700` → `border-border`
- `bg-cyan-600 hover:bg-cyan-700` → `bg-primary hover:bg-primary/90`

### Step 4: Update Admin Components
**Estimated Time: 60 minutes**

#### Session Management Components
- `SessionCreateForm`: Update form inputs and buttons
- `SessionList`: Update card backgrounds and text colors
- `SessionStatusCard`: Update status indicators and card styling

#### Component-Specific Updates
```tsx
// Form inputs
<input className="bg-input border-input text-foreground" />

// Primary buttons
<button className="bg-primary hover:bg-primary/90 text-primary-foreground" />

// Cards
<div className="bg-card border-border text-card-foreground" />
```

### Step 5: Update Viewer Interface (/frontend/src/routes/viewer/index.tsx)
**Estimated Time: 30 minutes**

Focus on large-screen readability with high contrast Halloween colors.

### Step 6: Update Participant Interface (/frontend/src/routes/participant/index.tsx)
**Estimated Time: 30 minutes**

Ensure mobile-friendly Halloween theme with accessible touch targets.

## Testing Strategy

### Automated Testing
- **Visual Regression Tests**: Capture screenshots before/after changes
- **Accessibility Tests**: Run axe-core accessibility testing
- **Cross-browser Tests**: Test in Chrome, Firefox, Safari, Edge

### Manual Testing Checklist
- [ ] Admin interface displays correctly with Halloween colors
- [ ] Viewer interface maintains readability on large screens
- [ ] Participant interface works well on mobile devices
- [ ] Dark/light theme switching functions properly
- [ ] All interactive elements have proper hover states
- [ ] Focus indicators are visible and accessible
- [ ] Color contrast meets WCAG AA standards

### Testing Commands
```bash
# Run accessibility tests
npm run test:a11y

# Run visual regression tests
npm run test:visual

# Start development server for manual testing
npm run dev
```

## Deployment Considerations

### No Database Changes
This is a frontend-only update with no backend or database impacts.

### Environment Variables
No new environment variables required.

### Build Process
- CSS custom properties will be processed by existing Tailwind/PostCSS pipeline
- No additional build configuration needed
- Bundle size impact should be negligible

### Rollback Plan
If issues arise, revert the CSS custom property values in `styles.css` to restore original colors.

## Risk Assessment

### Low Risk Areas
- CSS custom properties are well-supported across browsers
- Existing component structure remains unchanged
- No functional logic modifications required

### Medium Risk Areas
- **Contrast Ratios**: Halloween colors may create accessibility issues
  - *Mitigation*: Test all color combinations with WebAIM contrast checker
  - *Validation*: Run automated accessibility tests before deployment

- **Brand Recognition**: Dramatic color change may confuse users
  - *Mitigation*: Ensure logo and key branding elements remain recognizable
  - *Validation*: User acceptance testing with stakeholders

### Monitoring
- Watch for accessibility complaints after deployment
- Monitor user feedback about visual changes
- Track any increase in support tickets related to UI visibility

## Estimated Effort

### Development Time: 3.5 hours
- CSS Custom Properties: 30 minutes
- Admin Interface Updates: 45 minutes
- Navigation Component: 30 minutes
- Admin Components: 60 minutes
- Viewer Interface: 30 minutes
- Participant Interface: 30 minutes
- Testing and QA: 45 minutes

### Complexity Assessment: Low-Medium
- **Technical Complexity**: Low (CSS-only changes)
- **Design Complexity**: Medium (ensuring accessibility and consistency)
- **Testing Complexity**: Medium (cross-platform validation required)

### Dependencies
- No external dependencies
- No coordination with other teams required
- Can be implemented independently of other features

## Success Metrics
- [ ] All acceptance criteria validated
- [ ] WCAG AA compliance maintained (4.5:1 contrast minimum)
- [ ] No increase in accessibility-related support tickets
- [ ] Positive feedback on seasonal visual update
- [ ] No performance regressions measured
