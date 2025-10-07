# Technical Decisions Log - Caja Frontend

## Testing Framework Migration: Jest → Vitest

**Date:** October 7, 2025
**Issue:** React frontend test framework alignment
**Decision:** Migrate from Jest to Vitest for better Vite integration

### Background
The React frontend was initially implemented with Jest testing but the project uses Vite as the build tool. This created conflicts and compatibility issues when running `npm test`.

### Problem Details
- Jest configuration (`jest.config.js`) was incompatible with Vite setup
- Tests used Jest-specific matchers (`toBeInTheDocument`, `toHaveAttribute`, etc.) that don't exist in Vitest
- DOM testing utilities needed to be reconfigured for Vitest environment
- Mock setup required conversion from Jest syntax to Vitest syntax

### Solution Implemented

#### 1. Configuration Changes
- **Removed:** `jest.config.js`
- **Added:** `vitest.config.ts` with proper Vite plugin integration
- **Environment:** Configured `jsdom` environment for DOM testing
- **Setup:** Created `src/__tests__/setup.ts` for test environment configuration

#### 2. Test Utilities Migration
**From Jest DOM matchers to native assertions:**
```javascript
// Before (Jest)
expect(element).toBeInTheDocument()
expect(element).toHaveAttribute('href', '/admin')
expect(element).toHaveTextContent('12')
expect(button).toBeDisabled()

// After (Vitest)
expect(element).toBeDefined()
expect(element.getAttribute('href')).toBe('/admin')
expect(element.textContent).toBe('12')
expect((button as HTMLButtonElement).disabled).toBe(true)
```

#### 3. Mock System Conversion
**From Jest mocks to Vitest mocks:**
```javascript
// Before
jest.fn()
jest.mock()

// After
vi.fn()
vi.mock()
```

#### 4. Test Setup Changes
- **Browser APIs:** Mocked `localStorage`, `ResizeObserver`, `matchMedia`
- **External Libraries:** Mocked TanStack Router, TanStack Query, Lucide React icons
- **Cleanup:** Added `afterEach(() => cleanup())` for proper test isolation

### Results
- ✅ All 15 tests now pass with Vitest
- ✅ Faster test execution due to native Vite integration
- ✅ Better TypeScript support out of the box
- ✅ Simplified mock syntax and setup
- ✅ Native ES modules support

### Configuration Files

**vitest.config.ts:**
```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.ts'],
    include: [
      'src/**/*.{test,spec}.{ts,tsx}',
      'src/**/__tests__/**/*.{test,spec}.{ts,tsx}'
    ],
    exclude: [
      '**/setup.ts',
      '**/setup.js'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/__tests__/**',
        'src/**/node_modules/**'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  }
})
```

### Impact on Development Workflow
- `npm run test` now works seamlessly with the Vite build system
- Test development aligned with build toolchain (Vite)
- Improved developer experience with faster test feedback
- Consistent toolchain reduces context switching

### Recommendations for Future Development
1. Use Vitest-native assertions instead of testing-library/jest-dom
2. Leverage Vitest's built-in coverage reporting (v8 provider)
3. Use `vi.mock()` for all external library mocking
4. Test setup should focus on browser API mocks in `setup.ts`
5. Prefer `toBeDefined()`, `.textContent`, `.getAttribute()` over Jest DOM matchers

---

## Frontend Architecture Implementation

**Date:** October 7, 2025
**Component:** React Multi-Persona Interface System
**Status:** Completed - MVP Implementation

### Implementation Summary
Successfully implemented the three-persona interface system with:

#### Routes Structure
```
src/routes/
├── __root.tsx           # Root layout with TanStack Router
├── index.tsx            # Landing page with persona selection
├── admin/
│   └── index.tsx        # Administrative interface
├── viewer/
│   └── index.tsx        # Large screen display interface
└── participant/
    └── index.tsx        # Mobile-optimized participant interface
```

#### Component Architecture
- **PersonaLayout:** Reusable layout component with persona-specific theming
- **UI Components:** shadcn/ui component library integration
- **State Management:** TanStack Query for server state with polling
- **Routing:** File-based routing via TanStack Router

#### Key Features Implemented
1. **Landing Page:** Persona selection with responsive cards
2. **Admin Interface:** Session creation forms and management controls
3. **Viewer Interface:** QR code display and live results visualization
4. **Participant Interface:** Mobile-optimized voting and interaction UI

#### Testing Coverage
- 13 component tests covering all three personas
- Mock implementations for session management hooks
- Test utilities for TanStack Query and Router integration

### Technical Stack Validation
✅ **React 18+** with TypeScript for type safety
✅ **TanStack Start** for file-based routing and SSR capability
✅ **TanStack Query** for server state management with polling
✅ **shadcn/ui + Tailwind CSS** for consistent UI components
✅ **Vitest** for testing framework aligned with Vite build system
✅ **Lucide React** for consistent iconography

### Performance Considerations
- Implemented 2-3 second polling intervals for real-time updates
- Responsive design optimized for mobile-first participant experience
- Large screen optimization for viewer displays
- Component-level code splitting ready for production

---

## Development Tooling Enhancements

**Date:** October 7, 2025
**Area:** Testing and Development Workflow
**Impact:** Improved Developer Experience

### Key Improvements
1. **Test Framework Alignment:** Vitest integration with Vite build system
2. **Type Safety:** Comprehensive TypeScript coverage across all components
3. **Component Testing:** Full test coverage for multi-persona interface system
4. **Mock Strategy:** Streamlined mocking for external dependencies
5. **Development Scripts:** Working `npm test` with proper coverage reporting

### Development Workflow Validation
- ✅ Fast test feedback loop with Vitest
- ✅ Type checking integrated with build process
- ✅ Component development with hot reload
- ✅ Mock implementations for external APIs ready for backend integration
- ✅ Coverage reporting configured for CI/CD pipeline

### Future Development Readiness
The frontend foundation is now ready for:
- Backend API integration (TanStack Query setup complete)
- WebSocket real-time communication (polling framework in place)
- Additional activity type implementations (component architecture established)
- Production deployment (build system optimized)

---

## Backend Data Architecture Refinement

**Date:** October 7, 2025
**Issue:** Activity data model and user response storage strategy
**Decision:** Flexible JSON-based user response storage with activity-specific components

### Background
During backend architecture refinement discussions, the team debated between a structured relational approach vs. a flexible JSON-based approach for storing user responses across different activity types.

### Problem Analysis

#### Structured Relational Approach
**Proposed Structure:**
- Session → Activities → Questions → Answers (with predefined answer types)
- Enforced schema: statement, question_type, possible_answers
- Relational integrity and easy querying

**Challenges Identified:**
- Premature optimization for unknown future activity types
- System responsibility for data structure interpretation
- Rigid schema limiting activity innovation
- Complex migrations when adding new activity types

#### Flexible JSON Approach
**Proposed Structure:**
- Session → Activities → User Responses (JSON blobs)
- Activity-defined response schema
- Front-end responsibility for data interpretation

**Advantages:**
- Future-proof for unknown activity types
- Activity autonomy over data structure
- Simpler backend implementation
- Easier activity development and deployment

### Decision Rationale

#### Why JSON Blob Storage Won
1. **Modularity:** Each activity type becomes self-contained with its own data contract
2. **Extensibility:** New activities can be added without backend schema changes
3. **Simplicity:** Backend becomes activity-agnostic data storage
4. **Scale Appropriate:** Expected response volumes (≤100 per activity) make JSON querying feasible

#### Trade-offs Accepted
- **Query Complexity:** Aggregation requires JSON processing instead of SQL joins
- **Type Safety:** Response structure validation moves to application layer
- **Reporting:** Cross-activity analytics become more complex

### Implementation Details

#### Database Schema
```sql
-- Core entities
sessions (id, name, status, admin_id, created_at)
activities (id, session_id, type, config, order, status)
participants (id, session_id, nickname, joined_at)

-- Flexible user responses
user_responses (id, session_id, activity_id, participant_id, response_data, created_at)
-- response_data: JSONB column containing activity-specific response structure
```

#### Activity Component Architecture
Each activity type implements three distinct components:
1. **Configuration Component:** Admin interface for activity setup
2. **Participant Component:** User interaction interface
3. **Viewer Component:** Real-time results display

#### Data Flow Pattern
1. **Configuration:** Admin configures activity using configuration component
2. **Storage:** Configuration stored in `activities.config` (JSON)
3. **Participation:** Users interact via participant component
4. **Response:** User responses stored in `user_responses.response_data` (JSON)
5. **Aggregation:** Viewer component processes and displays aggregated responses

### Activity Autonomy Principle
- **Frontend Responsibility:** Each activity defines its own data structure
- **Backend Responsibility:** Generic CRUD operations on JSON data
- **No System Interpretation:** Backend has no knowledge of response semantics

### Session Configuration vs. Instance Pattern
**Configuration (Class):** Template defining activity types and order
**Instance (Object):** Runtime session with participant data and responses

Example: Sprint Planning session configuration enables repeated planning poker activities without predefined story count.

### Development Workflow Impact
- **New Activity Development:** Only requires frontend component creation
- **Backend Stability:** Core API remains unchanged for new activity types
- **Testing:** Each activity can be tested in isolation
- **Deployment:** Activity updates deployable independently

---

## Development Orchestration Enhancement

**Date:** October 7, 2025
**Issue:** Cross-service development workflow coordination
**Decision:** Comprehensive Makefile for backend and frontend orchestration

### Background
The project evolved from backend-only development to full-stack application requiring coordinated development workflows across both services.

### Implementation Plan
**Makefile targets identified for implementation:**
- `start-backend`, `start-frontend`, `start-all`
- `stop-all`, `restart-all`, `status`
- `test-backend`, `test-frontend`, `test-all`
- `test-watch`, `test-coverage`

### Development Process Innovation
**Enhanced Issue Implementation Process:**
1. AI generates implementation plan from issue description
2. Developer reviews and modifies plan before execution
3. Provides opportunity for scope refinement and technical approach validation
4. Estimated effort tracking for retrospective analysis

**Benefits:**
- Scope validation before implementation begins
- Technical approach alignment across team
- Effort estimation for planning purposes
- Implementation plan serves as documentation

---

## Next Implementation Phases

### Phase 2: Backend Data Foundation
- Implement flexible user response storage with JSONB
- Create generic activity CRUD endpoints
- Establish session configuration vs. instance pattern
- Build activity-agnostic aggregation endpoints

### Phase 3: Activity Component Framework
- Implement activity-specific React components (Poll, Poker, Quiz, Word Cloud)
- Create configuration interfaces for each activity type
- Build real-time viewer components with JSON response processing
- Establish activity development patterns and guidelines

### Phase 4: Development Workflow
- Complete Makefile implementation for service orchestration
- Establish activity deployment and versioning strategy
- Create activity development documentation and templates
- Implement cross-service testing automation

### Phase 5: Production Readiness
- Performance optimization for JSON querying at scale
- Error boundary implementation for activity component failures
- Activity monitoring and analytics integration
- Session archival and data retention policies
