import streamlit as st
from datetime import datetime
from utils.ui import setup_page
from utils.auth import login_required
from utils.sheets import read_sheet, update_row, delete_row

setup_page("إدارة الحركات", "🗂️")
login_required(role=["مدير"])
st.title("🗂️ إدارة الحركات")
st.caption("👑 هذه الصفحة متاحة للمدير فقط - تعديل وحذف الوارد والصادر")


def to_float(value, default=0.0):
    """تحويل آمن للأرقام - يتعامل مع الفاصلة والنقطة"""
    if value is None:
        return default
    try:
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip().replace(",", ".")
        return float(s) if s else default
    except (ValueError, TypeError):
        return default


transactions_df = read_sheet("transactions")

if transactions_df.empty:
    st.info("لا توجد حركات مسجلة بعد")
    st.stop()

# فلترة
col1, col2 = st.columns(2)
with col1:
    type_filter = st.selectbox("نوع الحركة", ["الكل", "وارد", "صادر"], key="trans_type")
with col2:
    search = st.text_input("🔍 بحث برقم الإذن أو كود الصنف", key="trans_search")

filtered = transactions_df.copy()
if type_filter != "الكل":
    filtered = filtered[filtered["النوع"] == type_filter]
if search:
    mask = filtered.astype(str).apply(
        lambda r: r.str.contains(search, case=False, na=False).any(), axis=1
    )
    filtered = filtered[mask]

st.markdown(f"### 📋 الحركات ({len(filtered)} نتيجة)")
st.dataframe(filtered, use_container_width=True)

if filtered.empty:
    st.stop()

st.markdown("---")
st.markdown("### ✏️ تعديل أو حذف حركة")

# قائمة اختيار الحركة
filtered_reset = filtered.reset_index(drop=True)
trans_options = [
    f"{row['رقم الإذن']} | {row['النوع']} | {row['كود الصنف']} | {row['التاريخ']}"
    for _, row in filtered_reset.iterrows()
]
selected = st.selectbox("اختر الحركة", trans_options, key="select_trans")
selected_receipt = selected.split(" | ")[0]

# إيجاد الحركة في DataFrame الأصلي
original_matches = transactions_df[transactions_df["رقم الإذن"].astype(str) == selected_receipt]

if original_matches.empty:
    st.error("⚠️ لم يتم العثور على الحركة")
    st.stop()

# إذا كان الإذن يحتوي عدة أصناف
if len(original_matches) > 1:
    st.info(f"ℹ️ رقم الإذن {selected_receipt} يحتوي على {len(original_matches)} أصناف. اختر السطر المحدد.")
    row_labels = [
        f"{row['كود الصنف']} | كمية: {row['الكمية']}"
        for _, row in original_matches.iterrows()
    ]
    chosen_row_label = st.selectbox("اختر السطر", row_labels, key="select_row_in_receipt")
    chosen_idx_label = row_labels.index(chosen_row_label)
    current = original_matches.iloc[chosen_idx_label]
    real_idx = original_matches.index[chosen_idx_label]
else:
    current = original_matches.iloc[0]
    real_idx = original_matches.index[0]

# عرض تفاصيل الحركة
st.markdown("#### 📄 تفاصيل الحركة المختارة")
info_col1, info_col2 = st.columns(2)
info_col1.write(f"**رقم الإذن:** {current['رقم الإذن']}")
info_col1.write(f"**النوع:** {current['النوع']}")
info_col1.write(f"**التاريخ:** {current['التاريخ']}")
info_col1.write(f"**كود الصنف:** {current['كود الصنف']}")
info_col1.write(f"**الكمية:** {current['الكمية']}")
info_col2.write(f"**المخزن:** {current.get('كود المخزن', '')}")
info_col2.write(f"**المورد/الجهة:** {current.get('المورد/الجهة', '')}")
info_col2.write(f"**الموظف:** {current.get('الموظف', '')}")
info_col2.write(f"**ملاحظات:** {current.get('ملاحظات', '')}")

st.markdown("---")

# فورم التعديل - مع تحويل آمن
st.markdown("### 💾 تعديل الحركة")
current_qty = to_float(current["الكمية"], 1.0)

with st.form("edit_trans"):
    col1, col2 = st.columns(2)
    new_qty = col1.number_input(
        "الكمية",
        min_value=0.01,
        value=current_qty,
        step=1.0,
        format="%.2f"
    )
    new_entity = col2.text_input("المورد/الجهة", value=str(current.get("المورد/الجهة", "")))
    new_notes = st.text_area("ملاحظات", value=str(current.get("ملاحظات", "")), height=80)
    
    if st.form_submit_button("💾 حفظ التعديلات", use_container_width=True):
        real_row_num = transactions_df.index.get_loc(real_idx) + 2
        
        updated_data = current.to_dict()
        updated_data["الكمية"] = new_qty
        updated_data["المورد/الجهة"] = new_entity
        updated_data["ملاحظات"] = new_notes
        
        update_row("transactions", real_row_num, updated_data)
        st.success("✅ تم تحديث الحركة بنجاح")
        st.rerun()

st.markdown("---")
st.markdown("### 🗑️ حذف الحركة")
st.error(f"⚠️ سيتم حذف الحركة نهائياً (رقم الإذن: {current['رقم الإذن']} - كود: {current['كود الصنف']})")
st.caption("ملاحظة: حذف الحركة سيؤدي إلى إعادة حساب الرصيد تلقائياً.")

confirm_del = st.checkbox("نعم، أريد الحذف نهائياً", key="confirm_del_trans")
if st.button("🗑️ حذف الحركة", type="primary", disabled=not confirm_del, key="btn_del_trans"):
    real_row_num = transactions_df.index.get_loc(real_idx) + 2
    delete_row("transactions", real_row_num)
    st.success("✅ تم الحذف بنجاح")
    st.rerun()
