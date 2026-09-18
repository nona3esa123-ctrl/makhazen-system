import streamlit as st
from utils.auth import login_required
from utils.sheets import read_sheet, append_row

login_required(role=["مدير", "أمين مخزن"])
st.title("📦 إدارة الأصناف")

items_df = read_sheet("items")

tab1, tab2 = st.tabs(["📋 عرض", "➕ إضافة"])

with tab1:
    if items_df.empty:
        st.info("لا توجد أصناف بعد")
    else:
        st.dataframe(items_df, use_container_width=True)

with tab2:
    with st.form("add_item"):
        col1, col2 = st.columns(2)
        code = col1.text_input("كود الصنف *")
        name = col2.text_input("اسم الصنف *")
        unit = col1.selectbox("الوحدة", ["قطعة", "رزمة", "كرتونة", "كيلو", "لتر", "متر"])
        category = col2.text_input("التصنيف")
        reorder = col1.number_input("حد الطلب", min_value=0, value=10)
        opening = col2.number_input("الرصيد الافتتاحي", min_value=0, value=0)
        
        if st.form_submit_button("➕ إضافة الصنف", use_container_width=True):
            if not code or not name:
                st.error("⚠️ الكود والاسم مطلوبان")
            else:
                append_row("items", {
                    "كود الصنف": code, "اسم الصنف": name, "الوحدة": unit,
                    "التصنيف": category, "حد الطلب": reorder, "الرصيد الافتتاحي": opening
                })
                st.success(f"✅ تم إضافة {name}")
                st.rerun()
