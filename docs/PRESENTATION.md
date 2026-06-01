# PPT Presentation Content (15–20 slides)

## Slide 1: Title
**Disease Outbreak Prediction & Early Warning Intelligence System (DOPEWIS)**  
B.Tech AI — Final Year Project  
[Your Name] | [Institution] | 2025–26

## Slide 2: Problem Statement
- Delayed outbreak detection costs lives
- Manual surveillance cannot scale to 700+ districts
- Climate change amplifies vector-borne diseases

## Slide 3: Solution Overview
AI platform answering:
- Which disease will increase?
- Which districts are at risk?
- How severe? How many cases?
- What drivers? What actions?

## Slide 4: Stakeholders
WHO • State Health Departments • IDSP • Hospitals • NVBDCP

## Slide 5: Data Sources
IDSP India | WHO | Dengue/Malaria/Cholera/Chikungunya/AES/ADD  
Climate: temp, rainfall, humidity, AQI, LAI  
Geographic: state, district, population

## Slide 6: Architecture
[Insert architecture diagram from ARCHITECTURE.md]

## Slide 7: Feature Engineering
50+ features — lags, rolling stats, epidemic intelligence, climate, geospatial

## Slide 8: ML Models
Classical + Time Series + Deep Learning + Hybrid Ensembles

## Slide 9: Leakage Prevention
TimeSeriesSplit | Chronological validation | Audit reports

## Slide 10: Model Results
| Model | ROC-AUC | F1 |
| XGBoost+SMOTE | 0.XX | 0.XX |
| Stacking Ensemble | Best | Best |

## Slide 11: Explainable AI
SHAP waterfall — top drivers: rainfall, lag cases, temperature

## Slide 12: Dashboard Demo
[Screenshot] KPI cards, trend charts, risk heatmap

## Slide 13: Smart Alerts
Green → Yellow → Orange → Red  
Email + dashboard notifications

## Slide 14: Map Intelligence
India district hotspots — Leaflet visualization

## Slide 15: MLOps
MLflow tracking | Model registry | Retraining pipeline

## Slide 16: Security
JWT | RBAC | Rate limiting | bcrypt

## Slide 17: Deployment
Docker | AWS/Azure/GCP | Render/Railway ready

## Slide 18: Future Work
Real IDSP API | Mobile app | Federated learning

## Slide 19: Live Demo
Login → Dashboard → Forecast → XAI → Report PDF

## Slide 20: Thank You
Questions?  
GitHub: [repo] | Demo: localhost:3000
