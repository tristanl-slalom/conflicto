# Implementation Plan: Add configurable API base URL for frontend environment configuration

**GitHub Issue:** [#81](https://github.com/tristanl-slalom/conflicto/issues/81)
**Generated:** October 8, 2025

## Implementation Strategy

This implementation follows a phased approach to eliminate hardcoded API URLs and introduce environment-based configuration. The strategy prioritizes backwards compatibility while enabling flexible deployment across multiple environments.

### High-Level Approach
1. **Environment Extension**: Extend existing `env.ts` configuration with API base URL support
2. **API Client Modernization**: Replace hardcoded URLs in Orval configuration with dynamic mutator
3. **Build Process Enhancement**: Add environment-specific build scripts and Docker integration
4. **Documentation Update**: Comprehensive documentation and example configurations

### Architecture Alignment
This implementation follows the established Caja frontend patterns:
- Extends existing zod-based environment validation
- Maintains TanStack Query integration patterns
- Preserves Vite build optimization
- Aligns with infrastructure-as-code approach

## File Structure Changes

### New Files to Create
```
frontend/
├── src/
│   └── api/
│       └── mutator.ts              # NEW: Custom API client mutator for environment URLs
├── .env.example                    # NEW: Comprehensive environment variable documentation
└── docker/
    └── .env.docker.example         # NEW: Docker-specific environment examples
```

### Existing Files to Modify
```
frontend/
├── src/
│   └── env.ts                      # MODIFY: Add VITE_API_BASE_URL configuration
├── orval.config.ts                 # MODIFY: Remove hardcoded URLs, add mutator
├── package.json                    # MODIFY: Add environment-specific build scripts
├── Dockerfile                      # MODIFY: Support environment variable injection
├── README.md                       # MODIFY: Add environment configuration documentation
└── vite.config.ts                  # MODIFY: Ensure proper environment variable handling
```

### Generated Files to Update
```
frontend/
└── src/
    └── api/
        └── generated.ts            # REGENERATED: API client with dynamic base URL
```

## Implementation Steps

### Step 1: Extend Environment Configuration
**Files:** `frontend/src/env.ts`

Update the existing environment configuration to include API base URL with proper validation:
```typescript
// Add VITE_API_BASE_URL to existing client configuration
client: {
  VITE_API_BASE_URL: z
    .string()
    .url("API base URL must be a valid URL")
    .default('http://localhost:8000'),
  // ... existing variables
}
```

**Validation:**
- Verify zod validation works correctly
- Test default value behavior
- Ensure type inference works properly

### Step 2: Create Custom API Mutator
**Files:** `frontend/src/api/mutator.ts` (new file)

Create a custom mutator that uses environment-configured base URL:
```typescript
import { env } from '../env';

export const customFetcher = <T>(
  url: string,
  options?: RequestInit
): Promise<T> => {
  const baseUrl = env.VITE_API_BASE_URL;
  const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;

  return fetch(fullUrl, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  }).then(async (response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return response.json();
  });
};
```

**Validation:**
- Test URL construction logic
- Verify error handling
- Ensure type safety

### Step 3: Update Orval Configuration
**Files:** `frontend/orval.config.ts`

Remove hardcoded base URL and configure custom mutator:
```typescript
export default defineConfig({
  caja: {
    input: './openapi.json',
    output: {
      target: './src/api/generated.ts',
      client: 'react-query',
      mock: true,
      httpClient: 'fetch',
      override: {
        mutator: {
          path: './src/api/mutator.ts',
          name: 'customFetcher'
        }
      }
    },
  }
});
```

**Validation:**
- Regenerate API client and verify no hardcoded URLs
- Test generated hooks with TanStack Query
- Ensure mock functionality still works

### Step 4: Add Environment-Specific Build Scripts
**Files:** `frontend/package.json`

Add build scripts for different environments:
```json
{
  "scripts": {
    "build:dev": "VITE_API_BASE_URL=http://localhost:8000 npm run build",
    "build:staging": "npm run build",
    "build:prod": "npm run build",
    "generate:api": "orval --config orval.config.ts",
    "prebuild": "npm run generate:api"
  }
}
```

**Validation:**
- Test each build script
- Verify API client regeneration in prebuild
- Ensure environment variables are properly injected

### Step 5: Update Docker Configuration
**Files:** `frontend/Dockerfile`

Add support for build-time and runtime environment variables:
```dockerfile
# Build stage
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**Validation:**
- Test Docker builds with different API URLs
- Verify runtime environment variable support
- Ensure production optimization works

### Step 6: Create Comprehensive Documentation
**Files:** `frontend/.env.example`, `frontend/README.md`

Create documented environment examples and update README:

`.env.example`:
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000

# Application Configuration
VITE_APP_TITLE=Conflicto

# Development Configuration
VITE_DEBUG=true
```

Update README with environment setup instructions and build process documentation.

**Validation:**
- Verify all environment variables are documented
- Test setup instructions with fresh environment
- Ensure examples work for different scenarios

### Step 7: Update Vite Configuration
**Files:** `frontend/vite.config.ts`

Ensure proper environment variable handling and build optimization:
```typescript
export default defineConfig({
  // ... existing configuration
  define: {
    // Ensure environment variables are properly replaced at build time
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
  },
  envPrefix: 'VITE_',
});
```

**Validation:**
- Test environment variable replacement
- Verify build optimization works
- Ensure hot reload works with environment changes

## Testing Strategy

### Unit Tests
- **Environment Validation**: Test zod schema validation for API URLs
- **Mutator Logic**: Test URL construction and error handling in custom fetcher
- **Build Configuration**: Test build script execution and environment injection

### Integration Tests
- **API Client Generation**: Verify Orval generates correct client with mutator
- **TanStack Query Integration**: Test generated hooks work with different base URLs
- **Environment Switching**: Test switching between dev/staging/production URLs

### End-to-End Tests
- **Multi-Environment Deployment**: Test deployment to different environments
- **Docker Build Process**: Test containerized builds with environment variables
- **Runtime Configuration**: Test application works correctly in each environment

### Manual Testing Scenarios
1. **Local Development**: Test with default localhost URL
2. **Environment Override**: Test with custom environment variables
3. **Production Build**: Test production build with production API URL
4. **Docker Deployment**: Test containerized deployment with injected variables

## Deployment Considerations

### Environment Variable Management
- **Development**: Use `.env.local` for local overrides
- **Staging**: Inject via CI/CD pipeline or container orchestration
- **Production**: Inject via infrastructure-as-code (Terraform)
- **Docker**: Support both build-time and runtime variable injection

### Build Process Integration
- **CI/CD Pipeline**: Update GitHub Actions to pass environment-specific variables
- **Infrastructure**: Ensure Terraform passes correct API URLs to frontend builds
- **CDN Configuration**: Ensure environment-specific builds are deployed to correct origins

### Migration Strategy
1. **Phase 1**: Deploy with backwards-compatible defaults
2. **Phase 2**: Update infrastructure to pass environment variables
3. **Phase 3**: Remove any remaining hardcoded fallbacks
4. **Phase 4**: Validate all environments are using dynamic configuration

## Risk Assessment

### Technical Risks
- **API Client Breaking Changes**: Mitigation through comprehensive testing of generated code
- **Environment Variable Confusion**: Clear documentation and validation prevent misconfiguration
- **Build Process Complexity**: Incremental rollout with fallbacks minimizes disruption
- **Docker Build Issues**: Multi-stage validation and testing catch container problems early

### Deployment Risks
- **Environment Misconfiguration**: Runtime validation and clear error messages help identify issues
- **CORS Problems**: Coordinate with backend team to update CORS configuration for new domains
- **CDN Caching Issues**: Document cache invalidation procedures for environment changes
- **Infrastructure Dependencies**: Ensure infrastructure team coordinates Terraform updates

### Mitigation Strategies
1. **Comprehensive Testing**: Full test coverage across all environment scenarios
2. **Incremental Deployment**: Roll out to development first, then staging, then production
3. **Rollback Plan**: Maintain ability to quickly revert to hardcoded URLs if needed
4. **Monitoring**: Add logging to track API base URL usage and detect configuration issues

## Estimated Effort

### Development Tasks
- **Environment Configuration**: 2 hours (extending existing patterns)
- **Custom Mutator Implementation**: 3 hours (including error handling and testing)
- **Orval Configuration Update**: 1 hour (straightforward configuration change)
- **Build Script Updates**: 2 hours (including Docker integration)
- **Documentation**: 2 hours (comprehensive examples and instructions)

### Testing Tasks
- **Unit Test Development**: 3 hours (environment validation and mutator logic)
- **Integration Testing**: 4 hours (API client generation and TanStack Query integration)
- **Manual Testing**: 3 hours (multi-environment deployment scenarios)
- **Docker Testing**: 2 hours (containerized build and deployment validation)

### Documentation and Review
- **Code Review**: 2 hours (peer review and feedback incorporation)
- **Documentation Review**: 1 hour (technical writing review and updates)
- **Infrastructure Coordination**: 2 hours (coordinate with platform engineering team)

### Total Estimated Effort: 1.25-1.5 days (27 hours)

### Risk Buffer: +25% (6-7 hours) for unexpected integration issues

### Final Estimate: 1.5-2 days including risk mitigation and comprehensive testing

## Success Metrics

### Functional Metrics
- ✅ Zero hardcoded API URLs in generated or source code
- ✅ Successful deployment to all environments (dev/staging/production)
- ✅ All TanStack Query hooks work correctly with dynamic URLs
- ✅ Build process works for all environment-specific scripts

### Quality Metrics
- ✅ >90% test coverage for environment configuration logic
- ✅ All environment variables properly documented with examples
- ✅ Docker builds complete successfully with environment injection
- ✅ No breaking changes to existing development workflows

### Performance Metrics
- ✅ Build times remain within 10% of baseline
- ✅ Bundle size impact <5KB after tree-shaking
- ✅ API client performance unchanged or improved
- ✅ Hot reload performance maintained for development
