import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split

MODELS_DIR = os.path.join(settings.BASE_DIR, 'models')
CLASSIFIER_PATH = os.path.join(MODELS_DIR, 'classifier.joblib')
REGRESSOR_PATH = os.path.join(MODELS_DIR, 'regressor.joblib')

classifier_model = None
regressor_model = None
models_loaded = False

def generate_synthetic_training_data():
    """Generates synthetic fleet tyre telemetry data to train the RF models"""
    np.random.seed(42)
    n_samples = 1000
    
    psi = np.random.uniform(70, 120, n_samples)
    depth = np.random.uniform(1.0, 12.0, n_samples)
    temp = np.random.uniform(15, 65, n_samples)
    total_km = np.random.uniform(1000, 100000, n_samples)
    
    data = pd.DataFrame({
        'PSI': psi,
        'Tyre Depth (mm)': depth,
        'Temperature (°C)': temp,
        'Total Kilometers': total_km
    })
    
    def calculate_condition_score(psi, depth, temp):
        psi_factor = 1 if 90 <= psi <= 110 else 0
        depth_factor = 1 if depth > 6 else 0.5 if 3 <= depth <= 6 else 0
        temp_factor = 1 if 20 <= temp <= 35 else 0
        return psi_factor + depth_factor + temp_factor

    data['Condition Score'] = data.apply(lambda row: calculate_condition_score(row['PSI'], row['Tyre Depth (mm)'], row['Temperature (°C)']), axis=1)
    data['Condition'] = data['Condition Score'].apply(lambda score: "Good" if score == 3 else "Average" if score >= 2 else "Bad")  
    
    expected_lifetime = data['Condition'].map({'Good': 100000, 'Average': 75000, 'Bad': 50000})
    data['Remaining Kilometers'] = expected_lifetime - data['Total Kilometers']
    data['Remaining Kilometers'] = data['Remaining Kilometers'].clip(lower=0)
    
    return data

def train_and_save_models():
    """Train RF models and save them to joblib format"""
    global classifier_model, regressor_model, models_loaded
    
    print("Training RandomForest models for Tyre health classification and RUL regression...")
    
    try:
        # Load dataset if exists
        csv_path = os.path.join(settings.BASE_DIR, 'realistic_fleet_tyre_data.csv')
        if os.path.exists(csv_path):
            data = pd.read_csv(csv_path)
            # Apply preprocessing
            data['Days In Use'] = 100 # mock value
            data['Total Kilometers'] = data['Days In Use'] * 100
            
            def calculate_condition_score(psi, depth, temp):
                psi_factor = 1 if 90 <= psi <= 110 else 0
                depth_factor = 1 if depth > 6 else 0.5 if 3 <= depth <= 6 else 0
                temp_factor = 1 if 20 <= temp <= 35 else 0
                return psi_factor + depth_factor + temp_factor

            data['Condition Score'] = data.apply(lambda row: calculate_condition_score(row['PSI'], row['Tyre Depth (mm)'], row['Temperature (°C)']), axis=1)
            data['Condition'] = data['Condition Score'].apply(lambda score: "Good" if score == 3 else "Average" if score >= 2 else "Bad")
            
            if 'Remaining Kilometers' not in data.columns:
                expected_lifetime = data['Condition'].map({'Good': 100000, 'Average': 75000, 'Bad': 50000})
                data['Remaining Kilometers'] = expected_lifetime - data['Total Kilometers']
        else:
            data = generate_synthetic_training_data()
            
        X = data[['PSI', 'Tyre Depth (mm)', 'Temperature (°C)', 'Total Kilometers']]
        y_condition = data['Condition']
        y_remaining_km = data['Remaining Kilometers']
        
        # Train classifier
        classifier_model = RandomForestClassifier(random_state=42)
        classifier_model.fit(X, y_condition)
        
        # Train regressor
        regressor_model = RandomForestRegressor(random_state=42)
        regressor_model.fit(X, y_remaining_km)
        
        # Save to disk
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(classifier_model, CLASSIFIER_PATH)
        joblib.dump(regressor_model, REGRESSOR_PATH)
        
        models_loaded = True
        print("Models successfully trained and saved.")
    except Exception as e:
        print(f"Error training models: {e}")

def load_models():
    """Load serialized models from disk, or trigger training if not found"""
    global classifier_model, regressor_model, models_loaded
    if models_loaded:
        return
        
    if os.path.exists(CLASSIFIER_PATH) and os.path.exists(REGRESSOR_PATH):
        try:
            classifier_model = joblib.load(CLASSIFIER_PATH)
            regressor_model = joblib.load(REGRESSOR_PATH)
            models_loaded = True
            print("Models loaded successfully from disk.")
        except Exception as e:
            print(f"Error loading models: {e}. Retraining...")
            train_and_save_models()
    else:
        train_and_save_models()

def run_prediction_for_telemetry(telemetry):
    """Run prediction on a telemetry log and save to Prediction model"""
    from predictions.models import Prediction
    
    load_models()
    
    psi = telemetry.psi
    depth = telemetry.depth
    temp = telemetry.temperature
    
    # Odometer simulation (e.g. 30000 + random variation)
    total_km = 30000.0 + (telemetry.id * 100 % 20000)
    
    if models_loaded:
        input_data = pd.DataFrame({
            'PSI': [psi],
            'Tyre Depth (mm)': [depth],
            'Temperature (°C)': [temp],
            'Total Kilometers': [total_km]
        })
        condition = classifier_model.predict(input_data)[0]
        remaining_km = int(regressor_model.predict(input_data)[0])
    else:
        # Rules-based fallback
        condition = "Good" if 90 <= psi <= 110 and depth > 6 and 20 <= temp <= 35 else "Average" if 80 <= psi <= 115 and depth > 3 else "Bad"
        remaining_km = max(0, 50000 - int(temp * 200))
        
    # Calculate Risk Score (0 to 100)
    # High risk when psi is outside bounds, depth is low, temperature is high
    psi_dev = abs(95 - psi) / 25.0  # Normalized deviation from optimal 95 PSI
    depth_dev = (10 - depth) / 10.0  # Normalized wear
    temp_dev = (temp - 20) / 40.0   # Normalized heat
    
    risk_raw = (psi_dev * 0.35 + depth_dev * 0.40 + temp_dev * 0.25) * 100
    risk_score = round(min(100.0, max(0.0, risk_raw)), 1)
    
    # Check if prediction for this vehicle and tyre already exists, if so overwrite or create new
    # The requirement says: "Store result in Prediction table."
    Prediction.objects.create(
        vehicle=telemetry.vehicle,
        tyre=telemetry.tyre,
        condition=condition,
        remaining_km=remaining_km,
        risk_score=risk_score
    )
