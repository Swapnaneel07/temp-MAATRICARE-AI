# 🏥 MaatriCare AI

**Personalized Maternal Risk Trajectory Prediction & Early Warning System**

An AI-powered, longitudinal maternal health tracking system designed for rural healthcare workers (ASHAs and ANMs). It continuously analyzes a pregnant woman's health timeline — tracking vitals, symptoms, and medical history across multiple visits — to predict evolving risk trajectories and trigger early interventions.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **XGBoost Risk Prediction** | ML model trained on maternal health data, outputs a probability score (0–1) mapped to GREEN / YELLOW / RED tiers |
| **SHAP Explainability** | Every prediction comes with human-readable explanations — e.g., *"Risk elevated due to high systolic BP (+2.53) and low hemoglobin (+2.40)"* |
| **Clinical Safety Net** | Deterministic rule engine that **overrides** the ML model for critical danger signs (BP ≥ 140/90, Hb < 7, vaginal bleeding, convulsions, etc.) |
| **Longitudinal Tracking** | Analyzes health *trajectories* over time, not just isolated snapshots — detects gradual trends like slowly rising BP |
| **Escalation System** | Automatically creates emergency escalations for RED-tier patients, visible on the Medical Officer dashboard |
| **Interactive Dashboard** | Clean single-page app with Chart.js trend charts, SHAP bar visualizations, and patient management |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Swapnaneel07/temp-MAATRICARE-AI.git
cd temp-MAATRICARE-AI

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

Open **http://localhost:5000** in your browser.

On first launch, the app will:
1. Initialize the SQLite database
2. Train the XGBoost model on synthetic maternal health data (~3 seconds)
3. Seed 3 demo patients at different risk levels

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (SPA)                    │
│         HTML/CSS/JS + Chart.js                      │
└──────────────────────┬──────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────┐
│                  Flask Backend                       │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  XGBoost +   │  │ Rules Engine │  │  SQLite    │ │
│  │  SHAP Model  │  │ (Safety Net) │  │  Database  │ │
│  └──────┬───────┘  └──────┬───────┘  └────────────┘ │
│         │                 │                          │
│         └────────┬────────┘                          │
│                  ▼                                    │
│         Risk Assessment                              │
│    (ML Score + Rule Override)                         │
└──────────────────────────────────────────────────────┘
```

### Data Flow

1. **Data Entry** → Frontend captures visit vitals and symptoms
2. **ML Inference** → XGBoost generates risk probability; SHAP explains the factors
3. **Safety Rules** → Deterministic rules check for critical thresholds (overrides ML if triggered)
4. **Storage** → Visit + risk data persisted to SQLite
5. **Escalation** → RED-tier visits auto-generate escalation alerts for Medical Officers

---

## 📁 Project Structure

```
├── app.py              # Flask API routes (8 endpoints)
├── database.py         # SQLite schema & query helpers
├── ml_pipeline.py      # XGBoost training + SHAP predictions
├── rules_engine.py     # Deterministic clinical safety rules
├── seed_data.py        # Demo data for 3 patients
├── run.py              # Entry point
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Single-page frontend application
├── static/
│   └── style.css       # Healthcare-themed styling
├── idea.md             # Original project idea
└── PRD.md              # Product Requirements Document
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/dashboard` | GET | Summary stats (patient count, pregnancies, escalations) |
| `/api/patients` | GET, POST | List / register patients |
| `/api/patients/<id>` | GET | Patient detail with pregnancies |
| `/api/pregnancies` | GET, POST | List / create pregnancy records |
| `/api/visits` | POST | Log visit → runs ML + rules → returns risk tier |
| `/api/visits/<pregnancy_id>/trend` | GET | Longitudinal visit history for trend charts |
| `/api/escalations` | GET | Pending/emergency escalations for MO |
| `/api/escalations/<id>/resolve` | POST | Resolve an escalation |

---

## 🧠 ML Pipeline

- **Model:** XGBoost Classifier
- **Training Data:** 1000 synthetic samples (70% normal, 30% high-risk) with realistic maternal health distributions
- **Features:** Systolic BP, Diastolic BP, Weight, Hemoglobin, Blood Sugar, Fundal Height, Symptoms (one-hot), Gestational Week
- **Tier Mapping:** Score < 0.3 → GREEN | 0.3–0.6 → YELLOW | ≥ 0.6 → RED
- **Explainability:** SHAP TreeExplainer provides per-feature contribution values with human-readable labels

## 🛡️ Clinical Safety Rules

These deterministic rules **always override** the ML model to RED:

| Condition | Trigger |
|---|---|
| BP ≥ 140/90 mmHg | Hypertension |
| Hemoglobin < 7 g/dL | Severe Anemia |
| Blood Sugar > 200 mg/dL | Hyperglycemia |
| Vaginal Bleeding | Danger Sign |
| Convulsions | Danger Sign |
| Unconsciousness | Danger Sign |
| Severe Headache + BP ≥ 130 | Preeclampsia Warning |

---

## 📊 Demo Patients

| Patient | Risk Level | Story |
|---|---|---|
| **Meera Devi** | 🟢 GREEN | Healthy pregnancy, 2 visits with stable vitals |
| **Sunita Kumari** | 🟡 YELLOW | Gradual BP increase (115 → 125 → 135) across 3 visits |
| **Lakshmi Bai** | 🔴 RED | BP 160/100, Hb 8.0, triggered safety rules + auto-escalation |

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, SQLite
- **ML:** XGBoost, SHAP, scikit-learn
- **Frontend:** Vanilla HTML/CSS/JS, Chart.js
- **Data:** NumPy, Pandas

---

## 👥 Team

**Group 6**

---

## 📝 License

This project is built for educational and showcase purposes.
