# 🔧 Platform Integrations - Required Fixes

**Date**: January 2025  
**Status**: **Fixes Required** - Critical production blockers

---

## ✅ FIXES APPLIED

### **1. LinkedIn Ads OAuth** ✅ **FIXED**
- ✅ Added input validation for `code` and `state`
- ✅ Added error handling for token exchange failures
- ✅ Added validation for token response
- ✅ Added logging import

---

## ⚠️ FIXES STILL REQUIRED

### **2. TikTok Ads OAuth** ❌ **NEEDS FIX**
**File**: `backend/api/tiktok_ads_oauth_routes.py`

**Required Changes**:
1. Add logging import
2. Add validation for `request.code` (not None/empty)
3. Add validation for `request.state` (not None/empty)
4. Add try/except around `oauth2.exchange_code_for_tokens()`
5. Add validation that `tokens["access_token"]` exists

---

### **3. YouTube Ads OAuth** ❌ **NEEDS FIX**
**File**: `backend/api/youtube_ads_oauth_routes.py`

**Required Changes**:
1. Add logging import
2. Add validation for `request.code` (not None/empty)
3. Add validation for `request.state` (not None/empty)
4. Add try/except around `oauth2.exchange_code_for_tokens()`
5. Add validation that `tokens["access_token"]` exists

---

### **4. GoHighLevel OAuth** ❌ **NEEDS FIX**
**File**: `backend/api/gohighlevel_oauth_routes.py`

**Required Changes**:
1. Add logging import
2. Add validation for `request.code` (not None/empty)
3. Add validation for `request.state` (not None/empty)
4. Add try/except around `oauth2.exchange_code_for_tokens()`
5. Add validation that `tokens["access_token"]` exists

---

### **5. Shopify OAuth** ⚠️ **PARTIALLY FIXED**
**File**: `backend/api/shopify_oauth_routes.py`

**Required Changes**:
1. Add logging import
2. Add validation for `request.code` (not None/empty)
3. Add validation for `request.state` (not None/empty)
4. ✅ Already has validation for `request.shop`
5. ✅ Already has check for `tokens` existence

---

### **6. Stripe OAuth** ❌ **NEEDS FIX**
**File**: `backend/api/stripe_oauth_routes.py`

**Required Changes**:
1. Add logging import
2. Add validation for `request.code` (not None/empty)
3. Add validation for `request.state` (not None/empty)
4. Add try/except around `oauth2.exchange_code_for_tokens()`
5. Add validation that `tokens["access_token"]` exists

---

## 🚨 CRITICAL: MOCK FALLBACK CODE REMOVAL

### **Google Ads Client** ❌ **CRITICAL**
**File**: `backend/integrations/google_ads/client.py`

**Lines to Fix**:
- Line 359-360: Remove `_create_mock_campaign` fallback
- Line 391-392: Remove `_create_mock_ad_group` fallback
- Line 424-425: Remove `_create_mock_keyword` fallback
- Line 439-440: Remove `_get_mock_metrics` fallback
- Lines 442-504: Delete all `_create_mock_*` methods

**Action**: Replace with proper exception raising:
```python
except Exception as e:
    logger.error(f"Failed to create Google Ads campaign: {e}", exc_info=True)
    raise RuntimeError(f"Google Ads API error: {str(e)}")
```

---

### **Meta Ads Client** ❌ **CRITICAL**
**File**: `backend/integrations/meta_ads/client.py`

**Lines to Fix**:
- Line 306-307: Remove `_create_mock_campaign` fallback
- Line 340-341: Remove `_create_mock_ad_set` fallback
- Line 371-372: Remove `_create_mock_ad` fallback
- Line 386-387: Remove `_get_mock_insights` fallback
- Lines 403-466: Delete all `_create_mock_*` methods

**Action**: Replace with proper exception raising

---

### **GoHighLevel Client** ❌ **CRITICAL**
**File**: `backend/integrations/gohighlevel/client.py`

**Lines to Fix**:
- Line 293-294: Remove `_create_mock_client` fallback
- Line 330-331: Remove `_create_mock_campaign` fallback
- Line 362-363: Remove `_create_mock_workflow` fallback
- Line 377-378: Remove `_get_mock_analytics` fallback
- Lines 380-437: Delete all `_create_mock_*` methods

**Action**: Replace with proper exception raising

---

## 📋 FIX TEMPLATE

### **OAuth Callback Fix Template**

```python
@router.post("/oauth/callback")
async def handle_oauth_callback(
    request: OAuthCallbackRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Handle OAuth2 callback"""
    try:
        # Validate required fields
        if not request.code or not request.code.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code is required"
            )
        
        if not request.state or not request.state.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="State parameter is required"
            )
        
        # Verify state
        state_doc = await db.oauth_states.find_one({
            "user_id": current_user["user_id"],
            "state": request.state,
            "platform": "{platform_name}",
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not state_doc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired state"
            )
        
        await db.oauth_states.delete_one({"_id": state_doc["_id"]})
        
        # Get OAuth configuration
        import os
        client_id = os.environ.get("{PLATFORM}_CLIENT_ID")
        client_secret = os.environ.get("{PLATFORM}_CLIENT_SECRET")
        redirect_uri = os.environ.get("{PLATFORM}_REDIRECT_URI", "...")
        
        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="{Platform} OAuth2 not configured"
            )
        
        # Exchange code for tokens
        oauth2 = {Platform}OAuth2(client_id, client_secret, redirect_uri)
        try:
            tokens = await oauth2.exchange_code_for_tokens(request.code)
        except Exception as e:
            logger.error(f"{Platform} token exchange failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code for tokens: {str(e)}"
            )
        
        # Validate token response
        if not tokens or not tokens.get("access_token"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid token response from {Platform}"
            )
        
        # ... rest of the code ...
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
```

---

## 🎯 PRIORITY ORDER

1. **P0 - CRITICAL**: Remove mock fallback code (data corruption risk)
2. **P0 - CRITICAL**: Add OAuth validation (security risk)
3. **P1 - HIGH**: Improve error handling (debugging impossible)
4. **P2 - MEDIUM**: Verify API endpoints (will fail in production)
5. **P2 - MEDIUM**: Add required field validation (API errors)

---

## ✅ VERIFICATION CHECKLIST

After fixes are applied:

- [ ] All OAuth routes have input validation
- [ ] All OAuth routes have proper error handling
- [ ] All mock fallback code removed
- [ ] All exceptions are properly logged
- [ ] All error messages are user-friendly
- [ ] Integration tests pass
- [ ] OAuth flows work end-to-end
- [ ] API clients raise exceptions instead of returning mock data

---

**Status**: **IN PROGRESS** - LinkedIn Ads fixed, 5 more OAuth routes need fixes, 3 clients need mock code removal

