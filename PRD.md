# MaatriCare AI: Showcase MVP Product Requirements Document (PRD)

**Project:** temp_MaatriCare AI
**Objective:** Build an AI-powered, multilingual maternal health clinical decision support system tailored for offline-first rural environments and frontline ASHA workers.
**Architecture:** Python/Flask backend, SQLite database, XGBoost + SHAP machine learning pipeline, HTML/JS frontend, and external Translation/SMS APIs.

## 1. Executive Technical Summary & Builder Directives

**Strict Builder Directives:**
* **Token Efficiency:** Write DRY, modular code. Omit redundant boilerplate and focus on functional business logic.
* **Schema Exactness:** Database architectures must map precisely to the ERD provided in the source documentation.
* **Determinism:** Probabilistic ML scores must immediately yield to hard-coded clinical safety nets.
* **Resilience:** Core inference and rule-based logic must run locally, falling back gracefully if external translation or SMS APIs fail.

## 2. System Architecture & Data Flow

Implement the end-to-end pipeline exactly as specified:
1. **Data Entry:** Frontend captures routine visit vitals, symptoms, and danger flags.
2. **Storage:** Raw longitudinal data is committed to the local `SQLite` database.
3. **Preprocessing:** Handle missing values, encode categorical fields, and flatten symptom arrays.
4. **Inference:** `XGBoost` model generates a probability risk score (0.0000–1.0000) mapped to a base tier (Green/Yellow/Red).
5. **Explainability:** `SHAP` Engine calculates localized feature contributions (e.g., `+0.31 from high BP`) and serializes the output as JSONB.
6. **Rule-Based Safety Net:** Evaluates hard clinical thresholds independent of the ML model.
7. **Escalation:** Route output through the Translation API. If the final tier is Red, generate a structured referral and trigger an SMS alert to the Medical Officer.

## 3. Database Architecture

Construct a relational `SQLite` database utilizing the following tables. Since SQLite lacks native `UUID` and `JSONB`, implement them as `TEXT` types with application-level validation.

| Table | Key Fields & Constraints | Purpose |
| :--- | :--- | :--- |
| **profiles** | `id` (PK, UUID), `full_name`, `phone_number`, `role`, `region_code` | System users (ASHA workers, Medical Officers). |
| **patients** | `id` (PK, UUID), `abha_id` (Unique), `first_name`, `last_name`, `date_of_birth` | Core demographic registry. |
| **pregnancies** | `id` (PK, UUID), `patient_id` (FK), `lmp_date`, `edd_date`, `gravida`, `parity`, `risk_status` | Tracks discrete pregnancies and overarching risk status. |
| **visits** | `id` (PK, UUID), `pregnancy_id` (FK), `conducted_by` (FK), `visit_date`, `systolic_bp`, `diastolic_bp`, `weight_kg`, `hemoglobin_g_dl`, `ml_risk_score`, `shap_explanations` (JSONB) | Transactional data for longitudinal tracking. |
| **escalations** | `id` (PK, UUID), `visit_id` (FK), `pregnancy_id` (FK), `status`, `assigned_to_mo` (FK) | Triggered automatically upon high-risk detection. |

## 4. ML Risk Pipeline & Explainability

### Core Model
* **Algorithm:** `XGBoost` Classifier.
* **Input Features:** `systolic_bp`, `diastolic_bp`, `weight_kg`, `hemoglobin_g_dl`, `blood_sugar_mg_dl`, `fundal_height_cm`, and one-hot encoded symptom arrays.
* **Explainability Extraction:** Instantiate `shap.TreeExplainer`. For every prediction, extract the baseline and feature-specific SHAP values. Format this as a JSON object detailing exactly *why* the tier was assigned.

### Deterministic Safety Net (Rule-Based Override)
The ML model serves as a probabilistic baseline. You must implement a strict deterministic rule engine that overrides the ML output to `RED` (`rule_triggered_alert = True`) if critical danger signs are present. Per clinical guidelines, danger signs such as blood pressure exceeding 140/90 mmHg, vaginal bleeding, unconsciousness, or severe anemia (< 7 g/dL) mandate an immediate emergency escalation.

## 5. API Endpoints (Flask)

Implement the following RESTful routes to support the frontend application:

| Endpoint | Method | Payload / Params | Function |
| :--- | :--- | :--- | :--- |
| `/api/patients` | POST | Demographics JSON | Registers a new patient and generates an ID. |
| `/api/pregnancies` | POST | `patient_id`, historical vitals | Initiates a pregnancy monitoring record. |
| `/api/visits` | POST | Visit vitals, symptoms | Runs ML + SHAP pipeline, checks rules, returns Risk Tier. |
| `/api/visits/<id>/trend` | GET | None | Fetches longitudinal visit history to display patient trends. |
| `/api/escalations` | GET | `mo_id` | Fetches all `PENDING` or `EMERGENCY` escalations for a Medical Officer. |

## 6. Multilingual & Edge Connectivity

* **Translation Layer:** Wrap responses in a service class using the Google Translation API to support English, Hindi, and Bengali. Implement a local dictionary fallback cache for core medical terms to ensure the app functions during internet outages.
* **SMS Fallback:** Integrate a communication module (Twilio or mock logger). Upon a Red tier trigger, format an SMS payload containing the Patient ID, the primary risk driver (derived from SHAP or the safety net rule), and the ASHA worker's contact details, dispatched asynchronously.
