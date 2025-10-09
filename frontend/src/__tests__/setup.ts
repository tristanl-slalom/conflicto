import { vi, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Test setup configuration for Caja frontend
// This file is loaded before each test to setup the testing environment

// Cleanup DOM after each test to prevent cross-test pollution
afterEach(() => {
  cleanup();
});

// Setup localStorage mock
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
  });

  // Setup ResizeObserver mock
  window.ResizeObserver = vi.fn().mockImplementation(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn(),
  }));

  // Setup matchMedia mock
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
}

// Mock TanStack Router
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(() => ({
    component: () => null,
  })),
  Link: ({ children }: any) => children,
  useNavigate: () => vi.fn(),
  useParams: () => ({}),
  useSearch: () => ({}),
}));

// Mock TanStack Query - allow actual implementation to work properly in tests
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    // Don't mock the core functionality, let it work normally for tests
  };
});

// Mock Lucide React icons
vi.mock('lucide-react', () => {
  const MockIcon = () => null;

  return {
    Settings: MockIcon,
    Monitor: MockIcon,
    Smartphone: MockIcon,
    Users: MockIcon,
    BarChart3: MockIcon,
    Zap: MockIcon,
    QrCode: MockIcon,
    Send: MockIcon,
    CheckCircle: MockIcon,
    Maximize: MockIcon,
    // Additional icons used in admin components
    Copy: MockIcon,
    AlertTriangle: MockIcon,
    Maximize2: MockIcon,
    Clock: MockIcon,
    Play: MockIcon,
    Pause: MockIcon,
    Square: MockIcon,
    UserPlus: MockIcon,
    UserMinus: MockIcon,
    Eye: MockIcon,
    EyeOff: MockIcon,
    Trash2: MockIcon,
    Plus: MockIcon,
    Edit: MockIcon,
    X: MockIcon,
    ExternalLink: MockIcon,
    Download: MockIcon,
    Save: MockIcon,
    RefreshCw: MockIcon,
  };
});
