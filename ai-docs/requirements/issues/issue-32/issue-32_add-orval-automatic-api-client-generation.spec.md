# Technical Specification: Add Orval for automatic API client generation from OpenAPI spec

**GitHub Issue:** [#32](https://github.com/tristanl-slalom/conflicto/issues/32)
**Generated:** 2025-10-07T17:30:00Z

## Problem Statement

The frontend currently uses manual API client code with mock implementations, leading to:
- Type safety gaps between backend OpenAPI schemas and frontend types
- Manual maintenance overhead when backend APIs change
- Inconsistent mock data for testing that doesn't match actual API responses
- Developer friction when adding new API endpoints

The backend already generates a comprehensive OpenAPI specification (`openapi.json`) but the frontend doesn't leverage it for type-safe API client generation.

## Technical Requirements

### Core Functionality
1. **Automatic TypeScript Generation**: Generate TypeScript interfaces from OpenAPI schemas matching backend models exactly
2. **React Query Integration**: Generate TanStack Query hooks for all API endpoints with proper typing
3. **MSW Mock Generation**: Create Mock Service Worker handlers that match the OpenAPI spec for testing
4. **Hot Reload Support**: Regenerate client code when OpenAPI spec changes during development
5. **Build Integration**: Ensure API client generation is part of the build process

### Type Safety Requirements
- Frontend types must match backend Pydantic models exactly
- Compile-time errors when frontend code doesn't match API contracts
- IntelliSense support for all API endpoints and response types
- Enum types must be preserved from backend to frontend

### Performance Requirements
- Generated code should not significantly increase bundle size
- React Query hooks should include appropriate caching strategies
- Polling-based real-time updates must continue to work (2-3 second intervals)

## API Specifications

Based on the current `openapi.json`, the following endpoints will have generated clients:

### Health Endpoints
- `GET /api/v1/health/` → `useHealthCheckQuery()`
- `GET /api/v1/health/ready` → `useReadinessCheckQuery()`
- `GET /api/v1/health/live` → `useLivenessCheckQuery()`

### Session Management Endpoints
- `POST /api/v1/sessions/` → `useCreateSessionMutation()`
- `GET /api/v1/sessions/` → `useListSessionsQuery({ offset?, limit? })`
- `GET /api/v1/sessions/{session_id}` → `useGetSessionQuery(sessionId)`
- `PUT /api/v1/sessions/{session_id}` → `useUpdateSessionMutation()`
- `DELETE /api/v1/sessions/{session_id}` → `useDeleteSessionMutation()`
- `GET /api/v1/sessions/code/{code}` → `useGetSessionByCodeQuery(code, codeType?)`

### Generated Hook Signatures
```typescript
// List sessions with pagination
const { data, isLoading, error } = useListSessionsQuery({ offset: 0, limit: 10 });
// data: SessionList | undefined

// Get specific session
const { data: session } = useGetSessionQuery(sessionId);
// data: SessionDetail | undefined

// Create session mutation
const createMutation = useCreateSessionMutation();
// createMutation.mutate(sessionData: SessionCreate)

// Update session mutation  
const updateMutation = useUpdateSessionMutation();
// updateMutation.mutate({ sessionId: number, data: SessionUpdate })
```

## Data Models

All OpenAPI component schemas will be generated as TypeScript interfaces:

### Core Types
```typescript
interface SessionResponse {
  id: number;
  created_at: string;
  updated_at: string;
  title: string;
  description: string | null;
  status: SessionStatus;
  qr_code: string | null;
  admin_code: string | null;
  max_participants: number;
  started_at: string | null;
  completed_at: string | null;
  participant_count: number;
  activity_count: number;
}

interface SessionDetail extends SessionResponse {
  activities: ActivityResponse[];
  participants: ParticipantResponse[];
}

interface SessionCreate {
  title: string;
  description?: string | null;
  max_participants?: number;
}

type SessionStatus = "draft" | "active" | "completed";
type ActivityType = "poll" | "word_cloud" | "qa" | "planning_poker";
type ParticipantRole = "admin" | "viewer" | "participant";
```

### Error Handling Types
```typescript
interface ErrorResponse {
  detail: string;
  error_type?: string;
  timestamp?: string;
}

interface HTTPValidationError {
  detail?: ValidationError[];
}
```

## Interface Requirements

### Orval Configuration Structure
- Configuration file: `orval.config.ts` in frontend root
- Generated API client: `src/api/generated.ts`
- Generated MSW handlers: `src/mocks/handlers.ts`
- HTTP client: Axios (to be added as dependency)

### Integration with Existing Code
- Replace current mock API implementations in `useSession.ts`
- Maintain existing React Query hook names where possible
- Preserve polling intervals and caching strategies
- Update component imports to use generated types

### Development Workflow
- `npm run generate:api` - Manual generation
- `npm run generate:api:watch` - Watch mode for development
- `npm run dev` - Should include API generation step
- `npm run build` - Must include API generation step

## Integration Points

### TanStack Query Integration
- Generated hooks must use existing QueryClient configuration
- Maintain current query key patterns for cache invalidation
- Preserve optimistic updates and polling behavior

### Testing Integration
- MSW handlers generated from same OpenAPI spec
- Integration with existing Vitest setup
- Mock handlers available in test environment by default

### Build System Integration
- Vite plugin to watch OpenAPI file changes
- Pre-build API generation step
- Proper TypeScript compilation of generated code

## Acceptance Criteria

### Functional Requirements
- [ ] TypeScript interfaces generated for all OpenAPI schemas
- [ ] React Query hooks generated for all API endpoints
- [ ] MSW handlers generated for all endpoints matching OpenAPI spec
- [ ] Generated code follows project linting and formatting rules
- [ ] Hot reload works when `openapi.json` changes in development

### Quality Requirements
- [ ] Build process fails with clear error if OpenAPI spec is invalid
- [ ] Generated code has zero TypeScript compilation errors
- [ ] Generated hooks maintain existing caching and polling behavior
- [ ] All existing components continue to work with new generated types

### Developer Experience
- [ ] IntelliSense provides accurate completions for API endpoints
- [ ] Type errors occur when frontend code doesn't match backend API
- [ ] New backend endpoints automatically generate frontend code
- [ ] Clear documentation for using generated hooks and types

### Testing Requirements
- [ ] Generated MSW handlers work in test environment
- [ ] Tests can mock specific API responses using generated handlers
- [ ] Component tests continue to pass with generated types
- [ ] Integration tests validate generated code matches actual API

## Assumptions & Constraints

### Technical Assumptions
- `openapi.json` file will remain in project root
- Backend maintains backward-compatible API changes
- Existing TanStack Query configuration remains stable
- Axios is acceptable as HTTP client (currently not used)

### Development Constraints
- Must not break existing components during migration
- Generated code should be gitignored (ephemeral)
- Configuration should be minimal and self-documenting
- Should work seamlessly with existing development tools (VS Code, etc.)

### Performance Constraints
- API generation should complete within 10 seconds
- Generated code should not significantly increase bundle size
- Watch mode should have minimal performance impact
- Build time increase should be < 30 seconds

## Migration Strategy

### Phase 1: Setup and Configuration
- Install Orval and dependencies
- Create configuration file
- Generate initial API client
- Verify generated code compiles

### Phase 2: Hook Migration
- Update `useSession.ts` to use generated types
- Replace mock API calls with generated hooks
- Maintain existing hook names and signatures where possible
- Test with existing components

### Phase 3: Testing Integration
- Setup MSW with generated handlers
- Update test setup to use generated mocks
- Verify all tests pass with new API client

### Phase 4: Build Integration
- Add API generation to build process
- Configure watch mode for development
- Update documentation and developer guides

This specification ensures type-safe, maintainable API client generation that integrates seamlessly with the existing Caja platform architecture while improving developer experience and reducing maintenance overhead.