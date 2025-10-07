# API Integration with Orval

This project uses [Orval](https://orval.dev/) to automatically generate TypeScript API clients from the OpenAPI specification.

## Generated Files

- `src/api/generated.ts` - Auto-generated API client with React Query hooks and MSW mocks
- This file is regenerated each time you run `npm run generate:api`

## Available Scripts

- `npm run generate:api` - Generate API client from OpenAPI spec
- `npm run generate:api:watch` - Watch mode for API generation (if supported)
- `npm run dev` - Start development server (automatically generates API first)
- `npm run build` - Build for production (automatically generates API first)

## Usage Examples

### Using React Query Hooks

```typescript
import { 
  useListSessionsApiV1SessionsGet,
  useGetSessionApiV1SessionsSessionIdGet,
  useCreateSessionApiV1SessionsPost
} from '../api/generated'

// List all sessions
function SessionsList() {
  const { data, isLoading, error } = useListSessionsApiV1SessionsGet()
  
  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  
  return (
    <div>
      {data?.data.sessions.map(session => (
        <div key={session.id}>{session.title}</div>
      ))}
    </div>
  )
}

// Get specific session
function SessionDetail({ sessionId }: { sessionId: number }) {
  const { data, isLoading } = useGetSessionApiV1SessionsSessionIdGet(sessionId)
  
  if (isLoading) return <div>Loading...</div>
  
  return <div>{data?.data.title}</div>
}

// Create new session
function CreateSession() {
  const mutation = useCreateSessionApiV1SessionsPost()
  
  const handleCreate = () => {
    mutation.mutate({
      data: {
        title: "New Session",
        description: "A test session"
      }
    })
  }
  
  return <button onClick={handleCreate}>Create Session</button>
}
```

### Using MSW for Testing

```typescript
import { setupServer } from 'msw/node'
import { getCajaBackendMock } from '../api/generated'

// Setup MSW server with generated handlers
const server = setupServer(...getCajaBackendMock())

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// Test with custom response
test('should handle session creation', () => {
  server.use(
    getCreateSessionApiV1SessionsPostMockHandler({
      id: 1,
      title: "Test Session",
      status: "draft"
    })
  )
  
  // Your test code here
})
```

## Configuration

The API generation is configured in `orval.config.ts`:

```typescript
import { defineConfig } from 'orval';

export default defineConfig({
  caja: {
    input: '../openapi.json',
    output: {
      target: './src/api/generated.ts',
      client: 'react-query',
      mock: true
    },
  }
});
```

## Updating the API

When the backend OpenAPI specification changes:

1. Run `npm run generate:api` to regenerate the client
2. Update any code that uses changed endpoints
3. The generated file includes TypeScript types that will help catch breaking changes

## Legacy Hooks

The existing `useSession.ts` hooks have been updated to use the generated API client while maintaining backward compatibility. These will be gradually migrated to use the generated types directly.