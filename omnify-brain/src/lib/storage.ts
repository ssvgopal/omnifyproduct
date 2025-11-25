/**
 * Supabase Storage Utilities
 * Handles file uploads, downloads, and management
 */

import { supabaseAdmin, supabase } from '@/lib/db/supabase';

export const STORAGE_BUCKETS = {
  CREATIVES: 'creatives',
  AVATARS: 'avatars',
  LOGOS: 'logos',
  EXPORTS: 'exports',
} as const;

export type StorageBucket = typeof STORAGE_BUCKETS[keyof typeof STORAGE_BUCKETS];

/**
 * File upload options
 */
export interface UploadOptions {
  bucket: StorageBucket;
  path: string;
  file: File | Blob;
  contentType?: string;
  cacheControl?: string;
  upsert?: boolean;
}

/**
 * Upload a file to Supabase Storage
 * 
 * Note: Uses supabaseAdmin (service role) to bypass RLS.
 * For client-side uploads, use the regular supabase client.
 */
export async function uploadFile(options: UploadOptions) {
  const { bucket, path, file, contentType, cacheControl = '3600', upsert = false } = options;

  const { data, error } = await supabaseAdmin.storage
    .from(bucket)
    .upload(path, file, {
      contentType: contentType || file.type,
      cacheControl,
      upsert,
    });

  if (error) {
    // If bucket doesn't exist, provide helpful error
    if (error.message.includes('Bucket not found') || error.message.includes('does not exist')) {
      throw new Error(
        `Storage bucket '${bucket}' not found. Please create it in Supabase Dashboard → Storage first.`
      );
    }
    throw new Error(`Failed to upload file: ${error.message}`);
  }

  return data;
}

/**
 * Get public URL for a file
 */
export function getPublicUrl(bucket: StorageBucket, path: string) {
  const { data } = supabase.storage.from(bucket).getPublicUrl(path);
  return data.publicUrl;
}

/**
 * Get signed URL for a file (temporary access)
 */
export async function getSignedUrl(
  bucket: StorageBucket,
  path: string,
  expiresIn: number = 3600
) {
  const { data, error } = await supabaseAdmin.storage
    .from(bucket)
    .createSignedUrl(path, expiresIn);

  if (error) {
    throw new Error(`Failed to create signed URL: ${error.message}`);
  }

  return data.signedUrl;
}

/**
 * Delete a file from storage
 */
export async function deleteFile(bucket: StorageBucket, path: string) {
  const { error } = await supabaseAdmin.storage.from(bucket).remove([path]);

  if (error) {
    throw new Error(`Failed to delete file: ${error.message}`);
  }
}

/**
 * List files in a bucket (with optional prefix)
 */
export async function listFiles(bucket: StorageBucket, prefix?: string) {
  const { data, error } = await supabaseAdmin.storage
    .from(bucket)
    .list(prefix || '', {
      limit: 100,
      offset: 0,
      sortBy: { column: 'created_at', order: 'desc' },
    });

  if (error) {
    throw new Error(`Failed to list files: ${error.message}`);
  }

  return data;
}

/**
 * Get file metadata
 */
export async function getFileMetadata(bucket: StorageBucket, path: string) {
  const { data, error } = await supabaseAdmin.storage
    .from(bucket)
    .list(path.split('/').slice(0, -1).join('/') || '', {
      limit: 1000,
    });

  if (error) {
    throw new Error(`Failed to get file metadata: ${error.message}`);
  }

  const file = data.find((f) => f.name === path.split('/').pop());
  return file;
}

/**
 * Generate optimized image URL with transformations
 */
export function getOptimizedImageUrl(
  bucket: StorageBucket,
  path: string,
  options?: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'jpg' | 'png';
  }
) {
  const { width, height, quality = 80, format = 'webp' } = options || {};
  
  const url = getPublicUrl(bucket, path);
  
  // Supabase Storage supports image transformations via query params
  // Note: This requires Supabase Storage image transformation feature
  const params = new URLSearchParams();
  if (width) params.set('width', width.toString());
  if (height) params.set('height', height.toString());
  if (quality) params.set('quality', quality.toString());
  if (format) params.set('format', format);

  return params.toString() ? `${url}?${params.toString()}` : url;
}

/**
 * Validate file before upload
 */
export function validateFile(file: File, options?: {
  maxSize?: number; // in bytes
  allowedTypes?: string[];
}): { valid: boolean; error?: string } {
  const { maxSize = 10 * 1024 * 1024, allowedTypes } = options || {}; // 10MB default

  // Check file size
  if (file.size > maxSize) {
    return {
      valid: false,
      error: `File size exceeds maximum allowed size of ${Math.round(maxSize / 1024 / 1024)}MB`,
    };
  }

  // Check file type
  if (allowedTypes && !allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `File type ${file.type} is not allowed. Allowed types: ${allowedTypes.join(', ')}`,
    };
  }

  return { valid: true };
}

/**
 * Generate storage path for creative
 */
export function getCreativePath(organizationId: string, creativeId: string, filename: string): string {
  const extension = filename.split('.').pop();
  return `${organizationId}/creatives/${creativeId}.${extension}`;
}

/**
 * Generate storage path for avatar
 */
export function getAvatarPath(userId: string, extension: string = 'jpg'): string {
  return `avatars/${userId}.${extension}`;
}

/**
 * Generate storage path for logo
 */
export function getLogoPath(organizationId: string, extension: string = 'png'): string {
  return `logos/${organizationId}.${extension}`;
}

/**
 * Generate storage path for export
 */
export function getExportPath(organizationId: string, exportId: string, filename: string): string {
  return `${organizationId}/exports/${exportId}/${filename}`;
}

