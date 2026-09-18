import streamlit as st
from datetime import datetime
from utils.auth import login_required
from utils.sheets import read_sheet, append_row, generate_id

login_required(role=["مدير", "أمين مخزن"])
st.title("📥 تسجيل وارد جديد")

items_df = read_sheet("items")
warehouses_df = read_sheet("warehouses")
suppliers_df = read_sheet("suppliers")

if items_df.empty:
    st.warning("⚠️ أضف أصنافاً أولاً")
    st.stop()

with st.form("incoming_form"):
    col1, col2 = st.columns(2)
    item_options = (items_df["كود الصنف"].astype(str) + " - " + items_df["اسم الصنف"].astype(str)).tolist()
    item = col1.selectbox("الصنف *", item_options)
    qty = col1.number_input("الكمية *", min_value=0.01, step=1.0)
    
    warehouse_opts = warehouses_df["اسم المخزن"].tolist() if not warehouses_df.empty else ["افتراضي"]
    warehouse = col2.selectbox("المخزن *", warehouse_opts)
    
    supplier_opts = suppliers_df["الاسم"].tolist() if not suppliers_df.empty else ["غير محدد"]
    supplier = col2.selectbox("المورد", supplier_opts)
    
    price = col1.number_input("سعر الوحدة", min_value=0.0, step=0.5)
    notes = col2.text_area("ملاحظات", height=80)
    
    if st.form_submit_button("✅ حفظ الوارد", use_container_width=True):
        code = item.split(" - ")[0]
        receipt_no = generate_id("IN")
        append_row("transactions", {
            "رقم الإذن": receipt_no,
            "النوع": "وارد",
            "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "كود الصنف": code,
            "الكمية": qty,
            "كود المخزن": warehouse,
            "المورد/الجهة": supplier,
            "سعر الوحدة": price,
            "الموظف": st.session_state["user"]["name"],
            "ملاحظات": notes
        })
        st.success(f"✅ تم التسجيل بإذن رقم {receipt_no}")
