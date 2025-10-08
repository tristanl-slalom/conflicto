# Technical Specification: Enhance admin interface to create sessions and integrate with backend API

**GitHub Issue:** [#70](https://github.com/tristanl-slalom/conflicto/issues/70)
**Generated:** 2025-10-08T17:55:00Z

## Problem Statement

The current admin interface exists but lacks proper integration with the backend API for session management. The interface needs to be enhanced to provide a functional way for administrators to create and manage sessions while properly handling API communication, error states, and user feedback.

## Technical Requirements

### Core Session Management
- **Session Creation**: Complete form implementation with proper validation
- **API Integration**: Full connection to backend `/api/v1/sessions` endpoints
- **State Management**: Proper React state management with TanStack Query
- **Error Handling**: Comprehensive error handling for network and validation errors
- **Loading States**: Clear visual feedback during API operations

### Data Validation
- **Client-side Validation**: Form field validation before API submission
- **Server-side Validation**: Proper handling of backend validation responses
- **Field Requirements**: Enforce required fields (session name) and optional fields (description)

### User Experience
- **Success Feedback**: Clear success messages when sessions are created
- **Error Feedback**: Detailed error messages for different failure scenarios
- **Loading Indicators**: Visual feedback during async operations
- **Form Reset**: Clear form after successful submission

## API Specifications

### Session Creation Endpoint
- **Endpoint**: `POST /api/v1/sessions`
- **Request Body**:
  ```typescript
  interface SessionCreate {
    name: string;
    description?: string | null;
  }
  ```
- **Response**: `SessionDetail` object with created session information
- **Error Responses**: 
  - `422`: Validation errors
  - `500`: Server errors

### Session List Endpoint
- **Endpoint**: `GET /api/v1/sessions`
- **Response**: `SessionList` with array of sessions and total count
- **Usage**: Display existing sessions in the admin interface

### Session Detail Endpoint
- **Endpoint**: `GET /api/v1/sessions/{id}`
- **Response**: `SessionDetail` with complete session information
- **Usage**: View and manage individual session details

## Data Models

### Session Create Request
```typescript
interface SessionCreate {
  name: string;           // Required: Session title/name
  description?: string;   // Optional: Session description
}
```

### Session Detail Response
```typescript
interface SessionDetail {
  id: number;
  name: string;
  description: string | null;
  status: SessionStatus;  // 'draft' | 'active' | 'completed'
  qr_code: string | null;
  admin_code: string | null;
  admin_id: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}
```

### Session Status Enumeration
```typescript
type SessionStatus = 'draft' | 'active' | 'completed';
```

## Interface Requirements

### Form Components
- **Session Name Input**: Required text field with validation
- **Session Description Textarea**: Optional multi-line text input
- **Submit Button**: Primary action with loading state
- **Reset/Clear Button**: Secondary action to clear form

### Feedback Components
- **Success Alert**: Green notification for successful session creation
- **Error Alert**: Red notification for validation or server errors
- **Loading Spinner**: Visual indicator during API calls

### Layout Updates
- **Current Session Display**: Show created session information
- **Session List**: Display recent/existing sessions
- **Quick Actions**: Navigate to viewer or manage session

### Responsive Design
- **Mobile Compatibility**: Ensure form works on tablet and mobile devices
- **Accessibility**: Proper ARIA labels and keyboard navigation
- **Loading States**: Clear visual feedback on all screen sizes

## Integration Points

### TanStack Query Integration
- **Mutation Hook**: `useCreateSessionApiV1SessionsPost` for session creation
- **Query Hook**: `useGetSessionsApiV1SessionsGet` for session listing
- **Cache Management**: Proper cache invalidation after session creation
- **Optimistic Updates**: Update UI optimistically where appropriate

### React Router Integration
- **Navigation**: Redirect to session management after creation
- **State Passing**: Pass session data between routes
- **URL Management**: Proper URL structure for session access

### Form State Management
- **React Hook Form**: Use for form validation and state management
- **Validation Schema**: Zod or similar for type-safe validation
- **Error Mapping**: Map API errors to form field errors

## Acceptance Criteria

### Functional Requirements
- [ ] Admin can successfully create a new session through the interface
- [ ] Session name field is required and validates properly
- [ ] Session description field is optional and accepts multi-line text
- [ ] Form validation prevents submission with invalid data
- [ ] API integration creates sessions in the backend database
- [ ] Success message displays after successful session creation
- [ ] Error messages display for network failures and validation errors
- [ ] Form clears after successful submission

### Technical Requirements
- [ ] Uses generated API client from `frontend/src/api/generated.ts`
- [ ] Implements proper TypeScript types throughout
- [ ] Follows existing code patterns and conventions
- [ ] Includes comprehensive error handling
- [ ] Provides loading states for all async operations
- [ ] Implements proper accessibility features

### User Experience Requirements
- [ ] UI is clean and intuitive to use
- [ ] Form provides clear visual feedback
- [ ] Error messages are helpful and specific
- [ ] Loading states prevent user confusion
- [ ] Success flow feels responsive and complete

## Assumptions & Constraints

### Technical Assumptions
- Backend API endpoints are fully functional and tested
- Generated API client types are accurate and up-to-date
- TanStack Query is properly configured in the application
- React Router is set up for navigation
- Tailwind CSS is available for styling

### Business Constraints
- No authentication required for MVP (as per current architecture)
- Session creation is immediate (no approval workflow)
- Simple form validation sufficient for initial release
- Focus on core functionality over advanced features

### Performance Constraints
- Form submission should complete within 3 seconds under normal conditions
- Error handling should be immediate and clear
- Loading states should appear within 100ms of user action
- UI should remain responsive during API calls

## Security Considerations

### Input Validation
- Sanitize all user input before API submission
- Validate input length limits (name max 255 chars, description max 1000 chars)
- Prevent XSS attacks through proper escaping

### API Security
- Use HTTPS for all API communications
- Handle API errors without exposing sensitive server information
- Implement proper CORS handling

### Data Privacy
- No sensitive data collected in session creation
- Session names and descriptions are considered public within the platform
- No persistent user data storage required