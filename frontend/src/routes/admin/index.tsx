import { createFileRoute } from '@tanstack/react-router'
import QRCodeDisplay from '../../components/QRCodeDisplay'
import ParticipantList from '../../components/ParticipantList'

export const Route = createFileRoute('/admin/')({
  component: AdminLayout,
})

function AdminLayout() {
  return (
    <div className="min-h-screen bg-slate-900">
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
              <span className="text-sm text-gray-400">Session Management Interface</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Session Controls */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-medium text-white mb-4">Session Configuration</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Session Name
                  </label>
                  <input
                    type="text"
                    placeholder="Enter session name..."
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Session Type
                  </label>
                  <select className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option value="poll">Live Polling</option>
                    <option value="quiz">Quiz/Trivia</option>
                    <option value="poker">Planning Poker</option>
                    <option value="wordcloud">Word Cloud</option>
                  </select>
                </div>
                <div className="flex gap-3">
                  <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md transition-colors">
                    Create Session
                  </button>
                  <button className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-md transition-colors">
                    Save Draft
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-medium text-white mb-4">Content Management</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Question/Prompt
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Enter your question or prompt..."
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Response Options (for polls/quizzes)
                  </label>
                  <div className="space-y-2">
                    <input
                      type="text"
                      placeholder="Option 1"
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <input
                      type="text"
                      placeholder="Option 2"
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button className="text-blue-400 hover:text-blue-300 text-sm">
                      + Add Option
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Session Status */}
          <div className="space-y-6">
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-medium text-white mb-4">Session Status</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Status</span>
                  <span className="px-2 py-1 bg-green-900 text-green-300 rounded-full text-sm">
                    Active
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Participants</span>
                  <span className="text-white font-mono">3</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300">Session ID</span>
                  <span className="text-white font-mono text-sm">123</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-medium text-white mb-4">Participant QR Code</h2>
              <div className="flex justify-center">
                <QRCodeDisplay sessionId={123} size={180} />
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-medium text-white mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md transition-colors">
                  Start Session
                </button>
                <button className="w-full bg-slate-600 hover:bg-slate-500 text-white py-2 px-4 rounded-md transition-colors">
                  Preview on Viewer
                </button>
                <button className="w-full bg-slate-600 hover:bg-slate-500 text-white py-2 px-4 rounded-md transition-colors">
                  Export Results
                </button>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h2 className="text-lg font-medium text-white mb-4">Participants</h2>
              <ParticipantList sessionId={123} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}