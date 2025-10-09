import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SessionControls } from '../SessionControls';
import { SessionStatus, type SessionDetail } from '../../../api/generated';

// Mock the API calls
vi.mock('../../../api/generated', async () => {
  const actual = await vi.importActual('../../../api/generated');
  return {
    ...actual,
    updateSessionApiV1SessionsSessionIdPut: vi.fn().mockResolvedValue({
      data: { status: 'active' }
    }),
  };
});

const createQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const mockSession: SessionDetail = {
  id: 1,
  title: 'Test Session',
  description: 'Test Description',
  status: SessionStatus.draft,
  qr_code: 'TEST123',
  admin_code: 'ADMIN456',
  max_participants: 50,
  started_at: null,
  completed_at: null,
  activities: [],
  participants: [],
  participant_count: 0,
  activity_count: 2,
  created_at: '2023-01-01T00:00:00Z',
  updated_at: '2023-01-01T00:00:00Z',
};

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('SessionControls', () => {
  it('renders session status and info', () => {
    renderWithQueryClient(<SessionControls session={mockSession} />);

    expect(screen.getByText('Session Controls')).toBeInTheDocument();
    expect(screen.getByText('draft')).toBeInTheDocument();
    expect(screen.getByText('Activities:')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('shows start button for draft session with activities', () => {
    renderWithQueryClient(<SessionControls session={mockSession} />);

    expect(screen.getByText('Start Session')).toBeInTheDocument();
  });

  it('disables start button for draft session without activities', () => {
    const sessionWithoutActivities = { ...mockSession, activity_count: 0 };
    renderWithQueryClient(<SessionControls session={sessionWithoutActivities} />);

    const startButton = screen.getByText('Start Session');
    expect(startButton).toBeDisabled();
    expect(screen.getByText('Add activities before starting the session')).toBeInTheDocument();
  });

  it('shows pause button for active session', () => {
    const activeSession = { ...mockSession, status: SessionStatus.active };
    renderWithQueryClient(<SessionControls session={activeSession} />);

    expect(screen.getByText('Pause Session')).toBeInTheDocument();
  });

  it('shows resume button for paused session', () => {
    const pausedSession = { ...mockSession, status: SessionStatus.paused };
    renderWithQueryClient(<SessionControls session={pausedSession} />);

    expect(screen.getByText('Resume Session')).toBeInTheDocument();
  });

  it('shows end button for active session', () => {
    const activeSession = { ...mockSession, status: SessionStatus.active };
    renderWithQueryClient(<SessionControls session={activeSession} />);

    expect(screen.getByText('End Session')).toBeInTheDocument();
  });

  it('calls onStatusChange when provided', async () => {
    const mockOnStatusChange = vi.fn();
    renderWithQueryClient(
      <SessionControls session={mockSession} onStatusChange={mockOnStatusChange} />
    );

    const startButton = screen.getByText('Start Session');
    fireEvent.click(startButton);

    // Wait for the mutation to complete
    await waitFor(() => {
      expect(mockOnStatusChange).toHaveBeenCalledWith('active');
    });
  });

  it('shows no session message when session is undefined', () => {
    renderWithQueryClient(<SessionControls session={undefined} />);

    expect(screen.getByText('No session selected')).toBeInTheDocument();
  });

  it('shows confirmation dialog for ending session', () => {
    const activeSession = { ...mockSession, status: SessionStatus.active };
    renderWithQueryClient(<SessionControls session={activeSession} />);

    const endButton = screen.getByText('End Session');
    fireEvent.click(endButton);

    expect(screen.getByRole('heading', { name: 'End Session' })).toBeInTheDocument();
    expect(screen.getByText(/Are you sure you want to end this session/)).toBeInTheDocument();
  });
});
