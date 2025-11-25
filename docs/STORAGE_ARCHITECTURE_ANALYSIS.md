# Storage Architecture Analysis - Brain MVP

**Date**: January 2025  
**Status**: 🔍 **ANALYSIS REQUIRED**  
**Purpose**: Evaluate storage needs for Brain MVP, especially for images/videos

---

## 🎯 CURRENT STATE

### **Supabase Storage Capabilities**

**What Supabase Provides:**
- ✅ **PostgreSQL Database** - Structured data (metrics, campaigns, users)
- ✅ **Supabase Storage** - File storage (images, videos, documents)
- ✅ **Row Level Security (RLS)** - Secure file access
- ✅ **CDN Integration** - Fast file delivery
- ✅ **Image Transformations** - On-the-fly image resizing/optimization

**Supabase Storage Limits (Free Tier):**
- 1 GB storage
- 2 GB bandwidth/month
- Unlimited files

**Supabase Storage Limits (Pro Tier):**
- 100 GB storage
- 200 GB bandwidth/month
- Unlimited files

---

## 📊 STORAGE REQUIREMENTS ANALYSIS

### **What Needs Storage in Brain MVP?**

#### **1. Ad Creatives (Images/Videos)**
- **Purpose**: Store ad creative assets (images, videos)
- **Estimated Size**: 
  - Image: 500 KB - 2 MB per image
  - Video: 5 MB - 50 MB per video (15-30s ads)
- **Volume**: 
  - Per organization: 50-200 creatives
  - Total: ~100 MB - 4 GB per organization
- **Access Pattern**: Frequent reads, infrequent writes

#### **2. User Profile Images**
- **Purpose**: User avatars
- **Estimated Size**: 50-200 KB per image
- **Volume**: 1 per user
- **Access Pattern**: Frequent reads, rare writes

#### **3. Organization Logos**
- **Purpose**: Company logos
- **Estimated Size**: 50-500 KB per logo
- **Volume**: 1 per organization
- **Access Pattern**: Frequent reads, rare writes

#### **4. Reports/Exports**
- **Purpose**: Generated PDF reports, CSV exports
- **Estimated Size**: 1-10 MB per report
- **Volume**: 10-50 per organization/month
- **Access Pattern**: Infrequent reads, periodic writes

#### **5. Brain State Snapshots (Optional)**
- **Purpose**: Historical brain state backups
- **Estimated Size**: 100-500 KB per snapshot
- **Volume**: Daily snapshots
- **Access Pattern**: Rare reads, daily writes

---

## ✅ RECOMMENDATION: Supabase Storage is Sufficient for MVP

### **Why Supabase Storage Works:**

1. **✅ Built-in File Storage**
   - Supabase Storage is built on top of S3-compatible storage
   - Provides REST API and SDK for file uploads
   - Integrates seamlessly with Supabase Auth (RLS)

2. **✅ Cost-Effective for MVP**
   - Free tier: 1 GB (sufficient for initial testing)
   - Pro tier: $25/month for 100 GB (sufficient for 25-50 organizations)
   - No additional infrastructure needed

3. **✅ Security Built-in**
   - Row Level Security (RLS) for file access
   - Organization-scoped buckets
   - Automatic CDN delivery

4. **✅ Image Optimization**
   - Built-in image transformations (resize, crop, format conversion)
   - Automatic WebP conversion
   - CDN caching

5. **✅ Simple Integration**
   - Same authentication (Supabase Auth)
   - Same SDK (`@supabase/supabase-js`)
   - No additional service setup

---

## 🏗️ RECOMMENDED ARCHITECTURE

### **Storage Buckets Structure**

```
supabase-storage/
├── creatives/              # Ad creative assets
│   ├── {organization_id}/
│   │   ├── images/
│   │   │   └── {creative_id}.jpg
│   │   └── videos/
│   │       └── {creative_id}.mp4
│
├── avatars/                # User profile images
│   └── {user_id}.jpg
│
├── logos/                  # Organization logos
│   └── {organization_id}.png
│
└── exports/                # Generated reports
    └── {organization_id}/
        └── {report_id}.pdf
```

### **RLS Policies**

```sql
-- Creatives: Organization-scoped access
CREATE POLICY "Users can view creatives in their organization"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'creatives' AND
  (storage.foldername(name))[1] = current_setting('app.organization_id')
);

-- Avatars: User-scoped access
CREATE POLICY "Users can view their own avatar"
ON storage.objects FOR SELECT
USING (
  bucket_id = 'avatars' AND
  name = current_setting('app.user_id') || '.jpg'
);
```

---

## 🚀 IMPLEMENTATION PLAN

### **Phase 1: Basic File Upload (MVP)**

**Files to Create:**
1. `omnify-brain/src/app/api/upload/creative/route.ts` - Creative upload
2. `omnify-brain/src/app/api/upload/avatar/route.ts` - Avatar upload
3. `omnify-brain/src/lib/storage.ts` - Storage utilities
4. `omnify-brain/src/components/upload/CreativeUpload.tsx` - Upload component

**Features:**
- ✅ Upload images/videos to Supabase Storage
- ✅ Organization-scoped buckets
- ✅ File validation (size, type)
- ✅ Image optimization (resize, compress)

### **Phase 2: Image Optimization**

**Features:**
- ✅ Automatic image resizing (multiple sizes)
- ✅ WebP conversion
- ✅ Thumbnail generation
- ✅ CDN caching

### **Phase 3: Video Processing (Future)**

**Features:**
- ⏳ Video transcoding (if needed)
- ⏳ Thumbnail extraction
- ⏳ Progress tracking

---

## 💰 COST ANALYSIS

### **Supabase Storage Costs**

**Free Tier (Development):**
- 1 GB storage
- 2 GB bandwidth/month
- ✅ Sufficient for: 1-2 organizations, testing

**Pro Tier ($25/month):**
- 100 GB storage
- 200 GB bandwidth/month
- ✅ Sufficient for: 25-50 organizations
- ✅ ~2-4 GB per organization

**Enterprise Tier (Custom):**
- Unlimited storage
- Custom bandwidth
- ✅ For scale (100+ organizations)

### **Alternative: AWS S3 + CloudFront**

**Cost Comparison:**
- S3: $0.023/GB/month
- CloudFront: $0.085/GB (first 10 TB)
- **Total**: ~$0.11/GB/month

**For 100 GB:**
- Supabase Pro: $25/month (flat)
- AWS S3+CloudFront: ~$11/month (pay-as-you-go)

**Verdict:** Supabase is more cost-effective for MVP (< 100 GB)

---

## ⚡ OPTIMIZATIONS

### **1. Image Optimization**

**Strategy:**
- Upload original → Supabase Storage
- Generate multiple sizes on-the-fly (via Supabase Transformations)
- Serve optimized images via CDN

**Implementation:**
```typescript
// Use Supabase Image Transformations
const imageUrl = supabase
  .storage
  .from('creatives')
  .getPublicUrl(`${orgId}/images/${creativeId}.jpg`, {
    transform: {
      width: 800,
      height: 600,
      format: 'webp',
      quality: 80
    }
  })
```

**Benefits:**
- ✅ Automatic optimization
- ✅ No server processing needed
- ✅ CDN caching
- ✅ Reduced bandwidth

### **2. Lazy Loading**

**Strategy:**
- Load thumbnails first
- Load full images on demand
- Use Next.js Image component

**Implementation:**
```tsx
<Image
  src={thumbnailUrl}
  placeholder="blur"
  loading="lazy"
  sizes="(max-width: 768px) 100vw, 50vw"
/>
```

### **3. Video Optimization**

**Strategy:**
- Upload videos in compressed format (H.264)
- Generate thumbnails on upload
- Use video CDN (Supabase Storage CDN)

**Implementation:**
```typescript
// Upload video
const { data, error } = await supabase.storage
  .from('creatives')
  .upload(`${orgId}/videos/${creativeId}.mp4`, videoFile, {
    contentType: 'video/mp4',
    cacheControl: '3600'
  })

// Generate thumbnail (client-side or server-side)
```

### **4. Caching Strategy**

**Strategy:**
- Cache static assets (images, videos) via CDN
- Cache for 1 year (immutable assets)
- Use cache headers

**Implementation:**
```typescript
// Set cache headers on upload
await supabase.storage
  .from('creatives')
  .upload(path, file, {
    cacheControl: '31536000', // 1 year
    upsert: false
  })
```

### **5. Storage Cleanup**

**Strategy:**
- Delete unused creatives after 90 days
- Archive old reports after 1 year
- Monitor storage usage

**Implementation:**
```typescript
// Scheduled cleanup job
export async function cleanupOldCreatives() {
  const oldCreatives = await supabase
    .from('creatives')
    .select('id, organization_id')
    .eq('status', 'archived')
    .lt('archived_at', new Date(Date.now() - 90 * 24 * 60 * 60 * 1000))
  
  // Delete from storage
  for (const creative of oldCreatives.data) {
    await supabase.storage
      .from('creatives')
      .remove([`${creative.organization_id}/images/${creative.id}.jpg`])
  }
}
```

---

## 📋 IMPLEMENTATION CHECKLIST

### **Immediate (MVP)**
- [ ] Create Supabase Storage buckets (creatives, avatars, logos)
- [ ] Set up RLS policies for file access
- [ ] Create file upload API routes
- [ ] Create upload UI components
- [ ] Add file validation (size, type)

### **Short-term (Optimization)**
- [ ] Implement image transformations
- [ ] Add lazy loading for images
- [ ] Set up CDN caching
- [ ] Add storage usage monitoring

### **Long-term (Scale)**
- [ ] Implement video processing
- [ ] Add storage cleanup jobs
- [ ] Monitor costs and optimize
- [ ] Consider S3 migration if needed (> 100 GB)

---

## ✅ CONCLUSION

### **Answer: Yes, Supabase Storage is Sufficient for MVP**

**Reasons:**
1. ✅ Built-in file storage (no additional service needed)
2. ✅ Cost-effective for MVP (free tier → $25/month)
3. ✅ Security built-in (RLS, organization-scoped)
4. ✅ Image optimization built-in
5. ✅ CDN delivery included
6. ✅ Simple integration (same SDK)

**When to Consider Alternatives:**
- ⚠️ Storage > 100 GB (consider S3)
- ⚠️ Bandwidth > 200 GB/month (consider CloudFront)
- ⚠️ Need advanced video processing (consider Mux/Cloudinary)
- ⚠️ Need global edge locations (consider CloudFront)

**For MVP:** ✅ **Supabase Storage is the right choice**

---

**Status**: ✅ **RECOMMENDATION: Use Supabase Storage for MVP**  
**Next Steps**: Implement file upload functionality

