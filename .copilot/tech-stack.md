# Implementation Standards & Tech Stack Guidelines

## API Development (FastAPI)

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database connection
│   │   └── security.py      # Authentication & authorization
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependency injection
│   │   └── v1/
│   │       ├── sessions.py  # Session endpoints
│   │       ├── activities.py # Activity endpoints
│   │       └── participants.py # Participant endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── session.py       # SQLAlchemy models
│   │   ├── activity.py
│   │   └── participant.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── session.py       # Pydantic schemas
│   │   ├── activity.py
│   │   └── participant.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── session_service.py # Business logic
│   │   ├── activity_service.py
│   │   └── polling_service.py
│   └── tests/
│       ├── conftest.py
│       ├── test_sessions.py
│       └── test_activities.py
├── migrations/              # Alembic migrations
├── Dockerfile
└── requirements.txt
```

### FastAPI Application Setup
```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title="Caja Live Engagement API",
    description="API for live event engagement platform",
    version="1.0.0",
    docs_url="/api/docs" if settings.DEBUG else None
)

# Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Health check endpoint for ECS
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include routers
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(activities.router, prefix="/api/v1", tags=["activities"])
app.include_router(participants.router, prefix="/api/v1", tags=["participants"])
```

### Database Configuration
```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Configure connection pooling for production
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Validate connections before use
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Pydantic Schemas
```python
# app/schemas/session.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class SessionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class SessionCreate(SessionBase):
    admin_id: str = Field(..., min_length=1)

class SessionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None, regex="^(draft|active|completed)$")

class SessionResponse(SessionBase):
    id: UUID
    status: str
    admin_id: str
    qr_code_url: Optional[str]
    current_activity_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

### API Endpoints with Dependency Injection
```python
# app/api/v1/sessions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.services.session_service import SessionService
from app.schemas.session import SessionCreate, SessionUpdate, SessionResponse

router = APIRouter()

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends()
):
    """Create a new session"""
    try:
        session = await session_service.create_session(db, session_data)
        logger.info("Session created", session_id=session.id, admin_id=session.admin_id)
        return session
    except Exception as e:
        logger.error("Session creation failed", error=str(e))
        raise HTTPException(status_code=400, detail="Failed to create session")

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    session_service: SessionService = Depends()
):
    """Get session by ID"""
    session = await session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/sessions/{session_id}/state")
async def get_session_state(
    session_id: UUID,
    last_update: Optional[datetime] = None,
    db: Session = Depends(get_db),
    polling_service: PollingService = Depends()
):
    """Get session state changes for polling clients"""
    return await polling_service.get_state_updates(db, session_id, last_update)
```

### Service Layer Pattern
```python
# app/services/session_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from uuid import UUID, uuid4
from datetime import datetime
import qrcode
import io
import base64

from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionUpdate

class SessionService:
    async def create_session(self, db: Session, session_data: SessionCreate) -> SessionModel:
        # Generate QR code
        qr_code_url = self._generate_qr_code(session_data.name)

        db_session = SessionModel(
            id=uuid4(),
            name=session_data.name,
            description=session_data.description,
            admin_id=session_data.admin_id,
            qr_code_url=qr_code_url,
            status='draft',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(db_session)
        db.commit()
        db.refresh(db_session)

        return db_session

    def _generate_qr_code(self, session_name: str) -> str:
        """Generate QR code for session joining"""
        join_url = f"{settings.FRONTEND_URL}/join/{session_name}"

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(join_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"
```

## Frontend Development (React + TypeScript)

### Project Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   ├── admin/           # Admin-specific components
│   │   ├── viewer/          # Viewer-specific components
│   │   └── participant/     # Participant-specific components
│   ├── hooks/
│   │   ├── usePolling.ts    # Polling hook
│   │   ├── useSession.ts    # Session state management
│   │   └── useActivity.ts   # Activity state management
│   ├── services/
│   │   ├── api.ts           # API client configuration
│   │   ├── sessionApi.ts    # Session API calls
│   │   └── activityApi.ts   # Activity API calls
│   ├── types/
│   │   ├── session.ts       # Session type definitions
│   │   ├── activity.ts      # Activity type definitions
│   │   └── api.ts           # API response types
│   ├── pages/
│   │   ├── AdminDashboard.tsx
│   │   ├── ViewerDisplay.tsx
│   │   └── ParticipantJoin.tsx
│   ├── context/
│   │   └── SessionContext.tsx
│   └── utils/
│       ├── polling.ts
│       └── validation.ts
├── public/
├── package.json
├── tailwind.config.js
└── vite.config.ts
```

### Polling Implementation
```typescript
// hooks/usePolling.ts
import { useState, useEffect, useRef } from 'react';

interface PollingOptions {
  interval: number;
  enabled?: boolean;
  dependencies?: any[];
}

export function usePolling<T>(
  url: string,
  options: PollingOptions
): { data: T | null; error: Error | null; loading: boolean } {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout>();
  const lastUpdateRef = useRef<Date>();

  useEffect(() => {
    if (!options.enabled) return;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        const params = new URLSearchParams();
        if (lastUpdateRef.current) {
          params.append('last_update', lastUpdateRef.current.toISOString());
        }

        const response = await fetch(`${url}?${params}`);
        if (!response.ok) throw new Error('Polling request failed');

        const newData = await response.json();
        if (newData) {
          setData(prevData => ({ ...prevData, ...newData }));
          lastUpdateRef.current = new Date();
        }
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Set up polling interval
    intervalRef.current = setInterval(fetchData, options.interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [url, options.interval, options.enabled, ...(options.dependencies || [])]);

  return { data, error, loading };
}
```

### Session Context Provider
```typescript
// context/SessionContext.tsx
import React, { createContext, useContext, ReactNode } from 'react';
import { usePolling } from '../hooks/usePolling';
import { Session, Activity, Participant } from '../types';

interface SessionContextType {
  session: Session | null;
  currentActivity: Activity | null;
  participants: Participant[];
  loading: boolean;
  error: Error | null;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

interface SessionProviderProps {
  sessionId: string;
  children: ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({
  sessionId,
  children
}) => {
  const { data: sessionData, loading, error } = usePolling<{
    session: Session;
    current_activity: Activity;
    participants: Participant[];
  }>(`/api/v1/sessions/${sessionId}/state`, {
    interval: 2000,
    enabled: !!sessionId
  });

  const value = {
    session: sessionData?.session || null,
    currentActivity: sessionData?.current_activity || null,
    participants: sessionData?.participants || [],
    loading,
    error
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};
```

### API Client Configuration
```typescript
// services/api.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth headers
apiClient.interceptors.request.use(
  (config) => {
    // Add authentication headers if needed
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);
```

## AWS Infrastructure (Terraform)

### Directory Structure
```
infrastructure/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── ecs/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/
│   └── s3-cloudfront/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
└── shared/
    ├── backend.tf
    └── providers.tf
```

### ECS Service Configuration
```hcl
# modules/ecs/main.tf
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = var.tags
}

resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  health_check_grace_period_seconds = 300

  depends_on = [aws_lb_listener.api]
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = "${var.api_image_uri}:${var.api_image_tag}"

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "DATABASE_URL"
          value = var.database_url
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        }
      ]

      secrets = [
        {
          name      = "DATABASE_PASSWORD"
          valueFrom = var.database_password_secret_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}
```

## Testing Strategies

### Backend Testing (Pytest)
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

# tests/test_sessions.py
def test_create_session(client):
    response = client.post(
        "/api/v1/sessions",
        json={
            "name": "Test Session",
            "description": "Test session description",
            "admin_id": "test_admin"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Session"
    assert "id" in data
```

### Frontend Testing (Jest + RTL)
```typescript
// components/__tests__/SessionJoin.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SessionJoin } from '../SessionJoin';
import { SessionProvider } from '../../context/SessionContext';

const MockSessionProvider = ({ children }: { children: React.ReactNode }) => (
  <SessionProvider sessionId="test-session">
    {children}
  </SessionProvider>
);

describe('SessionJoin', () => {
  it('allows participant to join with nickname', async () => {
    render(
      <MockSessionProvider>
        <SessionJoin />
      </MockSessionProvider>
    );

    const nicknameInput = screen.getByPlaceholderText('Enter your nickname');
    const joinButton = screen.getByText('Join Session');

    fireEvent.change(nicknameInput, { target: { value: 'TestUser' } });
    fireEvent.click(joinButton);

    await waitFor(() => {
      expect(screen.getByText('Welcome, TestUser!')).toBeInTheDocument();
    });
  });
});
```

## Deployment Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run backend tests
        run: |
          cd backend
          pytest

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci

      - name: Run frontend tests
        run: |
          cd frontend
          npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: caja-api
          IMAGE_TAG: ${{ github.sha }}
        run: |
          cd backend
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Deploy infrastructure
        run: |
          cd infrastructure/environments/prod
          terraform init
          terraform plan
          terraform apply -auto-approve

      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster caja-prod \
            --service caja-api \
            --force-new-deployment

      - name: Deploy frontend to S3
        run: |
          cd frontend
          npm run build
          aws s3 sync dist/ s3://caja-frontend-prod --delete
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```

This comprehensive tech stack guide ensures consistent implementation patterns across all aspects of the Caja platform, from API development to infrastructure deployment.
