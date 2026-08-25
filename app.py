from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "diabetes_prediction_pipeline.pkl"
FEATURE_NAMES = [
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "smoking_history",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level",
]


class PredictionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gender: Literal["Female", "Male", "Other"]
    age: float = Field(ge=0, le=120)
    hypertension: Literal[0, 1]
    heart_disease: Literal[0, 1]
    smoking_history: Literal[
        "No Info", "current", "ever", "former", "never", "not current"
    ]
    bmi: float = Field(gt=0, le=100)
    HbA1c_level: float = Field(gt=0, le=20)
    blood_glucose_level: float = Field(gt=0, le=1000)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.is_file():
        raise RuntimeError(
            f"Không tìm thấy model tại {MODEL_PATH}. "
            "Hãy đặt diabetes_prediction_pipeline.pkl vào thư mục model/."
        )

    pipeline = joblib.load(MODEL_PATH)
    actual_features = list(getattr(pipeline, "feature_names_in_", []))
    if actual_features and actual_features != FEATURE_NAMES:
        raise RuntimeError(
            "Feature của pipeline không khớp với ứng dụng: "
            f"{actual_features}"
        )

    app.state.pipeline = pipeline
    yield
    app.state.pipeline = None


app = FastAPI(
    title="Diabetes Prediction",
    description="Ứng dụng dự đoán phục vụ mục đích học tập.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "model_loaded": app.state.pipeline is not None}


@app.post("/predict", tags=["prediction"])
async def predict(payload: PredictionInput):
    try:
        frame = pd.DataFrame(
            [[getattr(payload, feature) for feature in FEATURE_NAMES]],
            columns=FEATURE_NAMES,
        )
        prediction = int(app.state.pipeline.predict(frame)[0])
    except Exception as exc:
        # Log details server-side while keeping the API response safe and friendly.
        print(f"Prediction error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Không thể thực hiện dự đoán lúc này. Vui lòng thử lại.",
        ) from exc

    labels = {
        0: "Không thuộc lớp tiểu đường",
        1: "Thuộc lớp tiểu đường",
    }
    if prediction not in labels:
        raise HTTPException(status_code=500, detail="Model trả về kết quả không hợp lệ.")

    return {"prediction": prediction, "label": labels[prediction]}
