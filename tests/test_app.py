from fastapi.testclient import TestClient

from app import app


SAMPLES = [
    {
        "gender": "Female", "age": 25, "hypertension": 0,
        "heart_disease": 0, "smoking_history": "never", "bmi": 21.5,
        "HbA1c_level": 4.8, "blood_glucose_level": 90,
    },
    {
        "gender": "Male", "age": 55, "hypertension": 1,
        "heart_disease": 0, "smoking_history": "former", "bmi": 31.2,
        "HbA1c_level": 6.8, "blood_glucose_level": 180,
    },
    {
        "gender": "Female", "age": 70, "hypertension": 1,
        "heart_disease": 1, "smoking_history": "never", "bmi": 35.0,
        "HbA1c_level": 8.0, "blood_glucose_level": 240,
    },
]


def test_home_and_health():
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/health").json() == {"status": "ok", "model_loaded": True}


def test_three_predictions():
    with TestClient(app) as client:
        predictions = [client.post("/predict", json=sample) for sample in SAMPLES]
    assert all(response.status_code == 200 for response in predictions)
    assert all(response.json()["prediction"] in (0, 1) for response in predictions)


def test_invalid_payload_is_rejected():
    with TestClient(app) as client:
        response = client.post("/predict", json={**SAMPLES[0], "age": -1})
    assert response.status_code == 422
