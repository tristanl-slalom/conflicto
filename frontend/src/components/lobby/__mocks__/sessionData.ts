import type { ParticipantStatus } from '../../../api/generated';

export const mockSessionData = {
  id: 123,
  title: 'Test Session',
  description: 'A test session for unit testing',
  status: 'draft' as const,
  participant_count: 3,
  qr_code: 'TEST123',
  admin_code: 'ADMIN123',
  max_participants: 50,
  created_at: '2025-10-08T20:00:00Z',
  updated_at: '2025-10-08T20:00:00Z',
  started_at: null,
  completed_at: null,
};

export const mockParticipants: ParticipantStatus[] = [
  {
    participant_id: 'participant-1',
    nickname: 'Alice',
    status: 'online',
    joined_at: '2025-10-08T20:01:00Z',
    last_seen: '2025-10-08T20:05:00Z',
  },
  {
    participant_id: 'participant-2',
    nickname: 'Bob',
    status: 'idle',
    joined_at: '2025-10-08T20:02:00Z',
    last_seen: '2025-10-08T20:04:00Z',
  },
  {
    participant_id: 'participant-3',
    nickname: 'Charlie',
    status: 'online',
    joined_at: '2025-10-08T20:03:00Z',
    last_seen: '2025-10-08T20:05:30Z',
  },
];

export const mockParticipantsResponse = {
  status: 200,
  data: {
    participants: mockParticipants,
    total_count: mockParticipants.length,
  },
};

export const mockSessionResponse = {
  status: 200,
  data: mockSessionData,
};

export const mockJoinResponse = {
  status: 200,
  data: {
    participant_id: 'participant-new',
    session_state: {
      session_id: 123,
      session_title: 'Test Session',
      session_status: 'draft',
      current_activity: null,
      participant_count: 4,
    },
  },
};