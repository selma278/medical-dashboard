import streamlit as st
import boto3
import pandas as pd
import os
import json
from dotenv import load_dotenv

# 1. تحميل الإعدادات من ملف .env
load_dotenv()

# 2. إعدادات الصفحة
st.set_page_config(page_title="Secure Medical Dashboard", layout="wide")

# --- دالة تسجيل الدخول (Login System) ---
def login():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.sidebar.title("🔒 Doctor Access")
        with st.sidebar.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                # يمكنك تغيير اليوزر والباسورد هنا
                if username == "admin" and password == "salma2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.sidebar.error("❌ Invalid Credentials")
    
    return st.session_state["authenticated"]

# تحقق من حالة تسجيل الدخول
if not login():
    st.title("🏥 Smart Medical Monitoring System")
    st.info("Please enter your credentials in the sidebar to access patient data.")
    st.image("https://img.freepik.com/free-vector/security-concept-illustration_114360-1098.jpg", width=500)
    st.stop()

# --- لو الدخول ناجح، الكود اللي تحت هيشتغل ---

# 3. إعداد الاتصال بـ AWS
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bucket_name = os.getenv('BUCKET_NAME')

st.success(f"🔓 Welcome Dr. Salma | Connected to Cloud: {bucket_name}")
st.title("🏥 Real-Time Patient Monitoring")
st.markdown("---")

try:
    # 4. جلب البيانات من S3
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' in response:
        all_data = []
        for obj in response['Contents']:
            if obj['Key'].endswith('.json'):
                file_obj = s3.get_object(Bucket=bucket_name, Key=obj['Key'])
                file_content = file_obj['Body'].read().decode('utf-8')
                data = json.loads(file_content)
                all_data.append(data)
        
        # تحويل البيانات لـ DataFrame وتنظيفها
        df = pd.DataFrame(all_data)
        df = df.fillna(0) # استبدال أي NaN بـ 0

        # 5. عرض كروت المرضى (Patient Cards)
        st.subheader("👨‍⚕️ Current Patient Status")
        for index, row in df.iterrows():
            status = row.get('status', 'Stable')
            # تحديد لون الحالة
            if status == "Critical":
                color = "#dc3545"
            elif status == "Warning":
                color = "#ffc107"
            else:
                color = "#28a745"
            
            with st.expander(f"📋 {row['name']} (ID: {row['patient_id']}) - Status: {status}"):
                c1, c2, c3, c4, c5 = st.columns(5)
                c1.metric("Heart Rate", f"{int(row.get('heart_rate', 0))} BPM")
                c2.metric("Oxygen", f"{int(row.get('oxygen_level', 0))}%")
                c3.metric("Sugar", f"{int(row.get('sugar_blood', 0))} mg/dL")
                c4.metric("Temp", f"{row.get('temperature', 0)}°C")
                c5.metric("Blood Pressure", row.get('blood_pressure', 'N/A'))

        st.markdown("---")

        # 6. قسم الجرافات المتنوعة (Diversified Charts)
        st.subheader("📊 Vital Signs Visualization")
        
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.write("### ❤️ Heart Rate Tracker (Line)")
            st.line_chart(df.set_index('name')['heart_rate'])
        with row1_col2:
            st.write("### 🌬️ Oxygen Saturation (Area)")
            st.area_chart(df.set_index('name')['oxygen_level'])

        st.markdown("---")

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.write("### 🩸 Blood Sugar (Bar)")
            st.bar_chart(df.set_index('name')['sugar_blood'])
        with row2_col2:
            st.write("### 🌡️ Temperature (Bar)")
            st.bar_chart(df.set_index('name')['temperature'])

        st.markdown("---")

        # 7. الجدول الكامل للبيانات
        st.subheader("📑 Full Medical Records Table")
        st.dataframe(df, use_container_width=True)

    else:
        st.warning("⚠️ No data files found in your S3 Bucket.")

except Exception as e:
    st.error(f"❌ Connection Error: {e}")

# زر لتسجيل الخروج في الجنب
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.rerun()