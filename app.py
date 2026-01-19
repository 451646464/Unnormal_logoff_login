"""from flask import Flask, render_template, request
import pandas as pd
import joblib
import re

app = Flask(__name__)

# ================= تحميل النموذج والمقياس =================
model = joblib.load("models/logon_logoff_anomaly_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# ================= دالة استخراج اسم المستخدم =================
def extract_user(text):
    if pd.isna(text):
        return "UNKNOWN"
    text = str(text)
    match = re.search(r"Account Name:\s*(\S+)", text)
    return match.group(1) if match else "UNKNOWN"

# ================= دالة تحليل الملف =================
def analyze_file(file_path):
    df = pd.read_csv(file_path)
    df["Date and Time"] = pd.to_datetime(df["Date and Time"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["Date and Time"])
    df = df.sort_values("Date and Time")
    df["user"] = df["Keywords"].apply(extract_user)

    LOGON = [4624, 4672]
    LOGOFF = [4634, 4647]
    FAILED_LOGON = [4625]

    sessions = []

    for user in df["user"].unique():
        user_df = df[df["user"] == user]
        logons = user_df[user_df["Event ID"].isin(LOGON)]
        logoffs = user_df[user_df["Event ID"].isin(LOGOFF)]
        failed = user_df[user_df["Event ID"].isin(FAILED_LOGON)]

        if logons.empty:
            continue

        for _, logon in logons.iterrows():
            next_logoff = logoffs[logoffs["Date and Time"] > logon["Date and Time"]].head(1)
            if next_logoff.empty:
                # نفترض مدة 10 دقائق إذا لم يوجد logoff
                logoff_time = logon["Date and Time"] + pd.Timedelta(minutes=10)
                abnormal_logoff = 1  # جلسة بدون logoff طبيعي
            else:
                logoff_time = next_logoff.iloc[0]["Date and Time"]
                abnormal_logoff = 0  # logoff طبيعي

            duration = (logoff_time - logon["Date and Time"]).total_seconds() / 60
            failed_before = failed[
                (failed["Date and Time"] > logon["Date and Time"]) &
                (failed["Date and Time"] < logoff_time)
            ].shape[0]

            sessions.append({
                "user": user,
                "logon_time": logon["Date and Time"],
                "logoff_time": logoff_time,
                "session_duration": round(duration, 2),
                "failed_logons": failed_before,
                "hour": logon["Date and Time"].hour,
                "day": logon["Date and Time"].weekday(),
                "unusual_time": int(logon["Date and Time"].hour < 6),
                "short_session": int(duration < 5),
                "abnormal_logoff": abnormal_logoff
            })

    sessions_df = pd.DataFrame(sessions)
    if sessions_df.empty:
        return None

    # ترتيب الأعمدة بالضبط كما تم التدريب
    feature_columns = [
        "hour", "day", "session_duration", "failed_logons",
        "unusual_time", "short_session", "abnormal_logoff"
    ]
    X_scaled = scaler.transform(sessions_df[feature_columns])
    sessions_df["anomaly"] = model.predict(X_scaled)

    # تقرير لكل مستخدم
    report = []
    for user, group in sessions_df.groupby("user"):
        report.append({
            "user": user,
            "total_sessions": len(group),
            "failed_logons": group["failed_logons"].sum(),
            "short_sessions": group["short_session"].sum(),
            "unusual_time_sessions": group["unusual_time"].sum(),
            "abnormal_logoffs": group["abnormal_logoff"].sum(),
            "anomalies": (group["anomaly"] == -1).sum(),
            "avg_duration": round(group["session_duration"].mean(), 2)
        })

    return report


# ================= الصفحة الرئيسية =================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            file_path = "uploaded.csv"
            file.save(file_path)
            report = analyze_file(file_path)
            if report is None:
                return render_template("index.html", error="❌ لم يتم العثور على جلسات صالحة في الملف.")
            return render_template("report.html", report=report)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
"""

from flask import Flask, render_template, request
import pandas as pd
import joblib
import re
import os
import chardet

app = Flask(__name__)

# ================= تحميل النموذج والمقياس =================
model = joblib.load("models/logon_logoff_anomaly_model.pkl")
scaler = joblib.load("models/scaler.pkl")


# ================= دالة استخراج اسم المستخدم =================
def extract_user(text):
    if pd.isna(text):
        return "UNKNOWN"
    text = str(text)
    match = re.search(r"Account Name:\s*(\S+)", text)
    return match.group(1) if match else "UNKNOWN"


# ================= دالة لفحص ترميز الملف =================
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']


# ================= دالة تحليل الملف =================
def analyze_file(file_path):
    try:
        # اكتشاف ترميز الملف أولاً
        encoding = detect_encoding(file_path)
        print(f"تم اكتشاف ترميز الملف: {encoding}")

        # قراءة الملف بتشفيره المناسب
        try:
            df = pd.read_csv(file_path, encoding=encoding)
        except:
            # إذا فشل، نجرب ترميزات أخرى شائعة
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252', 'cp1256']
            for enc in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    print(f"تم قراءة الملف باستخدام ترميز: {enc}")
                    break
                except:
                    continue

        # تسجيل معلومات عن الملف
        print(f"تم قراءة {len(df)} سطر من الملف")
        print(f"الأعمدة المتوفرة: {df.columns.tolist()}")

        # عرض عينة من البيانات
        print("\nعينة من أول 5 صفوف:")
        for i in range(min(5, len(df))):
            print(f"الصف {i}: {dict(df.iloc[i])}")

        # التحقق من وجود الأعمدة المطلوبة
        required_columns = ["Date and Time", "Keywords", "Event ID"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            # البحث عن أسماء أعمدة مشابهة
            available_columns = df.columns.tolist()
            print(f"الأعمدة الموجودة: {available_columns}")

            # محاولة العثور على أعمدة بأسماء مشابهة
            column_mapping = {}
            for required in missing_columns:
                for available in available_columns:
                    if required.lower() in available.lower() or available.lower() in required.lower():
                        column_mapping[required] = available
                        print(f"  وجدت عمود مشابه: '{required}' -> '{available}'")
                        break

            # إذا وجدنا أعمدة مشابهة، نعيد تسميتها
            for required, available in column_mapping.items():
                df = df.rename(columns={available: required})

        # التحقق مرة أخرى بعد إعادة التسمية
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"الأعمدة المطلوبة مفقودة: {missing_columns}. الأعمدة الموجودة: {df.columns.tolist()}"
            print(error_msg)
            return None, error_msg

        # عرض عينة من عمود التاريخ
        print("\nعينة من عمود 'Date and Time':")
        date_samples = df["Date and Time"].head(10).tolist()
        for i, date in enumerate(date_samples):
            print(f"  {i}: {repr(date)} (نوع: {type(date).__name__})")

        # تحويل التاريخ والوقت - محاولة بتنسيقات متعددة
        print("\nمحاولة تحويل التواريخ...")

        # تحويل عمود التاريخ إلى نص أولاً (في حال كان نوعه غير نصي)
        df["Date and Time"] = df["Date and Time"].astype(str).str.strip()

        # قائمة بتنسيقات التاريخ الشائعة
        date_formats = [
            "%d/%m/%Y %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%d.%m.%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",  # تنسيق أمريكي
            "%d/%m/%Y %H:%M",  # بدون ثواني
            "%d-%m-%Y %H:%M",  # بدون ثواني
            "%Y%m%d %H:%M:%S",  # بدون فواصل
            "%d/%m/%Y",  # تاريخ فقط
            "%d-%m-%Y",  # تاريخ فقط
            "%Y-%m-%d",  # تاريخ فقط
            "%d %b %Y %H:%M:%S",  # مع أشهر نصية
            "%d %B %Y %H:%M:%S",  # مع أشهر نصية كاملة
        ]

        # محاولة كل تنسيق
        for fmt in date_formats:
            try:
                temp_dates = pd.to_datetime(df["Date and Time"], format=fmt, errors='coerce')
                valid_count = temp_dates.notna().sum()
                if valid_count > len(df) * 0.5:  # إذا نجح مع أكثر من 50% من التواريخ
                    df["Date and Time"] = temp_dates
                    print(f"✓ تم تحويل {valid_count}/{len(df)} تاريخ باستخدام التنسيق: {fmt}")
                    break
            except Exception as e:
                continue

        # إذا فشلت جميع التنسيقات، نجرب التحويل التلقائي
        if df["Date and Time"].dtype != 'datetime64[ns]':
            print("محاولة التحويل التلقائي...")
            df["Date and Time"] = pd.to_datetime(df["Date and Time"], errors='coerce', dayfirst=True)

        # التحقق من التواريخ التي تم تحويلها
        valid_dates = df["Date and Time"].notna().sum()
        print(f"\nنتيجة التحويل: {valid_dates} تاريخ صالح، {len(df) - valid_dates} تاريخ غير صالح")

        if valid_dates == 0:
            # عرض أمثلة على التواريخ التي فشل تحويلها
            invalid_samples = df[df["Date and Time"].isna()]["Date and Time"].head(10).tolist()
            error_msg = f"لا يمكن تحويل التواريخ في الملف. أمثلة على التواريخ غير الصالحة: {invalid_samples[:5]}"
            print(error_msg)
            return None, error_msg

        # المتابعة مع باقي الكود...
        df = df.dropna(subset=["Date and Time"])
        df = df.sort_values("Date and Time")

        # تحويل Event ID إلى أرقام
        df["Event ID"] = pd.to_numeric(df["Event ID"], errors='coerce')
        df = df.dropna(subset=["Event ID"])
        df["Event ID"] = df["Event ID"].astype(int)

        df["user"] = df["Keywords"].apply(extract_user)

        # إحصائيات
        print(f"\nعدد الأسطر بعد التنظيف: {len(df)}")
        print(f"عدد المستخدمين: {df['user'].nunique()}")
        print(f"قيم Event ID الفريدة: {df['Event ID'].unique()}")

        LOGON = [4624, 4672]
        LOGOFF = [4634, 4647]
        FAILED_LOGON = [4625]

        sessions = []

        for user in df["user"].unique():
            user_df = df[df["user"] == user]
            logons = user_df[user_df["Event ID"].isin(LOGON)]
            logoffs = user_df[user_df["Event ID"].isin(LOGOFF)]
            failed = user_df[user_df["Event ID"].isin(FAILED_LOGON)]

            print(f"المستخدم {user}: {len(logons)} حدث تسجيل دخول")

            if logons.empty:
                continue

            for idx, logon in logons.iterrows():
                next_logoff = logoffs[logoffs["Date and Time"] > logon["Date and Time"]].head(1)
                if next_logoff.empty:
                    logoff_time = logon["Date and Time"] + pd.Timedelta(minutes=10)
                    abnormal_logoff = 1
                else:
                    logoff_time = next_logoff.iloc[0]["Date and Time"]
                    abnormal_logoff = 0

                duration = (logoff_time - logon["Date and Time"]).total_seconds() / 60
                failed_before = failed[
                    (failed["Date and Time"] > logon["Date and Time"]) &
                    (failed["Date and Time"] < logoff_time)
                    ].shape[0]

                sessions.append({
                    "user": user,
                    "logon_time": logon["Date and Time"],
                    "logoff_time": logoff_time,
                    "session_duration": round(duration, 2),
                    "failed_logons": failed_before,
                    "hour": logon["Date and Time"].hour,
                    "day": logon["Date and Time"].weekday(),
                    "unusual_time": int(logon["Date and Time"].hour < 6),
                    "short_session": int(duration < 5),
                    "abnormal_logoff": abnormal_logoff
                })

        sessions_df = pd.DataFrame(sessions)
        print(f"\nتم استخراج {len(sessions_df)} جلسة")

        if sessions_df.empty:
            return None, "تم تحليل الملف ولكن لم يتم العثور على أحداث تسجيل دخول (Event ID: 4624 أو 4672)."

        # المتابعة مع باقي الكود...
        feature_columns = [
            "hour", "day", "session_duration", "failed_logons",
            "unusual_time", "short_session", "abnormal_logoff"
        ]

        X_scaled = scaler.transform(sessions_df[feature_columns])
        sessions_df["anomaly"] = model.predict(X_scaled)

        # تقرير لكل مستخدم
        report = []
        for user, group in sessions_df.groupby("user"):
            report.append({
                "user": user,
                "total_sessions": len(group),
                "failed_logons": group["failed_logons"].sum(),
                "short_sessions": group["short_session"].sum(),
                "unusual_time_sessions": group["unusual_time"].sum(),
                "abnormal_logoffs": group["abnormal_logoff"].sum(),
                "anomalies": (group["anomaly"] == -1).sum(),
                "avg_duration": round(group["session_duration"].mean(), 2)
            })

        print(f"✓ تم إنشاء تقرير لـ {len(report)} مستخدم")
        return report, None

    except Exception as e:
        print(f"❌ خطأ أثناء تحليل الملف: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, f"خطأ أثناء معالجة الملف: {str(e)}"


# ================= الصفحة الرئيسية =================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            # التحقق من نوع الملف
            if not file.filename.lower().endswith('.csv'):
                return render_template("index.html", error="❌ يرجى تحميل ملف CSV فقط.")

            file_path = "uploaded.csv"
            file.save(file_path)

            # التحقق من حجم الملف
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return render_template("index.html", error="❌ الملف فارغ.")

            report, error = analyze_file(file_path)

            # تنظيف الملف المؤقت
            try:
                os.remove(file_path)
            except:
                pass

            if error:
                return render_template("index.html", error=error)

            if report is None or len(report) == 0:
                return render_template("index.html", error="❌ لم يتم العثور على جلسات صالحة في الملف.")

            return render_template("report.html", report=report)
        else:
            return render_template("index.html", error="❌ لم يتم تحميل ملف.")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)