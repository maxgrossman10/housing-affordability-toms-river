# %%
# Libraries
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer


# Load raw FEMA data
df = pd.read_csv("C:/Users/maxgr/OneDrive/Desktop/housing_analysis/toms_river_nj_fema_policies_2025.csv")


# Create two new columns
df["elevation_diff_calc"] = df["lowestFloorElevation"] - df["baseFloodElevation"]
df["is_below_bfe"] = (df["elevation_diff_calc"] < 0).astype(int)


# Our prediction target
target = "totalInsurancePremiumOfThePolicy"


# Numerical features from FEMA dataset
numeric_features = [
    "elevationDifference",
    "lowestFloorElevation",
    "baseFloodElevation",
    "elevation_diff_calc",
    "is_below_bfe",
    "buildingReplacementCost",
    "totalBuildingInsuranceCoverage"
]


# Categorical features from FEMA dataset
categorical_features = [
    "floodZoneCurrent",
    "ratedFloodZone",
    "census_tract",
    "nfipCommunityNumberCurrent",
    "reportedZipCode"
]


# Remove rows with missing target values
df = df.dropna(subset=[target])


# Create predictor matrix
X = df[numeric_features + categorical_features]


# Create target vector
y = df[target]


# Check predictor and target shapes
print(X.shape)
print(y.shape)


# Split into training/testing data sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
