import streamlit as st
import boto3
import pandas as pd
from botocore.config import Config

# إعداد الصفحة
st.set_page_config(page_title="Jaundice Detection Dashboard", layout="wide")

st.title("📊 Jaundice Detection Real-time Dashboard")
st.write("عرض تلقائي لنتائج التشخيص من DynamoDB")

# الربط مع AWS
# ملاحظة: في Streamlit Cloud هنستخدم st.secrets عشان الأمان
def get_data():
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=st.secrets["aws_access_key_id"],
            aws_secret_access_key=st.secrets["aws_secret_access_key"],
            region_name=st.secrets["aws_region"]
        )
        table = dynamodb.Table('JaundiceResults')
        response = table.scan()
        return response['Items']
    except Exception as e:
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        return []

# زر لتحديث البيانات
if st.button('🔄 تحديث البيانات'):
    data = get_data()
    if data:
        df = pd.DataFrame(data)
        # ترتيب حسب الوقت الأحدث
        df = df.sort_values(by='timestamp', ascending=False)
        
        # عرض إحصائيات سريعة
        col1, col2, col3 = st.columns(3)
        col1.metric("إجمالي الحالات", len(df))
        col2.metric("حالات Jaundice", len(df[df['result'] == 'Jaundice']))
        col3.metric("حالات Normal", len(df[df['result'] == 'Normal']))

        # عرض الجدول
        st.subheader("📋 سجل التشخيصات")
        st.dataframe(df[['image_name', 'result', 'confidence', 'timestamp']], use_container_width=True)
    else:
        st.warning("لا توجد بيانات حالياً في الجدول.")
