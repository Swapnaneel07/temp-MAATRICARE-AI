def check_safety_rules(visit_data):
    systolic_bp = visit_data.get('systolic_bp')
    diastolic_bp = visit_data.get('diastolic_bp')
    hemoglobin_g_dl = visit_data.get('hemoglobin_g_dl')
    blood_sugar_mg_dl = visit_data.get('blood_sugar_mg_dl')
    symptoms = visit_data.get('symptoms', [])
    
    reasons = []
    
    if (systolic_bp is not None and systolic_bp >= 140) or (diastolic_bp is not None and diastolic_bp >= 90):
        reasons.append(f"Hypertension: BP {systolic_bp}/{diastolic_bp} mmHg")
        
    if hemoglobin_g_dl is not None and hemoglobin_g_dl < 7.0:
        reasons.append(f"Severe Anemia: Hb {hemoglobin_g_dl} g/dL")
        
    if blood_sugar_mg_dl is not None and blood_sugar_mg_dl > 200:
        reasons.append(f"Hyperglycemia: Blood sugar {blood_sugar_mg_dl} mg/dL")
        
    if 'vaginal_bleeding' in symptoms:
        reasons.append("Danger sign: Vaginal bleeding")
        
    if 'convulsions' in symptoms:
        reasons.append("Danger sign: Convulsions")
        
    if 'unconsciousness' in symptoms:
        reasons.append("Danger sign: Unconsciousness")
        
    if 'severe_headache' in symptoms and (systolic_bp is not None and systolic_bp >= 130):
        reasons.append("Preeclampsia warning: Severe headache with elevated BP")
        
    if reasons:
        return {'triggered': True, 'reasons': reasons, 'tier': 'RED'}
    else:
        return {'triggered': False, 'reasons': [], 'tier': None}
