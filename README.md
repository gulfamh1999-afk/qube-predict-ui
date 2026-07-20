# 🧬 QUBE Predict

> **Cloud-Based Biomedical AI Platform for Drug Response Prediction**

QUBE Predict is a production-ready biomedical machine learning platform that enables researchers, biotechnology companies, pharmaceutical organizations, and academic institutions to predict drug response from molecular and gene-expression data.

Built with **FastAPI**, **Streamlit**, **PostgreSQL**, and **Scikit-learn**, QUBE Predict combines secure cloud infrastructure with machine learning to deliver fast, scalable, and reproducible drug-response predictions through an intuitive web interface and REST API.

---

# 🚀 Features

### 🔬 Biomedical Prediction

- 🧬 Single Sample Drug Response Prediction
- 📦 Batch Prediction from CSV Files
- 🎯 Drug-Specific Machine Learning Models
- 📈 Probability & Response Score
- ⭐ Treatment Suitability Rating
- 📊 Confidence Estimation
- 🏥 Clinical Interpretation
- ⚠️ Treatment Failure Risk Assessment

---

### ☁️ Cloud Platform

- 🔐 JWT Authentication
- 🔑 API Key Management
- 💳 Razorpay Subscription Billing
- 📊 Usage Dashboard
- 📈 Billing History
- 👤 User Profile Management
- 🚀 REST API
- 📉 Prediction Usage Tracking

---

### 📊 Machine Learning

- 327+ Pre-trained Biomedical Models
- Scikit-learn Classification Pipelines
- Drug Response Prediction
- Batch Inference
- Model Registry
- Validation Metrics
- Performance Benchmarking

---

# 🌐 Live Platform

### Frontend

https://qube-predict.streamlit.app

### Backend API

https://qube-predict.onrender.com

---

# 🏗 Platform Architecture

```
                Streamlit Cloud
                     │
                     ▼
          QUBE Predict Web Platform
                     │
             Secure REST API
                     │
                     ▼
         FastAPI Backend (Render)
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
 PostgreSQL Database       Machine Learning Models
        │                         │
        └────────────┬────────────┘
                     ▼
            Drug Response Engine
```

---

# 🔬 Example Prediction Workflow

1. Create an account
2. Subscribe to a prediction plan
3. Receive an API Key
4. Upload molecular or gene-expression data
5. Select a drug
6. Run prediction
7. Receive:

- Drug Response Prediction
- Probability Score
- Confidence Level
- Treatment Suitability
- Clinical Interpretation
- Downloadable Results

---

# 📦 REST API Example

## Request

```http
POST /api/v1/predict
```

```json
{
    "drug": "(5Z)-7-Oxozeaenol",
    "sample": {
        "...": "..."
    }
}
```

## Response

```json
{
    "drug": "(5Z)-7-Oxozeaenol",
    "prediction": "Moderately Sensitive",
    "probability": 0.7267,
    "response_score": 72.7,
    "confidence": "Moderate",
    "confidence_score": 0.7267,
    "treatment_suitability": "Potential Candidate",
    "treatment_stars": 3,
    "treatment_rating": "★★★☆☆",
    "treatment_failure_risk": "Moderate",
    "clinical_interpretation": "...",
    "disclaimer": "For research and clinical decision support only."
}
```

---

# 💻 Installation

Clone the repository

```bash
git clone https://github.com/gulfamh1999-afk/Qube-Predict.git

cd Qube-Predict
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run locally

```bash
streamlit run app.py
```

---

# 📂 Project Structure

```
Qube-Predict/

├── app.py
├── backend/
│   ├── backend_api_server.py
│   ├── auth.py
│   ├── billing.py
│   ├── database.py
│   ├── predictor.py
│   ├── model_registry.py
│   ├── models.py
│   └── schemas.py
│
├── views/
│   ├── dashboard.py
│   ├── single_prediction.py
│   ├── batch_prediction.py
│   ├── billing.py
│   ├── billing_history.py
│   ├── api_keys.py
│   ├── profile.py
│   └── contact.py
│
├── models/
├── assets/
├── reports/
├── requirements.txt
└── README.md
```

---

# 🧠 Technology Stack

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Razorpay API

### Machine Learning

- Scikit-learn
- Pandas
- NumPy
- Joblib

### Frontend

- Streamlit
- Plotly
- Matplotlib

### Deployment

- Render
- Streamlit Cloud

---

# 📊 Supported Data

QUBE Predict supports molecular and pharmacogenomics datasets including:

- Gene Expression Matrices
- Drug Response Data
- CCLE
- GDSC
- CCLE + GDSC Merged Datasets
- User Uploaded CSV Files

---

# 🎯 Current Capabilities

✅ Secure User Authentication

✅ Subscription Billing

✅ API Key Generation

✅ Cloud Prediction API

✅ Single Sample Prediction

✅ Batch Prediction

✅ Clinical Prediction Reports

✅ Usage Monitoring

✅ Billing Dashboard

✅ Drug Response Modelling

---

# 🛣 Roadmap

Upcoming features include:

- Explainable AI (SHAP)
- Multi-omics Integration
- Survival Analysis
- PDF Clinical Reports
- Model Versioning
- Enterprise SSO
- Team Workspaces
- Docker Deployment
- Kubernetes Support

---

# 📄 License

This project is released under the MIT License.

See the LICENSE file for details.

---

# 📚 Citation

If you use QUBE Predict in your research, please cite:

```bibtex
@software{qube_predict,
  author = {Gulfam Hussain},
  title = {QUBE Predict},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/gulfamh1999-afk/Qube-Predict}
}
```
# 📄 Technical Paper

The research paper describing the methodology, experimental evaluation, and validation of **QUBE Predict** is publicly available on Zenodo.

**Title**

> **QUBE Predict: A Graph-Based Quantum-Inspired Machine Learning Framework for Drug Response Prediction**

**DOI**

https://doi.org/10.5281/zenodo.21455765

**Zenodo Record**

https://zenodo.org/records/21455765

The paper describes:

- Graph-based biological descriptor generation
- Quantum-inspired representation learning
- Drug response prediction methodology
- Experimental evaluation on CCLE and GDSC pharmacogenomic datasets
- Statistical validation and leakage control experiments
- Modular machine learning framework design
---

# 🤝 Contributing

Contributions are welcome.

You can contribute by:

- Improving documentation
- Reporting bugs
- Adding biomedical datasets
- Enhancing machine learning models
- Improving the user interface
- Optimizing prediction performance

Please fork the repository, create a feature branch, and submit a Pull Request.

---

# 👨‍💻 Author

**Gulfam Hussain**

GitHub:

https://github.com/gulfamh1999-afk

---

# ⭐ Support

If you find QUBE Predict useful:

⭐ Star the repository

🍴 Fork the project

🐞 Report Issues

💡 Suggest New Features

---

## 🧬 QUBE Predict

**Advancing precision medicine through scalable biomedical machine learning.**
