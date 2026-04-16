"""
Build an interactive parcel-level map for Toms River using parcel geometry
and MOD-IV property assessment data.

This script reads parcel boundaries and property assessment records from an
Ocean County geodatabase, filters both datasets to Toms River Township,
joins parcel geometry with selected tax and sales attributes, cleans key
numeric fields, and exports an interactive Folium map.

Primary use case:
    Create a local parcel map that can support housing-cost analysis,
    affordability workflows, and future joins to insurance or census-based
    datasets.

Output:
    toms_river_tax_sales_map.html
"""

from pathlib import Path
import json
import geopandas as gpd
import pandas as pd
import folium
from dash import Dash, html
import dash_leaflet as dl
from pyogrio import read_dataframe

# Path to the local geodatabase containing Ocean County parcel and MOD-IV data.
gdb = Path(r"C:\Users\mgrossman\Desktop\mls\oc_parc_msdata\340290000_parcels_v2024_rd.gdb")

# Read parcel geometry for Toms River Township only.
# Keep a focused set of parcel identifiers and address-related fields needed
# for mapping and downstream joins.
parcels_tr = read_dataframe(
    gdb,
    layer="parcels_2024",
    where="MUNICIPALITY = 'TOMS RIVER TWP'",
    columns=["PAMS_PIN", "MUNICIPALITY", "HNUM", "HADD", "BLOCK", "LOT", "QCODE"]
)

print(parcels_tr.shape)
print(parcels_tr.head())

# Read MOD-IV assessment records from the same geodatabase.
# This table contains tax, sales, and building-related attributes but does
# not need parcel geometry, so read_geometry=False keeps it as a regular table.
modiv_tr = read_dataframe(
    gdb,
    layer="m4_2024",
    columns=[
        "CtyDstNo", "PAMS_PIN", "ParcelAddress", "Owner", "PropertyClass",
        "LandVal", "ImpVal", "NetTaxVal",
        "SalesDate", "SalesPrice", "BuildingSqft"
    ],
    read_geometry=False
)

# Filter MOD-IV records to Toms River Township using county/district code.
modiv_tr = modiv_tr[modiv_tr["CtyDstNo"] == "1508"].copy()

print(modiv_tr.shape)
print(modiv_tr.head())

# Convert tax and sales-related fields to numeric values so they can be used
# reliably in mapping, summary statistics, and later analysis steps.
for col in ["LandVal", "ImpVal", "NetTaxVal", "SalesPrice", "BuildingSqft"]:
    modiv_tr[col] = pd.to_numeric(modiv_tr[col], errors="coerce")

# Join parcel geometry to MOD-IV attributes using the parcel identifier.
# The resulting GeoDataFrame becomes the main dataset used for mapping.
gdf = parcels_tr.merge(modiv_tr, on="PAMS_PIN", how="left")

print(gdf.shape)
print(gdf[["PAMS_PIN", "LandVal", "ImpVal", "NetTaxVal", "SalesPrice"]].head())

# Create a cleaner display address by combining house number and street name.
gdf["Address"] = (
    gdf["HNUM"].fillna("").astype(str).str.strip() + " " +
    gdf["HADD"].fillna("").astype(str).str.strip()
).str.strip()

# Reproject parcel geometry to WGS84 latitude/longitude for web mapping.
gdf = gdf.to_crs(4326)

print(gdf.crs)
print(gdf[["PAMS_PIN", "Address", "NetTaxVal", "SalesPrice"]].head())

# Build an interactive Folium map centered on Toms River.
m = folium.Map(location=[39.97, -74.20], zoom_start=12)

# Add parcel polygons with a hover tooltip showing parcel ID, address,
# net tax value, and sale price.
folium.GeoJson(
    gdf[["PAMS_PIN", "Address", "NetTaxVal", "SalesPrice", "geometry"]],
    tooltip=folium.GeoJsonTooltip(
        fields=["PAMS_PIN", "Address", "NetTaxVal", "SalesPrice"],
        aliases=["PIN", "Address", "Net Tax Value", "Sales Price"]
    )
).add_to(m)

# Save the finished map as a standalone HTML file for local viewing or sharing.
m.save("toms_river_tax_sales_map.html")
print("saved folium map")