import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

// Types for Caja platform
export interface Session {
  id: string
  name: string
  type: 'poll' | 'quiz' | 'poker' | 'wordcloud'
  status: 'draft' | 'active' | 'completed'
  question: string
  options: string[]
  participantCount: number
  createdAt: string
  updatedAt: string
}

export interface SessionResponse {
  optionIndex: number
  count: number
  percentage: number
}

export interface ParticipantVote {
  sessionId: string
  optionIndex: number
  participantId: string
}

// Mock API functions (replace with actual API calls)
const mockApi = {
  getSessions: async (): Promise<Session[]> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
    return [
      {
        id: '1',
        name: 'Team Retrospective Poll',
        type: 'poll',
        status: 'active',
        question: 'What went well in our last sprint?',
        options: ['Great collaboration', 'Smooth deployment', 'Good communication', 'Clear requirements'],
        participantCount: 12,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
    ]
  },

  getSession: async (id: string): Promise<Session | null> => {
    const sessions = await mockApi.getSessions()
    return sessions.find(s => s.id === id) || null
  },

  createSession: async (session: Omit<Session, 'id' | 'createdAt' | 'updatedAt'>): Promise<Session> => {
    await new Promise(resolve => setTimeout(resolve, 500))
    return {
      ...session,
      id: Math.random().toString(36).substr(2, 9),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
  },

  updateSession: async (id: string, updates: Partial<Session>): Promise<Session> => {
    await new Promise(resolve => setTimeout(resolve, 300))
    const session = await mockApi.getSession(id)
    if (!session) throw new Error('Session not found')
    return { ...session, ...updates, updatedAt: new Date().toISOString() }
  },

  getSessionResponses: async (sessionId: string): Promise<SessionResponse[]> => {
    await new Promise(resolve => setTimeout(resolve, 200))
    // Mock response data
    return [
      { optionIndex: 0, count: 8, percentage: 67 },
      { optionIndex: 1, count: 3, percentage: 25 },
      { optionIndex: 2, count: 1, percentage: 8 },
      { optionIndex: 3, count: 0, percentage: 0 },
    ]
  },

  submitVote: async (vote: ParticipantVote): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 300))
    // Mock vote submission
    console.log('Vote submitted:', vote)
  }
}

// Session management hook
export function useSession(sessionId?: string) {
  return useQuery({
    queryKey: ['session', sessionId],
    queryFn: () => sessionId ? mockApi.getSession(sessionId) : Promise.resolve(null),
    enabled: !!sessionId,
    staleTime: 30000, // 30 seconds
  })
}

// Sessions list hook
export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: mockApi.getSessions,
    staleTime: 60000, // 1 minute
  })
}

// Session responses hook with real-time polling
export function useSessionResponses(sessionId: string, enabled = false) {
  return useQuery({
    queryKey: ['session-responses', sessionId],
    queryFn: () => mockApi.getSessionResponses(sessionId),
    enabled: enabled && !!sessionId,
    refetchInterval: 2000, // Poll every 2 seconds for real-time updates
    staleTime: 1000, // Consider data stale after 1 second
  })
}

// Create session mutation
export function useCreateSession() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: mockApi.createSession,
    onSuccess: () => {
      // Invalidate sessions query to refresh the list
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
  })
}

// Update session mutation
export function useUpdateSession() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, updates }: { id: string, updates: Partial<Session> }) => 
      mockApi.updateSession(id, updates),
    onSuccess: (updatedSession) => {
      // Update the session in the cache
      queryClient.setQueryData(['session', updatedSession.id], updatedSession)
      // Invalidate sessions list to refresh
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
  })
}

// Submit vote mutation
export function useSubmitVote() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: mockApi.submitVote,
    onSuccess: (_, variables) => {
      // Invalidate session responses to get updated results
      queryClient.invalidateQueries({ 
        queryKey: ['session-responses', variables.sessionId] 
      })
    },
  })
}

// Local storage hook for participant data
export function useParticipantSession() {
  const [participantId] = useState(() => {
    const stored = localStorage.getItem('caja-participant-id')
    if (stored) return stored
    
    const newId = Math.random().toString(36).substr(2, 9)
    localStorage.setItem('caja-participant-id', newId)
    return newId
  })

  const [currentSessionId, setCurrentSessionId] = useState<string | null>(() => {
    return localStorage.getItem('caja-current-session') || null
  })

  const joinSession = (sessionId: string) => {
    setCurrentSessionId(sessionId)
    localStorage.setItem('caja-current-session', sessionId)
  }

  const leaveSession = () => {
    setCurrentSessionId(null)
    localStorage.removeItem('caja-current-session')
  }

  return {
    participantId,
    currentSessionId,
    joinSession,
    leaveSession,
  }
}

// Polling hook for real-time updates
export function usePolling(callback: () => void, interval = 3000, enabled = true) {
  useEffect(() => {
    if (!enabled) return

    const id = setInterval(callback, interval)
    return () => clearInterval(id)
  }, [callback, interval, enabled])
}