---
name: sigint-terrain-rendering-swarm
version: "1.0.0"
owner: tactical-geospatial-visualization
status: active
orchestrates: sigint-terrain-rendering-engine
mission: >
  Coordinate specialized agents to compile a trustworthy terrain rendering package
  from elevation sources, telemetry, and operational overlays with deterministic,
  audit-friendly outputs.
entrypoint: RenderOrchestrator
success_definition: >
  A coding agent can execute the swarm end-to-end and produce a render package,
  manifest, and verification report without inventing layer rules, field names,
  or fallback behavior.
---

# Swarm Topology

## 1) RenderOrchestrator
**Role:** Owns the run, receives request, sets mode, assigns work, merges outputs.

**Inputs**
- `analysis_request`
- `viewport_context`
- `terrain_profile_override`

**Responsibilities**
- resolve requested output products
- select default terrain profile if no override exists
- enforce hard-stop rules before downstream agents proceed
- consolidate manifest and final package

**Never do**
- invent geospatial transforms
- rewrite downstream verification results
- silently suppress warnings

---

## 2) TerrainProfileAgent
**Role:** Determines terrain profile and terrain-specific rendering parameters.

**Inputs**
- DEM metadata
- viewport bounds
- AO waterline intersection result
- delta-Z analysis
- optional override

**Outputs**
- `terrain_profile`
- `terrain_profile_params`
- `terrain_profile_warnings`

**Logic**
- choose `nyc_littoral_low_relief` for NYC harbor/low-relief coastal contexts
- choose `alpine_high_delta_z` when viewport delta-Z exceeds profile threshold
- choose `urban_canyon_lidar` when DSM contamination risk is high
- otherwise choose `standard_regional`

---

## 3) DatumNormalizationAgent
**Role:** Harmonizes vertical references and source metadata.

**Inputs**
- topo DEM
- bathy DEM
- vertical datum metadata

**Outputs**
- unified vertical reference
- merge status
- datum conversion log

**Hard rules**
- do not merge topo and bathy without explicit datum normalization
- do not claim NAVD88 if source is unknown
- emit blocking error for invalid water-crossing profile with no bathy source

---

## 4) TerrainInterpretationAgent
**Role:** Computes terrain derivatives for rendering and analysis.

**Inputs**
- normalized DEM
- terrain profile params
- analysis_request

**Outputs**
- hillshade substrate
- slope raster
- contours or hachure vectors
- z-exaggeration decision log

**Subtasks**
- compute hillshade at profile-specific sun altitude
- compute slope bands and contour interval
- flag rooftop/building contamination in LOS-sensitive modes

---

## 5) TelemetryStateAgent
**Role:** Converts feed freshness and provenance into overlay-ready tactical states.

**Inputs**
- telemetry_tracks
- sensor_feed_registry

**Outputs**
- feed age buckets
- provenance classes
- uncertainty wash tiers
- scan-line eligibility map

**Hard rules**
- unknown timestamp can never become CURRENT or RECENT
- live scan lines only apply to active ingest surfaces
- synthetic/interpolated data must increase grain, not reduce it

---

## 6) ThreatOverlayAgent
**Role:** Compiles denied, contested, or blackout geometry overlays.

**Inputs**
- threat_geometry
- viewport_context

**Outputs**
- vector overlays
- crosshatch pattern assignments
- clipping masks

**Hard rules**
- denied zones must remain readable above terrain substrate
- no low-contrast alternatives
- no blur or feathering that weakens boundary readability

---

## 7) LOSFresnelAgent
**Role:** Produces analytical profile outputs for LOS and Fresnel checks.

**Inputs**
- normalized DEM
- observer/target geometry
- requested frequency class
- bathy merge result

**Outputs**
- elevation transect samples
- LOS clear/masked result
- first Fresnel clearance result
- profile annotations

**Hard rules**
- require observer and target height references
- emit explicit uncertainty if DSM contamination was not removed
- declare frequency class used in all Fresnel results

---

## 8) LayerCompilationAgent
**Role:** Builds the canonical layer stack and applies device budget degradation.

**Inputs**
- terrain derivatives
- overlay states
- viewport_context
- terrain_profile_params

**Outputs**
- ordered layer stack
- active/suppressed layer lists
- style tokens / pattern assets / shader inputs

**Hard rules**
- canonical layer order is mandatory
- field tablet max = 3 simultaneous textures
- degraded edge device keeps hillshade + 1 operational overlay only
- reduced-fidelity outputs must still preserve semantic meaning

---

## 9) VerificationAgent
**Role:** Converts doctrine into pass/fail checks.

**Inputs**
- layer stack
- manifest draft
- terrain profile params
- LOS/Fresnel outputs

**Outputs**
- `verification_report.md`
- check results array
- blocking errors list

**Checks**
- layer compositing audit
- palette compliance
- terrain profile compliance
- timestamp provenance handling
- LOS geometry validation
- Fresnel equation validation
- mobile texture budget check

---

## 10) PackagingAgent
**Role:** Writes the final reproducible package.

**Outputs**
- `/layers/*`
- `/patterns/*`
- `/shaders/*`
- `/profiles/*`
- `/render_state_manifest.json`
- `/verification_report.md`
- final zip bundle

**Hard rules**
- package must be reproducible from logged manifest values
- all suppressed layers must include a reason
- all warnings must survive packaging unchanged

# Coordination Protocol
1. Orchestrator validates request shape.
2. TerrainProfileAgent chooses profile.
3. DatumNormalizationAgent resolves elevation frame.
4. TerrainInterpretationAgent computes terrain derivatives.
5. TelemetryStateAgent computes feed freshness and provenance overlays.
6. ThreatOverlayAgent compiles denied geometry overlays.
7. LOSFresnelAgent computes analytical profile outputs if requested.

> **Note:** Steps 5, 6, and 7 have no inter-dependencies and may run concurrently after step 4 completes.

8. LayerCompilationAgent assembles layers and applies degradation rules.
9. VerificationAgent runs pass/fail checks.
10. PackagingAgent emits the reproducible deliverable.

# Error Propagation

- **Blocking errors** from any agent must be surfaced to RenderOrchestrator immediately. The Orchestrator halts all downstream agents that depend on the failed agent's output.
- **Non-blocking warnings** are accumulated into the manifest draft and the pipeline continues. Each warning must survive all the way to the final package unchanged.
- **PackagingAgent** must include all accumulated warnings regardless of overall status. A `blocked` output is still a valid package — it must contain a manifest and verification report explaining the block.
- **Orchestrator** must never swallow a blocking error by retrying silently or defaulting to a degraded state. Fail loud; let the caller decide how to handle it.

# Shared State Contract
All agents read/write only via the shared schema in `common-schema.yaml`.
No agent may introduce new top-level keys ad hoc.

# Escalation Conditions
- Missing vertical datum on water-crossing requests
- Unknown timestamps on safety-relevant displays
- Device budget unable to preserve mandatory semantics
- DSM contamination unresolved in LOS/Fresnel mode
- Missing frequency class for Fresnel request

# Default Execution Mode
- prefer 2D + profile outputs over optional 3D
- preserve semantic overlays before visual richness
- fail loud rather than produce ambiguous trust signals
