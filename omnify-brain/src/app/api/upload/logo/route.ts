import { NextRequest, NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { supabaseAdmin } from '@/lib/db/supabase';
import { uploadFile, getLogoPath, validateFile, getSignedUrl, STORAGE_BUCKETS } from '@/lib/storage';

/**
 * POST /api/upload/logo
 * Upload an organization logo
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

    // Only admins can upload logos
    if (user.role !== 'admin') {
      return NextResponse.json(
        { error: 'Only admins can upload organization logos' },
        { status: 403 }
      );
    }

    const formData = await request.formData();
    const file = formData.get('file') as File;
    const organizationId = user.organizationId || formData.get('organizationId') as string;

    if (!file) {
      return NextResponse.json(
        { error: 'File is required' },
        { status: 400 }
      );
    }

    if (!organizationId) {
      return NextResponse.json(
        { error: 'Organization ID is required' },
        { status: 400 }
      );
    }

    // Validate file (images only)
    const allowedTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/webp',
      'image/svg+xml',
    ];
    
    const validation = validateFile(file, {
      maxSize: 5 * 1024 * 1024, // 5MB
      allowedTypes,
    });

    if (!validation.valid) {
      return NextResponse.json(
        { error: validation.error },
        { status: 400 }
      );
    }

    // Generate storage path
    const extension = file.name.split('.').pop() || 'png';
    const path = getLogoPath(organizationId, extension);

    // Upload file
    await uploadFile({
      bucket: STORAGE_BUCKETS.LOGOS,
      path,
      file,
      contentType: file.type,
      cacheControl: '31536000', // 1 year
      upsert: true,
    });

    // Get signed URL (private bucket - expires in 1 year)
    const signedUrl = await getSignedUrl(STORAGE_BUCKETS.LOGOS, path, 31536000);

    // Update organization record with logo path (store path, not URL, since URLs expire)
    await supabaseAdmin
      .from('organizations')
      .update({
        metadata: {
          logo_path: path,
          logo_updated_at: new Date().toISOString(),
        },
      })
      .eq('id', organizationId);

    return NextResponse.json({
      success: true,
      url: signedUrl,
      path: path,
      size: file.size,
    });
  } catch (error: any) {
    console.error('[UPLOAD LOGO] Error:', error);
    return NextResponse.json(
      { error: error.message || 'Failed to upload logo' },
      { status: 500 }
    );
  }
}

