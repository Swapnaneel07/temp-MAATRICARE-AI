import uuid
import json
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template

from database import query_db, insert_db
from ml_pipeline import predict_risk
from rules_engine import check_safety_rules

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard')
def dashboard():
    total_patients = query_db("SELECT COUNT(*) as c FROM patients", one=True)['c']
    active_pregnancies = query_db("SELECT COUNT(*) as c FROM pregnancies WHERE is_active=1", one=True)['c']
    pending_escalations = query_db("SELECT COUNT(*) as c FROM escalations WHERE status IN ('PENDING', 'EMERGENCY')", one=True)['c']
    
    recent_visits = []
    rv_raw = query_db("""
        SELECT v.*, p.first_name || ' ' || p.last_name as patient_name
        FROM visits v
        JOIN pregnancies pr ON v.pregnancy_id = pr.id
        JOIN patients p ON pr.patient_id = p.id
        ORDER BY v.visit_date DESC LIMIT 5
    """)
    if rv_raw:
        recent_visits = [dict(r) for r in rv_raw]
        
    return jsonify({
        'total_patients': total_patients,
        'active_pregnancies': active_pregnancies,
        'pending_escalations': pending_escalations,
        'recent_visits': recent_visits
    })

@app.route('/api/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'GET':
        patients_list = query_db("SELECT * FROM patients")
        return jsonify([dict(p) for p in patients_list] if patients_list else [])
        
    data = request.json
    new_id = str(uuid.uuid4())
    patient_data = {
        'id': new_id,
        'abha_id': data.get('abha_id'),
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'date_of_birth': data.get('date_of_birth'),
        'village': data.get('village'),
        'phone_number': data.get('phone_number')
    }
    insert_db('patients', patient_data)
    return jsonify(patient_data), 201

@app.route('/api/patients/<patient_id>')
def get_patient(patient_id):
    patient = query_db("SELECT * FROM patients WHERE id = ?", (patient_id,), one=True)
    if not patient:
        return jsonify({'error': 'Not found'}), 404
        
    pregnancies = query_db("SELECT * FROM pregnancies WHERE patient_id = ?", (patient_id,))
    
    res = dict(patient)
    res['pregnancies'] = [dict(p) for p in pregnancies] if pregnancies else []
    return jsonify(res)

@app.route('/api/pregnancies', methods=['GET', 'POST'])
def pregnancies():
    if request.method == 'GET':
        patient_id = request.args.get('patient_id')
        if patient_id:
            pregs = query_db("SELECT * FROM pregnancies WHERE patient_id = ?", (patient_id,))
        else:
            pregs = query_db("SELECT * FROM pregnancies")
        return jsonify([dict(p) for p in pregs] if pregs else [])
        
    data = request.json
    new_id = str(uuid.uuid4())
    lmp_date_str = data.get('lmp_date')
    lmp_date = datetime.strptime(lmp_date_str, '%Y-%m-%d')
    edd_date = lmp_date + timedelta(days=280)
    
    preg_data = {
        'id': new_id,
        'patient_id': data.get('patient_id'),
        'lmp_date': lmp_date_str,
        'edd_date': edd_date.strftime('%Y-%m-%d'),
        'gravida': data.get('gravida', 1),
        'parity': data.get('parity', 0)
    }
    insert_db('pregnancies', preg_data)
    return jsonify(preg_data), 201

@app.route('/api/visits', methods=['POST'])
def create_visit():
    data = request.json
    pregnancy_id = data.get('pregnancy_id')
    
    preg = query_db("SELECT lmp_date FROM pregnancies WHERE id = ?", (pregnancy_id,), one=True)
    if not preg:
        return jsonify({'error': 'Pregnancy not found'}), 404
        
    visit_date_str = data.get('visit_date', datetime.now().strftime('%Y-%m-%d'))
    visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d')
    lmp_date = datetime.strptime(preg['lmp_date'], '%Y-%m-%d')
    gestational_week = (visit_date - lmp_date).days // 7
    
    symptoms = data.get('symptoms', [])
    
    ml_features = {
        'systolic_bp': data.get('systolic_bp'),
        'diastolic_bp': data.get('diastolic_bp'),
        'weight_kg': data.get('weight_kg'),
        'hemoglobin_g_dl': data.get('hemoglobin_g_dl'),
        'blood_sugar_mg_dl': data.get('blood_sugar_mg_dl'),
        'fundal_height_cm': data.get('fundal_height_cm'),
        'has_swelling': 1 if 'swelling' in symptoms else 0,
        'has_headache': 1 if 'severe_headache' in symptoms else 0,
        'has_blurred_vision': 1 if 'blurred_vision' in symptoms else 0,
        'has_bleeding': 1 if 'vaginal_bleeding' in symptoms else 0,
        'gestational_week': gestational_week
    }
    
    ml_res = predict_risk(ml_features)
    risk_tier = ml_res['tier']
    ml_score = ml_res['score']
    
    rule_res = check_safety_rules(data)
    if rule_res['triggered']:
        risk_tier = 'RED'
        
    visit_id = str(uuid.uuid4())
    visit_data = {
        'id': visit_id,
        'pregnancy_id': pregnancy_id,
        'conducted_by': data.get('conducted_by'),
        'visit_date': visit_date_str,
        'gestational_week': gestational_week,
        'systolic_bp': data.get('systolic_bp'),
        'diastolic_bp': data.get('diastolic_bp'),
        'weight_kg': data.get('weight_kg'),
        'hemoglobin_g_dl': data.get('hemoglobin_g_dl'),
        'blood_sugar_mg_dl': data.get('blood_sugar_mg_dl'),
        'fundal_height_cm': data.get('fundal_height_cm'),
        'symptoms': json.dumps(symptoms),
        'ml_risk_score': ml_score,
        'risk_tier': risk_tier,
        'shap_explanations': json.dumps(ml_res['shap_values']),
        'rule_triggered': 1 if rule_res['triggered'] else 0,
        'rule_trigger_reason': json.dumps(rule_res['reasons']) if rule_res['triggered'] else None
    }
    
    insert_db('visits', visit_data)
    
    query_db("UPDATE pregnancies SET risk_status = ? WHERE id = ?", (risk_tier, pregnancy_id))
    
    if risk_tier == 'RED':
        esc_data = {
            'id': str(uuid.uuid4()),
            'visit_id': visit_id,
            'pregnancy_id': pregnancy_id,
            'trigger_reason': json.dumps(rule_res['reasons']) if rule_res['triggered'] else "ML Model flagged high risk",
            'status': 'EMERGENCY' if rule_res['triggered'] else 'PENDING'
        }
        insert_db('escalations', esc_data)
        
    return jsonify(visit_data), 201

@app.route('/api/visits/<pregnancy_id>/trend')
def visit_trend(pregnancy_id):
    visits = query_db("SELECT * FROM visits WHERE pregnancy_id = ? ORDER BY visit_date ASC", (pregnancy_id,))
    result = []
    for v in (visits or []):
        d = dict(v)
        # Parse JSON strings for frontend consumption
        try:
            d['shap_explanations'] = json.loads(d.get('shap_explanations') or '{}')
        except (json.JSONDecodeError, TypeError):
            d['shap_explanations'] = {}
        try:
            d['symptoms'] = json.loads(d.get('symptoms') or '[]')
        except (json.JSONDecodeError, TypeError):
            d['symptoms'] = []
        if d.get('rule_trigger_reason'):
            try:
                d['rule_trigger_reason'] = json.loads(d['rule_trigger_reason'])
            except (json.JSONDecodeError, TypeError):
                pass
        result.append(d)
    return jsonify(result)

@app.route('/api/escalations')
def escalations():
    escs = query_db('''
        SELECT e.*, p.first_name || ' ' || p.last_name as patient_name, 
               v.visit_date, v.risk_tier
        FROM escalations e
        JOIN pregnancies pr ON e.pregnancy_id = pr.id
        JOIN patients p ON pr.patient_id = p.id
        JOIN visits v ON e.visit_id = v.id
        WHERE e.status IN ('PENDING', 'EMERGENCY')
    ''')
    result = []
    for e in (escs or []):
        d = dict(e)
        # Parse trigger_reason if it's JSON
        if d.get('trigger_reason'):
            try:
                parsed = json.loads(d['trigger_reason'])
                if isinstance(parsed, list):
                    d['trigger_reason'] = '; '.join(parsed)
            except (json.JSONDecodeError, TypeError):
                pass
        result.append(d)
    return jsonify(result)

@app.route('/api/escalations/<esc_id>/resolve', methods=['POST'])
def resolve_escalation(esc_id):
    query_db("UPDATE escalations SET status = 'RESOLVED', resolved_at = datetime('now') WHERE id = ?", (esc_id,))
    return jsonify({'status': 'success'})
