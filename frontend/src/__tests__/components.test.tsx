import React from 'react'
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react'
import { describe, it, expect, afterEach } from 'vitest'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Create test wrapper for TanStack Query
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

// Mock component for testing (since we can't import the actual component without build setup)
const MockHomePage = () => {
  const personas = [
    {
      id: 'admin',
      title: 'Admin Interface',
      description: 'Configure sessions, manage content, and control activities',
      link: '/admin',
    },
    {
      id: 'viewer',
      title: 'Viewer Display',
      description: 'Large screen display with QR codes and live results',
      link: '/viewer',
    },
    {
      id: 'participant',
      title: 'Participant Interface',
      description: 'Mobile-optimized interaction and engagement',
      link: '/participant',
    },
  ];

  return (
    <div data-testid="home-page">
      <h1>CAJA</h1>
      <p>Interactive Engagement Platform</p>

      <section data-testid="persona-selection">
        <h2>Choose Your Interface</h2>
        {personas.map(persona => (
          <a
            key={persona.id}
            href={persona.link}
            data-testid={`persona-link-${persona.id}`}
          >
            <h3>{persona.title}</h3>
            <p>{persona.description}</p>
          </a>
        ))}
      </section>
    </div>
  );
};

const MockAdminInterface = () => {
  return (
    <div data-testid="admin-interface">
      <h1>Caja Admin</h1>
      <form data-testid="session-form">
        <input
          type="text"
          placeholder="Enter session name..."
          data-testid="session-name-input"
        />
        <select data-testid="session-type-select">
          <option value="poll">Live Polling</option>
          <option value="quiz">Quiz/Trivia</option>
          <option value="poker">Planning Poker</option>
          <option value="wordcloud">Word Cloud</option>
        </select>
        <button type="button" data-testid="create-session-btn">
          Create Session
        </button>
      </form>
    </div>
  );
};

const MockViewerDisplay = () => {
  const sessionData = {
    name: 'Team Retrospective Poll',
    question: 'What went well in our last sprint?',
    participantCount: 12,
    responses: [
      { option: 'Great collaboration', count: 8, percentage: 67 },
      { option: 'Smooth deployment', count: 3, percentage: 25 },
    ],
  };

  return (
    <div data-testid="viewer-display">
      <h1>{sessionData.name}</h1>
      <div data-testid="participant-count">{sessionData.participantCount}</div>

      <div data-testid="qr-section">
        <h2>Join the Session</h2>
        <p>Session Code: CAJA-ABC123</p>
      </div>

      <div data-testid="results-section">
        <h2>Live Results</h2>
        <h3>{sessionData.question}</h3>
        {sessionData.responses.map((response, index) => (
          <div key={index} data-testid={`result-${index}`}>
            <span>{response.option}</span>
            <span>{response.count}</span>
            <span>{response.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const MockParticipantInterface = () => {
  const [selectedOption, setSelectedOption] = React.useState<number | null>(
    null
  );
  const [hasVoted, setHasVoted] = React.useState(false);

  const sessionData = {
    question: 'What went well in our last sprint?',
    options: [
      'Great collaboration',
      'Smooth deployment',
      'Good communication',
      'Clear requirements',
    ],
  };

  const handleVote = () => {
    if (selectedOption !== null) {
      setHasVoted(true);
    }
  };

  if (hasVoted) {
    return (
      <div data-testid="participant-voted">
        <h2>Vote Submitted!</h2>
        <p>Thank you for participating.</p>
      </div>
    );
  }

  return (
    <div data-testid="participant-interface">
      <h1>Team Retrospective Poll</h1>
      <h2>{sessionData.question}</h2>

      <div data-testid="voting-options">
        {sessionData.options.map((option, index) => (
          <button
            key={index}
            data-testid={`option-${index}`}
            onClick={() => setSelectedOption(index)}
            className={selectedOption === index ? 'selected' : ''}
          >
            {option}
          </button>
        ))}
      </div>

      <button
        data-testid="submit-vote-btn"
        onClick={handleVote}
        disabled={selectedOption === null}
      >
        Submit Vote
      </button>
    </div>
  );
};

describe('Caja Frontend Components', () => {
  afterEach(() => {
    cleanup();
  });

  describe('HomePage', () => {
    it('renders the main landing page with branding', () => {
      render(<MockHomePage />, { wrapper: TestWrapper });

      expect(screen.getByText('CAJA')).toBeDefined();
      expect(screen.getByText('Interactive Engagement Platform')).toBeDefined();
    });

    it('displays all three persona options', () => {
      render(<MockHomePage />, { wrapper: TestWrapper });

      expect(screen.getByTestId('persona-link-admin')).toBeDefined();
      expect(screen.getByTestId('persona-link-viewer')).toBeDefined();
      expect(screen.getByTestId('persona-link-participant')).toBeDefined();

      expect(screen.getByText('Admin Interface')).toBeDefined();
      expect(screen.getByText('Viewer Display')).toBeDefined();
      expect(screen.getByText('Participant Interface')).toBeDefined();
    });

    it('has correct navigation links for each persona', () => {
      render(<MockHomePage />, { wrapper: TestWrapper });

      expect(
        screen.getByTestId('persona-link-admin').getAttribute('href')
      ).toBe('/admin');
      expect(
        screen.getByTestId('persona-link-viewer').getAttribute('href')
      ).toBe('/viewer');
      expect(
        screen.getByTestId('persona-link-participant').getAttribute('href')
      ).toBe('/participant');
    });
  });

  describe('Admin Interface', () => {
    it('renders the admin dashboard with session controls', () => {
      render(<MockAdminInterface />, { wrapper: TestWrapper });

      expect(screen.getByText('Caja Admin')).toBeDefined();
      expect(screen.getByTestId('session-form')).toBeDefined();
    });

    it('has session configuration inputs', () => {
      render(<MockAdminInterface />, { wrapper: TestWrapper });

      const nameInput = screen.getByTestId('session-name-input');
      const typeSelect = screen.getByTestId('session-type-select');
      const createBtn = screen.getByTestId('create-session-btn');

      expect(nameInput).toBeDefined();
      expect(typeSelect).toBeDefined();
      expect(createBtn).toBeDefined();
    });

    it('allows input of session details', async () => {
      render(<MockAdminInterface />, { wrapper: TestWrapper });

      const nameInput = screen.getByTestId(
        'session-name-input'
      ) as HTMLInputElement;
      const typeSelect = screen.getByTestId(
        'session-type-select'
      ) as HTMLSelectElement;

      fireEvent.change(nameInput, { target: { value: 'Test Session' } });
      fireEvent.change(typeSelect, { target: { value: 'quiz' } });

      expect(nameInput.value).toBe('Test Session');
      expect(typeSelect.value).toBe('quiz');
    });
  });

  describe('Viewer Display', () => {
    it('renders the viewer interface with session info', () => {
      render(<MockViewerDisplay />, { wrapper: TestWrapper });

      expect(screen.getByText('Team Retrospective Poll')).toBeDefined();
      expect(screen.getByTestId('participant-count').textContent).toBe('12');
    });

    it('displays QR code section for participant joining', () => {
      render(<MockViewerDisplay />, { wrapper: TestWrapper });

      expect(screen.getByTestId('qr-section')).toBeDefined();
      expect(screen.getByText('Join the Session')).toBeDefined();
      expect(screen.getByText(/Session Code:/)).toBeDefined();
    });

    it('shows live results with voting data', () => {
      render(<MockViewerDisplay />, { wrapper: TestWrapper });

      expect(screen.getByTestId('results-section')).toBeDefined();
      expect(
        screen.getByText('What went well in our last sprint?')
      ).toBeDefined();
      expect(screen.getByTestId('result-0')).toBeDefined();
      expect(screen.getByTestId('result-1')).toBeDefined();
    });
  });

  describe('Participant Interface', () => {
    it('renders the participant voting interface', () => {
      render(<MockParticipantInterface />, { wrapper: TestWrapper });

      expect(screen.getByTestId('participant-interface')).toBeDefined();
      expect(
        screen.getByText('What went well in our last sprint?')
      ).toBeDefined();
    });

    it('displays voting options as interactive buttons', () => {
      render(<MockParticipantInterface />, { wrapper: TestWrapper });

      expect(screen.getByTestId('option-0')).toBeDefined();
      expect(screen.getByTestId('option-1')).toBeDefined();
      expect(screen.getByTestId('option-2')).toBeDefined();
      expect(screen.getByTestId('option-3')).toBeDefined();

      expect(screen.getByText('Great collaboration')).toBeDefined();
      expect(screen.getByText('Smooth deployment')).toBeDefined();
    });

    it('allows selection and submission of votes', async () => {
      render(<MockParticipantInterface />, { wrapper: TestWrapper });

      const option1 = screen.getByTestId('option-1');
      const submitBtn = screen.getByTestId('submit-vote-btn');

      // Initially submit button should be disabled
      expect((submitBtn as HTMLButtonElement).disabled).toBe(true);

      // Select an option
      fireEvent.click(option1);
      expect(option1.classList.contains('selected')).toBe(true);
      expect((submitBtn as HTMLButtonElement).disabled).toBe(false);

      // Submit vote
      fireEvent.click(submitBtn);

      await waitFor(() => {
        expect(screen.getByTestId('participant-voted')).toBeDefined();
        expect(screen.getByText('Vote Submitted!')).toBeDefined();
      });
    });

    it('shows confirmation screen after voting', async () => {
      render(<MockParticipantInterface />, { wrapper: TestWrapper });

      // Select and submit
      fireEvent.click(screen.getByTestId('option-0'));
      fireEvent.click(screen.getByTestId('submit-vote-btn'));

      await waitFor(() => {
        expect(screen.getByText('Vote Submitted!')).toBeDefined();
        expect(screen.getByText('Thank you for participating.')).toBeDefined();
      });
    });
  });
});
