/**
 * Polling Admin Component
 *
 * Administrative interface for configuring polling activities.
 */

import { useState, useEffect } from 'react';
import { AdminActivityProps } from '@/lib/activity-framework';
import { PollingConfig } from './types';

export default function PollingAdmin({
  activity,
  configuration,
  onConfigUpdate,
  onSave,
  validation,
  isLoading = false
}: AdminActivityProps) {
  const config = (configuration as unknown) as PollingConfig;

  const [question, setQuestion] = useState(config.question || '');
  const [options, setOptions] = useState<string[]>(
    config.options?.length ? config.options : ['', '']
  );
  const [allowMultipleChoice, setAllowMultipleChoice] = useState(
    config.allow_multiple_choice ?? false
  );
  const [showLiveResults, setShowLiveResults] = useState(
    config.show_live_results ?? true
  );
  const [anonymousVoting, setAnonymousVoting] = useState(
    config.anonymous_voting ?? true
  );

  // Update parent when configuration changes
  useEffect(() => {
    const newConfig: PollingConfig = {
      question,
      options: options.filter(opt => opt.trim() !== ''),
      allow_multiple_choice: allowMultipleChoice,
      show_live_results: showLiveResults,
      anonymous_voting: anonymousVoting,
    };
    onConfigUpdate(newConfig as unknown as Record<string, unknown>);
  }, [question, options, allowMultipleChoice, showLiveResults, anonymousVoting, onConfigUpdate]);

  const addOption = () => {
    setOptions([...options, '']);
  };

  const updateOption = (index: number, value: string) => {
    const newOptions = [...options];
    newOptions[index] = value;
    setOptions(newOptions);
  };

  const removeOption = (index: number) => {
    if (options.length > 2) {
      const newOptions = options.filter((_, i) => i !== index);
      setOptions(newOptions);
    }
  };

  const validOptions = options.filter(opt => opt.trim() !== '');
  const canSave = question.trim() !== '' && validOptions.length >= 2;

  return (
    <div className="polling-admin space-y-6">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Configure Polling Activity
        </h3>

        {/* Question Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Poll Question *
          </label>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter your polling question..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            maxLength={500}
          />
          <p className="text-xs text-gray-500 mt-1">
            {question.length}/500 characters
          </p>
        </div>

        {/* Options */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Answer Options *
          </label>
          <div className="space-y-2">
            {options.map((option, index) => (
              <div key={index} className="flex items-center gap-2">
                <span className="text-sm text-gray-500 w-6">
                  {index + 1}.
                </span>
                <input
                  type="text"
                  value={option}
                  onChange={(e) => updateOption(index, e.target.value)}
                  placeholder={`Option ${index + 1}`}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  maxLength={200}
                />
                {options.length > 2 && (
                  <button
                    type="button"
                    onClick={() => removeOption(index)}
                    className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-md"
                    title="Remove option"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                )}
              </div>
            ))}
          </div>

          {options.length < 10 && (
            <button
              type="button"
              onClick={addOption}
              className="mt-2 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md border border-blue-200"
            >
              + Add Option
            </button>
          )}

          <p className="text-xs text-gray-500 mt-1">
            At least 2 options required, maximum 10 options
          </p>
        </div>

        {/* Settings */}
        <div className="space-y-4 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Allow Multiple Choice
              </label>
              <p className="text-xs text-gray-500">
                Let participants select more than one option
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={allowMultipleChoice}
                onChange={(e) => setAllowMultipleChoice(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Show Live Results
              </label>
              <p className="text-xs text-gray-500">
                Display results in real-time to viewers
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={showLiveResults}
                onChange={(e) => setShowLiveResults(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-gray-700">
                Anonymous Voting
              </label>
              <p className="text-xs text-gray-500">
                Hide participant identities in responses
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={anonymousVoting}
                onChange={(e) => setAnonymousVoting(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>

        {/* Validation Errors */}
        {validation && !validation.valid && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700 font-medium mb-1">
              Configuration Errors:
            </p>
            <ul className="text-sm text-red-600 list-disc list-inside">
              {validation.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Save Button */}
        <div className="flex justify-between items-center pt-4 border-t">
          <div className="text-sm text-gray-500">
            Activity: {activity.title}
          </div>
          <button
            type="button"
            onClick={onSave}
            disabled={!canSave || isLoading}
            className={`px-4 py-2 rounded-md font-medium transition-colors ${
              canSave && !isLoading
                ? 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {isLoading ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>

      {/* Preview */}
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Preview</h4>
        <div className="bg-white rounded-md p-4 border">
          <h5 className="font-medium text-gray-900 mb-3">
            {question || 'Your poll question will appear here...'}
          </h5>
          <div className="space-y-2">
            {validOptions.map((option, index) => (
              <label key={index} className="flex items-center gap-2 cursor-pointer">
                <input
                  type={allowMultipleChoice ? 'checkbox' : 'radio'}
                  name="preview-poll"
                  disabled
                  className="text-blue-600"
                />
                <span className="text-gray-700">{option}</span>
              </label>
            ))}
            {validOptions.length === 0 && (
              <p className="text-gray-500 text-sm italic">
                Add poll options to see preview
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
