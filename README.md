# Diabetes Prediction Web

Ứng dụng Web dự đoán lớp bệnh tiểu đường bằng pipeline Machine Learning đã huấn luyện. Dự án thuộc Assignment 01 – Phát triển hệ thống thông minh và chỉ phục vụ mục đích học tập, không thay thế chẩn đoán y khoa.

## Công nghệ

- Backend: Python, FastAPI, Pandas, scikit-learn, Joblib
- Frontend: HTML, CSS, Vanilla JavaScript
- Model: pipeline tiền xử lý + Random Forest Classifier
- Deploy: Render (đã có `render.yaml`)

## Cấu trúc

```text
diabetes_prediction/
├── app.py
├── requirements.txt
├── render.yaml
├── model/
│   └── diabetes_prediction_pipeline.pkl
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/app.js
├── scripts/
│   └── inspect_model.py
└── tests/
    └── test_app.py
```

## Chuẩn bị model

Model phải nằm tại:

```text
model/diabetes_prediction_pipeline.pkl
```

Model gốc đã được sao chép từ `C:\DATAA\models\diabetes_prediction_pipeline.pkl`. Không sửa hoặc huấn luyện lại file này. Có thể kiểm tra metadata bằng:

```powershell
python scripts/inspect_model.py
```

Pipeline hiện tại nhận đúng 8 field: `gender`, `age`, `hypertension`, `heart_disease`, `smoking_history`, `bmi`, `HbA1c_level`, `blood_glucose_level`.

## Chạy local trên Windows

```powershell
cd D:\diabetes_prediction
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app:app --reload
```

Mở [http://127.0.0.1:8000](http://127.0.0.1:8000). Tài liệu API tự động có tại [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Chạy kiểm thử:

```powershell
pytest -q
```

## API dự đoán

`POST /predict`

Request:

```json
{
  "gender": "Female",
  "age": 45,
  "hypertension": 0,
  "heart_disease": 0,
  "smoking_history": "never",
  "bmi": 24.5,
  "HbA1c_level": 5.5,
  "blood_glucose_level": 110
}
```

Response:

```json
{
  "prediction": 0,
  "label": "Không thuộc lớp tiểu đường"
}
```

Các category lấy trực tiếp từ pipeline:

- `gender`: `Female`, `Male`, `Other`
- `smoking_history`: `No Info`, `current`, `ever`, `former`, `never`, `not current`
- `hypertension`, `heart_disease`: `0` hoặc `1`

## Deploy lên Render

### Cách 1: Blueprint

1. Đẩy toàn bộ project (bao gồm model) lên một repository GitHub riêng hoặc công khai.
2. Trên Render, chọn **New → Blueprint**.
3. Kết nối repository. Render tự đọc `render.yaml` và tạo Web Service.
4. Chọn **Apply** và chờ build hoàn tất.

### Cách 2: Web Service thủ công

- Runtime: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`

Frontend dùng đường dẫn tương đối `/predict`, vì vậy chạy được cả local lẫn production mà không cần hard-code domain. Model khoảng 56 MB; cần chắc chắn file được Git theo dõi và giới hạn dung lượng của Git host/Render cho phép. Nếu repository không muốn chứa model, cần dùng cơ chế lưu trữ artifact riêng và tải model trong build step.

## Lưu ý

Kết quả là đầu ra của mô hình học máy phục vụ demo kỹ thuật và học tập. Không sử dụng kết quả này để tự chẩn đoán hoặc thay thế tư vấn của chuyên gia y tế.
