# Technical Specification: Add configurable API base URL for frontend environment configuration

**GitHub Issue:** [#81](https://github.com/tristanl-slalom/conflicto/issues/81)
**Generated:** October 8, 2025

## Problem Statement

The frontend currently hardcodes the API base URL to `http://localhost:8000` in multiple places, making it impossible to deploy to different environments (dev, staging, production) without manual code changes. This creates deployment issues and prevents proper environment separation.

### Current Issues
1. **Hardcoded API URLs**: The Orval-generated API client hardcodes `http://localhost:8000` in all endpoint functions
2. **No Environment Configuration**: Missing environment variable support for API base URL
3. **Deployment Blockers**: Cannot deploy frontend to different environments without code changes
4. **Development Friction**: Local development requires manual URL updates when backend runs on different ports

## Technical Requirements

### 1. Environment Variable Management
- Implement `VITE_API_BASE_URL` environment variable with proper validation
- Extend existing `frontend/src/env.ts` configuration schema
- Provide sensible defaults for different deployment environments
- Ensure type safety and runtime validation using existing zod schemas

### 2. Orval Configuration Modernization
- Update `frontend/orval.config.ts` to eliminate hardcoded base URLs
- Implement custom API mutator for environment-aware requests
- Maintain generated API client compatibility with existing TanStack Query integration
- Support build-time configuration for static optimization

### 3. Build Process Enhancement
- Add environment-specific build scripts for dev/staging/production
- Create comprehensive `.env.example` with documentation
- Integrate with existing Docker build processes
- Support Vite's environment variable system

### 4. Infrastructure Integration
- Align with existing Terraform infrastructure variables
- Support CDN and custom domain configurations from infrastructure layer
- Enable proper CORS configuration management
- Maintain compatibility with existing deployment pipeline

## API Specifications

### Environment Configuration Schema
```typescript
// Extension to existing frontend/src/env.ts
export const env = createEnv({
  client: {
    VITE_API_BASE_URL: z
      .string()
      .url("Invalid API base URL format")
      .default('http://localhost:8000'),
    VITE_APP_TITLE: z.string().min(1).optional(),
    // ... existing configuration
  },
  // ... existing server-side configuration
});
```

### API Client Mutator Interface
```typescript
// frontend/src/api/mutator.ts
export interface ApiMutatorConfig {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}

export const customFetcher = <T>(
  url: string,
  options?: RequestInit
): Promise<T>;
```

### Build Script Configuration
```json
{
  "scripts": {
    "build:dev": "VITE_API_BASE_URL=${DEV_API_URL:-http://localhost:8000} npm run build",
    "build:staging": "VITE_API_BASE_URL=${STAGING_API_URL} npm run build",
    "build:prod": "VITE_API_BASE_URL=${PROD_API_URL} npm run build"
  }
}
```

## Data Models

### Environment Configuration Types
```typescript
// Types for environment configuration
export interface EnvironmentConfig {
  apiBaseUrl: string;
  appTitle?: string;
  environment: 'development' | 'staging' | 'production';
}

// Runtime environment validation
export interface ApiClientConfig {
  baseUrl: string;
  defaultHeaders: Record<string, string>;
  timeout: number;
}
```

### Orval Configuration Schema
```typescript
// Updated orval.config.ts structure
export interface OrvalConfig {
  caja: {
    input: string;
    output: {
      target: string;
      client: 'react-query';
      mock: boolean;
      httpClient: 'fetch';
      override: {
        mutator: {
          path: string;
          name: string;
        };
      };
    };
  };
}
```

## Interface Requirements

### Developer Experience
- Seamless local development with sensible defaults
- Clear error messages for invalid API URLs
- Hot reload support for environment variable changes
- Backwards compatibility with existing development workflows

### Build Process Interface
- Environment-specific build commands
- Docker build argument support
- CI/CD pipeline integration points
- Static asset optimization for different environments

### Configuration Management
- Clear documentation in `.env.example`
- Type-safe environment variable access
- Runtime validation with meaningful error messages
- Development vs production configuration patterns

## Integration Points

### Existing Frontend Architecture
- **TanStack Query Integration**: Generated API client must maintain existing query hooks
- **Environment System**: Extends existing `frontend/src/env.ts` configuration
- **Build Process**: Integrates with existing Vite configuration and npm scripts
- **Docker Integration**: Works with existing `frontend/Dockerfile` and build processes

### Backend Coordination
- **CORS Configuration**: Backend must accept requests from different frontend origins
- **API Versioning**: Maintains compatibility with existing API endpoints
- **Health Checks**: Support for environment-specific health check endpoints

### Infrastructure Dependencies
- **Terraform Variables**: Aligns with existing infrastructure environment configuration
- **CI/CD Pipeline**: Integrates with existing GitHub Actions workflows
- **CDN Configuration**: Supports infrastructure-managed CDN domains
- **Domain Management**: Works with DNS configuration from infrastructure layer

## Acceptance Criteria

### Environment Configuration
- [ ] `VITE_API_BASE_URL` environment variable is properly typed and validated in `frontend/src/env.ts`
- [ ] Frontend respects API base URL from environment variables across all API calls
- [ ] Fallback to `http://localhost:8000` for local development when not specified
- [ ] Environment validation prevents invalid URLs with clear error messages
- [ ] Hot reload works correctly when environment variables change

### API Client Generation
- [ ] Orval generates API client with configurable base URL (no hardcoded URLs)
- [ ] Generated API functions use environment-configured base URL via custom mutator
- [ ] No hardcoded localhost references in generated code (`frontend/src/api/generated.ts`)
- [ ] API client works correctly in all environments (dev/staging/production)
- [ ] Existing TanStack Query hooks continue to function without breaking changes

### Build and Deployment
- [ ] Environment-specific build scripts work correctly (`npm run build:dev`, `build:staging`, `build:prod`)
- [ ] Production builds use production API URLs without hardcoded references
- [ ] Development builds use development API URLs with proper fallbacks
- [ ] Docker builds support environment variable injection at build and runtime
- [ ] Vite build optimization works correctly with environment variables

### Documentation and Examples
- [ ] `.env.example` file documents all required environment variables with examples
- [ ] README updated with environment configuration setup instructions
- [ ] Build process documentation includes environment setup procedures
- [ ] Developer onboarding documentation reflects new configuration requirements

## Assumptions & Constraints

### Technical Assumptions
- Vite environment variable system will be used (VITE_ prefixed variables)
- Existing zod-based environment validation pattern will be extended
- Orval code generation will continue to be used for API client
- TanStack Query integration must remain unchanged
- Docker build process supports multi-stage builds with environment arguments

### Development Constraints
- Must maintain backwards compatibility with existing development workflows
- Cannot introduce breaking changes to existing API client usage
- Must work with existing CI/CD pipeline without major modifications
- Should not require changes to backend API endpoints
- Must support offline development scenarios

### Deployment Constraints
- Static site deployment requirements (no server-side environment resolution)
- CDN caching considerations for environment-specific builds
- Container orchestration environment variable injection patterns
- Infrastructure-as-code integration requirements

### Performance Constraints
- No significant impact on build times
- No runtime performance degradation for API calls
- Minimal bundle size impact from environment configuration
- Efficient tree-shaking for unused environment variables
