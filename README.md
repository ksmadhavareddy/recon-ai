# 🧠 CrewAI Reconciliation App

This project implements a modular, agent-based reconciliation engine powered by Crew-style coordination. It compares old and new pricing models across PV and Delta risk, enriched with funding metadata and rule-based diagnostics.

---

## 🚀 Key Features

- ✅ PV and Delta comparison with configurable thresholds
- 📉 Rule-based funding-aware diagnostics
- 🧩 Modular agents: Loader, Reconciler, Analyzer, Narrator
- 📤 Final Excel report with root cause annotations

---

## 📁 Folder Structure

crewai_recon_app/
├── crew/
│   ├── agents/                      # Modular agents
│   │   ├── data_loader.py
│   │   ├── recon_agent.py
│   │   ├── analyzer_agent.py
│   │   └── narrator_agent.py
│   ├── crew_builder.py             # CrewAI team definition
│   └── tools/
│       └── ml_tool.py              # (Optional) ML model wrapper
├── data/
│   ├── old_pricing.xlsx
│   ├── new_pricing.xlsx
│   ├── trade_metadata.xlsx
│   └── funding_model_reference.xlsx
├── models/
│   └── catboost_diagnoser.pkl      # Placeholder for trained model
├── pipeline.py                     # Orchestration entry point
├── requirements.txt
└── README.md


---

## 🛠️ How to Use

1. 🧱 Install requirements:

```bash
pip install -r requirements.txt

2. 📂 Place input files into data/:

old_pricing.xlsx

new_pricing.xlsx

trade_metadata.xlsx

funding_model_reference.xlsx

3. 🚀 Run the workflow:
python pipeline.py

4. 📊 Output:

final_recon_report.xlsx containing mismatches and diagnostics

👨‍💼 Agents in Action
Agent	Role
DataLoaderAgent	Loads and merges pricing, trade, and funding data
ReconAgent	Flags mismatches in PV and Delta values
AnalyzerAgent	Provides funding-aware diagnostic tags
NarratorAgent	Summarizes results and generates the Excel report

🧠 Optional ML Extension
Plug in a CatBoost or XGBoost model to predict mismatch reasons using funding features. Agent-ready hooks included in crew/tools/ml_tool.py (placeholder).

🏗️ Future Enhancements
🔄 Cashflow-level diagnostics

🤖 ML/LLM hybrid analyzer agent

🌐 Streamlit UI for upload and visualization

👋 Author
Developed with clarity and modularity by Madhava GitHub: ksmadhavareddy