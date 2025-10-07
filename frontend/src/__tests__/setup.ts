import { vi } from 'vitest';

// Test setup configuration for Caja frontend
// This file is loaded before each test to setup the testing environment

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

// Mock TanStack Query
vi.mock('@tanstack/react-query', () => ({
  useQuery: vi.fn(() => ({
    data: null,
    isLoading: false,
    error: null,
  })),
  useMutation: vi.fn(() => ({
    mutate: vi.fn(),
    isLoading: false,
    error: null,
  })),
  useQueryClient: vi.fn(() => ({
    invalidateQueries: vi.fn(),
    setQueryData: vi.fn(),
  })),
  QueryClient: vi.fn(() => ({
    invalidateQueries: vi.fn(),
    setQueryData: vi.fn(),
  })),
  QueryClientProvider: ({ children }: { children: any }) => children,
}));

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
  };
});
