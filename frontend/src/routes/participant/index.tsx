import { createFileRoute } from '@tanstack/react-router';
import { Smartphone, Send, Users, CheckCircle } from 'lucide-react';
import { useState } from 'react';

export const Route = createFileRoute('/participant/')({
  component: ParticipantInterface,
});

function ParticipantInterface() {
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [hasVoted, setHasVoted] = useState(false);

  // Mock session data
  const sessionData = {
    name: 'Team Retrospective Poll',
    question: 'What went well in our last sprint?',
    options: [
      'Great collaboration',
      'Smooth deployment',
      'Good communication',
      'Clear requirements',
    ],
    participantCount: 12,
  };

  const handleVote = () => {
    if (selectedOption !== null) {
      setHasVoted(true);
      // Here would be the API call to submit the vote
    }
  };

  const handleJoinSession = () => {
    // Mock joining session
    console.log('Joining session...');
  };

  if (!hasVoted && sessionData.question) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
        {/* Header */}
        <div className="bg-slate-800/80 backdrop-blur-sm border-b border-slate-700 sticky top-0 z-10">
          <div className="px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                  <Smartphone className="w-4 h-4" />
                </div>
                <div>
                  <h1 className="font-semibold">{sessionData.name}</h1>
                  <p className="text-xs text-gray-400">Participant View</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-purple-400">
                <Users className="w-4 h-4" />
                <span className="text-sm font-mono">
                  {sessionData.participantCount}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="px-4 py-6 max-w-md mx-auto">
          {/* Question */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4 text-center leading-relaxed">
              {sessionData.question}
            </h2>
            <div className="flex justify-center">
              <div className="w-12 h-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
            </div>
          </div>

          {/* Options */}
          <div className="space-y-3 mb-8">
            {sessionData.options.map((option, index) => (
              <button
                key={index}
                onClick={() => setSelectedOption(index)}
                className={`w-full p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                  selectedOption === index
                    ? 'border-purple-500 bg-purple-500/20 shadow-lg shadow-purple-500/20'
                    : 'border-slate-700 bg-slate-800/50 hover:border-slate-600 hover:bg-slate-700/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{option}</span>
                  {selectedOption === index && (
                    <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-4 h-4" />
                    </div>
                  )}
                </div>
              </button>
            ))}
          </div>

          {/* Submit Button */}
          <button
            onClick={handleVote}
            disabled={selectedOption === null}
            className={`w-full py-4 rounded-xl font-semibold transition-all duration-200 flex items-center justify-center gap-2 ${
              selectedOption !== null
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg shadow-purple-500/30'
                : 'bg-slate-700 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Send className="w-5 h-5" />
            Submit Vote
          </button>

          <p className="text-center text-gray-400 text-sm mt-4">
            Select an option above to submit your response
          </p>
        </div>
      </div>
    );
  }

  // After voting state
  if (hasVoted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
        <div className="px-4 max-w-md mx-auto text-center">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-8">
            <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold mb-4">Vote Submitted!</h2>
            <p className="text-gray-300 mb-6">
              Thank you for participating. Watch the viewer display for live
              results.
            </p>
            <div className="space-y-3">
              <button className="w-full bg-purple-600 hover:bg-purple-700 text-white py-3 px-4 rounded-lg transition-colors">
                View Results
              </button>
              <button className="w-full bg-slate-600 hover:bg-slate-500 text-white py-3 px-4 rounded-lg transition-colors">
                Join Another Session
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Join session state (default)
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white flex items-center justify-center">
      <div className="px-4 max-w-md mx-auto text-center">
        <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-8">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <Smartphone className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold mb-4">Join Session</h2>
          <p className="text-gray-300 mb-6">
            Enter your session code to participate in live polling and
            activities.
          </p>

          <div className="space-y-4">
            <input
              type="text"
              placeholder="Enter session code..."
              className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-center text-lg font-mono"
            />
            <button
              onClick={handleJoinSession}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-3 px-4 rounded-lg transition-all duration-200 shadow-lg shadow-purple-500/30"
            >
              Join Session
            </button>
          </div>
          <p className="text-gray-400 text-sm mt-4">
            Or scan the QR code displayed on the viewer screen
          </p>
        </div>
      </div>
    </div>
  );
}
