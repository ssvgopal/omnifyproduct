# Deprecated Backend Code - Archive

**Date Archived**: January 2025  
**Reason**: Not aligned with MVP roadmap. Supabase-based MVP is the strategic direction.

## What's Here

This directory contains backend code that has been deprecated because it's not part of the MVP roadmap:

1. **AgentKit Integration** - Over-engineered for MVP validation
2. **GoHighLevel Integration** - Replaced by TripleWhale/HubSpot/Klaviyo strategy
3. **MongoDB Infrastructure** - Replaced by Supabase (PostgreSQL)
4. **Non-MVP Brain Modules** - EYES, VOICE, REFLEXES (Phase 2 features)
5. **Magic Features** - Advanced features not in MVP scope

## Can This Be Deleted?

**Phase 1 Files** (AgentKit, GoHighLevel, MongoDB, Non-MVP Brain, Magic Features):
- ✅ **Safe to delete after 3 months** if MVP is successful
- ⚠️ **Keep archived** until MVP validation complete

**Phase 2/3 Files** (Non-MVP integrations, Advanced infrastructure):
- 📦 **Archive only** - May be needed in Phase 2
- ⚠️ **Do not delete** - Keep for future use

## Restoration

If you need to restore any of this code:

1. Check `docs/DEPRECATION_ACTION_PLAN.md` for what was moved
2. Copy files back from this archive
3. Update imports and dependencies
4. Test thoroughly

## Related Documentation

- **Deprecation Plan**: `docs/DEPRECATION_ACTION_PLAN.md`
- **MVP Roadmap**: `UNIFIED_GAP_ANALYSIS_AND_STRATEGIC_ROADMAP.md`
- **Implementation Summary**: `omnify-brain/docs/IMPLEMENTATION_SUMMARY.md`

