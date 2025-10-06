# System Architecture & Data Models

## Monorepo Structure
```
caja/
├── backend/          # Python FastAPI application
│   ├── app/
│   │   ├── models/      # SQLAlchemy models
│   │   ├── api/         # API route handlers
│   │   ├── services/    # Business logic layer
│   │   ├── activities/  # Activity type implementations
│   │   └── polling/     # Polling-based communication
├── frontend/         # React application
│   ├── src/
│   │   ├── components/  # Reusable UI components
│   │   ├── pages/       # Route-based page components
│   │   ├── hooks/       # Custom React hooks
│   │   ├── services/    # API communication
│   │   └── types/       # TypeScript type definitions
├── infrastructure/   # Terraform configurations
│   ├── modules/         # Reusable Terraform modules
│   ├── environments/    # Environment-specific configs
│   └── shared/          # Shared infrastructure resources
└── shared/           # Shared types and utilities
```

## Core Data Models

### Session
```typescript
interface Session {
  id: UUID;
  name: string;
  status: 'draft' | 'active' | 'completed';
  activities: Activity[];
  created_at: datetime;
  admin_id: string;
  qr_code_url?: string;
  current_activity_id?: UUID;
}
```

### Activity
```typescript
interface Activity {
  id: UUID;
  session_id: UUID;
  type: 'poll' | 'poker' | 'quiz' | 'wordcloud';
  config: ActivityConfig; // activity-specific configuration
  order: integer;
  status: 'draft' | 'active' | 'expired';
  title: string;
  description?: string;
  timeout_seconds?: integer;
}
```

### Participant
```typescript
interface Participant {
  id: UUID; // session-scoped
  session_id: UUID;
  nickname: string;
  joined_at: datetime;
  last_activity: datetime;
  connection_status: 'connected' | 'disconnected';
}
```

### Response
```typescript
interface Response {
  id: UUID;
  participant_id: UUID;
  activity_id: UUID;
  response_data: JSON; // activity-specific response format
  submitted_at: datetime;
}
```

## Database Schema Guidelines

### PostgreSQL Tables
- Use UUID primary keys for all entities
- Include created_at and updated_at timestamps
- Use JSONB for flexible configuration storage
- Implement proper foreign key constraints
- Add indexes for frequent query patterns

### Example SQLAlchemy Model
```python
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default='draft')
    admin_id = Column(String(255), nullable=False)
    qr_code_url = Column(Text)
    current_activity_id = Column(UUID(as_uuid=True), ForeignKey('activities.id'))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
```

## API Architecture Patterns

### FastAPI Structure
- Group routes by domain (sessions, activities, participants)
- Use dependency injection for database connections
- Implement Pydantic models for request/response validation
- Add comprehensive OpenAPI documentation
- Include proper error handling and HTTP status codes

### Polling-Based Updates
```python
# Example polling endpoint
@app.get("/api/sessions/{session_id}/state")
async def get_session_state(
    session_id: UUID,
    last_update: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Return session state changes since last_update timestamp"""
    # Only return changes since last_update to minimize data transfer
    pass
```

## Frontend Architecture

### React Component Hierarchy
```
App
├── Router
├── SessionProvider (Context)
├── Admin/
│   ├── SessionManager
│   ├── ActivityEditor
│   └── ContentPreview
├── Viewer/
│   ├── SessionDisplay
│   ├── QRCodeOverlay
│   └── ResultsView
└── Participant/
    ├── SessionJoin
    ├── ActivityInterface
    └── ResponseFeedback
```

### State Management
- Use React Context for session-level state
- Custom hooks for polling logic
- React Query for API state management
- Local component state for UI interactions

### Polling Implementation
```typescript
// Custom hook for polling session state
function useSessionPolling(sessionId: string) {
  const [sessionState, setSessionState] = useState();
  
  useEffect(() => {
    const interval = setInterval(async () => {
      const updates = await fetchSessionUpdates(sessionId, lastUpdate);
      if (updates.length > 0) {
        setSessionState(prev => mergeUpdates(prev, updates));
      }
    }, 2000); // Poll every 2 seconds
    
    return () => clearInterval(interval);
  }, [sessionId]);
  
  return sessionState;
}
```

## AWS Infrastructure Architecture

### ECS Service Configuration
- Use Fargate for serverless containers
- Auto-scaling based on CPU/memory metrics
- Health checks on custom endpoints
- Blue-green deployment strategy

### RDS Configuration
- Multi-AZ deployment for high availability
- Automated backups with point-in-time recovery
- Connection pooling for efficient database access
- Read replicas for read-heavy workloads (if needed)

### S3 and CloudFront
- S3 for static asset hosting and file uploads
- CloudFront for global CDN with caching rules
- Proper CORS configuration for API access
- SSL/TLS termination at CloudFront

### Security Patterns
- Private subnets for database and backend services
- Public subnets only for load balancers
- Security groups with least-privilege access
- AWS Secrets Manager for database credentials
- IAM roles with minimal required permissions

## Development Patterns

### Error Handling
```python
# Backend error handling
from fastapi import HTTPException
from pydantic import ValidationError

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": exc.errors()}
    )
```

```typescript
// Frontend error handling
function useApiCall<T>(apiFunction: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);
  
  const execute = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction();
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };
  
  return { data, error, loading, execute };
}
```

### Testing Patterns
- Unit tests for business logic and utilities
- Integration tests for API endpoints with test database
- Component tests for React components with React Testing Library
- End-to-end tests for critical user flows with Playwright
- Infrastructure tests with Terraform validation

### Logging Standards
```python
import structlog

logger = structlog.get_logger()

# Structured logging for CloudWatch
logger.info("Session created", 
    session_id=session.id,
    admin_id=session.admin_id,
    activity_count=len(session.activities)
)
```