import { createFileRoute } from '@tanstack/react-router';
import { QrCode, Users, BarChart3, Maximize } from 'lucide-react';

export const Route = createFileRoute('/viewer/')({
  component: ViewerDisplay,
});

function ViewerDisplay() {
  // Mock data for demonstration
  const sessionData = {
    name: 'Team Retrospective Poll',
    question: 'What went well in our last sprint?',
    qrCode: 'CAJA-ABC123',
    participantCount: 12,
    responses: [
      { option: 'Great collaboration', count: 8, percentage: 67 },
      { option: 'Smooth deployment', count: 3, percentage: 25 },
      { option: 'Good communication', count: 1, percentage: 8 },
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <div className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">C</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold">{sessionData.name}</h1>
                <p className="text-gray-400">Live Session Display</p>
              </div>
            </div>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-green-400">
                <Users className="w-5 h-5" />
                <span className="font-mono text-xl">
                  {sessionData.participantCount}
                </span>
                <span className="text-gray-400">participants</span>
              </div>
              <button className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
                <Maximize className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-200px)]">
          {/* QR Code Section */}
          <div className="lg:col-span-1 flex flex-col">
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-8 flex-1 flex flex-col items-center justify-center">
              <h2 className="text-2xl font-bold mb-6 text-center">
                Join the Session
              </h2>

              {/* QR Code Placeholder */}
              <div className="bg-white p-6 rounded-xl mb-6">
                <div className="w-48 h-48 bg-black rounded-lg flex items-center justify-center">
                  <QrCode className="w-32 h-32 text-white" />
                </div>
              </div>
              <div className="text-center">
                <p className="text-gray-300 mb-2">Scan QR code or visit:</p>
                <p className="text-2xl font-mono font-bold text-cyan-400 mb-4">
                  caja.app/join
                </p>
                <p className="text-gray-400">Session Code:</p>
                <p className="text-3xl font-mono font-bold text-green-400">
                  {sessionData.qrCode}
                </p>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2 flex flex-col">
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-8 flex-1">
              <div className="flex items-center gap-3 mb-8">
                <BarChart3 className="w-8 h-8 text-cyan-400" />
                <h2 className="text-3xl font-bold">Live Results</h2>
              </div>
              <div className="mb-8">
                <h3 className="text-2xl font-semibold mb-6 text-center bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  {sessionData.question}
                </h3>
              </div>
              <div className="space-y-6">
                {sessionData.responses.map((response, index) => (
                  <div key={index} className="bg-slate-700/50 rounded-lg p-6">
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-lg font-medium">
                        {response.option}
                      </span>
                      <div className="flex items-center gap-3">
                        <span className="text-2xl font-bold text-cyan-400">
                          {response.count}
                        </span>
                        <span className="text-lg text-gray-400">
                          ({response.percentage}%)
                        </span>
                      </div>
                    </div>
                    <div className="w-full bg-slate-600 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-1000 ease-out"
                        style={{ width: `${response.percentage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-8 text-center">
                <p className="text-gray-400 text-lg">
                  Results update in real-time as participants vote
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
