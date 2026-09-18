import streamlit as st
from utils.auth import login_required
from utils.sheets import read_sheet, calculate_stock

login_required()
st.title("📈 التقارير")

items_df = read_sheet("items")
transactions_df = read_sheet("transactions")

tab1, tab2, tab3 = st.tabs(["📊 الرصيد", "📥 الوارد", "📤 الصادر"])

with tab1:
    stock_df = calculate_stock(items_df, transactions_df)
    st.dataframe(stock_df, use_container_width=True)
    if not stock_df.empty:
        csv = stock_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 تحميل CSV", csv, "stock.csv", "text/csv")

if not transactions_df.empty:
    with tab2:
        incoming = transactions_df[transactions_df["النوع"] == "وارد"]
        st.dataframe(incoming, use_container_width=True)
    with tab3:
        outgoing = transactions_df[transactions_df["النوع"] == "صادر"]
        st.dataframe(outgoing, use_container_width=True)
