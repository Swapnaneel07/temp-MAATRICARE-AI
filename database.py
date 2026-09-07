import sqlite3
import json

DB_PATH = 'maatricare.db'

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    schema = """
    CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        phone_number TEXT,
        role TEXT NOT NULL CHECK(role IN ('ASHA', 'ANM', 'MO')),
        region_code TEXT
    );

    CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY,
        abha_id TEXT UNIQUE,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth TEXT,
        village TEXT,
        phone_number TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS pregnancies (
        id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL REFERENCES patients(id),
        lmp_date TEXT NOT NULL,
        edd_date TEXT NOT NULL,
        gravida INTEGER DEFAULT 1,
        parity INTEGER DEFAULT 0,
        risk_status TEXT DEFAULT 'GREEN',
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS visits (
        id TEXT PRIMARY KEY,
        pregnancy_id TEXT NOT NULL REFERENCES pregnancies(id),
        conducted_by TEXT REFERENCES profiles(id),
        visit_date TEXT NOT NULL,
        gestational_week INTEGER,
        systolic_bp INTEGER,
        diastolic_bp INTEGER,
        weight_kg REAL,
        hemoglobin_g_dl REAL,
        blood_sugar_mg_dl REAL,
        fundal_height_cm REAL,
        symptoms TEXT DEFAULT '[]',
        ml_risk_score REAL,
        risk_tier TEXT,
        shap_explanations TEXT DEFAULT '{}',
        rule_triggered INTEGER DEFAULT 0,
        rule_trigger_reason TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS escalations (
        id TEXT PRIMARY KEY,
        visit_id TEXT NOT NULL REFERENCES visits(id),
        pregnancy_id TEXT NOT NULL REFERENCES pregnancies(id),
        trigger_reason TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'ACKNOWLEDGED', 'RESOLVED', 'EMERGENCY')),
        assigned_to_mo TEXT REFERENCES profiles(id),
        created_at TEXT DEFAULT (datetime('now')),
        resolved_at TEXT
    );
    """
    conn = get_db()
    with conn:
        conn.executescript(schema)
    conn.close()

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(table, data):
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, tuple(data.values()))
    conn.commit()
    conn.close()
    return data.get('id')
