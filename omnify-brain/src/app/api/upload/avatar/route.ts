import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { uploadFile, getAvatarPath, validateFile, getSignedUrl, STORAGE_BUCKETS } from '@/lib/storage';

/**
 * POST /api/upload/avatar
 * Upload a user avatar image
 */
export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser();
    
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const formData = await request.formData();
    const file = formData.get('file') as File;
    const userId = user.id || formData.get('userId') as string;

    if (!file) {
      return NextResponse.json(
        { error: 'File is required' },
        { status: 400 }
      );
    }

    // Validate file (images only, smaller size)
    const allowedTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/webp',
    ];
    
    const validation = validateFile(file, {
      maxSize: 2 * 1024 * 1024, // 2MB
      allowedTypes,
    });

    if (!validation.valid) {
      return NextResponse.json(
        { error: validation.error },
        { status: 400 }
      );
    }

    // Generate storage path
    const extension = file.name.split('.').pop() || 'jpg';
    const path = getAvatarPath(userId, extension);

    // Upload file
    await uploadFile({
      bucket: STORAGE_BUCKETS.AVATARS,
      path,
      file,
      contentType: file.type,
      cacheControl: '31536000', // 1 year
      upsert: true,
    });

    // Get signed URL (private bucket - expires in 1 year)
    const signedUrl = await getSignedUrl(STORAGE_BUCKETS.AVATARS, path, 31536000);

    // Update user record with avatar path (store path, not URL, since URLs expire)
    await supabaseAdmin
      .from('users')
      .update({
        metadata: {
          avatar_path: path,
          avatar_updated_at: new Date().toISOString(),
        },
      })
      .eq('id', userId);

    return NextResponse.json({
      success: true,
      url: signedUrl,
      path: path,
      size: file.size,
    });
  } catch (error: any) {
    console.error('[UPLOAD AVATAR] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to upload avatar' },
      { status: 500 }
    );
  }
}

