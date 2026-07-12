# 🧬 QUBE Predict

> Open-source AI framework for drug response prediction, cancer response modeling, and biomedical machine learning.

QUBE Predict is a modular Streamlit application built for researchers, students, and developers working with drug-response prediction datasets. It provides an interactive interface for training, evaluating, and benchmarking predictive models on pharmacogenomics datasets.

---

# 🚀 Features

- 🧬 Single sample drug-response prediction
- 📦 Batch prediction from CSV files
- 📊 Interactive dashboard
- 📈 Model diagnostics
- 🧪 Validation reports
- 📑 PDF report generation
- ⚙️ Modular backend architecture
- 🎯 Drug library browser
- 📉 Performance metrics
- 🔬 Biomedical machine learning workflow
- 🎨 Modern Streamlit interface

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/gulfamh1999-afk/Qube-Predict.git

cd Qube-Predict
```

Install dependencies

```bash
pip install -r requirements.txt
```

Launch the application

```bash
streamlit run app.py
```

---

# ▶️ Quick Start

1. Launch Streamlit.
2. Upload a supported dataset.
3. Select prediction mode.
4. Train or load a model.
5. Generate predictions.
6. View metrics.
7. Export reports.

---

# 📊 Supported Datasets

QUBE Predict currently supports biomedical datasets including:

- CCLE Gene Expression
- GDSC Drug Response
- CCLE + GDSC merged datasets
- User-provided CSV datasets
- Gene expression matrices
- Drug sensitivity datasets

Typical input includes:

- Gene expression features
- Drug name
- IC50 values
- Binary response labels
- Continuous response values

---

# 🏗️ Project Architecture

```
Qube-Predict/

├── app.py
├── backend/
│   ├── config.py
│   ├── data.py
│   ├── metrics.py
│   ├── qube_wrapper.py
│   └── state.py
│
├── pages/
│   ├── dashboard.py
│   ├── single_prediction.py
│   ├── batch_prediction.py
│   ├── validation_results.py
│   ├── model_diagnostics.py
│   ├── drug_library.py
│   └── settings.py
│
├── reports/
├── validation/
├── ui/
├── assets/
├── models/
└── requirements.txt
```

---

# 🧠 Technologies

- Python
- Streamlit
- Scikit-learn
- Pandas
- NumPy
- Plotly
- Matplotlib
- Joblib

---

# 🎯 Current Capabilities

- Drug response prediction
- Model evaluation
- Classification metrics
- Regression metrics
- Interactive visualization
- Report generation
- Biomedical data preprocessing

---

# 🛣️ Roadmap

Future development may include:

- Additional machine learning models
- Deep learning integration
- AutoML pipelines
- Explainable AI (SHAP)
- Survival analysis
- Multi-omics support
- Cloud deployment
- API integration

---

# 🤝 Contributing

Contributions are welcome.

You can contribute by:

- Improving documentation
- Fixing bugs
- Adding datasets
- Implementing new algorithms
- Improving visualizations
- Creating tutorials

Fork the repository, create a feature branch, and submit a Pull Request.

---

# 📄 License

This project is released under the MIT License.

See the LICENSE file for details.

---

# 📚 Citation

If you use QUBE Predict in your research, please cite the repository:

```bibtex
@software{qube_predict,
  author = {Gulfam Hussain},
  title = {QUBE Predict},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/gulfamh1999-afk/Qube-Predict}
}
```

---

# ⭐ Support

If you find this project useful:

- ⭐ Star the repository
- 🍴 Fork the project
- 🐞 Report issues
- 💡 Suggest new features

---

# 👨‍💻 Author

**Gulfam Hussain**

GitHub:

https://github.com/gulfamh1999-afk

---

## Acknowledgements

This project builds upon open scientific datasets and the Python scientific ecosystem, including Streamlit, Scikit-learn, Pandas, NumPy, and related open-source libraries.

---

**QUBE Predict**

Open-source AI framework for biomedical machine learning and drug response prediction.
