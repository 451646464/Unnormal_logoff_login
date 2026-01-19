import pandas as pd
import re
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# ================= تحميل البيانات =================
df = pd.read_csv("windows_security_logs.csv")
df["Date and Time"] = pd.to_datetime(df["Date and Time"], dayfirst=True, errors="coerce")
df = df.dropna(subset=["Date and Time"])
df = df.sort_values("Date and Time")


# ================= استخراج اسم المستخدم =================
def extract_user(text):
    if pd.isna(text):
        return "UNKNOWN"
    match = re.search(r"Account Name:\s*(\S+)", str(text))
    return match.group(1) if match else "UNKNOWN"


df["user"] = df["Keywords"].apply(extract_user)

# ================= Event IDs =================
LOGON = [4624]
LOGOFF = [4634, 4647]
FAILED_LOGON = [4625]

# ================= بناء الجلسات =================
sessions = []

for user in df["user"].unique():
    user_df = df[df["user"] == user]

    logons = user_df[user_df["Event ID"].isin(LOGON)]
    logoffs = user_df[user_df["Event ID"].isin(LOGOFF)]
    failed = user_df[user_df["Event ID"].isin(FAILED_LOGON)]

    for _, logon in logons.iterrows():
        # إيجاد أول Logoff بعد Logon
        next_logoff = logoffs[logoffs["Date and Time"] > logon["Date and Time"]].head(1)

        # إذا لم يوجد Logoff، نفترض مدة الجلسة = 10 دقائق (يمكن تعديلها)
        if next_logoff.empty:
            logoff_time = logon["Date and Time"] + pd.Timedelta(minutes=10)
            abnormal_logoff = 1  # مؤشر أن Logoff غير طبيعي
        else:
            logoff_time = next_logoff.iloc[0]["Date and Time"]
            abnormal_logoff = 0

        # عدد محاولات الدخول الفاشلة ضمن الجلسة
        failed_before = failed[
            (failed["Date and Time"] > logon["Date and Time"]) &
            (failed["Date and Time"] < logoff_time)
            ].shape[0]

        # مدة الجلسة بالدقائق
        duration = (logoff_time - logon["Date and Time"]).total_seconds() / 60

        sessions.append({
            "user": user,
            "logon_time": logon["Date and Time"],
            "logoff_time": logoff_time,
            "hour": logon["Date and Time"].hour,
            "day": logon["Date and Time"].weekday(),
            "session_duration": duration,
            "failed_logons": failed_before,
            "abnormal_logoff": abnormal_logoff
        })

# ================= إنشاء DataFrame للجلسات =================
sessions_df = pd.DataFrame(sessions)
print("✅ Sessions Created:", len(sessions_df))

# ================= Feature Engineering =================
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

# ================= Scaling =================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(sessions_df[features])

# ================= تدريب نموذج Isolation Forest =================
model = IsolationForest(
    n_estimators=300,
    contamination=0.1,
    random_state=42
)
model.fit(X_scaled)

# ================= تقييم النتائج =================
scores = model.decision_function(X_scaled)
preds = model.predict(X_scaled)

sessions_df["anomaly_score"] = scores
sessions_df["anomaly"] = preds  # -1 = anomaly, 1 = normal

total_sessions = len(sessions_df)
anomalies = (preds == -1).sum()
normal = (preds == 1).sum()

print("\n====== Training Evaluation ======")
print(f"Total Sessions     : {total_sessions}")
print(f"Normal Sessions    : {normal}")
print(f"Anomalies Detected : {anomalies}")
print(f"Avg Anomaly Score  : {scores.mean():.4f}")

# ================= حفظ النموذج والنتائج =================
joblib.dump(model, "models/logon_logoff_anomaly_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
sessions_df.to_csv("sessions_anomaly_results.csv", index=False)

print("✅ Model, scaler & results saved successfully")
