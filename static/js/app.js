"use strict";

const form = document.querySelector("#prediction-form");
const submitButton = document.querySelector("#predict-button");
const buttonText = submitButton.querySelector("span");
const formError = document.querySelector("#form-error");
const resultPanel = document.querySelector("#result-panel");
const resultLabel = document.querySelector("#result-label");
const resultScore = document.querySelector("#result-score");
const resultDescription = document.querySelector("#result-description");

const numberRules = {
  age: { label: "Tuổi", min: 0, max: 120 },
  bmi: { label: "BMI", min: 0.1, max: 100 },
  HbA1c_level: { label: "HbA1c", min: 0.1, max: 20 },
  blood_glucose_level: { label: "Đường huyết", min: 1, max: 1000 },
};

function setFieldError(name, message = "") {
  const row = form.querySelector(`[data-field="${name}"]`);
  const output = document.querySelector(`#${name}-error`);
  row.classList.toggle("invalid", Boolean(message));
  output.textContent = message;
}

function validateNumber(name) {
  const input = form.elements[name];
  const rule = numberRules[name];
  const rawValue = input.value.trim();
  if (!rawValue) {
    setFieldError(name, `Vui lòng nhập ${rule.label.toLowerCase()}.`);
    return null;
  }

  const value = Number(rawValue);
  if (!Number.isFinite(value)) {
    setFieldError(name, `${rule.label} phải là một số hợp lệ.`);
    return null;
  }
  if (value < rule.min || value > rule.max) {
    setFieldError(name, `${rule.label} phải nằm trong khoảng ${rule.min}–${rule.max}.`);
    return null;
  }

  setFieldError(name);
  return value;
}

function collectPayload() {
  const values = {};
  let valid = true;
  Object.keys(numberRules).forEach((name) => {
    const value = validateNumber(name);
    if (value === null) valid = false;
    values[name] = value;
  });

  if (!valid) return null;
  return {
    gender: form.elements.gender.value,
    age: values.age,
    hypertension: Number(form.elements.hypertension.value),
    heart_disease: Number(form.elements.heart_disease.value),
    smoking_history: form.elements.smoking_history.value,
    bmi: values.bmi,
    HbA1c_level: values.HbA1c_level,
    blood_glucose_level: values.blood_glucose_level,
  };
}

function setLoading(loading) {
  submitButton.disabled = loading;
  submitButton.classList.toggle("loading", loading);
  buttonText.textContent = loading ? "Đang dự đoán..." : "Dự đoán kết quả";
}

function showResult(prediction, label) {
  const isPositive = prediction === 1;
  resultPanel.className = `result-panel ${isPositive ? "warning" : "success"}`;
  resultLabel.textContent = label;
  resultScore.hidden = false;
  resultScore.querySelector("strong").textContent = String(prediction);
  resultDescription.textContent = isPositive
    ? "Mô hình dự đoán mẫu hiện tại thuộc lớp tiểu đường. Hãy xem đây là một kết quả tham khảo."
    : "Mô hình dự đoán mẫu hiện tại không thuộc lớp tiểu đường.";

  if (window.matchMedia("(max-width: 768px)").matches) {
    document.querySelector(".result-card").scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function showApiError(message) {
  formError.textContent = message;
  formError.hidden = false;
}

Object.keys(numberRules).forEach((name) => {
  form.elements[name].addEventListener("input", () => {
    if (form.querySelector(`[data-field="${name}"]`).classList.contains("invalid")) {
      validateNumber(name);
    }
  });
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  formError.hidden = true;
  const payload = collectPayload();
  if (!payload) {
    const firstInvalid = form.querySelector(".field-row.invalid input");
    firstInvalid?.focus();
    return;
  }

  setLoading(true);
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      const detail = typeof data.detail === "string" ? data.detail : "Dữ liệu chưa hợp lệ.";
      throw new Error(detail);
    }
    showResult(data.prediction, data.label);
  } catch (error) {
    const offline = !navigator.onLine;
    showApiError(offline ? "Bạn đang ngoại tuyến. Vui lòng kiểm tra kết nối." : error.message || "Không thể kết nối đến máy chủ. Vui lòng thử lại.");
  } finally {
    setLoading(false);
  }
});
