# %%
# Libraries
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.ensemble import RandomForestRegressor


# Load raw FEMA data
df = pd.read_csv(
    "C:/Users/maxgr/OneDrive/Desktop/housing_analysis/toms_river_nj_fema_policies_2025.csv"
)


# Create two new columns
df["elevation_diff_calc"] = df["lowestFloorElevation"] - df["baseFloodElevation"]

# Keep missing elevation differences as missing.
# Without this, NaN < 0 becomes False, which incorrectly turns missing values into 0.
df["is_below_bfe"] = (df["elevation_diff_calc"] < 0).astype(float)
df.loc[df["elevation_diff_calc"].isna(), "is_below_bfe"] = np.nan


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
    "totalBuildingInsuranceCoverage",
]


# Categorical features from FEMA dataset
categorical_features = [
    "floodZoneCurrent",
    "ratedFloodZone",
    "census_tract",
    "nfipCommunityNumberCurrent",
    "reportedZipCode",
]


# Remove rows with missing target values
df = df.dropna(subset=[target])


# Check missing numeric predictor values
print("Missing values in numeric features:")
print(df[numeric_features].isna().sum())


# Create predictor matrix
X = df[numeric_features + categorical_features]


# Create target vector
y = df[target]


# Split into training/testing data sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
)


# ------------------------------------------------------------
# Shared categorical preprocessing
# ------------------------------------------------------------

categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ]
)


# ------------------------------------------------------------
# Median-imputation version
# ------------------------------------------------------------

numeric_transformer_median = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
    ]
)


preprocessor_median = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer_median, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)


rf_model_median = Pipeline(
    steps=[
        ("preprocessor", preprocessor_median),
        (
            "model",
            RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)


# ------------------------------------------------------------
# KNN-imputation version
# ------------------------------------------------------------

numeric_transformer_knn = Pipeline(
    steps=[
        ("scaler", StandardScaler()),
        ("imputer", KNNImputer(n_neighbors=5, weights="distance")),
    ]
)


preprocessor_knn = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer_knn, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)


rf_model_knn = Pipeline(
    steps=[
        ("preprocessor", preprocessor_knn),
        (
            "model",
            RandomForestRegressor(
                n_estimators=300,
                random_state=42,
                n_jobs=-1,
            ),
        ),
    ]
)


# ------------------------------------------------------------
# Function to train and evaluate a model
# ------------------------------------------------------------


def evaluate_model(model_name, model, X_train, X_test, y_train, y_test):
    # Train model
    model.fit(X_train, y_train)

    # Predict test set premiums
    y_pred = model.predict(X_test)

    # Calculate error metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5

    # Store actual vs predicted results
    results = pd.DataFrame(
        {
            "actual_premium": y_test,
            "predicted_premium": y_pred,
        }
    )

    results["error"] = results["predicted_premium"] - results["actual_premium"]
    results["absolute_error"] = results["error"].abs()

    return {
        "model_name": model_name,
        "mae": mae,
        "rmse": rmse,
        "mae_as_pct_of_mean": mae / y.mean(),
        "mae_as_pct_of_median": mae / y.median(),
        "results": results,
    }


# ------------------------------------------------------------
# Evaluate both models side by side
# ------------------------------------------------------------

median_eval = evaluate_model(
    "Random Forest with Median Imputer",
    rf_model_median,
    X_train,
    X_test,
    y_train,
    y_test,
)

knn_eval = evaluate_model(
    "Random Forest with KNN Imputer",
    rf_model_knn,
    X_train,
    X_test,
    y_train,
    y_test,
)


# ------------------------------------------------------------
# Compare model scores
# ------------------------------------------------------------

comparison = pd.DataFrame(
    [
        {
            "model": median_eval["model_name"],
            "MAE": median_eval["mae"],
            "RMSE": median_eval["rmse"],
            "MAE_as_pct_of_mean": median_eval["mae_as_pct_of_mean"],
            "MAE_as_pct_of_median": median_eval["mae_as_pct_of_median"],
        },
        {
            "model": knn_eval["model_name"],
            "MAE": knn_eval["mae"],
            "RMSE": knn_eval["rmse"],
            "MAE_as_pct_of_mean": knn_eval["mae_as_pct_of_mean"],
            "MAE_as_pct_of_median": knn_eval["mae_as_pct_of_median"],
        },
    ]
)


print("\nTarget premium summary:")
print(y.describe())


print("\nModel comparison:")
print(comparison[["model", "MAE", "RMSE"]])


# ------------------------------------------------------------
# Pick better model based on MAE
# ------------------------------------------------------------

if knn_eval["mae"] < median_eval["mae"]:
    print("\nKNN imputer performed better based on MAE.")
    best_model = rf_model_knn
    best_results = knn_eval["results"]
else:
    print("\nMedian imputer performed better based on MAE.")
    best_model = rf_model_median
    best_results = median_eval["results"]


# ------------------------------------------------------------
# Show actual vs predicted results for the better model
# ------------------------------------------------------------

print("\nActual vs predicted premiums from best model:")
print(best_results.head(20))
