# Project Log

This file records technical progress, key decisions, debugging notes, and next steps for the Toms River housing affordability project.

---

## 2026-04-18

### Completed today
- Built an interactive parcel-level map for Toms River using parcel geometry and MOD-IV assessment data.
- Built a FEMA flood-zone map clipped to the Toms River study area.
- Downloaded DEM elevation raster tiles from USGS.
- Merged DEM tiles into a single raster.
- Clipped the DEM to the local study area.
- Visualized the DEM successfully.
- Built a parcel-flood-elevation workflow linking:
  - parcel geometry
  - FEMA flood zones
  - DEM-derived parcel elevation statistics
- Exported a working Folium map showing flood-intersecting parcels and flood zones.

### Key technical issues solved
- Parcel elevation values initially returned null.
- Cause: CRS mismatch between parcel geometry and DEM raster.
- Parcel CRS: `EPSG:3424`
- DEM CRS: `EPSG:26918`
- Fix: reproject parcel geometry to the DEM CRS before running zonal statistics.

### Outputs created
- Parcel map
- Flood-zone map
- Merged DEM raster
- Clipped DEM raster
- Parcel-flood-elevation CSV
- Parcel-flood-elevation GeoPackage
- Parcel-flood-elevation Folium HTML map

### What I learned
- A DEM is a raster where each cell stores elevation.
- Parcel polygons, flood polygons, and DEM rasters require different handling.
- Flood-intersecting parcels can be identified with a spatial join.
- Parcel elevation can be estimated using zonal statistics such as minimum, mean, and maximum elevation.
- CRS alignment is essential before combining vector and raster data.

### Immediate next steps
- Inspect parcel-level flood/elevation outputs manually.
- Decide which parcel elevation statistic is most appropriate for flood premium estimation.
- Compare parcel elevation to FEMA base flood elevation where available.
- Begin building a simple framework for parcel-level flood premium estimation.
- Continue improving project documentation and repo structure.

---

## Notes to self
This file should stay chronological and factual.
It is a technical work log, not a polished narrative.
