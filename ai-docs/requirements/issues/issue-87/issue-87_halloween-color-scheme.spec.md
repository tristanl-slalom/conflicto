# Technical Specification: Adjust color scheme to Halloween theme

**GitHub Issue:** [#87](https://github.com/tristanl-slalom/conflicto/issues/87)
**Generated:** 2025-10-15T20:45:00Z

## Problem Statement
The Caja live event engagement platform needs a seasonal Halloween color scheme to create a festive appearance. The current color scheme uses neutral grays and blues that don't match the seasonal theme requirements.

## Technical Requirements

### Color Palette Specifications
- **Primary Orange**: `#E55100` (oklch: 0.65 0.25 35) - Pumpkin orange for primary actions and branding
- **Deep Purple**: `#4A148C` (oklch: 0.45 0.15 300) - Accent color for secondary elements
- **Dark Background**: `#1A1A1A` (oklch: 0.15 0.02 350) - Charcoal background for dark theme
- **Light Background**: `#F5F5F5` (oklch: 0.95 0.02 40) - Warm off-white for light theme
- **Text Colors**:
  - Primary text (dark): `#2C2C2C` (oklch: 0.15 0.02 350)
  - Primary text (light): `#F5F5F5` (oklch: 0.95 0.02 40)
- **Secondary Colors**:
  - Warning/Alert: `#FF8F00` (oklch: 0.75 0.20 50) - Amber orange
  - Success: `#558B2F` (oklch: 0.55 0.15 120) - Dark green

### CSS Custom Properties Implementation
Update CSS custom properties in `/frontend/src/styles.css` for both light and dark themes:
- Replace existing OKLCH color values with Halloween palette
- Maintain semantic naming convention (--primary, --secondary, --background, etc.)
- Ensure proper contrast ratios for WCAG AA compliance

### Component Color Updates
Replace hardcoded Tailwind color classes throughout components:
- `bg-slate-*` → Halloween background colors
- `text-*` → Halloween text colors
- `border-*` → Halloween border colors
- `from-blue-500 to-purple-500` → `from-orange-500 to-purple-600` gradients

## API Specifications
No API changes required - this is purely a frontend visual update.

## Data Models
No database schema changes required.

## Interface Requirements

### Multi-Persona Consistency
- **Admin Interface**: Use dark Halloween theme with orange primary actions
- **Viewer Interface**: Large screen optimized with high contrast Halloween colors
- **Participant Interface**: Mobile-friendly Halloween theme with accessible contrast

### Responsive Design
- Maintain mobile-first approach with Halloween colors
- Ensure readability across all screen sizes
- Preserve existing layout and spacing

### Accessibility Requirements
- Maintain WCAG 2.1 AA contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Ensure color is not the only means of conveying information
- Test with color vision deficiency simulators

## Integration Points
- CSS custom properties system
- Tailwind CSS utility classes
- React component styling
- Dark/light theme switching mechanism

## Acceptance Criteria

### Functional Requirements
- [ ] All primary colors updated to Halloween orange (#E55100)
- [ ] Secondary colors updated to Halloween purple (#4A148C)
- [ ] Background colors updated to Halloween dark theme
- [ ] All text colors maintain readability
- [ ] Button hover states use Halloween colors
- [ ] Card backgrounds use Halloween theme
- [ ] Navigation components use Halloween colors

### Technical Requirements
- [ ] Color contrast meets WCAG AA standards (4.5:1 minimum)
- [ ] CSS custom properties properly updated
- [ ] Tailwind classes consistently replaced
- [ ] No hardcoded color values remain
- [ ] Dark/light theme variants both work
- [ ] No visual regressions in functionality

### Cross-Platform Requirements
- [ ] Desktop appearance consistent and readable
- [ ] Mobile appearance optimized and accessible
- [ ] Cross-browser compatibility maintained
- [ ] Performance impact negligible

## Assumptions & Constraints

### Technical Assumptions
- Existing CSS custom property system can accommodate new colors
- Current dark/light theme switching mechanism will work with Halloween colors
- Component structure allows for color-only changes without layout modifications

### Design Constraints
- Must maintain existing component layouts and spacing
- Cannot break existing functionality or user workflows
- Must preserve brand recognition while adding seasonal flair
- Color changes should feel intentional, not jarring

### Performance Constraints
- No additional CSS bundle size increase
- No impact on page load times
- Maintain existing CSS optimization and bundling

### Accessibility Constraints
- Must not reduce accessibility for users with visual impairments
- Must maintain keyboard navigation visual indicators
- Must work with screen readers and assistive technologies
