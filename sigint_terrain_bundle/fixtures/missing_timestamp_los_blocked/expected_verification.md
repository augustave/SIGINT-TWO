# SIGINT Terrain Verification Report

**Fixture:** missing_timestamp_los_blocked_v1  
**Overall Status:** 🔴 BLOCKED  
**Purpose:** Validates hard-stop behavior when a safety-relevant LOS request is made against a feed with no timestamp.

---

## Summary

This fixture exercises the doctrine's most critical safety invariant: unknown feed timestamps must never be assigned CURRENT or RECENT tier, and a safety-relevant LOS request against such a feed must be blocked — not degraded, not warned — **blocked**.

The renderer produced a hillshade-only substrate with all feed-dependent overlays suppressed and the LOS result set to `UNKNOWN`. The `FEED_FRESHNESS_UNDEFINED` warning was emitted and propagated to the manifest.

---

## Check Results

| Check | Status | Notes |
|-------|--------|-------|
| Layer compositing audit | ✅ Pass | Active layers in canonical order; all suppressed layers carry reasons |
| Palette compliance | ✅ Pass | No illegal palette applied |
| Terrain profile compliance | ✅ Pass | `nyc_littoral_low_relief` with correct z_exaggeration, altitude, interval |
| Timestamp / provenance check | ❌ Fail | `feed_alpha_eoir` has no `timestamp_utc`; LOS mode requested |
| LOS geometry validation | 🔴 Blocked | LOS result set to `UNKNOWN`; feed trust state unverifiable |
| Mobile texture budget | ✅ Pass | `desktop_analyst` — no constraint |

---

## Blocking Errors

```
FEED_FRESHNESS_UNDEFINED: feed_alpha_eoir missing timestamp_utc.
LOS output blocked. CURRENT and RECENT tiers prohibited for this feed.
```

---

## Required Warnings

- `FEED_FRESHNESS_UNDEFINED` — emitted and present in manifest ✅

---

## Pass Criteria for This Fixture

A renderer passes this fixture only if all of the following are true:

1. `overall_status` is `blocked`
2. `los_check` result is `UNKNOWN`
3. `FEED_FRESHNESS_UNDEFINED` is present in `warnings`
4. No `CURRENT` or `RECENT` feed age tier appears anywhere in the manifest
5. Suppressed layers all carry `reason` fields
6. `blocking_errors` array is non-empty and references the feed freshness failure
