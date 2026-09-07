import uuid
import json
from datetime import datetime, timedelta
from database import insert_db
from ml_pipeline import predict_risk
from rules_engine import check_safety_rules

def seed_demo_data():
    asha_id = 'asha-001'
    mo_id = 'mo-001'
    
    insert_db('profiles', {
        'id': asha_id,
        'full_name': 'Priya Sharma',
        'phone_number': '9876543210',
        'role': 'ASHA',
        'region_code': 'UP-001'
    })
    
    insert_db('profiles', {
        'id': mo_id,
        'full_name': 'Dr. Anjali Verma',
        'phone_number': '9123456780',
        'role': 'MO',
        'region_code': 'UP-001'
    })
    
    today = datetime(2026, 9, 8)
    
    # ─────────────────────────────────────────────────
    # Patient 1: Meera Devi — Healthy (GREEN)
    # Story: Textbook normal pregnancy, all vitals stable
    # ─────────────────────────────────────────────────
    p1_id = str(uuid.uuid4())
    insert_db('patients', {
        'id': p1_id,
        'abha_id': 'ABHA-1001',
        'first_name': 'Meera',
        'last_name': 'Devi',
        'date_of_birth': '1995-04-12',
        'village': 'Rampur',
        'phone_number': '9876500001'
    })
    
    preg1_id = str(uuid.uuid4())
    lmp1 = today - timedelta(days=182)  # ~26 weeks pregnant
    insert_db('pregnancies', {
        'id': preg1_id,
        'patient_id': p1_id,
        'lmp_date': lmp1.strftime('%Y-%m-%d'),
        'edd_date': (lmp1 + timedelta(days=280)).strftime('%Y-%m-%d'),
        'gravida': 2,
        'parity': 1,
        'risk_status': 'GREEN'
    })
    
    meera_visits = [
        # Visit 1: 12 weeks — first registration
        {'days_ago': 98, 'systolic_bp': 108, 'diastolic_bp': 68, 'weight_kg': 55.0, 'hemoglobin_g_dl': 12.8, 'blood_sugar_mg_dl': 85, 'fundal_height_cm': 12, 'symptoms': []},
        # Visit 2: 16 weeks
        {'days_ago': 70, 'systolic_bp': 110, 'diastolic_bp': 70, 'weight_kg': 57.5, 'hemoglobin_g_dl': 12.5, 'blood_sugar_mg_dl': 88, 'fundal_height_cm': 16, 'symptoms': []},
        # Visit 3: 20 weeks
        {'days_ago': 42, 'systolic_bp': 112, 'diastolic_bp': 72, 'weight_kg': 59.0, 'hemoglobin_g_dl': 12.3, 'blood_sugar_mg_dl': 90, 'fundal_height_cm': 20, 'symptoms': []},
        # Visit 4: 24 weeks
        {'days_ago': 14, 'systolic_bp': 114, 'diastolic_bp': 72, 'weight_kg': 61.0, 'hemoglobin_g_dl': 12.0, 'blood_sugar_mg_dl': 92, 'fundal_height_cm': 24, 'symptoms': []},
        # Visit 5: 26 weeks — today
        {'days_ago': 0, 'systolic_bp': 112, 'diastolic_bp': 70, 'weight_kg': 62.5, 'hemoglobin_g_dl': 12.1, 'blood_sugar_mg_dl': 88, 'fundal_height_cm': 26, 'symptoms': []},
    ]
    
    # ─────────────────────────────────────────────────
    # Patient 2: Sunita Kumari — Gradual Deterioration (YELLOW)
    # Story: Starts normal, BP creeping up, gaining weight fast,
    #        hemoglobin dropping — classic trajectory detection case
    # ─────────────────────────────────────────────────
    p2_id = str(uuid.uuid4())
    insert_db('patients', {
        'id': p2_id,
        'abha_id': 'ABHA-1002',
        'first_name': 'Sunita',
        'last_name': 'Kumari',
        'date_of_birth': '1998-08-22',
        'village': 'Sitapur',
        'phone_number': '9876500002'
    })
    
    preg2_id = str(uuid.uuid4())
    lmp2 = today - timedelta(days=210)  # ~30 weeks pregnant
    insert_db('pregnancies', {
        'id': preg2_id,
        'patient_id': p2_id,
        'lmp_date': lmp2.strftime('%Y-%m-%d'),
        'edd_date': (lmp2 + timedelta(days=280)).strftime('%Y-%m-%d'),
        'gravida': 1,
        'parity': 0,
        'risk_status': 'YELLOW'
    })
    
    sunita_visits = [
        # Visit 1: 12 weeks — looks fine
        {'days_ago': 126, 'systolic_bp': 110, 'diastolic_bp': 70, 'weight_kg': 65.0, 'hemoglobin_g_dl': 11.8, 'blood_sugar_mg_dl': 95, 'fundal_height_cm': 12, 'symptoms': []},
        # Visit 2: 16 weeks — still normal
        {'days_ago': 98, 'systolic_bp': 115, 'diastolic_bp': 74, 'weight_kg': 67.0, 'hemoglobin_g_dl': 11.5, 'blood_sugar_mg_dl': 100, 'fundal_height_cm': 16, 'symptoms': []},
        # Visit 3: 20 weeks — BP starting to rise
        {'days_ago': 70, 'systolic_bp': 120, 'diastolic_bp': 78, 'weight_kg': 70.0, 'hemoglobin_g_dl': 11.2, 'blood_sugar_mg_dl': 108, 'fundal_height_cm': 20, 'symptoms': []},
        # Visit 4: 24 weeks — noticeable trend now
        {'days_ago': 42, 'systolic_bp': 126, 'diastolic_bp': 82, 'weight_kg': 73.0, 'hemoglobin_g_dl': 10.8, 'blood_sugar_mg_dl': 118, 'fundal_height_cm': 24, 'symptoms': ['swelling']},
        # Visit 5: 28 weeks — approaching danger zone
        {'days_ago': 14, 'systolic_bp': 132, 'diastolic_bp': 84, 'weight_kg': 76.0, 'hemoglobin_g_dl': 10.2, 'blood_sugar_mg_dl': 125, 'fundal_height_cm': 27, 'symptoms': ['swelling', 'headache']},
        # Visit 6: 30 weeks — clearly elevated, ML flags YELLOW
        {'days_ago': 0, 'systolic_bp': 136, 'diastolic_bp': 86, 'weight_kg': 78.0, 'hemoglobin_g_dl': 10.0, 'blood_sugar_mg_dl': 132, 'fundal_height_cm': 29, 'symptoms': ['swelling', 'headache']},
    ]
    
    # ─────────────────────────────────────────────────
    # Patient 3: Lakshmi Bai — High Risk (RED)
    # Story: Started borderline, progressed to dangerous levels.
    #        Last visit triggers multiple safety rules + emergency escalation.
    # ─────────────────────────────────────────────────
    p3_id = str(uuid.uuid4())
    insert_db('patients', {
        'id': p3_id,
        'abha_id': 'ABHA-1003',
        'first_name': 'Lakshmi',
        'last_name': 'Bai',
        'date_of_birth': '1990-11-05',
        'village': 'Gopalpur',
        'phone_number': '9876500003'
    })
    
    preg3_id = str(uuid.uuid4())
    lmp3 = today - timedelta(days=231)  # ~33 weeks pregnant
    insert_db('pregnancies', {
        'id': preg3_id,
        'patient_id': p3_id,
        'lmp_date': lmp3.strftime('%Y-%m-%d'),
        'edd_date': (lmp3 + timedelta(days=280)).strftime('%Y-%m-%d'),
        'gravida': 3,
        'parity': 2,
        'risk_status': 'RED'
    })
    
    lakshmi_visits = [
        # Visit 1: 14 weeks — slightly low Hb but otherwise ok
        {'days_ago': 133, 'systolic_bp': 118, 'diastolic_bp': 76, 'weight_kg': 72.0, 'hemoglobin_g_dl': 10.0, 'blood_sugar_mg_dl': 92, 'fundal_height_cm': 14, 'symptoms': []},
        # Visit 2: 18 weeks — Hb dropping, BP edging up
        {'days_ago': 105, 'systolic_bp': 124, 'diastolic_bp': 80, 'weight_kg': 74.0, 'hemoglobin_g_dl': 9.5, 'blood_sugar_mg_dl': 98, 'fundal_height_cm': 18, 'symptoms': []},
        # Visit 3: 22 weeks — concerning trajectory
        {'days_ago': 77, 'systolic_bp': 130, 'diastolic_bp': 84, 'weight_kg': 76.0, 'hemoglobin_g_dl': 9.0, 'blood_sugar_mg_dl': 105, 'fundal_height_cm': 22, 'symptoms': ['headache']},
        # Visit 4: 26 weeks — clear risk, swelling + headache
        {'days_ago': 49, 'systolic_bp': 138, 'diastolic_bp': 88, 'weight_kg': 79.0, 'hemoglobin_g_dl': 8.5, 'blood_sugar_mg_dl': 112, 'fundal_height_cm': 25, 'symptoms': ['swelling', 'headache']},
        # Visit 5: 30 weeks — elevated but just under rule threshold
        {'days_ago': 21, 'systolic_bp': 138, 'diastolic_bp': 89, 'weight_kg': 80.0, 'hemoglobin_g_dl': 8.2, 'blood_sugar_mg_dl': 108, 'fundal_height_cm': 28, 'symptoms': ['swelling', 'severe_headache']},
        # Visit 6: 33 weeks — DANGEROUS: high BP + severe headache = rule triggers
        {'days_ago': 0, 'systolic_bp': 160, 'diastolic_bp': 100, 'weight_kg': 82.0, 'hemoglobin_g_dl': 7.8, 'blood_sugar_mg_dl': 118, 'fundal_height_cm': 31, 'symptoms': ['swelling', 'severe_headache', 'blurred_vision']},
    ]
    
    # ─────────────────────────────────────────────────
    # Process and save all visits
    # ─────────────────────────────────────────────────
    def process_and_save_visit(v_data, preg_id, lmp_date, visit_date):
        v_date_str = visit_date.strftime('%Y-%m-%d')
        gw = (visit_date - lmp_date).days // 7
        
        symptoms = v_data.get('symptoms', [])
        ml_features = {
            'systolic_bp': v_data['systolic_bp'],
            'diastolic_bp': v_data['diastolic_bp'],
            'weight_kg': v_data['weight_kg'],
            'hemoglobin_g_dl': v_data['hemoglobin_g_dl'],
            'blood_sugar_mg_dl': v_data['blood_sugar_mg_dl'],
            'fundal_height_cm': v_data.get('fundal_height_cm', 0),
            'has_swelling': 1 if 'swelling' in symptoms else 0,
            'has_headache': 1 if 'severe_headache' in symptoms or 'headache' in symptoms else 0,
            'has_blurred_vision': 1 if 'blurred_vision' in symptoms else 0,
            'has_bleeding': 1 if 'vaginal_bleeding' in symptoms else 0,
            'gestational_week': gw
        }
        ml_res = predict_risk(ml_features)
        risk_tier = ml_res['tier']
        
        rule_data = {
            'systolic_bp': v_data['systolic_bp'],
            'diastolic_bp': v_data['diastolic_bp'],
            'hemoglobin_g_dl': v_data['hemoglobin_g_dl'],
            'blood_sugar_mg_dl': v_data['blood_sugar_mg_dl'],
            'symptoms': symptoms
        }
        rule_res = check_safety_rules(rule_data)
        if rule_res['triggered']:
            risk_tier = 'RED'
            
        visit_id = str(uuid.uuid4())
        insert_db('visits', {
            'id': visit_id,
            'pregnancy_id': preg_id,
            'conducted_by': asha_id,
            'visit_date': v_date_str,
            'gestational_week': gw,
            'systolic_bp': v_data['systolic_bp'],
            'diastolic_bp': v_data['diastolic_bp'],
            'weight_kg': v_data['weight_kg'],
            'hemoglobin_g_dl': v_data['hemoglobin_g_dl'],
            'blood_sugar_mg_dl': v_data['blood_sugar_mg_dl'],
            'fundal_height_cm': v_data.get('fundal_height_cm'),
            'symptoms': json.dumps(symptoms),
            'ml_risk_score': ml_res['score'],
            'risk_tier': risk_tier,
            'shap_explanations': json.dumps(ml_res['shap_values']),
            'rule_triggered': 1 if rule_res['triggered'] else 0,
            'rule_trigger_reason': json.dumps(rule_res['reasons']) if rule_res['triggered'] else None
        })
        
        if risk_tier == 'RED':
            insert_db('escalations', {
                'id': str(uuid.uuid4()),
                'visit_id': visit_id,
                'pregnancy_id': preg_id,
                'trigger_reason': json.dumps(rule_res['reasons']) if rule_res['triggered'] else 'ML Model flagged high risk',
                'status': 'EMERGENCY' if rule_res['triggered'] else 'PENDING',
                'assigned_to_mo': mo_id
            })
        
        return risk_tier
    
    # Meera Devi — 5 visits
    for v in meera_visits:
        visit_date = today - timedelta(days=v['days_ago'])
        process_and_save_visit(v, preg1_id, lmp1, visit_date)
    
    # Sunita Kumari — 6 visits
    for v in sunita_visits:
        visit_date = today - timedelta(days=v['days_ago'])
        process_and_save_visit(v, preg2_id, lmp2, visit_date)
    
    # Lakshmi Bai — 6 visits
    for v in lakshmi_visits:
        visit_date = today - timedelta(days=v['days_ago'])
        process_and_save_visit(v, preg3_id, lmp3, visit_date)
