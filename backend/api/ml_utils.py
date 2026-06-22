import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error
# Global variables to store trained models
condition_model = None
remaining_km_model = None
models_trained = False
def train_models():
    """Train the ML models if not already trained"""
    global condition_model, remaining_km_model, models_trained
    if models_trained:
        return
    try:
        # Load dataset
        data = pd.read_csv("realistic_fleet_tyre_data.csv")
        # Define average usage per day (km/day)
        avg_km_per_day = 100
        # Preprocessing: Calculate days in use and total kilometers traveled
        data['Days In Use'] = (datetime.now() - pd.to_datetime(data['Installation Date'])).dt.days
        data['Total Kilometers'] = data['Days In Use'] * avg_km_per_day
        # Calculate condition score to use as target for classification model
        def calculate_condition_score(psi, depth, temp):
            psi_factor = 1 if 90 <= psi <= 110 else 0
            depth_factor = 1 if depth > 6 else 0.5 if 3 <= depth <= 6 else 0
            temp_factor = 1 if 20 <= temp <= 35 else 0
            return psi_factor + depth_factor + temp_factor
        # Apply condition score and assign condition labels
        data['Condition Score'] = data.apply(lambda row: calculate_condition_score(row['PSI'], row['Tyre Depth (mm)'], row['Temperature (°C)']), axis=1)
        data['Condition'] = data['Condition Score'].apply(lambda score: "Good" if score == 3 else "Average" if score >= 2 else "Bad")  
        # Add 'Remaining Kilometers' if it doesn't exist by calculating based on expected lifetime
        if 'Remaining Kilometers' not in data.columns:
            expected_lifetime = data['Condition'].map({'Good': 100000, 'Average': 75000, 'Bad': 50000})
            data['Remaining Kilometers'] = expected_lifetime - data['Total Kilometers']
        # Define features and targets for model training
        X = data[['PSI', 'Tyre Depth (mm)', 'Temperature (°C)', 'Total Kilometers']]
        y_condition = data['Condition']
        y_remaining_km = data['Remaining Kilometers']
        # Split data into training and test sets
        X_train, X_test, y_condition_train, y_condition_test = train_test_split(X, y_condition, test_size=0.2, random_state=42)
        _, _, y_remaining_km_train, y_remaining_km_test = train_test_split(X, y_remaining_km, test_size=0.2, random_state=42)
        # Train a classifier for tire condition
        condition_model = RandomForestClassifier(random_state=42)
        condition_model.fit(X_train, y_condition_train)
        # Train a regressor for remaining kilometers
        remaining_km_model = RandomForestRegressor(random_state=42)
        remaining_km_model.fit(X_train, y_remaining_km_train)
        models_trained = True
    except FileNotFoundError:
        # If dataset not found, use fallback logic
        print("Dataset not found, using fallback prediction logic")
        models_trained = True
def predict_tyre_batch(df):
    """Predict tyre conditions for a batch of tyres"""
    global condition_model, remaining_km_model, models_trained
    # Train models if not already trained
    if not models_trained:
        train_models()
    results = []
    for idx, row in df.iterrows():
        # Extract features
        psi = float(row.get('psi', row.get('PSI', 32)))
        depth = float(row.get('depth', row.get('Tyre Depth (mm)', 6)))
        temp = float(row.get('temp', row.get('Temperature (°C)', 60)))
        # Calculate total kilometers (fallback if not in data)
        total_km = float(row.get('Total Kilometers', 50000))
        if condition_model is not None and remaining_km_model is not None:
            # Use trained models for prediction
            input_data = pd.DataFrame({
                'PSI': [psi],
                'Tyre Depth (mm)': [depth],
                'Temperature (°C)': [temp],
                'Total Kilometers': [total_km]
            })
            condition_pred = condition_model.predict(input_data)[0]
            remaining_km_pred = remaining_km_model.predict(input_data)[0]
        else:
            # Fallback prediction logic
            condition_pred = "Good" if psi >= 90 and depth > 6 and 20 <= temp <= 35 else "Average" if psi >= 80 and depth > 3 else "Bad"
            remaining_km_pred = max(0, 20000 - int(temp * 100))
        # Determine if replacement is needed
        replace = condition_pred == "Bad" or remaining_km_pred <= 0
        results.append({
            'tyre_id': row.get('tyre_id', row.get('Tyre ID', f'T{idx+1}')),
            'psi': psi,
            'depth': depth,
            'temp': temp,
            'remaining_km': int(remaining_km_pred),
            'replace': replace
        })
    return results
