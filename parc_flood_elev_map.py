# %%
# Create parcel/flood map with DEM-derived parcel elevations

from pathlib import Path

import folium
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from pyogrio import read_dataframe
from rasterstats import zonal_stats

# -----------------------------
# paths
# -----------------------------
parcel_gdb = Path(
    r"C:\Users\maxgr\OneDrive\Desktop\housing_analysis\oc_parcel_data\340290000_parcels_v2024_rd.gdb"
)
flood_shp = Path(
    r"C:\Users\maxgr\OneDrive\Desktop\housing_analysis\oc_fema_flooddata\oc_fema_flooddata\S_FLD_HAZ_AR.shp"
)
dem_tif = Path(
    r"C:\Users\maxgr\OneDrive\Desktop\housing_analysis\toms_river_dem_bbox_clip.tif"
)

output_gpkg = Path(
    r"C:\Users\maxgr\OneDrive\Desktop\housing_analysis\toms_river_parcels_flood_elev.gpkg"
)
output_csv = Path(
    r"C:\Users\maxgr\OneDrive\Desktop\housing_analysis\toms_river_parcels_flood_elev.csv"
)
output_html = Path(
    r"C:\Users\maxgr\OneDrive\Desktop\housing_analysis\toms_river_parcels_flood_elev_map.html"
)

# -----------------------------
# 1. load parcels
# -----------------------------
parcels = read_dataframe(
    parcel_gdb,
    layer="parcels_2024",
    where="MUNICIPALITY = 'TOMS RIVER TWP'",
    columns=["PAMS_PIN", "MUNICIPALITY", "HNUM", "HADD", "BLOCK", "LOT", "QCODE"],
).copy()

parcels["Address"] = (
    parcels["HNUM"].fillna("").astype(str).str.strip()
    + " "
    + parcels["HADD"].fillna("").astype(str).str.strip()
).str.strip()

print("Parcels:", parcels.shape)
print("Parcel CRS:", parcels.crs)

# -----------------------------
# 2. load flood zones
# -----------------------------
flood = gpd.read_file(flood_shp)[
    ["FLD_ZONE", "ZONE_SUBTY", "SFHA_TF", "STATIC_BFE", "geometry"]
].copy()

hazard_zones = {"A", "AE", "AH", "AO", "A99", "AR", "V", "VE", "D"}
flood = flood[flood["FLD_ZONE"].fillna("").str.upper().isin(hazard_zones)].copy()

if flood.crs != parcels.crs:
    flood = flood.to_crs(parcels.crs)

print("Flood zones:", flood.shape)
print("Flood CRS:", flood.crs)

# -----------------------------
# 3. spatial join parcels to flood zones
# -----------------------------
parcels_flood = gpd.sjoin(parcels, flood, how="inner", predicate="intersects").copy()

parcels_flood = parcels_flood.drop(columns=["index_right"], errors="ignore")

print("Flood-intersecting parcel rows:", parcels_flood.shape)
print("Unique parcels in flood zones:", parcels_flood["PAMS_PIN"].nunique())

# -----------------------------
# 4. reproject parcels to DEM CRS BEFORE zonal stats
# -----------------------------
with rasterio.open(dem_tif) as src:
    dem_crs = src.crs
    dem_bounds = src.bounds
    dem_nodata = src.nodata

print("DEM CRS:", dem_crs)
print("DEM bounds:", dem_bounds)
print("DEM nodata:", dem_nodata)

parcels_flood_dem = parcels_flood.to_crs(dem_crs).copy()
print("Parcels for zonal stats CRS:", parcels_flood_dem.crs)

# -----------------------------
# 5. zonal statistics on DEM
# -----------------------------
stats = zonal_stats(
    parcels_flood_dem.geometry,
    str(dem_tif),
    stats=["min", "mean", "max"],
    all_touched=True,
    nodata=dem_nodata,
    geojson_out=False,
)

stats_df = pd.DataFrame(stats).rename(
    columns={"min": "elev_min", "mean": "elev_mean", "max": "elev_max"}
)

parcels_flood = parcels_flood.reset_index(drop=True)
stats_df = stats_df.reset_index(drop=True)

parcels_flood[["elev_min", "elev_mean", "elev_max"]] = stats_df[
    ["elev_min", "elev_mean", "elev_max"]
]

print(
    parcels_flood[
        ["PAMS_PIN", "FLD_ZONE", "STATIC_BFE", "elev_min", "elev_mean", "elev_max"]
    ].head()
)

print("Null elevation counts:")
print(parcels_flood[["elev_min", "elev_mean", "elev_max"]].isna().sum())

# -----------------------------
# 6. compute BFE comparison fields
# -----------------------------
parcels_flood["STATIC_BFE"] = pd.to_numeric(
    parcels_flood["STATIC_BFE"], errors="coerce"
)

parcels_flood["bfe_minus_elev_mean"] = (
    parcels_flood["STATIC_BFE"] - parcels_flood["elev_mean"]
)
parcels_flood["bfe_minus_elev_min"] = (
    parcels_flood["STATIC_BFE"] - parcels_flood["elev_min"]
)

# -----------------------------
# 7. save outputs
# -----------------------------
parcels_flood.to_file(output_gpkg, layer="parcels_flood_elev", driver="GPKG")

parcels_flood[
    [
        "PAMS_PIN",
        "Address",
        "BLOCK",
        "LOT",
        "QCODE",
        "FLD_ZONE",
        "ZONE_SUBTY",
        "SFHA_TF",
        "STATIC_BFE",
        "elev_min",
        "elev_mean",
        "elev_max",
        "bfe_minus_elev_mean",
        "bfe_minus_elev_min",
    ]
].to_csv(output_csv, index=False)

print(f"Saved GeoPackage: {output_gpkg}")
print(f"Saved CSV: {output_csv}")

# -----------------------------
# 8. folium map
# -----------------------------
parcels_map = parcels_flood.to_crs(4326)
flood_map = flood.to_crs(4326)


def flood_style(feature):
    zone = str(feature["properties"].get("FLD_ZONE", "")).upper().strip()

    if zone in {"V", "VE"}:
        return {
            "fillColor": "#7a3b8f",
            "color": "#7a3b8f",
            "weight": 1,
            "fillOpacity": 0.30,
        }
    if zone in {"A", "AE", "AH", "AO", "A99", "AR"}:
        return {
            "fillColor": "#8c6d1f",
            "color": "#8c6d1f",
            "weight": 1,
            "fillOpacity": 0.25,
        }
    if zone == "D":
        return {
            "fillColor": "#cc4c02",
            "color": "#cc4c02",
            "weight": 1,
            "fillOpacity": 0.20,
        }
    return {"fillOpacity": 0, "opacity": 0, "weight": 0}


def parcel_style(feature):
    return {
        "fillColor": "#2b8cbe",
        "color": "#08519c",
        "weight": 0.6,
        "fillOpacity": 0.20,
    }


m = folium.Map(location=[39.97, -74.20], zoom_start=12, tiles=None)

folium.TileLayer(
    tiles="Esri.WorldImagery",
    name="Imagery",
    attr="Esri",
).add_to(m)

folium.GeoJson(
    flood_map,
    name="Flood Zones",
    style_function=flood_style,
    tooltip=folium.GeoJsonTooltip(
        fields=["FLD_ZONE", "ZONE_SUBTY", "SFHA_TF", "STATIC_BFE"],
        aliases=["Flood Zone", "Subtype", "SFHA", "Base Flood Elevation"],
    ),
).add_to(m)

folium.GeoJson(
    parcels_map,
    name="Flood-Intersecting Parcels",
    style_function=parcel_style,
    tooltip=folium.GeoJsonTooltip(
        fields=[
            "PAMS_PIN",
            "Address",
            "FLD_ZONE",
            "STATIC_BFE",
            "elev_min",
            "elev_mean",
            "elev_max",
            "bfe_minus_elev_mean",
            "bfe_minus_elev_min",
        ],
        aliases=[
            "PIN",
            "Address",
            "Flood Zone",
            "BFE",
            "Min Elev",
            "Mean Elev",
            "Max Elev",
            "BFE - Mean Elev",
            "BFE - Min Elev",
        ],
        localize=True,
    ),
).add_to(m)

folium.LayerControl().add_to(m)
m.save(output_html)

print(f"Saved map: {output_html}")
