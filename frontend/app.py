"""Streamlit UI for the SuperKart sales forecasting API."""
import os

import pandas as pd
import requests
import streamlit as st

# Backend address: "backend" is the container name on the shared Docker network
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:7860")

st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Sales Forecast")
st.write("Predict the total sales of a product in a store, for one product or a whole CSV file.")

# ---------------- Single prediction ----------------
st.subheader("Single prediction")
col1, col2 = st.columns(2)
with col1:
    product_weight = st.number_input("Product weight", min_value=0.0, max_value=50.0, value=12.66, step=0.01)
    product_sugar = st.selectbox("Product sugar content", ["Low Sugar", "Regular", "No Sugar"])
    product_area = st.number_input("Product allocated area (ratio)", min_value=0.0, max_value=1.0,
                                   value=0.027, step=0.001, format="%.3f")
    product_mrp = st.number_input("Product MRP", min_value=0.0, max_value=500.0, value=117.08, step=0.01)
    product_id_char = st.selectbox("Product group (Product_Id prefix)", ["FD", "DR", "NC"],
                                   help="FD = food, DR = drinks, NC = non-consumables")
with col2:
    store_size = st.selectbox("Store size", ["Small", "Medium", "High"], index=1)
    store_city = st.selectbox("Store city tier", ["Tier 1", "Tier 2", "Tier 3"], index=1)
    store_type = st.selectbox("Store type", ["Departmental Store", "Food Mart",
                                             "Supermarket Type1", "Supermarket Type2"], index=3)
    store_age = st.number_input("Store age (years)", min_value=0, max_value=100, value=16, step=1)
    product_category = st.selectbox("Product type category", ["Perishables", "Non Perishables"], index=1)

payload = {
    "Product_Weight": product_weight,
    "Product_Sugar_Content": product_sugar,
    "Product_Allocated_Area": product_area,
    "Product_MRP": product_mrp,
    "Store_Size": store_size,
    "Store_Location_City_Type": store_city,
    "Store_Type": store_type,
    "Product_Id_char": product_id_char,
    "Store_Age_Years": store_age,
    "Product_Type_Category": product_category,
}

if st.button("Predict", type="primary"):
    try:
        response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=30)
        response.raise_for_status()
        st.success(f"Predicted product-store sales: {response.json()['Sales']:,.2f}")
    except requests.RequestException as err:
        st.error(f"Prediction failed: {err}")

# ---------------- Batch prediction ----------------
st.subheader("Batch prediction")
uploaded_file = st.file_uploader("Upload a CSV file with the 10 feature columns", type=["csv"])

if uploaded_file is not None:
    batch_df = pd.read_csv(uploaded_file)
    st.write(f"{len(batch_df)} rows loaded")

    if st.button("Predict for batch", type="primary"):
        try:
            files = {"file": ("batch.csv", uploaded_file.getvalue(), "text/csv")}
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=60)
            response.raise_for_status()
            predictions = response.json()

            # Attach the predictions to the uploaded rows and offer a download
            batch_df["Predicted_Sales"] = [predictions[str(i)] for i in range(len(batch_df))]
            st.success("Predictions completed")
            st.dataframe(batch_df, use_container_width=True)
            st.download_button("Download predictions", batch_df.to_csv(index=False),
                               file_name="superkart_predictions.csv", mime="text/csv")
        except requests.RequestException as err:
            st.error(f"Batch prediction failed: {err}")
