import { describe, it, expect, beforeEach } from 'vitest';

interface MockSession {
  id: string;
  name: string;
  type: 'poll' | 'quiz' | 'poker' | 'wordcloud';
  status: 'draft' | 'active' | 'completed';
  question: string;
  options: string[];
  participantCount: number;
}

class SessionManager {
  private sessions: MockSession[] = [];

  createSession(
    sessionData: Omit<MockSession, 'id' | 'participantCount'>
  ): MockSession {
    const newSession: MockSession = {
      ...sessionData,
      id: Math.random().toString(36).substr(2, 9),
      participantCount: 0,
    };
    this.sessions.push(newSession);
    return newSession;
  }

  getSession(id: string): MockSession | null {
    return this.sessions.find(session => session.id === id) || null;
  }

  updateSession(id: string, updates: Partial<MockSession>): MockSession | null {
    const sessionIndex = this.sessions.findIndex(session => session.id === id);
    if (sessionIndex === -1) return null;

    this.sessions[sessionIndex] = {
      ...this.sessions[sessionIndex],
      ...updates,
    };
    return this.sessions[sessionIndex];
  }

  addParticipant(sessionId: string): boolean {
    const session = this.getSession(sessionId);
    if (!session) return false;

    session.participantCount++;
    return true;
  }
}

describe('Session Management Hooks', () => {
  describe('SessionManager', () => {
    let sessionManager: SessionManager;

    beforeEach(() => {
      sessionManager = new SessionManager();
    });

    it('creates a session with proper data', () => {
      const testSession = sessionManager.createSession({
        name: 'Test Session',
        type: 'poll',
        status: 'draft',
        question: 'What is your favorite color?',
        options: ['Red', 'Blue', 'Green', 'Yellow'],
      });

      expect(testSession.id.length).toBeGreaterThan(0);
      expect(testSession.name).toBe('Test Session');
      expect(testSession.participantCount).toBe(0);
    });

    it('retrieves session by ID', () => {
      const testSession = sessionManager.createSession({
        name: 'Test Session',
        type: 'poll',
        status: 'draft',
        question: 'What is your favorite color?',
        options: ['Red', 'Blue', 'Green', 'Yellow'],
      });

      const retrievedSession = sessionManager.getSession(testSession.id);
      expect(retrievedSession?.id).toBe(testSession.id);
    });
  });
});
