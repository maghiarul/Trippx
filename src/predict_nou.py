import joblib
import numpy as np
import pandas as pd

# 📂 Load the saved models
rf_model = joblib.load("E:/@py_proj/tripper/tripx/src/assets/models/random_forest_model.pkl")
xgb_model = joblib.load("E:/@py_proj/tripper/tripx/src/assets/models/xgb_model.pkl")

def predict_rating(hotel_data: dict):
    """Predict hotel rating based on input features using Random Forest & XGBoost."""
    
    # Ensure hotel_data contains the required fields
    required_fields = ["Staff", "Facilities", "Cleanliness", "Comfort", "Value_for_money", "Location", "Wifi"]
    
    if not all(field in hotel_data for field in required_fields):
        raise ValueError("Missing required hotel features in hotel_data!")

    # Convert the dictionary values into a DataFrame
    new_hotel = pd.DataFrame([[
        float(hotel_data["Staff"]),
        float(hotel_data["Facilities"]),
        float(hotel_data["Cleanliness"]),
        float(hotel_data["Comfort"]),
        float(hotel_data["Value_for_money"]),
        float(hotel_data["Location"]),
        float(hotel_data["Wifi"])
    ]], columns=required_fields)

    # 🌲 Predict using Random Forest
    pred_rf = rf_model.predict(new_hotel)[0]

    # ⚡ Predict using XGBoost
    pred_xgb = xgb_model.predict(new_hotel)[0]

    # 📊 Display estimated ratings
    print("\n🔮 **Predicție Rating Hotel**")
    print(f"🌲 Random Forest: {pred_rf:.2f}")
    print(f"⚡ XGBoost: {pred_xgb:.2f}")
    
    return pred_rf, pred_xgb
