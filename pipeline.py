import argparse
import json
from crew.crew_builder import ReconciliationCrew

def main():
    parser = argparse.ArgumentParser(description="Agent-Based Reconciliation Workflow")
    parser.add_argument("--data-dir", default="data", help="Directory containing Excel files")
    parser.add_argument("--api-config", help="Path to API configuration JSON file")
    parser.add_argument("--source", choices=["files", "api", "auto", "hybrid"], 
                       default="auto", help="Data source to use")
    parser.add_argument("--trade-ids", nargs="+", help="List of trade IDs to process")
    parser.add_argument("--date", help="Specific date for pricing data")
    
    args = parser.parse_args()
    
    # Load API configuration if provided
    api_config = None
    if args.api_config:
        try:
            with open(args.api_config, 'r') as f:
                api_config = json.load(f)
        except Exception as e:
            print(f"❌ Error loading API config: {e}")
            return
    
    print("🚀 Starting Agent-Based Reconciliation Workflow...\n")
    
    try:
        crew = ReconciliationCrew(data_dir=args.data_dir, api_config=api_config)
        df = crew.run(source=args.source, trade_ids=args.trade_ids, date=args.date)
        
        if df is not None:
            print(f"\n✅ Workflow complete! Processed {len(df)} trades.")
            print("📊 Check your reconciliation report: final_recon_report.xlsx")
        else:
            print("\n❌ Workflow failed. Check the error messages above.")
            
    except Exception as e:
        print(f"\n❌ Error running workflow: {e}")

if __name__ == "__main__":
    main()
