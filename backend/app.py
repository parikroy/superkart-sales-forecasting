"""Flask API that serves the SuperKart sales forecasting model."""
import joblib
import pandas as pd
from flask import Flask, jsonify, request

# Features the model pipeline expects
FEATURES = [
    "Product_Weight", "Product_Sugar_Content", "Product_Allocated_Area", "Product_MRP",
    "Store_Size", "Store_Location_City_Type", "Store_Type",
    "Product_Id_char", "Store_Age_Years", "Product_Type_Category",
]

# Initialize the Flask app; keep JSON keys in the order they are created
superkart_api = Flask("SuperKart")
superkart_api.json.sort_keys = False

# Load the serialized pipeline (pre-processing + model) once at start-up
model = joblib.load("superkart_model.joblib")


@superkart_api.get("/")
def home():
    """Health-check route."""
    return "Welcome to the SuperKart Sales Forecasting API"


@superkart_api.post("/v1/predict")
def predict_sales():
    """Predict sales for one product-store combination sent as JSON."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Build a one-row DataFrame in the expected column order and predict
    input_data = pd.DataFrame([{f: data[f] for f in FEATURES}])
    prediction = float(model.predict(input_data)[0])
    return jsonify({"Sales": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Predict sales for every row of an uploaded CSV file."""
    file = request.files.get("file")
    if file is None:
        return jsonify({"error": "Upload a CSV file in the 'file' field"}), 400

    input_data = pd.read_csv(file)
    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    predictions = model.predict(input_data[FEATURES])
    # Map each row index to its predicted sales
    return jsonify({str(i): round(float(p), 2) for i, p in enumerate(predictions)})


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
