# Methodology

This file describes the current analytical workflow and the assumptions behind it.

---

## Project objective

The long-term objective is to estimate housing affordability more realistically by incorporating parcel-level cost drivers and hazard-related variables.

The current phase is focused on building a defensible parcel-level spatial workflow.

---

## Current workflow

### 1. Load parcel geometry
Parcel boundaries for Toms River Township are read from the Ocean County parcel geodatabase.

### 2. Join MOD-IV property attributes
Selected assessment and sales fields are joined to parcel geometry using `PAMS_PIN`.

### 3. Load and clip FEMA flood-hazard polygons
FEMA flood-zone polygons are loaded and clipped to the Toms River study area.

### 4. Filter to mapped hazard zones
The workflow retains mapped flood-hazard categories such as:
- A
- AE
- AH
- AO
- A99
- AR
- V
- VE
- D

### 5. Build DEM surface for the study area
DEM tiles are downloaded, merged, and clipped to the local study area.

### 6. Identify parcels intersecting flood zones
A spatial join is used to identify parcels that intersect FEMA hazard polygons.

### 7. Compute parcel-level elevation statistics
Zonal statistics are used to compute:
- minimum elevation
- mean elevation
- maximum elevation

### 8. Compare parcel elevation with FEMA base flood elevation
Where FEMA `STATIC_BFE` is available, parcel elevation context can be compared against base flood elevation.

---

## Current assumptions

### Parcel elevation
A parcel does not have one single universally correct elevation value.
For now, this workflow treats parcel elevation as a set of DEM-derived summary statistics.

### Flood premium estimation
This project does not yet claim to produce insurer-grade flood premiums.
At this stage, the workflow is building parcel-level flood and elevation context that may support later estimation work.

### Public data limitations
Public datasets do not contain every variable needed for true policy pricing.
Any later premium estimation model will need to be framed as an approximation.

---

## Known technical issues already solved

### CRS mismatch
During parcel-level zonal statistics, elevation values initially returned null because the parcel geometry CRS did not match the DEM CRS.

Fix:
reproject parcel geometry to the DEM CRS before running zonal statistics.

---

## Next methodological decisions

The next important design questions are:

1. Which parcel elevation statistic should drive flood premium logic:
   - minimum elevation
   - mean elevation
   - maximum elevation

2. How should FEMA base flood elevation be incorporated into risk estimation?

3. What additional variables are required before attempting a parcel-level flood premium estimate?

4. How should uncertainty and assumptions be documented so the project remains analytically honest?
