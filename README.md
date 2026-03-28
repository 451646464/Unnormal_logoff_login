# 🛡️ Abnormal Logon/Logoff Session Analysis

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> A professional tool for analyzing Windows event CSV files to detect anomalous sessions using machine learning.

---

## 📖 About

This project analyzes CSV files containing Windows system events (such as logon and logoff events) and uses a pre-trained machine learning model to identify anomalous sessions. It provides a simple web interface for uploading files and viewing detailed reports per user.

### ✨ Features
- Easy CSV file upload.
- Automatic extraction of logon/logoff sessions.
- Calculates session duration and counts failed logon attempts.
- Detects anomalous sessions using a pre-trained machine learning model.
- Provides a comprehensive report per user including:
  - Total number of sessions.
  - Total failed logon attempts.
  - Number of short sessions.
  - Number of sessions during unusual hours.
  - Number of abnormal logoffs (sessions without a matching logoff event).
  - Number of anomalous sessions detected by the model.
  - Average session duration.

---

## 📥 Installation & Usage

### 1. Requirements
- Python 3.8 or higher.
- pip (Python package manager).

### 2. Clone the Repository
```bash
git clone https://github.com/451646464/Unnormal_logoff_login.git
cd Unnormal_logoff_login
```

### 3. Create a Virtual Environment (Recommended)
```bash
python -m venv venv
# Activate the environment:
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```
If `requirements.txt` does not exist, create it with the following content:
```txt
Flask==2.0.3
pandas==1.5.3
joblib==1.2.0
scikit-learn==1.2.2
chardet==5.1.0
```

### 5. Run the Application
```bash
python app.py
```
Once running, open your browser and go to `http://127.0.0.1:5000/`.

### 6. Use the Tool
- Select a CSV file containing Windows events (must include columns: `Date and Time`, `Keywords`, `Event ID`).
- Click the "Analyze" button.
- A detailed report for each user will be displayed.

---

## 📂 Project Structure
```
Unnormal_logoff_login/
├── app.py                      # Main Flask application
├── models/                     # Pre-trained models and scaler
│   ├── logon_logoff_anomaly_model.pkl
│   └── scaler.pkl
├── templates/                  # HTML templates
│   ├── index.html              # File upload page
│   └── report.html             # Report page
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── LICENSE                     # Project license (optional)
```

---

## 📄 Input CSV Format
The CSV file must contain at least the following columns:
- **Date and Time**: The timestamp of the event (e.g., `23/05/2024 14:30:00`).
- **Keywords**: Field containing the username in the format `Account Name: username`.
- **Event ID**: The Windows event ID (e.g., `4624` for logon, `4634` for logoff, `4625` for failed logon).

### Example Row:
```
Date and Time,Keywords,Event ID
23/05/2024 14:30:00,"Account Name: JohnDoe",4624
```

---

## 🔧 Troubleshooting
- **Missing required columns**: Ensure your CSV has `Date and Time`, `Keywords`, and `Event ID`. The tool attempts to auto‑detect similar column names.
- **Incorrect date format**: The system tries multiple common formats. If dates still fail, check the format in your file.
- **Model files not found**: Verify that the `models/` folder exists and contains the two `.pkl` files.
- **No usernames extracted**: The `Keywords` column must contain the text `Account Name:` followed by the actual username.

---

## 🤝 Contributing
You can contribute by:
- Opening an **Issue** to suggest improvements or report bugs.
- Submitting a **Pull Request** with new features or fixes.

---

## 📜 License
This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

## 📧 Contact
For any inquiries, please use the [GitHub Issues](https://github.com/451646464/Unnormal_logoff_login/issues) page.

---

**Developed by:** Rakan Al-Maliki  
**Last update:** March 2026
