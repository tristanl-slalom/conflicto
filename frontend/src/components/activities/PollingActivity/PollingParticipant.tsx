/**
 * Polling Participant Component
 *
 * Mobile-friendly interface for participants to vote in polls.
 */

import { useState, useEffect } from 'react';
import { ParticipantActivityProps } from '@/lib/activity-framework';
import { PollingConfig, PollingResponse } from './types';

export default function PollingParticipant({
  activity,
  configuration,
  onSubmitResponse,
  canSubmit,
  hasSubmitted,
  isSubmitting = false,
  lastResponse
}: ParticipantActivityProps) {
  const config = (configuration as unknown) as PollingConfig;
  const previousResponse = lastResponse ? (lastResponse.response_data as unknown as PollingResponse) : null;

  const [selectedOptions, setSelectedOptions] = useState<string[]>(
    previousResponse?.selected_options || []
  );
  const [hasChanges, setHasChanges] = useState(false);

  // Track changes from initial state
  useEffect(() => {
    const initial = previousResponse?.selected_options || [];
    const current = selectedOptions;
    const changed = initial.length !== current.length ||
                   !initial.every(opt => current.includes(opt));
    setHasChanges(changed);
  }, [selectedOptions, previousResponse]);

  if (!config.question) {
    return (
      <div className="polling-participant min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Poll Not Ready
          </h3>
          <p className="text-gray-600">
            This poll is being configured. Please wait.
          </p>
        </div>
      </div>
    );
  }

  const handleOptionChange = (option: string, checked: boolean) => {
    if (config.allow_multiple_choice) {
      // Multiple choice: add/remove from selection
      if (checked) {
        setSelectedOptions(prev => [...prev, option]);
      } else {
        setSelectedOptions(prev => prev.filter(opt => opt !== option));
      }
    } else {
      // Single choice: replace selection
      setSelectedOptions(checked ? [option] : []);
    }
  };

  const handleSubmit = () => {
    const response: PollingResponse = {
      selected_options: selectedOptions
    };
    onSubmitResponse(response);
  };

  const canSubmitVote = canSubmit && selectedOptions.length > 0 && !isSubmitting;
  const showSubmitButton = hasChanges;

  return (
    <div className="polling-participant min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-6">
        <div className="text-center">
          <h1 className="text-xl font-semibold text-gray-900 mb-1">
            {activity.title}
          </h1>
          <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            hasSubmitted ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
          }`}>
            {hasSubmitted ? 'Vote Submitted' : 'Vote Now'}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6">
        {/* Question */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-medium text-gray-900 leading-relaxed">
            {config.question}
          </h2>
        </div>

        {/* Options */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="space-y-4">
            {config.options.map((option, index) => (
              <label
                key={index}
                className={`flex items-start gap-3 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedOptions.includes(option)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <input
                  type={config.allow_multiple_choice ? 'checkbox' : 'radio'}
                  name="poll-option"
                  value={option}
                  checked={selectedOptions.includes(option)}
                  onChange={(e) => handleOptionChange(option, e.target.checked)}
                  disabled={!canSubmit}
                  className={`mt-1 ${config.allow_multiple_choice ? 'rounded' : 'rounded-full'} border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50`}
                />
                <span className="text-gray-900 font-medium flex-1">
                  {option}
                </span>
                {selectedOptions.includes(option) && (
                  <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </label>
            ))}
          </div>

          {/* Instructions */}
          <div className="mt-4 p-3 bg-gray-50 rounded-md">
            <p className="text-sm text-gray-600">
              {config.allow_multiple_choice
                ? 'Select one or more options'
                : 'Select one option'
              }
              {config.anonymous_voting && ' • Your vote is anonymous'}
            </p>
          </div>
        </div>

        {/* Submit Button */}
        {showSubmitButton && (
          <button
            onClick={handleSubmit}
            disabled={!canSubmitVote}
            className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all ${
              canSubmitVote
                ? 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-lg'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isSubmitting ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Submitting...
              </div>
            ) : hasSubmitted ? (
              hasChanges ? 'Update Vote' : 'Vote Submitted'
            ) : (
              `Submit ${config.allow_multiple_choice ? 'Votes' : 'Vote'}`
            )}
          </button>
        )}

        {/* Previous Response */}
        {hasSubmitted && !hasChanges && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium text-green-800">
                Vote submitted successfully!
              </span>
            </div>
            {config.show_live_results && (
              <p className="text-xs text-green-700 mt-1">
                Check the main screen to see live results.
              </p>
            )}
          </div>
        )}

        {/* Selection Summary */}
        {selectedOptions.length > 0 && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="text-sm font-medium text-blue-900 mb-2">
              Your selection{selectedOptions.length > 1 ? 's' : ''}:
            </h4>
            <div className="space-y-1">
              {selectedOptions.map((option, index) => (
                <div key={index} className="flex items-center text-sm text-blue-800">
                  <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  {option}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3">
        <div className="text-center text-xs text-gray-500">
          {canSubmit ? 'Tap an option to vote' : 'Voting is currently closed'}
        </div>
      </div>
    </div>
  );
}
