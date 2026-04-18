"""
Download FEMA NFIP policy records for Toms River-area ZIP codes in New Jersey.

This script queries FEMA's open NFIP policy API and retrieves policy-level
records for a set of target ZIP codes associated with Toms River and nearby
areas. It filters the data to policies effective during calendar year 2025,
keeps selected location, flood-risk, coverage, and policy-cost fields, and
exports the results to a CSV file for downstream geospatial analysis and
insurance risk modeling.

Primary use case:
    Build a local dataset that can be joined to other housing, parcel,
    and census-tract data for affordability and insurance analysis.

Output:
    toms_river_nj_fema_policies_2025.csv
"""

import requests
import pandas as pd
import time

# FEMA open data endpoint for NFIP policy records.
BASE_URL = "https://www.fema.gov/api/open/v2/FimaNfipPolicies"

# Number of rows to request per API call.
# The script paginates through the full result set using $skip.
PAGE_SIZE = 1000

# Columns selected from the API response.
# These fields focus on geography, flood-zone context, policy dates,
# premium/cost measures, coverage amounts, and elevation-related variables.
select_cols = [
    "id",
    "propertyState",
    "reportedCity",
    "reportedZipCode",
    "countyCode",
    "censusTract",
    "censusBlockGroupFips",
    "latitude",
    "longitude",
    "nfipCommunityName",
    "nfipCommunityNumberCurrent",
    "floodZoneCurrent",
    "ratedFloodZone",
    "policyEffectiveDate",
    "policyTerminationDate",
    "policyCost",
    "totalInsurancePremiumOfThePolicy",
    "totalBuildingInsuranceCoverage",
    "totalContentsInsuranceCoverage",
    "buildingReplacementCost",
    "occupancyType",
    "construction",
    "primaryResidenceIndicator",
    "postFIRMConstructionIndicator",
    "elevationDifference",
    "lowestFloorElevation",
    "baseFloodElevation",
]

# OData filter used by FEMA's API.
# This restricts the dataset to:
# - New Jersey properties
# - target ZIP codes in and around Toms River
# - policies effective during 2025
filter_str = (
    "propertyState eq 'NJ' and "
    "("
    "reportedZipCode eq '08753' or "
    "reportedZipCode eq '08754' or "
    "reportedZipCode eq '08755' or "
    "reportedZipCode eq '08756' or "
    "reportedZipCode eq '08757'"
    ") and "
    "policyEffectiveDate ge '2025-01-01' and "
    "policyEffectiveDate lt '2026-01-01'"
)

# Store paginated results here before combining them into one DataFrame.
all_rows = []

# FEMA pagination offset. Starts at 0 and increases by PAGE_SIZE.
skip = 0

# Request pages until the API returns no more results.
while True:
    url = (
        f"{BASE_URL}"
        f"?$filter={filter_str}"
        f"&$select={','.join(select_cols)}"
        f"&$top={PAGE_SIZE}"
        f"&$skip={skip}"
    )

    # Request one page of policy records from the API.
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    # Parse the JSON payload and extract the list of returned records.
    data = resp.json()
    rows = data.get("FimaNfipPolicies", [])

    # Stop when the API returns an empty page.
    if not rows:
        break

    # Add the current page of results to the full collection.
    all_rows.extend(rows)

    # If fewer rows than PAGE_SIZE are returned, this is the final page.
    if len(rows) < PAGE_SIZE:
        break

    # Advance to the next page and pause briefly to avoid hammering the API.
    skip += PAGE_SIZE
    time.sleep(0.5)

# Convert the collected records into a tabular dataset.
df = pd.DataFrame(all_rows)

# Export the cleaned result set for downstream analysis and dashboard joins.
df.to_csv("toms_river_nj_fema_policies_2025.csv", index=False)

print("CSV exported.")
