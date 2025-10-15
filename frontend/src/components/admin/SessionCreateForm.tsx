import { useState } from 'react';
import { sessionCreateSchema } from '../../lib/validations/sessionValidation';
import type { SessionCreateFormData } from '../../lib/validations/sessionValidation';
import { useSessionManagement } from '../../hooks/useSessionManagement';
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
  const { createSession, isCreating, creationError, creationSuccess } = useSessionManagement();

  const [formData, setFormData] = useState<SessionCreateFormData>({
    title: '',
    description: '',
  });

  const [errors, setErrors] = useState<FormErrors>({});

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

    try {
      const session = await createSession(formData);

      // Reset form
      setFormData({ title: '', description: '' });
      setErrors({});

      // Call success callback
      onSuccess?.(session);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create session';
      onError?.(errorMessage);
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
    <div className={`bg-card rounded-lg p-6 border border-border ${className}`}>
      <h2 className="text-lg font-medium text-foreground mb-4">
        Create New Session
      </h2>

      {/* Success Message */}
      {creationSuccess && (
        <div className="mb-4 p-3 bg-green-900/50 border border-green-700 rounded-md">
          <p className="text-green-300 text-sm">{creationSuccess}</p>
        </div>
      )}

      {/* Error Message */}
      {creationError && (
        <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded-md">
          <p className="text-red-300 text-sm">{creationError}</p>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-4"
      >
        {/* Session Title Field */}
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-2">
            Session Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => handleFieldChange('title', e.target.value)}
            onBlur={() => handleFieldBlur('title')}
            placeholder="Enter session title..."
            disabled={isCreating}
            className={`w-full px-3 py-2 bg-input border rounded-md text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-colors ${
              errors.title
                ? 'border-destructive'
                : 'border-border'
            } ${isCreating ? 'opacity-50 cursor-not-allowed' : ''}`}
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-400">
              {errors.title}
            </p>
          )}
        </div>

        {/* Session Description Field */}
        <div>
          <label className="block text-sm font-medium text-muted-foreground mb-2">
            Description
          </label>
          <textarea
            rows={3}
            value={formData.description}
            onChange={(e) => handleFieldChange('description', e.target.value)}
            onBlur={() => handleFieldBlur('description')}
            placeholder="Enter session description (optional)..."
            disabled={isCreating}
            className={`w-full px-3 py-2 bg-input border rounded-md text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-colors ${
              errors.description
                ? 'border-destructive'
                : 'border-border'
            } ${isCreating ? 'opacity-50 cursor-not-allowed' : ''}`}
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
            disabled={!canSubmit || isCreating}
            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
              canSubmit && !isCreating
                ? 'bg-primary hover:bg-primary/90 text-primary-foreground'
                : 'bg-muted text-muted-foreground cursor-not-allowed'
            }`}
          >
            {isCreating ? (
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
            disabled={isCreating}
            className={`px-4 py-2 rounded-md transition-colors ${
              isCreating
                ? 'bg-muted text-muted-foreground cursor-not-allowed'
                : 'bg-secondary hover:bg-secondary/90 text-secondary-foreground'
            }`}
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  );
};
