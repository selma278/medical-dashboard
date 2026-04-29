import streamlit as st
import boto3
import pandas as pd
from botocore.config import Config

# 1. إعداد الصفحة
st.set_page_config(page_title="Jaundice Detection Dashboard", layout="wide")

st.title("📊 Jaundice Detection Real-time Dashboard")
st.write("عرض تلقائي لنتائج التشخيص من DynamoDB")

# 2. دالة جلب البيانات من DynamoDB
def get_data():
    try:
        # التأكد من وجود المفاتيح في Secrets
        if "aws_access_key_id" not in st.secrets:
            st.error("❌ عطل فني: مفاتيح الوصول (Secrets) غير مكتملة في إعدادات Streamlit.")
            return []

        # الاتصال بـ AWS باستخدام البيانات السرية
        session = boto3.Session(
            aws_access_key_id=st.secrets["aws_access_key_id"],
            aws_secret_access_key=st.secrets["aws_secret_access_key"],
            region_name=st.secrets.get("aws_region", "us-east-1")
        )
        
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table('JaundiceResults')
        
        # جلب البيانات
        response = table.scan()
        return response.get('Items', [])

    except Exception as e:
        st.error(f"⚠️ خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        return []

# 3. واجهة العرض
if st.button('🔄 تحديث البيانات'):
    with st.spinner('جاري جلب البيانات من DynamoDB...'):
        data = get_data()
        
        if data:
            # تحويل البيانات لجدول Pandas
            df = pd.DataFrame(data)
            
            # ترتيب حسب الوقت (الأحدث فوق)
            if 'timestamp' in df.columns:
                df = df.sort_values(by='timestamp', ascending=False)
            
            # عرض عدادات سريعة
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي الفحوصات", len(df))
            with col2:
                j_count = len(df[df['result'] == 'Jaundice']) if 'result' in df.columns else 0
                st.metric("حالات إصابة", j_count, delta_color="inverse")
            with col3:
                n_count = len(df[df['result'] == 'Normal']) if 'result' in df.columns else 0
                st.metric("حالات سليمة", n_count)

            st.divider()

            # تنسيق الجدول للعرض
            # هنختار الأعمدة المهمة بس لو موجودة
            cols_to_show = [c for c in ['image_name', 'result', 'confidence', 'timestamp'] if c in df.columns]
            
            st.subheader("📋 سجل التشخيصات الأخير")
            st.dataframe(df[cols_to_show], use_container_width=True)
            
        else:
            st.info("💡 لا توجد بيانات حالياً. تأكد من رفع صور على S3 وتشغيل الـ Lambda.")

# تذييل الصفحة
st.caption("نظام تشخيص الصفراء الذكي - جميع البيانات يتم تحديثها لحظياً.")
