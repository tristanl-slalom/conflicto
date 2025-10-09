import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import SessionStatusIndicator from '../SessionStatusIndicator';

// Create a test wrapper with QueryClient
const createTestWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('SessionStatusIndicator', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders draft status correctly', () => {
    render(
      <SessionStatusIndicator 
        status="draft" 
        participantCount={3} 
      />,
      { wrapper: createTestWrapper() }
    );

    expect(screen.getByText('Waiting for session to start')).toBeDefined();
    expect(screen.getByText('3 participants waiting')).toBeDefined();
  });

  it('renders active status correctly', () => {
    render(
      <SessionStatusIndicator 
        status="active" 
        participantCount={5} 
      />,
      { wrapper: createTestWrapper() }
    );

    expect(screen.getByText('Session is active')).toBeDefined();
    expect(screen.getByText('5 participants active')).toBeDefined();
  });

  it('renders completed status correctly', () => {
    render(
      <SessionStatusIndicator 
        status="completed" 
        participantCount={0} 
      />,
      { wrapper: createTestWrapper() }
    );

    expect(screen.getByText('Session completed')).toBeDefined();
    expect(screen.getByText('Thank you for participating')).toBeDefined();
  });

  it('handles singular participant count correctly', () => {
    render(
      <SessionStatusIndicator 
        status="draft" 
        participantCount={1} 
      />,
      { wrapper: createTestWrapper() }
    );

    expect(screen.getByText('1 participant waiting')).toBeDefined();
  });

  it('handles zero participant count correctly', () => {
    render(
      <SessionStatusIndicator 
        status="draft" 
        participantCount={0} 
      />,
      { wrapper: createTestWrapper() }
    );

    expect(screen.getByText('0 participants waiting')).toBeDefined();
  });

  it('applies custom className', () => {
    const { container } = render(
      <SessionStatusIndicator 
        status="draft" 
        participantCount={1}
        className="custom-class"
      />,
      { wrapper: createTestWrapper() }
    );

    expect(container.firstChild).toBeDefined();
    expect((container.firstChild as Element).className).toContain('custom-class');
  });
});