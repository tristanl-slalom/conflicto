import { z } from 'zod';

/**
 * Validation schema for session creation form
 */
export const sessionCreateSchema = z.object({
  title: z
    .string()
    .min(1, 'Session title is required')
    .max(255, 'Session title must be less than 255 characters')
    .trim(),
  description: z
    .string()
    .max(1000, 'Description must be less than 1000 characters')
    .trim()
    .optional()
    .or(z.literal(''))
    .transform((val: string | undefined) => val === '' ? undefined : val),
});

/**
 * Type for session creation form data
 */
export type SessionCreateFormData = z.infer<typeof sessionCreateSchema>;

/**
 * Validation for session title field only (for real-time validation)
 */
export const sessionTitleSchema = z
  .string()
  .min(1, 'Session title is required')
  .max(255, 'Session title must be less than 255 characters')
  .trim();

/**
 * Validation for session description field only (for real-time validation)
 */
export const sessionDescriptionSchema = z
  .string()
  .max(1000, 'Description must be less than 1000 characters')
  .trim()
  .optional();