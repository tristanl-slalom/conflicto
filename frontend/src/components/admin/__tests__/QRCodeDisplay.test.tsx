import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { QRCodeDisplay } from '../QRCodeDisplay';
import type { SessionDetail } from '../../../api/generated';

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined),
  },
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
  status: 'active' as const,
  qr_code: 'TEST123',
  admin_code: 'ADMIN456',
  max_participants: 50,
  started_at: '2023-01-01T01:00:00Z',
  completed_at: null,
  activities: [],
  participants: [],
  participant_count: 0,
  activity_count: 0,
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

describe('QRCodeDisplay', () => {
  it('renders QR code information when session has QR code', () => {
    renderWithQueryClient(<QRCodeDisplay session={mockSession} />);

    expect(screen.getByRole('heading', { name: 'QR Code' })).toBeInTheDocument();
    expect(screen.getByText('TEST123')).toBeInTheDocument();
    expect(screen.getByText('Join URL')).toBeInTheDocument();
  });

  it('shows no QR code message when session has no QR code', () => {
    renderWithQueryClient(<QRCodeDisplay session={undefined} />);

    expect(screen.getByText('No QR code available')).toBeInTheDocument();
  });

  it('copies QR code to clipboard when copy button is clicked', async () => {
    renderWithQueryClient(<QRCodeDisplay session={mockSession} />);

    const copyButtons = screen.getAllByTitle('Copy QR code');
    fireEvent.click(copyButtons[0]);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('TEST123');
  });

  it('copies join URL to clipboard when copy URL button is clicked', async () => {
    renderWithQueryClient(<QRCodeDisplay session={mockSession} />);

    const copyUrlButtons = screen.getAllByTitle('Copy join URL');
    fireEvent.click(copyUrlButtons[0]);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('http://localhost:3000/session/TEST123');
  });

  it('opens large QR modal when maximize button is clicked', () => {
    renderWithQueryClient(<QRCodeDisplay session={mockSession} />);

    const maximizeButton = screen.getByTitle('View large QR code');
    fireEvent.click(maximizeButton);

    expect(screen.getByText('Scan to Join Session')).toBeInTheDocument();
  });

  it('shows session status info', () => {
    renderWithQueryClient(<QRCodeDisplay session={mockSession} />);

    expect(screen.getByText('Status:')).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
  });

  it('shows draft session warning', () => {
    const draftSession = { ...mockSession, status: 'draft' as const };
    renderWithQueryClient(<QRCodeDisplay session={draftSession} />);

    expect(screen.getByText('Start session to enable joining')).toBeInTheDocument();
  });

  it('hides URL and copy actions when configured', () => {
    renderWithQueryClient(
      <QRCodeDisplay session={mockSession} showUrl={false} showCopyActions={false} />
    );

    expect(screen.queryByText('Join URL')).not.toBeInTheDocument();
    expect(screen.queryByTitle('Copy QR code')).not.toBeInTheDocument();
  });
});
