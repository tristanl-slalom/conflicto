import { useState } from 'react';
import { sessionCreateSchema, type SessionCreateFormData } from '../../lib/validations/sessionValidation';
import { useSessionManagement } from '../../hooks/useSessionManagement';
import type { SessionCreateFormProps } from '../../types/admin';

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

  const validateForm = () => {
    try {
      sessionCreateSchema.parse(formData);
      setErrors({});
      return true;
    } catch (error: any) {
      const fieldErrors: FormErrors = {};
      if (error.errors) {
        error.errors.forEach((err: any) => {
          const field = err.path[0] as keyof FormErrors;
          fieldErrors[field] = err.message;
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

  const handleFieldChange = (field: keyof SessionCreateFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleFieldBlur = (field: keyof SessionCreateFormData) => {
    // Validate individual field
    try {
      if (field === 'title') {
        sessionCreateSchema.shape.title.parse(formData.title);
      } else if (field === 'description') {
        sessionCreateSchema.shape.description.parse(formData.description);
      }
      setErrors(prev => ({ ...prev, [field]: undefined }));
    } catch (error: any) {
      if (error.errors?.[0]) {
        setErrors(prev => ({ ...prev, [field]: error.errors[0].message }));
      }
    }
  };

  const canSubmit = formData.title.trim().length > 0 && Object.keys(errors).length === 0;

  return (
    <div className={`bg-slate-800 rounded-lg p-6 border border-slate-700 ${className}`}>
      <h2 className="text-lg font-medium text-white mb-4">
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
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Session Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => handleFieldChange('title', e.target.value)}
            onBlur={() => handleFieldBlur('title')}
            placeholder="Enter session title..."
            disabled={isCreating}
            className={`w-full px-3 py-2 bg-slate-700 border rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              errors.title
                ? 'border-red-600'
                : 'border-slate-600'
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
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Description
          </label>
          <textarea
            rows={3}
            value={formData.description}
            onChange={(e) => handleFieldChange('description', e.target.value)}
            onBlur={() => handleFieldBlur('description')}
            placeholder="Enter session description (optional)..."
            disabled={isCreating}
            className={`w-full px-3 py-2 bg-slate-700 border rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
              errors.description
                ? 'border-red-600'
                : 'border-slate-600'
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
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-slate-600 text-gray-400 cursor-not-allowed'
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