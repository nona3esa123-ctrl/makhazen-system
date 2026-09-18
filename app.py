import streamlit as st
from utils.auth import authenticate, init_session
from utils.ui import inject_css, render_sidebar

st.set_page_config(
    page_title="نظام المخازن",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session()
inject_css()

# ============ تسجيل الدخول ============
if st.session_state.get("user") is None:
    st.markdown("""
    <div class="main-header">
        <h1>📦 نظام إدارة المخازن المتكامل</h1>
        <p>يرجى تسجيل الدخول للمتابعة</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("📧 البريد الإلكتروني")
            password = st.text_input("🔒 كلمة المرور", type="password")
            submitted = st.form_submit_button("🔓 تسجيل الدخول", use_container_width=True)
            
            if submitted:
                user = authenticate(email, password)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
        st.info("💡 استخدم بيانات المدير المسجلة في ملف المستخدمين.")
    st.stop()

# ============ المستخدم مسجل الدخول ============
render_sidebar()

st.markdown("""
<div class="main-header">
    <h1>📦 مرحباً بك في نظام إدارة المخازن</h1>
    <p>اختر العملية من القائمة الجانبية</p>
</div>
""", unsafe_allow_html=True)

st.info("""
- **📊 لوحة التحكم**: نظرة عامة على المخزون
- **📦 الأصناف**: إدارة الأصناف
- **📥 الوارد**: تسجيل توريدات
- **📤 الصادر**: تسجيل صرفيات
- **📈 التقارير**: عرض الرصيد والتقارير
- **⚙️ الإعدادات**: إدارة المستخدمين والمخازن
""")
