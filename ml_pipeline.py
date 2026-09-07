import pandas as pd
import numpy as np
import xgboost as xgb
import shap
import warnings
from sklearn.model_selection import train_test_split

warnings.filterwarnings('ignore')

MODEL = None
EXPLAINER = None

def generate_synthetic_data(n=1000):
    np.random.seed(42)
    n_normal = int(0.7 * n)
    n_high_risk = n - n_normal
    
    normal_data = {
        'systolic_bp': np.random.uniform(100, 130, n_normal),
        'diastolic_bp': np.random.uniform(60, 85, n_normal),
        'weight_kg': np.random.uniform(45, 85, n_normal),
        'hemoglobin_g_dl': np.random.uniform(10, 14, n_normal),
        'blood_sugar_mg_dl': np.random.uniform(70, 140, n_normal),
        'fundal_height_cm': np.random.uniform(20, 36, n_normal),
        'has_swelling': np.random.choice([0, 1], n_normal, p=[0.9, 0.1]),
        'has_headache': np.random.choice([0, 1], n_normal, p=[0.8, 0.2]),
        'has_blurred_vision': np.random.choice([0, 1], n_normal, p=[0.95, 0.05]),
        'has_bleeding': np.random.choice([0, 1], n_normal, p=[0.99, 0.01]),
        'gestational_week': np.random.randint(12, 40, n_normal),
        'risk_label': np.zeros(n_normal)
    }
    
    high_risk_data = {
        'systolic_bp': np.random.uniform(130, 170, n_high_risk),
        'diastolic_bp': np.random.uniform(85, 110, n_high_risk),
        'weight_kg': np.random.uniform(40, 95, n_high_risk),
        'hemoglobin_g_dl': np.random.uniform(5, 10, n_high_risk),
        'blood_sugar_mg_dl': np.random.uniform(100, 250, n_high_risk),
        'fundal_height_cm': np.random.uniform(20, 36, n_high_risk),
        'has_swelling': np.random.choice([0, 1], n_high_risk, p=[0.4, 0.6]),
        'has_headache': np.random.choice([0, 1], n_high_risk, p=[0.3, 0.7]),
        'has_blurred_vision': np.random.choice([0, 1], n_high_risk, p=[0.6, 0.4]),
        'has_bleeding': np.random.choice([0, 1], n_high_risk, p=[0.8, 0.2]),
        'gestational_week': np.random.randint(12, 40, n_high_risk),
        'risk_label': np.ones(n_high_risk)
    }
    
    df_normal = pd.DataFrame(normal_data)
    df_high_risk = pd.DataFrame(high_risk_data)
    
    df = pd.concat([df_normal, df_high_risk], ignore_index=True)
    return df.sample(frac=1).reset_index(drop=True)

def train_model():
    global MODEL, EXPLAINER
    
    df = generate_synthetic_data()
    X = df.drop('risk_label', axis=1)
    y = df['risk_label']
    
    MODEL = xgb.XGBClassifier(eval_metric='logloss', random_state=42)
    MODEL.fit(X, y)
    
    EXPLAINER = shap.TreeExplainer(MODEL)
    return MODEL

def predict_risk(features_dict):
    if MODEL is None or EXPLAINER is None:
        return {'score': 0.1, 'tier': 'GREEN', 'shap_values': {}, 'top_factors': []}
        
    feature_cols = ['systolic_bp', 'diastolic_bp', 'weight_kg', 'hemoglobin_g_dl', 'blood_sugar_mg_dl', 
                    'fundal_height_cm', 'has_swelling', 'has_headache', 'has_blurred_vision', 'has_bleeding', 'gestational_week']
                    
    row = {col: features_dict.get(col, 0) for col in feature_cols}
    # Ensure None values are handled
    for k, v in row.items():
        if v is None:
            row[k] = 0
            
    X_input = pd.DataFrame([row])
    
    prob = float(MODEL.predict_proba(X_input)[0, 1])
    
    tier = 'GREEN'
    if prob >= 0.6:
        tier = 'RED'
    elif prob >= 0.3:
        tier = 'YELLOW'
        
    shap_vals = EXPLAINER.shap_values(X_input)[0]
    
    human_readable = {
        'systolic_bp': 'Blood Pressure (Systolic)',
        'diastolic_bp': 'Blood Pressure (Diastolic)',
        'weight_kg': 'Weight (kg)',
        'hemoglobin_g_dl': 'Hemoglobin (g/dL)',
        'blood_sugar_mg_dl': 'Blood Sugar (mg/dL)',
        'fundal_height_cm': 'Fundal Height (cm)',
        'has_swelling': 'Swelling Present',
        'has_headache': 'Headache Present',
        'has_blurred_vision': 'Blurred Vision Present',
        'has_bleeding': 'Bleeding Present',
        'gestational_week': 'Gestational Week'
    }
    
    result_shap = {}
    top_factors = []
    
    # Need to handle shap dimensions depending on objective
    if len(shap_vals.shape) > 1:
        s_vals = shap_vals[:, 1] if shap_vals.shape[1] > 1 else shap_vals[:, 0]
    else:
        s_vals = shap_vals
        
    for i, col in enumerate(feature_cols):
        val = float(s_vals[i])
        hr_name = human_readable.get(col, col)
        result_shap[hr_name] = val
        if abs(val) > 0.05:
            top_factors.append({
                'feature': hr_name,
                'contribution': abs(val),
                'direction': 'increases' if val > 0 else 'decreases'
            })
            
    top_factors = sorted(top_factors, key=lambda x: x['contribution'], reverse=True)[:3]
    
    return {
        'score': prob,
        'tier': tier,
        'shap_values': result_shap,
        'top_factors': top_factors
    }
