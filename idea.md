# Personalized Maternal Risk Trajectory Prediction and Early Warning System

## Brief Summary
A longitudinal, AI-augmented maternal health tracking system designed for rural healthcare workers (ASHAs and ANMs). It continuously analyzes a pregnant woman's health timeline—tracking vitals, symptoms, and medical history across multiple visits—to predict evolving risk trajectories. It combines personalized Machine Learning risk estimates with a strict clinical rule-based safety layer to ensure early intervention for pregnancy complications without replacing human medical judgment.

## Background & Problem Statement
In rural India, maternal health monitoring relies heavily on ASHA workers and physical Mother and Child Protection (MCP) cards. This system faces several critical bottlenecks:
1. **Fragmented Records:** Paper records are frequently lost, damaged, or incomplete, leading to a loss of historical health data.
2. **Static Assessment:** Current protocols often evaluate a patient based on her latest measurements, missing crucial subtle trends (e.g., a slow but steady rise in blood pressure).
3. **Delayed Interventions:** High-risk complications (like preeclampsia, anemia, or gestational diabetes) are often identified too late due to missed warning signs or loss to follow-up.
4. **Communication Gaps:** Escalating a case from an ASHA worker to a Medical Officer can be slow and lacks data-backed urgency.

## Unique Selling Proposition (USP)
* **Longitudinal over Static:** Analyzes the *trajectory* of health markers over time rather than isolated data points, providing a more accurate picture of evolving risk.
* **Explainable AI (XAI):** Does not just output a risk score; it highlights the specific driving factors (e.g., "Risk elevated due to dropping hemoglobin and recent headaches"), building trust with healthcare workers.
* **Dual-Layer Safety:** Features a deterministic, rule-based clinical layer that instantly triggers escalation for critical symptoms, overriding the ML model to guarantee patient safety.
* **Designed for the Edge:** Built around the reality of rural deployment, focusing on offline capabilities and seamless integration into the existing ASHA-ANM workflow.