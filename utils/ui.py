import streamlit as st

def inject_css():
    """حقن CSS لإخفاء القائمة الإنجليزية وتنسيق الصفحة"""
    st.markdown("""
    <style>
        * { font-family: 'Cairo', 'Tahoma', sans-serif; }
        
        /* إخفاء القائمة الإنجليزية بجميع الطرق الممكنة */
        [data-testid="stSidebarNav"] { display: none !important; }
        [data-testid="stSidebarNavItems"] { display: none !important; }
        [data-testid="stSidebarNavSeparator"] { display: none !important; }
        section[data-testid="stSidebarNav"] { display: none !important; }
        nav[data-testid="stSidebarNav"] { display: none !important; }
        
        /* تنسيق الأزرار */
        .stButton > button {
            background-color: #f0f4f8;
            color: #1a3a5c;
            border-radius: 8px;
            padding: 10px 15px;
            font-weight: bold;
            border: 1px solid #cbd5e1;
            text-align: right;
        }
        .stButton > button:hover { 
            background-color: #2b7a62; 
            color: white;
        }
        .logout-btn > button {
            background-color: #2b7a62 !important;
            color: white !important;
        }
        .main-header {
            background: linear-gradient(135deg, #2b7a62, #1a3a5c);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
        }
    </style>
    """, unsafe_allow_html=True)


def render_sidebar():
    """عرض الشريط الجانبي العربي"""
    user = st.session_state.get("user")
    if not user:
        return
    
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:#f0f4f8; border-radius:10px;">
            <h3 style="margin:5px;">👤 {user['name']}</h3>
            <p style="color:#2b7a62; margin:5px;">{user['role']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📋 القائمة الرئيسية")
        
        if st.button("📊 لوحة التحكم", use_container_width=True, key="nav_dash"):
            st.switch_page("pages/1_Dashboard.py")
        if st.button("📦 الأصناف", use_container_width=True, key="nav_items"):
            st.switch_page("pages/2_Items.py")
        if st.button("📥 الوارد", use_container_width=True, key="nav_in"):
            st.switch_page("pages/3_Incoming.py")
        if st.button("📤 الصادر", use_container_width=True, key="nav_out"):
            st.switch_page("pages/4_Outgoing.py")
        if st.button("📈 التقارير", use_container_width=True, key="nav_rep"):
            st.switch_page("pages/5_Reports.py")
        if user["role"] == "مدير":
            if st.button("⚙️ الإعدادات", use_container_width=True, key="nav_set"):
                st.switch_page("pages/6_Settings.py")
        
        st.markdown("---")
        if st.button("🚪 تسجيل الخروج", use_container_width=True, key="nav_logout"):
            st.session_state["user"] = None
            st.switch_page("app.py")


def setup_page(title, icon="📄"):
    """دالة موحدة لكل صفحة: تكوين الصفحة + CSS + الشريط الجانبي"""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    inject_css()
    render_sidebar()
