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
        'role': 'ASHA'
    })
    
    insert_db('profiles', {
        'id': mo_id,
        'full_name': 'Dr. Anjali Verma',
        'role': 'MO'
    })
    
    today = datetime(2026, 9, 8)
    
    # Patient 1: Meera Devi (GREEN)
    p1_id = str(uuid.uuid4())
    insert_db('patients', {
        'id': p1_id,
        'first_name': 'Meera',
        'last_name': 'Devi',
        'date_of_birth': '1995-04-12',
        'village': 'Rampur'
    })
    
    preg1_id = str(uuid.uuid4())
    lmp1 = today - timedelta(days=150)
    insert_db('pregnancies', {
        'id': preg1_id,
        'patient_id': p1_id,
        'lmp_date': lmp1.strftime('%Y-%m-%d'),
        'edd_date': (lmp1 + timedelta(days=280)).strftime('%Y-%m-%d'),
        'risk_status': 'GREEN'
    })
    
    v1_1 = {
        'pregnancy_id': preg1_id,
        'conducted_by': asha_id,
        'systolic_bp': 110,
        'diastolic_bp': 70,
        'weight_kg': 60,
        'hemoglobin_g_dl': 12.5,
        'blood_sugar_mg_dl': 90,
        'symptoms': []
    }
    
    v1_2 = {
        'pregnancy_id': preg1_id,
        'conducted_by': asha_id,
        'systolic_bp': 112,
        'diastolic_bp': 72,
        'weight_kg': 61,
        'hemoglobin_g_dl': 12.3,
        'blood_sugar_mg_dl': 92,
        'symptoms': []
    }
    
    # Patient 2: Sunita Kumari (YELLOW)
    p2_id = str(uuid.uuid4())
    insert_db('patients', {
        'id': p2_id,
        'first_name': 'Sunita',
        'last_name': 'Kumari',
        'date_of_birth': '1998-08-22',
        'village': 'Sitapur'
    })
    
    preg2_id = str(uuid.uuid4())
    lmp2 = today - timedelta(days=200)
    insert_db('pregnancies', {
        'id': preg2_id,
        'patient_id': p2_id,
        'lmp_date': lmp2.strftime('%Y-%m-%d'),
        'edd_date': (lmp2 + timedelta(days=280)).strftime('%Y-%m-%d'),
        'risk_status': 'YELLOW'
    })
    
    v2_1 = {
        'pregnancy_id': preg2_id,
        'conducted_by': asha_id,
        'systolic_bp': 115,
        'diastolic_bp': 75,
        'weight_kg': 70,
        'hemoglobin_g_dl': 11.5,
        'blood_sugar_mg_dl': 100,
        'symptoms': []
    }
    
    v2_2 = {
        'pregnancy_id': preg2_id,
        'conducted_by': asha_id,
        'systolic_bp': 125,
        'diastolic_bp': 80,
        'weight_kg': 72,
        'hemoglobin_g_dl': 11.0,
        'blood_sugar_mg_dl': 115,
        'symptoms': []
    }
    
    v2_3 = {
        'pregnancy_id': preg2_id,
        'conducted_by': asha_id,
        'systolic_bp': 135,
        'diastolic_bp': 85,
        'weight_kg': 75,
        'hemoglobin_g_dl': 10.5,
        'blood_sugar_mg_dl': 130,
        'symptoms': ['swelling']
    }
    
    # Patient 3: Lakshmi Bai (RED)
    p3_id = str(uuid.uuid4())
    insert_db('patients', {
        'id': p3_id,
        'first_name': 'Lakshmi',
        'last_name': 'Bai',
        'date_of_birth': '1990-11-05',
        'village': 'Gopalpur'
    })
    
    preg3_id = str(uuid.uuid4())
    lmp3 = today - timedelta(days=220)
    insert_db('pregnancies', {
        'id': preg3_id,
        'patient_id': p3_id,
        'lmp_date': lmp3.strftime('%Y-%m-%d'),
        'edd_date': (lmp3 + timedelta(days=280)).strftime('%Y-%m-%d'),
        'risk_status': 'RED'
    })
    
    v3_1 = {
        'pregnancy_id': preg3_id,
        'conducted_by': asha_id,
        'systolic_bp': 128,
        'diastolic_bp': 82,
        'weight_kg': 78,
        'hemoglobin_g_dl': 9.5,
        'blood_sugar_mg_dl': 95,
        'symptoms': []
    }
    
    v3_2 = {
        'pregnancy_id': preg3_id,
        'conducted_by': asha_id,
        'systolic_bp': 160,
        'diastolic_bp': 100,
        'weight_kg': 80,
        'hemoglobin_g_dl': 8.0,
        'blood_sugar_mg_dl': 110,
        'symptoms': ['severe_headache']
    }
    
    def process_and_save_visit(v_data, v_date, lmp_date):
        v_date_str = v_date.strftime('%Y-%m-%d')
        gw = (v_date - lmp_date).days // 7
        
        ml_features = {
            **v_data, 
            'gestational_week': gw, 
            'has_swelling': 1 if 'swelling' in v_data['symptoms'] else 0, 
            'has_headache': 1 if 'severe_headache' in v_data['symptoms'] else 0,
            'has_blurred_vision': 0,
            'has_bleeding': 0
        }
        ml_res = predict_risk(ml_features)
        risk_tier = ml_res['tier']
        
        rule_res = check_safety_rules(v_data)
        if rule_res['triggered']:
            risk_tier = 'RED'
            
        visit_id = str(uuid.uuid4())
        insert_db('visits', {
            'id': visit_id,
            'pregnancy_id': v_data['pregnancy_id'],
            'conducted_by': v_data['conducted_by'],
            'visit_date': v_date_str,
            'gestational_week': gw,
            'systolic_bp': v_data['systolic_bp'],
            'diastolic_bp': v_data['diastolic_bp'],
            'weight_kg': v_data['weight_kg'],
            'hemoglobin_g_dl': v_data['hemoglobin_g_dl'],
            'blood_sugar_mg_dl': v_data['blood_sugar_mg_dl'],
            'symptoms': json.dumps(v_data['symptoms']),
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
                'pregnancy_id': v_data['pregnancy_id'],
                'trigger_reason': json.dumps(rule_res['reasons']) if rule_res['triggered'] else "ML Flag",
                'status': 'EMERGENCY' if rule_res['triggered'] else 'PENDING'
            })
            
    # Meera
    process_and_save_visit(v1_1, today - timedelta(days=30), lmp1)
    process_and_save_visit(v1_2, today, lmp1)
    
    # Sunita
    process_and_save_visit(v2_1, today - timedelta(days=60), lmp2)
    process_and_save_visit(v2_2, today - timedelta(days=30), lmp2)
    process_and_save_visit(v2_3, today, lmp2)
    
    # Lakshmi
    process_and_save_visit(v3_1, today - timedelta(days=30), lmp3)
    process_and_save_visit(v3_2, today, lmp3)
