import streamlit as st
from utils.auth import login_required, hash_password
from utils.sheets import read_sheet, append_row

login_required(role=["مدير"])
st.title("⚙️ الإعدادات")

tab1, tab2, tab3 = st.tabs(["👥 المستخدمين", "🏢 المخازن", "🚚 الموردين"])

with tab1:
    users_df = read_sheet("users")
    if not users_df.empty:
        st.dataframe(users_df.drop(columns=["كلمة المرور"], errors="ignore"), use_container_width=True)
    
    with st.form("add_user"):
        st.markdown("### ➕ إضافة مستخدم")
        col1, col2 = st.columns(2)
        email = col1.text_input("البريد الإلكتروني")
        name = col2.text_input("الاسم")
        password = col1.text_input("كلمة المرور", type="password")
        role = col2.selectbox("الدور", ["مدير", "أمين مخزن", "مراجع"])
        
        if st.form_submit_button("إضافة"):
            if email and password and name:
                append_row("users", {
                    "الإيميل": email,
                    "كلمة المرور": hash_password(password),
                    "الاسم": name,
                    "الدور": role
                })
                st.success("✅ تمت الإضافة")
                st.rerun()

with tab2:
    wh_df = read_sheet("warehouses")
    if not wh_df.empty:
        st.dataframe(wh_df, use_container_width=True)
    
    with st.form("add_wh"):
        col1, col2, col3 = st.columns(3)
        code = col1.text_input("كود المخزن")
        name = col2.text_input("اسم المخزن")
        manager = col3.text_input("المسؤول")
        if st.form_submit_button("إضافة مخزن"):
            if code and name:
                append_row("warehouses", {"كود المخزن": code, "اسم المخزن": name, "المسؤول": manager})
                st.success("✅")
                st.rerun()

with tab3:
    sup_df = read_sheet("suppliers")
    if not sup_df.empty:
        st.dataframe(sup_df, use_container_width=True)
    
    with st.form("add_supplier"):
        col1, col2, col3 = st.columns(3)
        code = col1.text_input("كود المورد")
        name = col2.text_input("اسم المورد")
        phone = col3.text_input("التليفون")
        if st.form_submit_button("إضافة مورد"):
            if code and name:
                append_row("suppliers", {"كود المورد": code, "الاسم": name, "التليفون": phone})
                st.success("✅")
                st.rerun()
