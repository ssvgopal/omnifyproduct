'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Upload, X, Image, Video } from 'lucide-react';

interface CreativeUploadProps {
  creativeId: string;
  organizationId: string;
  onUploadComplete?: (url: string) => void;
  existingUrl?: string;
}

export function CreativeUpload({
  creativeId,
  organizationId,
  onUploadComplete,
  existingUrl,
}: CreativeUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(existingUrl || null);
  const [file, setFile] = useState<File | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    // Validate file type
    const allowedTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/webp',
      'video/mp4',
      'video/webm',
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Invalid file type. Please upload an image or video.');
      return;
    }

    // Validate file size (50MB max)
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError('File size exceeds 50MB limit.');
      return;
    }

    setFile(selectedFile);
    setError(null);

    // Create preview
    if (selectedFile.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(selectedFile);
    } else {
      setPreview(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('creativeId', creativeId);
      formData.append('organizationId', organizationId);

      const response = await fetch('/api/upload/creative', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Upload failed');
      }

      const data = await response.json();
      setPreview(data.url);
      onUploadComplete?.(data.url);
      setFile(null);
    } catch (err: any) {
      setError(err.message || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = () => {
    setFile(null);
    setPreview(existingUrl || null);
    setError(null);
  };

  const isImage = file?.type.startsWith('image/') || preview?.match(/\.(jpg|jpeg|png|gif|webp)/i);
  const isVideo = file?.type.startsWith('video/') || preview?.match(/\.(mp4|webm)/i);

  return (
    <div className="space-y-4">
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
        {preview ? (
          <div className="relative">
            {isImage && (
              <img
                src={preview}
                alt="Preview"
                className="max-w-full max-h-64 mx-auto rounded-lg"
              />
            )}
            {isVideo && (
              <video
                src={preview}
                controls
                className="max-w-full max-h-64 mx-auto rounded-lg"
              />
            )}
            <button
              onClick={handleRemove}
              className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload className="w-12 h-12 mx-auto text-gray-400" />
            <p className="text-sm text-gray-600">
              Drag and drop a file here, or click to select
            </p>
            <p className="text-xs text-gray-500">
              Images: JPEG, PNG, GIF, WebP (max 50MB)
              <br />
              Videos: MP4, WebM (max 50MB)
            </p>
            <input
              type="file"
              accept="image/*,video/*"
              onChange={handleFileSelect}
              className="hidden"
              id="creative-upload"
            />
            <label htmlFor="creative-upload">
              <Button type="button" variant="outline" asChild>
                <span>Select File</span>
              </Button>
            </label>
          </div>
        )}
      </div>

      {file && !preview && (
        <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
          {isImage ? (
            <Image className="w-5 h-5 text-gray-400" />
          ) : (
            <Video className="w-5 h-5 text-gray-400" />
          )}
          <span className="flex-1 text-sm text-gray-700">{file.name}</span>
          <span className="text-xs text-gray-500">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </span>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleRemove}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}

      {file && !uploading && (
        <Button onClick={handleUpload} className="w-full">
          Upload Creative
        </Button>
      )}

      {uploading && (
        <div className="text-center text-sm text-gray-600">
          Uploading... Please wait.
        </div>
      )}
    </div>
  );
}

