import requests
import json
import pandas as pd
from typing import Dict, Any, Optional
import time

class ReconciliationAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API not accessible: {str(e)}"}
    
    def get_excel_files(self) -> Dict[str, Any]:
        """Get list of available Excel files"""
        try:
            response = self.session.get(f"{self.base_url}/api/excel")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get Excel files: {str(e)}"}
    
    def get_excel_data(self, filename: str) -> Dict[str, Any]:
        """Get data from specific Excel file"""
        try:
            response = self.session.get(f"{self.base_url}/api/excel/{filename}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get Excel data: {str(e)}"}
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information"""
        try:
            response = self.session.get(f"{self.base_url}/api/database")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get database info: {str(e)}"}
    
    def get_table_data(self, table: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get data from specific database table"""
        try:
            params = {"limit": limit, "offset": offset}
            response = self.session.get(f"{self.base_url}/api/database/{table}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get table data: {str(e)}"}
    
    def get_merged_data(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get merged reconciliation data"""
        try:
            params = {"limit": limit, "offset": offset}
            response = self.session.get(f"{self.base_url}/api/merged", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get merged data: {str(e)}"}
    
    def search_data(self, table: str, search_term: str, column: Optional[str] = None) -> Dict[str, Any]:
        """Search data in specified table"""
        try:
            params = {"search_term": search_term}
            if column:
                params["column"] = column
            response = self.session.get(f"{self.base_url}/api/search", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to search data: {str(e)}"}

def demo_api_usage():
    """Demonstrate API usage with examples"""
    client = ReconciliationAPIClient()
    
    print("🔍 Testing Reconciliation Data API...")
    print("=" * 50)
    
    # 1. Health Check
    print("\n1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    
    # 2. Get Excel Files
    print("\n2. Available Excel Files:")
    excel_files = client.get_excel_files()
    print(json.dumps(excel_files, indent=2))
    
    # 3. Get Excel Data
    if excel_files.get("files"):
        print("\n3. Sample Excel Data (first file):")
        first_file = excel_files["files"][0]["filename"]
        excel_data = client.get_excel_data(first_file)
        print(f"File: {first_file}")
        print(f"Rows: {excel_data.get('rows', 'N/A')}")
        print(f"Columns: {excel_data.get('columns', [])}")
        if excel_data.get('data'):
            print(f"Sample data: {excel_data['data'][:2]}")  # First 2 rows
    
    # 4. Database Info
    print("\n4. Database Information:")
    db_info = client.get_database_info()
    print(json.dumps(db_info, indent=2))
    
    # 5. Get Table Data
    if db_info.get("tables"):
        print("\n5. Sample Database Data:")
        first_table = db_info["tables"][0]
        table_data = client.get_table_data(first_table, limit=5)
        print(f"Table: {first_table}")
        print(f"Total rows: {table_data.get('total_rows', 'N/A')}")
        print(f"Returned rows: {table_data.get('returned_rows', 'N/A')}")
        if table_data.get('data'):
            print(f"Sample data: {table_data['data'][:2]}")  # First 2 rows
    
    # 6. Get Merged Data
    print("\n6. Merged Reconciliation Data:")
    merged_data = client.get_merged_data(limit=5)
    print(f"Total rows: {merged_data.get('total_rows', 'N/A')}")
    print(f"Returned rows: {merged_data.get('returned_rows', 'N/A')}")
    print(f"Columns: {merged_data.get('columns', [])}")
    if merged_data.get('data'):
        print(f"Sample data: {merged_data['data'][:2]}")  # First 2 rows
    
    # 7. Search Data
    if db_info.get("tables"):
        print("\n7. Search Example:")
        search_results = client.search_data(db_info["tables"][0], "Trade")
        print(f"Search term: 'Trade'")
        print(f"Results count: {search_results.get('results_count', 'N/A')}")
        if search_results.get('data'):
            print(f"Sample results: {search_results['data'][:2]}")

def test_api_endpoints():
    """Test all API endpoints"""
    client = ReconciliationAPIClient()
    
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    endpoints = [
        ("Health Check", lambda: client.health_check()),
        ("Excel Files", lambda: client.get_excel_files()),
        ("Database Info", lambda: client.get_database_info()),
        ("Merged Data", lambda: client.get_merged_data(limit=10)),
    ]
    
    for name, func in endpoints:
        print(f"\n{name}:")
        try:
            result = func()
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"✅ Success - {len(str(result))} characters")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Reconciliation API Client")
    print("Make sure the API server is running on http://localhost:8000")
    print("=" * 50)
    
    # Wait a moment for server to start
    time.sleep(1)
    
    # Test endpoints
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("📊 Full API Demo:")
    demo_api_usage() 