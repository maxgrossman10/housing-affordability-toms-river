"""
Create an interactive FEMA flood-hazard map for Toms River, New Jersey.

This script reads parcel geometry for Toms River Township from the Ocean County
parcel geodatabase, dissolves those parcels into a single township-wide mask,
and uses that mask to clip FEMA flood-hazard polygons to the local study area.
It then filters the clipped FEMA layer to mapped flood-hazard zones, reprojects
the result to WGS84 for web display, and exports an interactive Folium map.

The final map displays flood-hazard polygons only. Parcel geometry is used
strictly to define the Toms River analysis footprint and is not plotted.

Output:
    toms_river_flood_zones_clipped_map.html
"""

from pathlib import Path

import folium
import geopandas as gpd
from pyogrio import read_dataframe


# Source data paths
parcel_gdb = Path(
    r"C:\Users\mgrossman\Desktop\mls\oc_parc_msdata\340290000_parcels_v2024_rd.gdb"
)
flood_shp = Path(
    r"C:\Users\mgrossman\Desktop\mls\oc_fema_flooddata\S_FLD_HAZ_AR.shp"
)


# Read parcel geometry for Toms River Township.
# These polygons are used only to define the township footprint for clipping.
parcels_tr = read_dataframe(
    parcel_gdb,
    layer="parcels_2024",
    where="MUNICIPALITY = 'TOMS RIVER TWP'",
    columns=["PAMS_PIN", "MUNICIPALITY"],
)

print("Toms River parcels:", parcels_tr.shape)
print("Parcel CRS:", parcels_tr.crs)


# Dissolve parcel polygons into a single geometry representing the township mask.
toms_river_mask = parcels_tr.dissolve()
print("Mask shape:", toms_river_mask.shape)


# Read FEMA flood-hazard polygons and retain only the attributes needed for
# styling, inspection, and tooltip display.
flood_zones = gpd.read_file(flood_shp)
flood_zones = flood_zones[
    ["FLD_ZONE", "ZONE_SUBTY", "SFHA_TF", "STATIC_BFE", "geometry"]
].copy()

print("Flood zones:", flood_zones.shape)
print("Flood CRS:", flood_zones.crs)


# Reproject the FEMA layer to the parcel CRS before performing the clip.
if flood_zones.crs != toms_river_mask.crs:
    flood_zones = flood_zones.to_crs(toms_river_mask.crs)


# Clip the FEMA flood layer to the Toms River footprint.
flood_tr = gpd.clip(flood_zones, toms_river_mask)

print("Clipped flood zones:", flood_tr.shape)
print(flood_tr["FLD_ZONE"].value_counts(dropna=False).head(20))


# Retain only mapped flood-hazard zones for display.
# Lower-risk and non-hazard categories such as X, B, C, or blanks are excluded.
hazard_zones = {"A", "AE", "AH", "AO", "A99", "AR", "V", "VE", "D"}

flood_tr = flood_tr[
    flood_tr["FLD_ZONE"].fillna("").str.upper().isin(hazard_zones)
].copy()

print("Mapped hazard zones only:", flood_tr.shape)
print(flood_tr["FLD_ZONE"].value_counts(dropna=False).head(20))


# Reproject to WGS84 latitude/longitude for Folium web mapping.
flood_tr = flood_tr.to_crs(4326)


def flood_style(feature):
    """
    Return a Folium style dictionary based on FEMA flood-zone classification.

    Coastal high-hazard zones (V/VE) are styled in purple, inland SFHA zones
    (A-family) in brown, and Zone D in orange. Any unexpected category is
    rendered invisible.
    """
    props = feature["properties"]
    zone = str(props.get("FLD_ZONE", "")).strip().upper()

    if zone in {"V", "VE"}:
        return {
            "fillColor": "#7a3b8f",
            "color": "#7a3b8f",
            "weight": 1.2,
            "fillOpacity": 0.35,
        }

    if zone in {"A", "AE", "AH", "AO", "A99", "AR"}:
        return {
            "fillColor": "#8c6d1f",
            "color": "#8c6d1f",
            "weight": 1.0,
            "fillOpacity": 0.35,
        }

    if zone == "D":
        return {
            "fillColor": "#cc4c02",
            "color": "#cc4c02",
            "weight": 1.0,
            "fillOpacity": 0.25,
        }

    return {
        "fillOpacity": 0.0,
        "opacity": 0.0,
        "weight": 0,
    }


# Build the map using imagery as the base layer to improve visual comparison
# with FEMA’s web map styling.
m = folium.Map(
    location=[39.97, -74.20],
    zoom_start=12,
    tiles=None,
)

folium.TileLayer(
    tiles="Esri.WorldImagery",
    name="Imagery",
    attr="Esri",
).add_to(m)


# Add the clipped FEMA flood-hazard layer.
folium.GeoJson(
    flood_tr,
    name="Toms River FEMA Flood Zones",
    style_function=flood_style,
    tooltip=folium.GeoJsonTooltip(
        fields=["FLD_ZONE", "ZONE_SUBTY", "SFHA_TF", "STATIC_BFE"],
        aliases=["Flood Zone", "Zone Subtype", "SFHA", "Base Flood Elevation"],
        localize=True,
    ),
).add_to(m)

folium.LayerControl().add_to(m)


# Export the finished map as a standalone HTML file.
output_file = "toms_river_flood_zones_clipped_map.html"
m.save(output_file)

print(f"Saved clipped flood map to {output_file}")