from crew.crew_builder import ReconciliationCrew

if __name__ == "__main__":
    print("🚀 Starting Agent-Based Reconciliation Workflow...\n")
    crew = ReconciliationCrew(data_dir="data")
    df = crew.run()
    print("\n🎉 Workflow complete. Check your reconciliation report!")
