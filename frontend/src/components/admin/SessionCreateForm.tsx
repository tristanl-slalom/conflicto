import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { sessionCreateSchema } from '../../lib/validations/sessionValidation';
import type { SessionCreateFormData } from '../../lib/validations/sessionValidation';
import {
  useCreateSessionApiV1SessionsPost,
  getListSessionsApiV1SessionsGetQueryKey,
  type SessionCreate,
  type SessionDetail
} from '../../api/generated';
import type { SessionCreateFormProps } from '../../types/admin';

// Form error type with explicit string keys
interface FormErrors {
  title?: string;
  description?: string;
}

export const SessionCreateForm = ({
  onSuccess,
  onError,
  className = ''
}: SessionCreateFormProps) => {
  const queryClient = useQueryClient();
  const createSessionMutation = useCreateSessionApiV1SessionsPost();

  const [formData, setFormData] = useState<SessionCreateFormData>({
    title: '',
    description: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [success, setSuccess] = useState<string | undefined>();

  const validateForm = (): boolean => {
    try {
      sessionCreateSchema.parse(formData);
      setErrors({});
      return true;
    } catch (error: any) {
      const fieldErrors: FormErrors = {};
      if (error.errors) {
        error.errors.forEach((err: any) => {
          const path = err.path;
          if (Array.isArray(path) && path.length > 0) {
            const field = path[0];
            if (field === 'title') {
              fieldErrors.title = err.message;
            } else if (field === 'description') {
              fieldErrors.description = err.message;
            }
          }
        });
      }
      setErrors(fieldErrors);
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setError(undefined);
    setSuccess(undefined);

    try {
      const sessionCreateData: SessionCreate = {
        title: formData.title,
        description: formData.description || undefined,
      };

      const response = await createSessionMutation.mutateAsync({
        data: sessionCreateData
      });

      // Invalidate sessions cache to trigger refetch across all components
      await queryClient.invalidateQueries({ queryKey: getListSessionsApiV1SessionsGetQueryKey() });

      // Convert SessionResponse to SessionDetail (they're compatible types)
      const sessionDetail = response.data as SessionDetail;

      // Reset form
      setFormData({ title: '', description: '' });
      setErrors({});
      setSuccess('Session created successfully!');

      // Call success callback
      onSuccess?.(sessionDetail);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create session';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFieldChange = (field: 'title' | 'description', value: string) => {
    setFormData((prev: SessionCreateFormData) => {
      const updated = { ...prev };
      updated[field] = value;
      return updated;
    });

    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev: FormErrors) => {
        const updated = { ...prev };
        updated[field] = undefined;
        return updated;
      });
    }
  };

  const handleFieldBlur = (field: 'title' | 'description') => {
    // Validate individual field
    try {
      if (field === 'title') {
        sessionCreateSchema.shape.title.parse(formData.title);
      } else if (field === 'description') {
        sessionCreateSchema.shape.description.parse(formData.description);
      }
      setErrors((prev: FormErrors) => {
        const updated = { ...prev };
        updated[field] = undefined;
        return updated;
      });
    } catch (error: any) {
      setErrors((prev: FormErrors) => {
        const updated = { ...prev };
        updated[field] = error.message;
        return updated;
      });
    }
  };

  const canSubmit = formData.title.trim().length > 0 && !errors.title;

  return (
    <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
      <h2 className="text-lg font-medium text-white mb-4">
        Create New Session
      </h2>

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-3 bg-green-900/50 border border-green-700 rounded-md">
          <p className="text-green-300 text-sm">{success}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded-md">
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-4"
      >
        {/* Session Title Field */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Session Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => handleFieldChange('title', e.target.value)}
            onBlur={() => handleFieldBlur('title')}
            placeholder="Enter session title..."
            disabled={isSubmitting}
            className={`w-full px-3 py-2 bg-slate-700 border rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              errors.title
                ? 'border-red-600'
                : 'border-slate-600'
            } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-400">
              {errors.title}
            </p>
          )}
        </div>

        {/* Session Description Field */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Description
          </label>
          <textarea
            rows={3}
            value={formData.description}
            onChange={(e) => handleFieldChange('description', e.target.value)}
            onBlur={() => handleFieldBlur('description')}
            placeholder="Enter session description (optional)..."
            disabled={isSubmitting}
            className={`w-full px-3 py-2 bg-slate-700 border rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              errors.description
                ? 'border-red-600'
                : 'border-slate-600'
            } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-400">
              {errors.description}
            </p>
          )}
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!canSubmit || isSubmitting}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              canSubmit && !isSubmitting
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-slate-600 text-gray-400 cursor-not-allowed'
            }`}
          >
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Creating...
              </span>
            ) : (
              'Create Session'
            )}
          </button>

          <button
            type="button"
            onClick={() => {
              setFormData({ title: '', description: '' });
              setErrors({});
            }}
            disabled={isSubmitting}
            className={`px-4 py-2 rounded-md transition-colors ${
              isSubmitting
                ? 'bg-slate-600 text-gray-400 cursor-not-allowed'
                : 'bg-slate-600 hover:bg-slate-500 text-white'
            }`}
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  );
};
