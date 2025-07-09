import streamlit as st
from crew.crew_builder import ReconciliationCrew
import pandas as pd
import io

# 🔧 Page setup
st.set_page_config(page_title="ReconAI", layout="wide")
st.title("🧠 Agent-Based Reconciliation Dashboard")

# 🚀 Run button
if st.button("Run Reconciliation"):
    with st.spinner("Running reconciliation pipeline..."):
        crew = ReconciliationCrew(data_dir="data/")
        df = crew.run()

    st.success("✅ Reconciliation complete!")

    # 🔍 Display mismatched trades
    st.subheader("🔎 Mismatched Trades")
    st.dataframe(df[df["Any_Mismatch"] == True][[
        "TradeID", "PV_Diff", "Delta_Diff", "Diagnosis"
    ]])

    # 💾 Prepare Excel file for download
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    st.download_button(
        label="📥 Download Full Excel Report",
        data=excel_buffer,
        file_name="final_recon_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
