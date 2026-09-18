import streamlit as st
from utils.ui import setup_page
from utils.auth import login_required
from utils.sheets import read_sheet, append_row, update_row, delete_row

setup_page("الأصناف", "📦")
login_required(role=["مدير", "أمين مخزن"])
st.title("📦 إدارة الأصناف")

user = st.session_state["user"]
is_admin = user["role"] == "مدير"

items_df = read_sheet("items")

if is_admin:
    tab1, tab2, tab3 = st.tabs(["📋 عرض", "➕ إضافة", "✏️ تعديل / حذف"])
else:
    tab1, tab2 = st.tabs(["📋 عرض", "➕ إضافة"])
    tab3 = None

with tab1:
    if items_df.empty:
        st.info("لا توجد أصناف بعد")
    else:
        search = st.text_input("🔍 ابحث بالاسم أو الكود", key="search_items")
        if search:
            mask = items_df.astype(str).apply(
                lambda r: r.str.contains(search, case=False, na=False).any(), axis=1
            )
            filtered = items_df[mask]
        else:
            filtered = items_df
        st.dataframe(filtered, use_container_width=True)
        st.caption(f"عدد الأصناف: {len(filtered)}")

with tab2:
    with st.form("add_item"):
        col1, col2 = st.columns(2)
        code = col1.text_input("كود الصنف *", placeholder="مثال: ITM-001")
        name = col2.text_input("اسم الصنف *", placeholder="مثال: ورق A4")
        unit = col1.selectbox("الوحدة", ["قطعة", "رزمة", "كرتونة", "كيلو", "لتر", "متر"])
        category = col2.text_input("التصنيف", placeholder="مثال: قرطاسية")
        reorder = col1.number_input("حد الطلب", min_value=0, value=20)
        opening = col2.number_input("الرصيد الافتتاحي", min_value=0, value=0)
        
        if st.form_submit_button("➕ إضافة الصنف", use_container_width=True):
            if not code or not name:
                st.error("⚠️ الكود والاسم مطلوبان")
            elif not items_df.empty and code in items_df["كود الصنف"].astype(str).values:
                st.error(f"⚠️ كود الصنف '{code}' موجود بالفعل!")
            else:
                append_row("items", {
                    "كود الصنف": code, "اسم الصنف": name, "الوحدة": unit,
                    "التصنيف": category, "حد الطلب": reorder, "الرصيد الافتتاحي": opening
                })
                st.success(f"✅ تم إضافة {name}")
                st.rerun()

# تبويب التعديل/الحذف - للمدير فقط
if is_admin and tab3 is not None:
    with tab3:
        if items_df.empty:
            st.info("لا توجد أصناف لتعديلها")
        else:
            st.info("👑 هذا القسم متاح للمدير فقط")
            item_options = (items_df["كود الصنف"].astype(str) + " | " + items_df["اسم الصنف"].astype(str)).tolist()
            selected = st.selectbox("اختر الصنف", item_options, key="edit_item_select")
            selected_code = selected.split(" | ")[0]
            current = items_df[items_df["كود الصنف"].astype(str) == selected_code].iloc[0]
            
            st.markdown("### ✏️ تعديل البيانات")
            with st.form("edit_item"):
                col1, col2 = st.columns(2)
                new_name = col1.text_input("اسم الصنف", value=str(current["اسم الصنف"]))
                units = ["قطعة", "رزمة", "كرتونة", "كيلو", "لتر", "متر"]
                curr_unit = str(current["الوحدة"])
                new_unit = col2.selectbox("الوحدة", units, index=units.index(curr_unit) if curr_unit in units else 0)
                new_cat = col1.text_input("التصنيف", value=str(current.get("التصنيف", "")))
                new_reorder = col2.number_input("حد الطلب", min_value=0, value=int(current["حد الطلب"]))
                
                if st.form_submit_button("💾 حفظ التعديلات", use_container_width=True):
                    row_idx = items_df[items_df["كود الصنف"].astype(str) == selected_code].index[0] + 2
                    update_row("items", row_idx, {
                        "كود الصنف": selected_code,
                        "اسم الصنف": new_name,
                        "الوحدة": new_unit,
                        "التصنيف": new_cat,
                        "حد الطلب": new_reorder,
                        "الرصيد الافتتاحي": current["الرصيد الافتتاحي"]
                    })
                    st.success("✅ تم الحفظ")
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 🗑️ حذف الصنف")
            st.warning(f"⚠️ أنت على وشك حذف: **{selected}** — لن يتم حذف الحركات المرتبطة به.")
            confirm = st.checkbox("نعم، أريد الحذف نهائياً", key="confirm_del_item")
            if st.button("🗑️ حذف الصنف", type="primary", disabled=not confirm, key="btn_del_item"):
                row_idx = items_df[items_df["كود الصنف"].astype(str) == selected_code].index[0] + 2
                delete_row("items", row_idx)
                st.success("✅ تم الحذف")
                st.rerun()
