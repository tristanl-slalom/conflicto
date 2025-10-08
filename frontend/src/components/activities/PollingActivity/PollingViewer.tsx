/**
 * Polling Viewer Component
 *
 * Large screen display interface for showing polling results.
 */

import { useState, useEffect } from 'react';
import { ViewerActivityProps } from '@/lib/activity-framework';
import { PollingConfig, PollingResults } from './types';

export default function PollingViewer({
  activity,
  configuration,
  results,
  status,
  onRefresh
}: ViewerActivityProps) {
  const config = (configuration as unknown) as PollingConfig;
  const pollingResults = (results as unknown) as PollingResults | null;

  const [_autoRefresh, setAutoRefresh] = useState(true);

  // Auto-refresh when live results are enabled
  useEffect(() => {
    if (!config.show_live_results || status !== 'active') return;

    const interval = setInterval(() => {
      onRefresh?.();
    }, 2000); // Refresh every 2 seconds

    return () => clearInterval(interval);
  }, [config.show_live_results, status, onRefresh]);

  if (!config.question) {
    return (
      <div className="polling-viewer flex items-center justify-center min-h-96 bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Poll Configuration
          </h3>
          <p className="text-gray-600">
            This polling activity needs to be configured first.
          </p>
        </div>
      </div>
    );
  }

  const totalVotes = pollingResults?.total_responses || 0;
  const optionResults = pollingResults?.vote_counts || {};
  const hasResults = totalVotes > 0;

  return (
    <div className="polling-viewer min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            {activity.title}
          </h1>
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            <div className={`w-2 h-2 rounded-full mr-2 ${
              status === 'active' ? 'bg-green-500' :
              status === 'completed' ? 'bg-blue-500' :
              'bg-gray-400'
            }`} />
            {status === 'active' ? 'Live Poll' :
             status === 'completed' ? 'Poll Closed' :
             'Poll Pending'}
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 text-center leading-relaxed">
            {config.question}
          </h2>
        </div>

        {/* Results or Instructions */}
        {hasResults && config.show_live_results ? (
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-900">
                Live Results
              </h3>
              <div className="text-sm text-gray-600">
                {totalVotes} {totalVotes === 1 ? 'vote' : 'votes'}
              </div>
            </div>

            <div className="space-y-4">
              {config.options.map((option, index) => {
                const count = optionResults[option] || 0;
                const percentage = totalVotes > 0 ? (count / totalVotes) * 100 : 0;

                return (
                  <div key={index} className="relative">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-lg font-medium text-gray-900">
                        {option}
                      </span>
                      <span className="text-lg font-bold text-gray-700">
                        {count}
                      </span>
                    </div>

                    <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>

                    <div className="text-right mt-1">
                      <span className="text-sm font-medium text-gray-600">
                        {percentage.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Additional Stats */}
            {pollingResults && (
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      {totalVotes}
                    </div>
                    <div className="text-sm text-gray-600">Total Votes</div>
                  </div>

                  <div>
                    <div className="text-2xl font-bold text-green-600">
                      {pollingResults?.most_popular?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Top Choices</div>
                  </div>

                  {config.allow_multiple_choice && (
                    <div>
                      <div className="text-2xl font-bold text-purple-600">
                        {(totalVotes / Math.max(Object.keys(optionResults).length, 1)).toFixed(1)}
                      </div>
                      <div className="text-sm text-gray-600">Avg per Option</div>
                    </div>
                  )}

                  <div>
                    <div className="text-2xl font-bold text-orange-600">
                      {Object.keys(optionResults).length}
                    </div>
                    <div className="text-sm text-gray-600">Options</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : status === 'active' ? (
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <div className="w-20 h-20 mx-auto mb-6 bg-blue-100 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
              </svg>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Waiting for Responses
            </h3>

            <p className="text-gray-600 mb-6">
              Participants can vote using their mobile devices.
              {config.show_live_results ? ' Results will appear here as votes come in.' : ' Results will be shown when the poll closes.'}
            </p>

            <div className="flex items-center justify-center space-x-2 text-blue-600">
              <div className="animate-pulse">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              </div>
              <div className="animate-pulse delay-75">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              </div>
              <div className="animate-pulse delay-150">
                <div className="w-2 h-2 bg-blue-600 rounded-full"></div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
            <div className="w-20 h-20 mx-auto mb-6 bg-gray-100 rounded-full flex items-center justify-center">
              <svg className="w-10 h-10 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Poll Not Active
            </h3>

            <p className="text-gray-600">
              This poll is not currently active. Check back when the facilitator starts the activity.
            </p>
          </div>
        )}

        {/* Settings Info */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <div className="flex items-center justify-center space-x-4">
            <span className={`inline-flex items-center ${config.allow_multiple_choice ? 'text-blue-600' : 'text-gray-400'}`}>
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Multiple Choice
            </span>

            <span className={`inline-flex items-center ${config.anonymous_voting ? 'text-green-600' : 'text-gray-400'}`}>
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
              </svg>
              Anonymous
            </span>

            <span className={`inline-flex items-center ${config.show_live_results ? 'text-purple-600' : 'text-gray-400'}`}>
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              Live Results
            </span>
          </div>
        </div>

        {/* Auto-refresh toggle for debugging */}
        {status === 'active' && config.show_live_results && (
          <div className="mt-4 text-center">
            <button
              onClick={() => setAutoRefresh(!_autoRefresh)}
              className="text-xs text-gray-500 hover:text-gray-700"
            >
              Auto-refresh: {_autoRefresh ? 'ON' : 'OFF'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
