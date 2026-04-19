# Glossary

Domain terms used throughout the SIGINT Terrain Bundle. Read this first if you bounce off the spec.

## Core domain

- **SIGINT** — *Signals Intelligence.* Intelligence derived from electronic signals (communications, radar, telemetry).
- **C4ISR** — Command, Control, Communications, Computers, Intelligence, Surveillance, Reconnaissance. The umbrella the renderer serves.
- **AO** — *Area of Operations.* The geographic region a request covers.
- **Operator** — The end user of the rendered output: an analyst, a field operator, or an edge-device user.
- **Tactical** — Applied to live or near-live operational decisions, as opposed to strategic (long-horizon) or archival.

## Terrain & elevation

- **DEM** — *Digital Elevation Model.* Raster grid of elevation values.
- **Bare-earth DEM** — DEM with vegetation and structures removed; represents the ground surface only.
- **DSM** — *Digital Surface Model.* DEM that includes buildings, vegetation, and other surface features. Causes false LOS blocking if used naïvely in line-of-sight analysis.
- **LiDAR** — *Light Detection and Ranging.* Laser-based remote sensing producing high-resolution point clouds; primary input for high-fidelity DEMs.
- **Hillshade** — Synthetic shaded-relief raster computed from a DEM by simulating sun illumination. Configured by sun **azimuth** and **altitude**.
- **Hachure** — Short parallel strokes whose density encodes slope steepness. Pre-photographic cartographic convention; still operationally useful.
- **Hypsometric** — Color-by-elevation. The doctrine permits a tactical hypso palette but **prohibits** rainbow hypsometric ramps.
- **z-exaggeration** — Vertical scale multiplier used in 3D terrain rendering to make low-relief terrain readable. Must be declared and clamped per terrain profile.
- **Bathymetry** — Below-water depth/terrain data. Required when a transect crosses water.
- **NAVD88** — *North American Vertical Datum of 1988.* Preferred topographic vertical reference for the bundle.
- **MLLW** — *Mean Lower Low Water.* Common bathymetric vertical reference in U.S. waters; must be normalized to NAVD88 before merging with topographic DEM.
- **EGM96 / EGM2008** — *Earth Gravitational Model.* Geoid models used for global vertical reference conversions.
- **Datum** — The reference surface against which elevations are measured. Mismatched datums silently corrupt elevation profiles.

## Geometry & analysis

- **LOS** — *Line of Sight.* A geometric check between an observer and a target across terrain. Either `LOS_CLEAR` (terrain does not block) or `LOS_MASKED` (terrain blocks).
- **Fresnel zone** — RF propagation concept: the elliptical 3D volume around the direct path between transmitter and receiver. The **first** Fresnel zone must be ≥60% clear of obstructions for reliable signal. Zone radius depends on frequency and path length.
- **Frequency class** — VHF, UHF, L_BAND, S_BAND, C_BAND, X_BAND. Required for any Fresnel calculation; determines zone radius.
- **AGL** — *Above Ground Level.* Height of an observer/target above the local terrain (vs. above sea level).
- **Transect** — A linear sampling path across terrain. The basis for elevation profile and LOS computation.
- **Elevation profile** — The 2D side-view of terrain elevation along a transect.

## Sensor & telemetry

- **EOIR** — *Electro-Optical / Infrared.* Sensor modality combining visible-light and thermal imaging.
- **Provenance** — The origin and confidence class of a data source. Encoded visually as **stipple grain**.
- **Live / cached / replayed / synthetic** — Sensor feed states. Only `live` qualifies for scan-line overlay; others are explicitly suppressed.

## Doctrine vocabulary

- **Texture is meaning** — The bundle's first invariant. Visual textures (stipple, hachure, crosshatch, wash) are **operational encodings**, never decoration.
- **Compositing is law** — The 7-layer canonical order is fixed. Reordering is a doctrine violation.
- **Degradation must be visible** — Performance fallback is permitted; silent semantic loss is not. Every suppressed layer must carry a `reason`.
- **Hard stop** — A condition that must block output rather than degrade. Example: missing timestamp on a safety-relevant LOS request.

## Verification & schema

- **Manifest** — `render_state_manifest.json`. The authoritative record of what was rendered, what was suppressed, and why.
- **Verification report** — `verification_report.md` / `.json`. Pass/fail checks against doctrine.
- **CoVe** — *Chain of Verification.* Claim/evidence pairs in `SKILL.md` that downstream tests must satisfy.
- **Conformance fixture** — A canonical input + expected output pair. A renderer is conformant only if it reproduces every fixture's expected output.

## Devices

- **Desktop analyst** — Fixed workstation. Full GPU budget. May render the complete 7-layer stack plus optional 3D.
- **Field tablet** — Constrained but modern field display. Max 3 simultaneous textures. Subject to the degradation ladder.
- **Degraded edge device** — Low-capability or compromised graphics support. Hillshade plus one operational overlay only. Always emits a degraded-state badge.
