import pandas as pd
import re
import joblib
from sklearn.preprocessing import StandardScaler
from weasyprint import HTML
from datetime import datetime

# ================= تحميل النموذج و scaler =================
model = joblib.load("models/logon_logoff_anomaly_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# ================= دالة استخراج اسم المستخدم =================
def extract_user(text):
    if pd.isna(text):
        return "UNKNOWN"
    match = re.search(r"Account Name:\s*(\S+)", str(text))
    return match.group(1) if match else "UNKNOWN"

# ================= دالة اختبار ملف CSV وعرض تقرير تفصيلي =================
def test_logs_detailed_pdf(csv_file, output_pdf="detailed_anomaly_report.pdf"):
    df = pd.read_csv(csv_file)
    df["Date and Time"] = pd.to_datetime(df["Date and Time"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date and Time"])
    df = df.sort_values("Date and Time")
    df["user"] = df["Keywords"].apply(extract_user)

    # Event IDs
    LOGON = [4624]
    LOGOFF = [4634, 4647]
    FAILED_LOGON = [4625]

    sessions = []

    for user in df["user"].unique():
        user_df = df[df["user"] == user]
        logons = user_df[user_df["Event ID"].isin(LOGON)]
        logoffs = user_df[user_df["Event ID"].isin(LOGOFF)]
        failed = user_df[user_df["Event ID"].isin(FAILED_LOGON)]

        for _, logon in logons.iterrows():
            next_logoff = logoffs[logoffs["Date and Time"] > logon["Date and Time"]].head(1)
            if next_logoff.empty:
                logoff_time = logon["Date and Time"] + pd.Timedelta(minutes=10)
                abnormal_logoff = 1
            else:
                logoff_time = next_logoff.iloc[0]["Date and Time"]
                abnormal_logoff = 0

            failed_before = failed[
                (failed["Date and Time"] > logon["Date and Time"]) &
                (failed["Date and Time"] < logoff_time)
            ].shape[0]

            duration = (logoff_time - logon["Date and Time"]).total_seconds() / 60

            sessions.append({
                "user": user,
                "logon_time": logon["Date and Time"],
                "logoff_time": logoff_time,
                "session_duration": round(duration, 2),
                "failed_logons": failed_before,
                "abnormal_logoff": abnormal_logoff,
                "hour": logon["Date and Time"].hour,
                "day": logon["Date and Time"].weekday()
            })

    sessions_df = pd.DataFrame(sessions)
    if sessions_df.empty:
        print("❌ لا توجد جلسات يمكن اختبارها في الملف.")
        return

    # Feature Engineering
    sessions_df["unusual_time"] = (sessions_df["hour"] < 6).astype(int)
    sessions_df["short_session"] = (sessions_df["session_duration"] < 5).astype(int)

    features = [
        "hour",
        "day",
        "session_duration",
        "failed_logons",
        "unusual_time",
        "short_session",
        "abnormal_logoff"
    ]

    X_scaled = scaler.transform(sessions_df[features])
    preds = model.predict(X_scaled)
    sessions_df["anomaly"] = preds  # -1 = anomaly

    # ================= إنشاء HTML لتقرير تفصيلي =================
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #dddddd; padding: 6px; text-align: center; font-size: 12px; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            h2 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h2>Detailed Windows Security Logs Anomaly Report</h2>
        <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <table>
            <tr>
                <th>User</th>
                <th>Logon Time</th>
                <th>Logoff Time</th>
                <th>Session Duration (min)</th>
                <th>Failed Logons</th>
                <th>Abnormal Logoff</th>
                <th>Short Session</th>
                <th>Unusual Time</th>
                <th>Anomaly</th>
            </tr>
    """

    for _, row in sessions_df.iterrows():
        issues = []
        if row["failed_logons"] > 0:
            issues.append(f"Failed Logons: {row['failed_logons']}")
        if row["abnormal_logoff"] == 1:
            issues.append("Abnormal Logoff")
        if row["short_session"] == 1:
            issues.append("Short Session")
        if row["unusual_time"] == 1:
            issues.append("Unusual Time")
        anomaly_text = "Yes" if row["anomaly"] == -1 else "No"
        html_content += f"""
            <tr>
                <td>{row['user']}</td>
                <td>{row['logon_time']}</td>
                <td>{row['logoff_time']}</td>
                <td>{row['session_duration']}</td>
                <td>{row['failed_logons']}</td>
                <td>{row['abnormal_logoff']}</td>
                <td>{row['short_session']}</td>
                <td>{row['unusual_time']}</td>
                <td>{anomaly_text}</td>
            </tr>
        """

    html_content += """
        </table>
    </body>
    </html>
    """

    # ================= تحويل HTML إلى PDF =================
    HTML(string=html_content).write_pdf(output_pdf)
    print(f"✅ Detailed PDF report generated: {output_pdf}")


# ================= مثال على الاستخدام =================
# استبدل 'new_logs.csv' باسم ملفك الجديد
test_logs_detailed_pdf("windows_security_logs.csv", output_pdf="detailed_anomaly_report.pdf")
