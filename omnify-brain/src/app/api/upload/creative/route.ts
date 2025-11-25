import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { uploadFile, getCreativePath, validateFile, getSignedUrl, STORAGE_BUCKETS } from '@/lib/storage';

/**
 * POST /api/upload/creative
 * Upload a creative asset (image or video)
 */
export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser(request);
    
    if (!user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const formData = await request.formData();
    const file = formData.get('file') as File;
    const creativeId = formData.get('creativeId') as string;
    const organizationId = user.organizationId || formData.get('organizationId') as string;

    if (!file) {
      return NextResponse.json(
        { error: 'File is required' },
        { status: 400 }
      );
    }

    if (!creativeId) {
      return NextResponse.json(
        { error: 'Creative ID is required' },
        { status: 400 }
      );
    }

    // Validate file
    const allowedTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/webp',
      'video/mp4',
      'video/webm',
    ];
    
    const validation = validateFile(file, {
      maxSize: 50 * 1024 * 1024, // 50MB
      allowedTypes,
    });

    if (!validation.valid) {
      return NextResponse.json(
        { error: validation.error },
        { status: 400 }
      );
    }

    // Generate storage path
    const path = getCreativePath(organizationId, creativeId, file.name);

    // Upload file
    const uploadResult = await uploadFile({
      bucket: STORAGE_BUCKETS.CREATIVES,
      path,
      file,
      contentType: file.type,
      cacheControl: '31536000', // 1 year (immutable assets)
      upsert: true, // Allow overwriting
    });

    // Get signed URL (private bucket - expires in 1 year)
    const signedUrl = await getSignedUrl(STORAGE_BUCKETS.CREATIVES, path, 31536000);

    // Update creative record with file path (store path, not URL, since URLs expire)
    if (creativeId) {
      await supabaseAdmin
        .from('creatives')
        .update({
          metadata: {
            ...(await supabaseAdmin
              .from('creatives')
              .select('metadata')
              .eq('id', creativeId)
              .single()
              .then(({ data }) => data?.metadata || {})),
            file_path: path,
            file_size: file.size,
            file_type: file.type,
            uploaded_at: new Date().toISOString(),
          },
        })
        .eq('id', creativeId);
    }

    return NextResponse.json({
      success: true,
      path: uploadResult.path,
      url: signedUrl,
      size: file.size,
      type: file.type,
    });
  } catch (error: any) {
    console.error('[UPLOAD CREATIVE] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to upload creative' },
      { status: 500 }
    );
  }
}

