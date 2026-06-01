# Project Report Content Outline

## Chapter 1: Introduction

- Global burden of infectious diseases
- Need for AI-powered early warning in India (IDSP context)
- Objectives of DOPEWIS platform

## Chapter 2: Literature Survey

- Epidemic forecasting methods (ARIMA, Prophet, ML)
- Climate-disease associations (dengue, malaria)
- Explainable AI in public health
- Ensemble learning for imbalanced outbreak detection

## Chapter 3: System Analysis

- Stakeholders: WHO, state health departments, hospitals
- Functional requirements (10 core objectives)
- Non-functional: scalability, security, explainability

## Chapter 4: System Design

- Architecture diagram (see ARCHITECTURE.md)
- ER diagram (see DATABASE.md)
- API design (REST + OpenAPI)
- UI/UX wireframes (dashboard, map, XAI pages)

## Chapter 5: Implementation

### 5.1 Data Pipeline
- IDSP-style surveillance data
- Climate variables (temperature, rainfall, LAI)
- Geographic attributes (district, lat/long, population)

### 5.2 Feature Engineering (50+ features)
- Temporal: lag_1..lag_12
- Rolling: mean/std windows
- Epidemic: acceleration, spike_ratio, outbreak_memory
- Climate: temperature_change, rainfall_change
- Geospatial: concentration_ratio, geo_spread

### 5.3 Data Leakage Control
- TimeSeriesSplit with 5 folds
- Leakage audit JSON report
- Shift-based feature computation

### 5.4 Machine Learning
- Classical: LR, RF, Extra Trees, XGBoost, LightGBM, CatBoost
- Deep: LSTM, Bi-LSTM, GRU
- Ensembles: Voting, Stacking, Blending
- Imbalance: SMOTE, Borderline SMOTE, ADASYN

### 5.5 MLOps
- MLflow experiment tracking
- Model registry and versioning
- Automated retraining pipeline

### 5.6 Web Application
- FastAPI backend with JWT
- Next.js professional dashboard
- Leaflet outbreak maps
- PDF report generation

## Chapter 6: Results

- Model comparison table (accuracy, F1, ROC-AUC)
- Sample outbreak prediction for Pune dengue
- SHAP feature importance interpretation
- Dashboard screenshots

## Chapter 7: Conclusion & Future Work

- Real-time IDSP API integration
- Mobile app for field officers
- Federated learning across states
- Integration with IHIP (Integrated Health Information Platform)

## References

- WHO Global Health Observatory
- NVBDCP India disease reports
- IDSP weekly surveillance format
- SHAP: Lundberg & Lee, 2017
