---
name: sigint-terrain-rendering-engine
version: "2.0.0"
owner: tactical-geospatial-visualization
status: active
domain_tags:
  [
    c4isr,
    geospatial-intelligence,
    terrain-analysis,
    shaders,
    webgl,
    svg,
    tactical-ui,
    data-visualization,
    line-of-sight,
    fresnel-analysis
  ]
risk_level: high
intent: >
  Deterministically compiles terrain, telemetry, and operational-state metadata
  into SIGINT-TERRAIN compliant 2D/3D render layers without semantic drift.
  It functions as a visual rules engine, not a stylistic renderer.

when_to_use: >
  Use when building tactical terrain views, line-of-sight tools, Fresnel planning
  panels, denied-zone overlays, terrain profiles, or low-relief situational
  awareness displays that must preserve the SIGINT-TERRAIN doctrine exactly.

when_not_to_use: >
  Do not use for consumer map products, decorative cartography, generic GIS dashboards,
  or any interface that cannot enforce blend order, terrain datum control,
  confidence encoding, or performance-based layer degradation.

operating_principle: >
  Every rendered mark must answer a tactical question. Texture, tone, contour,
  and wash are operational encodings, never cosmetic effects.

inputs:
  - name: terrain_dem_topographic
    type: file/geotiff|file/cog|file/netcdf
    description: >
      Bare-earth topographic elevation source. Preferred datum NAVD88.
      Must include resolution metadata and bounds.
    required: true

  - name: terrain_dem_bathymetric
    type: file/geotiff|file/cog|file/netcdf|null
    description: >
      Bathymetric source used when AO crosses littoral or harbor zones.
      Optional unless transect or viewport intersects water.
    required: false

  - name: telemetry_tracks
    type: json
    description: >
      Live or stored asset tracks, sensor origins, observer/target points,
      and per-track timestamps.
    required: false

  - name: threat_geometry
    type: geojson|json
    description: >
      Denied zones, blackout regions, fire-control areas, degraded sensing zones,
      or protected corridors.
    required: false

  - name: sensor_feed_registry
    type: json
    description: >
      Feed-level freshness, provenance, confidence class, modality, and whether
      the feed is live, cached, replayed, or synthetic.
    required: true

  - name: analysis_request
    type: json
    description: >
      Declares requested output mode(s), e.g. map_only, slope_overlay,
      elevation_profile, los_check, fresnel_check, terrain_3d, route_assessment.
    required: true

  - name: viewport_context
    type: json
    description: >
      Zoom, pitch, device class, GPU capability, desired FPS target,
      screen size, and field/desktop operating context.
    required: true

  - name: terrain_profile_override
    type: json|null
    description: >
      Optional named profile override such as nyc_littoral_low_relief,
      alpine_high_delta_z, urban_canyon_lidar, desert_escarpment.
    required: false

outputs:
  - name: sigint_rendering_package
    type: file/zip
    success_criteria: >
      Contains all compiled assets and manifests needed to reproduce the
      exact render state without hidden decisions.

  - name: render_state_manifest
    type: file/json
    success_criteria: >
      Explicitly lists activated layers, suppressed layers, opacities,
      blend modes, datum transforms, terrain profile, degradation decisions,
      and safety warnings.

  - name: verification_report
    type: file/markdown
    success_criteria: >
      Includes pass/fail checks for layer order, palette compliance,
      terrain profile compliance, timestamp handling, LOS/Fresnel logic,
      and mobile performance budget.

dependencies:
  tools:
    [
      dem_preprocessor,
      datum_transform_bridge,
      hillshade_generator,
      contour_vectorizer,
      slope_aspect_solver,
      svg_pattern_generator,
      shader_material_compiler,
      elevation_profile_sampler,
      los_fresnel_solver
    ]
  knowledge:
    [
      sigint_terrain_v1_1_core_spec,
      sigint_terrain_v1_1_textures_elevations_addendum,
      rf_fresnel_zone_physics,
      navd88_egm96_egm2008_datum_handling,
      tactical_rendering_accessibility_thresholds
    ]

verification:
  required: true
  methods:
    [
      cove,
      layer_compositing_audit,
      palette_compliance_check,
      terrain_profile_compliance_check,
      timestamp_provenance_check,
      los_geometry_validation,
      fresnel_equation_validation,
      z_exaggeration_sanity_check,
      mobile_texture_budget_check
    ]

policy:
  safety_notes: >
    Texture == operational meaning. Confidence grain, denied-zone crosshatch,
    and uncertainty wash must never be invented, suppressed, or stylized for visual taste.
    If provenance, timestamps, or terrain datum are uncertain, the renderer must fail loudly
    or downgrade to a marked degraded state.

  representation_rules:
    - "Do not default unknown timestamps to CURRENT."
    - "Do not apply hypsometric rainbow palettes."
    - "Do not merge topographic and bathymetric surfaces without explicit datum handling."
    - "Do not render denied zones with low-contrast or decorative patterns."
    - "Do not enable 3D briefing mode when device budget cannot preserve terrain fidelity."

ports:
  provides:
    [
      tactical_map_layers_v2,
      terrain_profile_panel_v2,
      los_elevation_profile_v2,
      fresnel_clearance_overlay_v2,
      slope_aspect_overlay_v2,
      terrain_mesh_materials_v2
    ]
  consumes:
    [
      raw_lidar_pointcloud_v1,
      bare_earth_dem_v1,
      bathymetry_grid_v1,
      live_asset_tracks_v1,
      denied_zone_geometry_v1,
      sensor_registry_v1
    ]
---

# Purpose
- Act as the **deterministic compiler** between terrain physics and tactical visual language.
- Produce a rendering stack where operators can infer terrain relief, slope trafficability,
  data freshness, denied-space presence, and LOS/Fresnel clearance without requiring
  legend-first reading.

# Core Doctrine
## Invariants
- **Texture Is Meaning:** grain = provenance/confidence, hatching = slope severity,
  crosshatch = contested/denied area, wash = data age.
- **Compositing Is Law:** layer order is fixed and semantically meaningful.
- **Terrain Must Be Honest:** all elevation rendering must declare datum, source class,
  and z-exaggeration.
- **Degradation Must Be Visible:** performance fallback is allowed; silent semantic loss is not.

## Canonical Layer Order
1. Base imagery / neutral substrate — normal
2. DEM hillshade — overlay, 55–65%
3. Contour or hachure slope overlay — multiply, 100%
4. Confidence stipple — screen, variable by provenance
5. Uncertainty wash — normal, variable by age tier
6. Denied-zone crosshatch — normal, 100%
7. Scan-line overlay — normal, 4%, live feeds only

# Input Normalization
Before any rendering:
1. Validate presence of terrain bounds, resolution, and vertical datum.
2. Normalize timestamps to UTC and compute feed age buckets.
3. Detect whether AO intersects waterline.
4. Detect whether AO is low-relief, high-relief, or urban-LiDAR contaminated.
5. Select terrain profile:
   - explicit override if provided
   - otherwise infer from AO characteristics

# Terrain Profiles
## nyc_littoral_low_relief
Use when AO intersects NYC low-relief littoral terrain.
- z_exaggeration: 3.0
- contour_interval_m: 5
- hillshade_altitude: 35
- hypsometric_bands: first_5_only
- require_bathymetry_merge: true if water crossed
- urban_lidar_building_filter: required above zoom 16

## standard_regional
- z_exaggeration: by zoom table
- contour_interval_m: 10 default
- hillshade_altitude: 45

## alpine_high_delta_z
- clamp_z_exaggeration: 1.0 to 1.5
- prioritize_contours_over_hillshade_microtexture
- disable_low-relief assumptions

## urban_canyon_lidar
- prefer_bare_earth_dem
- suppress rooftop false-relief in LOS mode
- require building contamination warning if DSM is used

# Rendering Decision Rules
## Hillshade
- Always active as the base terrain interpretation layer.
- Use 315° azimuth.
- Use 45° altitude unless terrain profile overrides it.
- At zoom > 14, reduce opacity if LiDAR micro-relief overwhelms legibility.

## Contours / Hachure
- Enable automatically for slope_analysis, mobility_planning, landing_zone_assessment.
- Spacing must correlate with slope band:
  - 0–5°: none
  - 5–15°: 8px
  - 15–30°: 4px
  - 30–45°: 2px
  - 45°+: 1px + heavier stroke

## Confidence Stipple
- high_res_lidar: minimal grain
- medium_confidence: moderate grain
- interpolated/synthetic: visible grain
- If provenance missing, force degraded-state warning and default to medium grain + warning badge

## Uncertainty Wash
- CURRENT: < 30m
- RECENT: 30m–2h
- AGING: 2h–6h
- STALE: 6h–24h
- HISTORICAL: > 24h
- If timestamp absent, never display CURRENT; force STALE and emit hard warning

## Denied / Contested Zones
- Always use diagonal crosshatch with red family encoding.
- Geometry must remain legible above hillshade and below live-track icons.
- No feathered, painterly, or low-contrast alternatives allowed.

## Scan Lines
- Only for live feeds and active ingest panels.
- Never apply to archived stills, static terrain panels, or analysis exports.

# Output Modes
## map_only
Return terrain stack and overlays for top-down SA view.

## slope_overlay
Add severity palette + hachure behavior for trafficability reading.

## elevation_profile
Generate transect panel with:
- terrain fill
- sea-level threshold
- distance/elevation labels
- bathymetric fill where applicable

## los_check
Overlay observer-target LOS with clear vs masked states.

## fresnel_check
Add first Fresnel zone and pass/fail clearance labeling by frequency class.

## terrain_3d
Generate perspective mesh only if device budget and source fidelity allow it.

## route_assessment
Reserved for v3. Not implemented in v2. A request containing this mode must be rejected with a validation error rather than silently ignored.

# Degradation Ladder
## Desktop Analyst
- Full 7-layer stack permitted
- 2D + profile + optional 3D

## Field Tablet
- Max 3 simultaneous textures
- **Semantic suppressions (applied unconditionally before budget math):**
  - Suppress scan_line_overlay when feed is not live (non_live_cached_feed)
- **Performance suppressions (applied in priority order until under texture budget):**
  1. Drop confidence_stipple first
  2. Drop contour_hachure second
  3. Drop uncertainty_wash third (last resort — semantic loss is significant)
- Simplify contour density below zoom 12 (not a suppression — a density reduction)
- Emit REDUCED_SEMANTIC_FIDELITY warning whenever any performance suppression fires

## Degraded Edge Device
- Keep hillshade + one operational overlay only
- Suppress 3D
- Emit degraded-state badge into manifest

## No Blend-Mode Support
- Block advanced render package
- Fallback to explicit vector contour + flat wash only
- Mark as reduced semantic fidelity

# Execution Steps
## Phase 1 — Orient
1. Read request and viewport.
2. Select terrain profile.
3. Validate terrain source class and datum.
4. Determine whether bathymetric merge is mandatory.
5. Compute device budget.

## Phase 2 — Normalize
1. Transform elevation inputs into unified vertical reference.
2. Remove or flag rooftop/building contamination if LOS/Fresnel mode is requested.
3. Bucket feed freshness.
4. Classify provenance confidence.

## Phase 3 — Compile
1. Build hillshade substrate.
2. Build contour/hachure vectors if mode requires.
3. Inject confidence stipple if provenance warrants and budget allows.
4. Inject uncertainty wash by age tier.
5. Inject denied-zone crosshatch from threat geometry.
6. Apply scan-line overlay only to live feed surfaces.
7. Generate profile/LOS/Fresnel overlays where requested.
8. Build 3D mesh only if approved by budget and fidelity gates.

## Phase 4 — Verify
1. Check layer order.
2. Check palette compliance.
3. Check profile-specific overrides.
4. Check timestamp handling.
5. Check LOS geometry output against terrain sampler.
6. Check Fresnel clearance calculations against declared frequency.
7. Check active texture count against device budget.

## Phase 5 — Package
Return:
- `/layers/*`
- `/shaders/*`
- `/patterns/*`
- `/profiles/*`
- `/render_state_manifest.json`
- `/verification_report.md`

# Acceptance Gates
A render is valid only if all are true:
- Layer order matches canonical stack.
- No illegal palette is used.
- Timestamp-less feeds are not shown as CURRENT.
- Water-crossing profile uses bathymetric fill or explicitly marks bathymetry unavailable.
- 3D mode respects terrain profile and device budget.
- Output manifest explains every suppressed or degraded layer.

# CoVe Assertions
1. **Claim:** Slope appearance reflects measured terrain gradient.
   - **Evidence:** hachure spacing and slope palette bands derive from DEM slope output.

2. **Claim:** Confidence texture reflects provenance, not decoration.
   - **Evidence:** grain density is selected from source class and manifest logs the choice.

3. **Claim:** Freshness wash reflects actual feed age.
   - **Evidence:** age tier derived from normalized timestamps; unknown timestamps force degraded state.

4. **Claim:** Littoral transects depict above-sea and below-sea terrain honestly.
   - **Evidence:** topographic and bathymetric surfaces are datum-normalized before profile generation.

5. **Claim:** LOS/Fresnel outputs are analytically grounded.
   - **Evidence:** terrain samples, observer/target heights, and frequency-specific Fresnel calculations are logged.

# Failure Modes & Escalation
- **Failure:** LiDAR rooftop contamination masquerades as blocking terrain.
  - **Fix:** switch to bare-earth DEM or emit `LOS_UNSAFE_DSM_CONTAMINATION`.

- **Failure:** Bathymetry missing for harbor-crossing transect.
  - **Fix:** block bathymetric fill and emit `BATHYMETRY_REQUIRED_FOR_WATER_CROSSING`.

- **Failure:** Device cannot sustain required blend modes.
  - **Fix:** return reduced-fidelity package with manifest warning; do not pretend full compliance.

- **Failure:** Terrain delta-Z is too high for requested z-exaggeration.
  - **Fix:** clamp per terrain profile and log adjustment.

- **Hard Stop:** sensor timestamps absent in safety-relevant view.
  - **Output:** `[BLOCKED: feed freshness undefined. CURRENT/RECENT states prohibited.]`

# Output Schema
## render_state_manifest.json
```json
{
  "terrain_profile": "nyc_littoral_low_relief",
  "vertical_datum": "NAVD88",
  "water_crossing": true,
  "z_exaggeration": 3.0,
  "device_budget": "field_tablet",
  "layers_active": [
    {"id":"hillshade_oblique","blend":"overlay","opacity":0.60},
    {"id":"contour_hachure","blend":"multiply","opacity":1.0},
    {"id":"uncertainty_wash","blend":"normal","tier":"AGING"},
    {"id":"denied_zone","blend":"normal","opacity":1.0}
  ],
  "layers_suppressed": [
    {"id":"stipple_confidence","reason":"performance_budget"},
    {"id":"scan_lines","reason":"not_live_feed_surface"}
  ],
  "warnings": [
    "bathymetry_merged",
    "urban_lidar_filter_applied"
  ],
  "analysis_products": {
    "elevation_profile": true,
    "los_check": true,
    "fresnel_check": "C_BAND_MASKED"
  }
}
```
