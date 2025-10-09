import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { SessionCreateForm, SessionList, SessionStatusCard, SessionControls, ActivityManagement, ParticipantManagement, QRCodeDisplay } from '../../components/admin';
import type { SessionDetail, SessionResponse } from '../../api/generated';
import { getSessionApiV1SessionsSessionIdGet } from '../../api/generated';

export const Route = createFileRoute('/admin/')({
  component: AdminLayout,
});

function AdminLayout() {
  const [selectedSessionId, setSelectedSessionId] = useState<number | undefined>();

  // Fetch the full session details when a session is selected
  const { data: sessionData } = useQuery({
    queryKey: ['session', selectedSessionId],
    queryFn: () => selectedSessionId ? getSessionApiV1SessionsSessionIdGet(selectedSessionId) : null,
    enabled: !!selectedSessionId,
  });

  // Use sessionData directly instead of selectedSession state

  const handleSessionCreated = (session: SessionDetail) => {
    setSelectedSessionId(session.id);
  };

  const handleSessionSelected = (session: SessionResponse) => {
    setSelectedSessionId(session.id);
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {/* Session Management */}
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
            {sessionData?.data && (
              <ActivityManagement
                session={sessionData.data}
                onActivityChange={() => {
                  // Session data will auto-refresh via TanStack Query
                }}
              />
            )}
          </div>

          {/* Session Status Sidebar */}
          <div className="space-y-6">
            {/* Session Controls */}
            {sessionData?.data && (
              <SessionControls
                session={sessionData.data}
                onStatusChange={(newStatus) => {
                  console.log('Session status changed to:', newStatus);
                  // Could refresh session data here
                }}
              />
            )}

            {/* QR Code Display - Main Desktop Version */}
            {sessionData?.data && sessionData.data.qr_code && (
              <QRCodeDisplay
                session={sessionData.data}
                size="large"
                showUrl={true}
                className="hidden lg:block" // Show on desktop/large screens
              />
            )}

            {/* Current Session Status */}
            {sessionData?.data && (
              <SessionStatusCard
                session={sessionData.data}
                onRefresh={() => {
                  // Session data will auto-refresh via TanStack Query
                }}
              />
            )}

            {/* Participant Management */}
            {sessionData?.data && (
              <ParticipantManagement
                session={sessionData.data}
              />
            )}

            {/* QR Code Display - Mobile/Tablet Version */}
            {sessionData?.data && sessionData.data.qr_code && (
              <QRCodeDisplay
                session={sessionData.data}
                size="medium"
                showUrl={true}
                className="lg:hidden" // Only show on mobile/tablet
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
              <h2 className="text-lg font-medium text-white mb-4">Getting Started</h2>
              <div className="space-y-2 text-sm text-gray-400">
                <p>• Create sessions with activities</p>
                <p>• Start sessions to enable joining</p>
                <p>• Share QR codes for easy access</p>
                <p>• Monitor live participation</p>
                <p>• Manage activities in real-time</p>
              </div>
              {sessionData?.data && (
                <div className="mt-4 pt-4 border-t border-slate-600">
                  <p className="text-xs text-slate-500">
                    Selected: <span className="text-white">{sessionData.data.title}</span>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
