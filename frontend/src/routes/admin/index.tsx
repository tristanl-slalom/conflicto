import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { SessionCreateForm, SessionList, SessionStatusCard, SessionControls, ActivityManagement, ParticipantManagement } from '../../components/admin';
import type { SessionDetail, SessionResponse } from '../../api/generated';

export const Route = createFileRoute('/admin/')({
  component: AdminLayout,
});

function AdminLayout() {
  const [selectedSession, setSelectedSession] = useState<SessionDetail | undefined>();

  const handleSessionCreated = (session: SessionDetail) => {
    setSelectedSession(session);
  };

  const handleSessionSelected = (session: SessionResponse) => {
    // Convert SessionResponse to SessionDetail for display
    // Note: In a real app, you might fetch full details here
    const sessionDetail: SessionDetail = {
      ...session,
      activities: [], // Would need to get this from API
      participants: [], // Would need to get this from API
    };
    setSelectedSession(sessionDetail);
  };

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">C</span>
                </div>
                <h1 className="text-xl font-semibold text-white">Caja Admin</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-400">
                Session Management Interface
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Session Controls */}
          <div className="lg:col-span-2 space-y-6">
            {/* Session Creation Form */}
            <SessionCreateForm
              onSuccess={handleSessionCreated}
              onError={(error) => {
                console.error('Session creation failed:', error);
                // Could add toast notification here
              }}
            />

            {/* Session List */}
            <SessionList
              onSessionSelect={handleSessionSelected}
              showActions={true}
              maxItems={5}
            />

            {/* Activity Management */}
            {selectedSession && (
              <ActivityManagement
                session={selectedSession}
                onActivityChange={() => {
                  console.log('Activity changed - refreshing session data...');
                  // Could refresh session data here
                }}
              />
            )}
          </div>

          {/* Session Status Sidebar */}
          <div className="space-y-6">
            {/* Session Controls */}
            <SessionControls
              session={selectedSession}
              onStatusChange={(newStatus) => {
                console.log('Session status changed to:', newStatus);
                // Could refresh session data here
              }}
            />

            {/* Current Session Status */}
            <SessionStatusCard
              session={selectedSession}
              onRefresh={() => {
                // Could refresh session data here
                console.log('Refreshing session data...');
              }}
            />

            {/* Participant Management */}
            {selectedSession && (
              <ParticipantManagement
                session={selectedSession}
              />
            )}

            {/* Quick Actions Card */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-medium text-white mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full bg-slate-600 hover:bg-slate-500 text-white py-2 px-4 rounded-md transition-colors">
                  View All Sessions
                </button>
                <button className="w-full bg-slate-600 hover:bg-slate-500 text-white py-2 px-4 rounded-md transition-colors">
                  Session Templates
                </button>
                <button className="w-full bg-slate-600 hover:bg-slate-500 text-white py-2 px-4 rounded-md transition-colors">
                  Export Data
                </button>
              </div>
            </div>

            {/* Help Card */}
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-medium text-white mb-4">Help</h2>
              <div className="space-y-2 text-sm text-gray-400">
                <p>• Create sessions with title and optional description</p>
                <p>• Sessions start in draft status</p>
                <p>• Share QR codes for participant access</p>
                <p>• Monitor real-time participation</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
