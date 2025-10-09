/**
 * Type definitions for pre-lobby and session status components
 */

export interface LobbySessionData {
  sessionId: number;
  title: string;
  description?: string;
  status: 'draft' | 'active' | 'completed';
  participantCount: number;
}

export interface LobbyParticipant {
  participantId: string;
  nickname: string;
  status: 'online' | 'idle' | 'disconnected';
  joinedAt: string;
  lastSeen: string;
}

export interface PreLobbyState {
  sessionData: LobbySessionData;
  participants: LobbyParticipant[];
  isLoading: boolean;
  error?: string;
}

export interface SessionStatusTransition {
  fromStatus: string | null;
  toStatus: string;
  timestamp: Date;
}

// Re-export types that might be used by lobby components
export type { ParticipantStatus } from '../api/generated';