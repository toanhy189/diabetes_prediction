"""Inspect the trained pipeline without modifying or retraining it."""

from pathlib import Path

import joblib


MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "diabetes_prediction_pipeline.pkl"


pipeline = joblib.load(MODEL_PATH)
print(f"Pipeline type: {type(pipeline).__name__}")
print(f"Steps: {list(pipeline.named_steps)}")
print(f"Features: {list(pipeline.feature_names_in_)}")

preprocessor = pipeline.named_steps["preprocessing"]
encoder = preprocessor.named_transformers_["cat"]
categorical_columns = preprocessor.transformers_[1][2]
for column, categories in zip(categorical_columns, encoder.categories_):
    print(f"{column}: {list(categories)}")

print(f"Final model: {type(pipeline.named_steps['model']).__name__}")
