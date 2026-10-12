# Unnormal Logoff / Login Anomaly Detector

<p align="center">
  <strong>Machine-learning-assisted analysis of Windows security events</strong><br>
  Detect unusual login sessions, failed authentication attempts, and potentially abnormal logoffs from exported security logs.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white">
  <img alt="Flask" src="https://img.shields.io/badge/Web%20Framework-Flask-000000?logo=flask&logoColor=white">
  <img alt="Pandas" src="https://img.shields.io/badge/Data-Pandas-150458?logo=pandas&logoColor=white">
  <img alt="Machine Learning" src="https://img.shields.io/badge/ML-scikit--learn-F7931E?logo=scikitlearn&logoColor=white">
  <img alt="Platform" src="https://img.shields.io/badge/Platform-Windows%20Event%20Logs-0078D4?logo=windows&logoColor=white">
</p>

## Overview

**Unnormal Logoff / Login Anomaly Detector** is a Python web application for reviewing exported Windows Security Event Logs and highlighting login-session patterns that may deserve further investigation.

The application accepts a CSV file, parses authentication-related events, groups events into user sessions, calculates session-related indicators, and uses a pre-trained machine-learning model to flag potentially anomalous sessions. It then presents a summary report grouped by user.

This project is intended as a learning and defensive-security tool for log analysis, security monitoring, and introductory anomaly detection.

## Key Features

- **CSV log upload:** Submit exported Windows security events through a web interface.
- **Event-based analysis:** Processes relevant Windows Security Event IDs:
  - `4624` — successful logon
  - `4672` — special privileges assigned to a new logon
  - `4634` — account logged off
  - `4647` — user-initiated logoff
  - `4625` — failed logon
- **Session indicators:** Calculates session duration, failed logons associated with a session, short sessions, unusual login times, and sessions without a matching logoff event.
- **Machine-learning scoring:** Uses a saved model and scaler to classify session feature records as normal or potentially anomalous.
- **Per-user report:** Summarizes total sessions, failed logons, short sessions, unusual-time sessions, abnormal logoffs, flagged anomalies, and average session duration.
- **Input validation and error feedback:** Checks for CSV input and reports common file-analysis problems.

> **Important:** An anomaly flag is an investigative signal, not proof of an attack or account compromise. Validate findings against the original event records and your environment's normal activity.

## How It Works

1. Export relevant Windows Security events to CSV.
2. Upload the CSV file in the Flask web interface.
3. The application parses timestamps and event IDs and extracts account names from event details.
4. Related logon and logoff events are used to derive session features.
5. The saved scaler transforms the features expected by the trained model.
6. The model flags potentially anomalous sessions and the application displays a user-level summary.

## Technology Stack

- **Python** — application logic
- **Flask** — web interface and request handling
- **Pandas** — CSV parsing and data preparation
- **Joblib** — loading serialized model artifacts
- **scikit-learn-compatible model/scaler artifacts** — anomaly classification and feature scaling
- **HTML/CSS** — web templates and styling

## Repository Structure

```text
Unnormal_logoff_login/
├── app.py                         # Flask application and log-analysis workflow
├── train_model.py                 # Model-training script
├── test_models.py                 # Model-related tests / evaluation script
├── models/                        # Pre-trained model and scaler artifacts
├── templates/                     # HTML templates for upload and report pages
├── static/
│   └── css/                       # Stylesheets
├── uploads/                       # Upload-related directory, if used by the app
├── windows_security_logs.csv       # Example Windows security-log data
├── uploaded.csv                   # CSV artifact present in the repository
├── sessions_anomaly_results.csv   # Session-analysis results
└── test_anomaly_results.csv        # Test/evaluation results
```

The exact contents may change as the project evolves. Do not commit real security logs or other sensitive data.

## Getting Started

### Prerequisites

- Python 3.10 or newer is recommended.
- Git.
- A CSV export of Windows Security Event Logs.
- The model and scaler files expected by `app.py` must exist in the `models/` directory.

### 1. Clone the repository

```bash
git clone https://github.com/451646464/Unnormal_logoff_login.git
cd Unnormal_logoff_login
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Install the packages used by the application:

```bash
python -m pip install --upgrade pip
pip install flask pandas joblib scikit-learn chardet
```

If the repository provides a `requirements.txt`, prefer installing its pinned dependencies instead:

```bash
pip install -r requirements.txt
```

### 4. Verify model files

Check that the files loaded by the application are present under `models/`. The application currently expects model artifacts named similarly to:

```text
models/
├── logon_logoff_anomaly_model.pkl
└── scaler.pkl
```

Only load serialized model files from a trusted source. Pickle/joblib files can execute code when loaded.

### 5. Run the application

```bash
python app.py
```

Open the local address printed by Flask in your terminal (commonly `http://127.0.0.1:5000`).

For local development only, keep the development server private and do not expose Flask's debug mode to an untrusted network.

## Input CSV Format

The analysis code expects a CSV export containing columns corresponding to:

| Column | Purpose |
| --- | --- |
| `Date and Time` | Timestamp for the security event |
| `Keywords` | Event details containing account information, such as `Account Name:` |
| `Event ID` | Windows Security event identifier |

Column names and timestamp formats should match the data exported from your environment. The application includes some timestamp and encoding handling, but exports can vary by Windows version, locale, and export method.

### Recommended workflow

1. Export only the event categories required for your investigation.
2. Remove unrelated personal or confidential information when possible.
3. Test the tool with a copy of the CSV, not the original evidence.
4. Compare flagged sessions with the original Windows Event Viewer records.

## Understanding the Report

The report groups results by user and includes metrics such as:

- **Total sessions:** Sessions derived from the available logon events.
- **Failed logons:** Failed authentication events associated with a derived session.
- **Short sessions:** Sessions shorter than the implementation's configured threshold.
- **Unusual-time sessions:** Sessions beginning during the time window configured by the code.
- **Abnormal logoffs:** Sessions for which the analysis did not find a later matching logoff event.
- **Anomalies:** Sessions the model classified as anomalous.
- **Average duration:** Mean derived session duration.

These values depend on the completeness and ordering of the exported logs and on the session-matching logic. Missing events, log rotation, time-zone differences, concurrent sessions, and imperfect account extraction may affect the results.

## Model Training and Testing

The repository includes `train_model.py` and `test_models.py` for model-related work. Review these scripts and the available datasets before retraining or interpreting evaluation results. For reliable evaluation, use representative labeled data, keep training and test data separate, and document the model type, features, thresholds, and metrics.

## Security and Privacy

Security logs can contain usernames, host information, and other sensitive operational details.

- Use only logs you own or are explicitly authorized to analyze.
- Run the application locally or behind an appropriately secured environment.
- Do not upload sensitive logs to public services or commit them to a public repository.
- Add upload-size limits, safe temporary-file handling, and appropriate access controls before any production deployment.
- Disable Flask debug mode outside local development.
- Treat model output as triage support; investigate alerts before taking action.

## Limitations

- Results depend on the quality and completeness of the source logs.
- Session matching is heuristic and may not correctly represent every concurrent or disconnected session.
- The model may produce false positives and false negatives.
- The project should not be treated as a replacement for a SIEM, endpoint detection platform, or full incident-response process.
- Production deployment requires additional security hardening and testing.

## Roadmap

Potential improvements include:

- Add a maintained `requirements.txt` with tested, pinned dependencies.
- Add sample sanitized CSV files and screenshots of the interface.
- Improve session correlation for concurrent logons and missing events.
- Add downloadable reports and explicit model evaluation metrics.
- Add automated tests for malformed files, timestamp formats, and edge cases.
- Improve upload validation, file-size limits, and production configuration.

## Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Open a pull request describing the change and its security impact.

## License

No license terms are specified here. Check the repository for a `LICENSE` file or add an appropriate license before redistributing or reusing the code.

## Author

Created by Rakan AL-Muliki.

---

If this project is useful to you, consider giving the repository a star.
