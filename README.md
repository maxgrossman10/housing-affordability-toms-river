# Housing Affordability in Toms River, NJ

![Project screenshot](images/git_parc_fl_elev_pic.png)

This repository documents an in-progress geospatial analysis project focused on housing affordability in Toms River, New Jersey.

The goal is to estimate how much income remains after the full cost of homeownership is considered - not just mortgage payments, but also property taxes, flood-related risk, insurance, utilities, and other location-sensitive housing costs. The project is being built at the parcel level so that affordability can be studied spatially rather than only through townwide or countywide averages.

At its current stage, the repository contains the early mapping and data-integration work needed to support that larger affordability model.


## What the project does right now
- loads parcel geometry for Toms River Township
- joins selected MOD-IV tax and property assessment attributes
- clips FEMA flood-hazard polygons to the study area
- downloads, merges, and clips DEM elevation raster data
- identifies parcels located in mapped flood-hazard zones
- calculates parcel-level elevation statistics from the DEM
- exports an interactive Folium map for visual inspection and downstream analysis

## Why this project exists

Housing affordability is often discussed in terms of sale prices or mortgage payments alone. That misses a major part of the real burden on households, especially in coastal communities like Toms River where flood exposure, insurance costs, taxes, utilities, and parcel-level variation matter.

This project is an attempt to build a more realistic affordability framework by combining geospatial, tax, hazard, insurance-related, and household-cost data into one workflow.


## Tech stack

- Python
- Pandas
- GeoPandas
- Folium
- FEMA / public hazard data
- Parcel and tax assessment data
- Planned machine learning workflows for insurance-cost estimation

## Project direction

The longer-term objective is to build a parcel-level affordability model that can answer questions such as:

- How much income remains after major housing costs are paid?
- How does affordability vary across neighborhoods and flood zones?
- Where do taxes, insurance, and utilities materially change the affordability picture?
- How different is the affordability story when flood risk is included?


## Next steps

- Add elevation and terrain data for parcel-level flood-risk context
- Join parcel and hazard layers to insurance datasets
- Add utility-cost assumptions or utility-related data inputs
- Build a PostgreSQL-backed spatial data pipeline
- Estimate flood-insurance costs where direct premium data is missing
- Add census tract and block group context
- Develop an interactive Dash dashboard for exploration and comparison


## Status
This project is under active development. The current code should be understood as the spatial and data-engineering foundation for a larger affordability and risk-analysis workflow, not a finished dashboard or finished model.


## Repository Structure

```text 
housing-affordability-toms-river/
├── README.md
├── field-notes/
│   ├── project-log.md
│   ├── data-sources.md
│   └── methodology.md
├── images/
│   └── tr_pic.png
├── src/
│   ├── tr_parcel_map.py
│   ├── tr_flood_map.py
│   └── tr_parcels_flood_elev.py
└── outputs/

