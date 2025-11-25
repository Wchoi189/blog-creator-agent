import { z } from 'zod'

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  fullName: z.string().min(2, 'Name must be at least 2 characters').optional(),
})

export const documentUploadSchema = z.object({
  file: z.custom<File>((file) => file instanceof File, 'File is required'),
  title: z.string().optional(),
})

export const blogGenerateSchema = z.object({
  documentIds: z.array(z.string()).min(1, 'At least one document is required'),
  title: z.string().min(1, 'Title is required'),
  description: z.string().optional(),
})

export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
export type DocumentUploadInput = z.infer<typeof documentUploadSchema>
export type BlogGenerateInput = z.infer<typeof blogGenerateSchema>
