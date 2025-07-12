#!/usr/bin/env python3
"""
API Connection Test Utility for AI Reconciliation System
"""

import json
import sys
import requests
from crew.agents.api_data_loader import APIDataLoaderAgent

def test_api_connection(config_file=None, base_url=None, api_key=None):
    """
    Test API connection and validate endpoints
    
    Args:
        config_file: Path to JSON config file
        base_url: API base URL
        api_key: API key for authentication
    """
    print("🔌 Testing API Connection for AI Reconciliation System")
    print("=" * 60)
    
    # Load configuration
    if config_file:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            base_url = config.get('base_url')
            api_key = config.get('api_key')
            timeout = config.get('timeout', 30)
            endpoints = config.get('endpoints', {})
            headers = config.get('headers', {})
        except Exception as e:
            print(f"❌ Error loading config file: {e}")
            return False
    else:
        timeout = 30
        endpoints = {}
        headers = {}
    
    if not base_url or not api_key:
        print("❌ Missing base_url or api_key")
        return False
    
    # Initialize API loader
    try:
        api_loader = APIDataLoaderAgent(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout
        )
        
        # Set custom endpoints and headers
        if endpoints:
            api_loader.set_endpoints(endpoints)
        if headers:
            api_loader.set_headers(headers)
        
        print(f"✅ API Loader initialized")
        print(f"📍 Base URL: {base_url}")
        print(f"🔑 API Key: {api_key[:8]}...")
        print(f"⏱️  Timeout: {timeout}s")
        
    except Exception as e:
        print(f"❌ Error initializing API loader: {e}")
        return False
    
    # Test connection
    print("\n🔍 Testing API Connection...")
    if api_loader.validate_api_connection():
        print("✅ API connection successful")
    else:
        print("❌ API connection failed")
        return False
    
    # Test individual endpoints
    print("\n📡 Testing Individual Endpoints...")
    endpoint_status = api_loader.get_api_status()
    
    all_endpoints_ok = True
    for endpoint_name, status in endpoint_status.items():
        status_icon = "✅" if status else "❌"
        status_text = "Online" if status else "Offline"
        print(f"{status_icon} {endpoint_name}: {status_text}")
        
        if not status:
            all_endpoints_ok = False
    
    if not all_endpoints_ok:
        print("\n⚠️  Some endpoints are offline. Check your API configuration.")
        return False
    
    # Test data fetching
    print("\n📊 Testing Data Fetching...")
    
    # Test old pricing
    print("🔍 Testing old pricing endpoint...")
    old_pricing = api_loader.fetch_old_pricing(trade_ids=['TEST'], date='2024-01-01')
    if old_pricing is not None:
        print(f"✅ Old pricing: {len(old_pricing)} records")
    else:
        print("❌ Old pricing: Failed to fetch")
        return False
    
    # Test new pricing
    print("🔍 Testing new pricing endpoint...")
    new_pricing = api_loader.fetch_new_pricing(trade_ids=['TEST'], date='2024-01-01')
    if new_pricing is not None:
        print(f"✅ New pricing: {len(new_pricing)} records")
    else:
        print("❌ New pricing: Failed to fetch")
        return False
    
    # Test metadata
    print("🔍 Testing metadata endpoint...")
    metadata = api_loader.fetch_trade_metadata(trade_ids=['TEST'])
    if metadata is not None:
        print(f"✅ Metadata: {len(metadata)} records")
    else:
        print("❌ Metadata: Failed to fetch")
        return False
    
    # Test funding reference
    print("🔍 Testing funding reference endpoint...")
    funding = api_loader.fetch_funding_reference(trade_ids=['TEST'])
    if funding is not None:
        print(f"✅ Funding reference: {len(funding)} records")
    else:
        print("❌ Funding reference: Failed to fetch")
        return False
    
    # Test complete data loading
    print("\n🔄 Testing Complete Data Loading...")
    complete_data = api_loader.load_all_data_from_api(trade_ids=['TEST'], date='2024-01-01')
    if complete_data is not None and not complete_data.empty:
        print(f"✅ Complete data loading: {len(complete_data)} trades")
        print(f"📋 Columns: {list(complete_data.columns)}")
    else:
        print("❌ Complete data loading: Failed")
        return False
    
    print("\n🎉 All API tests passed! Your API configuration is working correctly.")
    return True

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test API connection for AI Reconciliation System")
    parser.add_argument("--config", help="Path to API configuration JSON file")
    parser.add_argument("--base-url", help="API base URL")
    parser.add_argument("--api-key", help="API key")
    
    args = parser.parse_args()
    
    if not args.config and (not args.base_url or not args.api_key):
        print("❌ Please provide either --config file or --base-url and --api-key")
        print("\nExample usage:")
        print("  python test_api_connection.py --config api_config.json")
        print("  python test_api_connection.py --base-url https://api.example.com --api-key your_key")
        sys.exit(1)
    
    success = test_api_connection(
        config_file=args.config,
        base_url=args.base_url,
        api_key=args.api_key
    )
    
    if success:
        print("\n✅ API connection test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ API connection test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 