# Housing Affordability Toms River

This repository contains a geospatial dashboard for Toms River, NJ that estimates remaining spendable income after housing costs. It combines parcel, tax, flood insurance, and housing data to support tract-level risk analysis using Python, PostgreSQL, Dash, Folium, and machine learning.

## Tools & Stack

- Python
- PostgreSQL
- Pandas
- GeoPandas
- Plotly / Dash
- Folium
- FEMA NFIP API
- Public housing and parcel datasets
- Machine learning for insurance risk estimation

## Repository Structure

- `fema_ins.py`  
  Pulls FEMA NFIP policy records for Toms River-area ZIP codes in New Jersey and exports a CSV for downstream insurance and affordability analysis.

- `plotly_app.py`  
  Loads Toms River parcel geometry and MOD-IV assessment data, joins parcel tax and sales attributes, and exports an interactive Folium parcel map.

- `home_ins.py`  
  Pulls Treasury/FIO homeowners insurance metrics for selected Toms River ZIP codes and prepares a cleaned CSV for analysis.

- `mls.py`  
  Initial database setup and testing script for local data storage workflows.

## Project Goals

- Estimate remaining spendable income after total housing costs
- Integrate parcel, tax, and insurance-related data into one workflow
- Support tract-level insurance risk analysis for Toms River
- Build interactive geospatial tools for local housing analysis

## Planned Next Steps

- Connect cleaned data sources to PostgreSQL
- Build a full interactive Dash dashboard
- Add census tract and block group joins
- Develop machine learning models for insurance-related cost estimation
- Improve documentation and project organization

## Notes

This project is under active development. File names, workflow design, and model structure will evolve as the data pipeline and dashboard are refined.
