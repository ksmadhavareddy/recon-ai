#!/usr/bin/env python3
"""
API Connection Test Utility for AI Reconciliation System
"""

import json
import sys
import requests
from crew.agents.unified_data_loader import UnifiedDataLoaderAgent

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
    
    if not base_url:
        print("❌ Missing base_url")
        return False
    
    # Prepare API config for unified loader
    api_config = {
        'base_url': base_url,
        'api_key': api_key,
        'timeout': timeout,
        'endpoints': endpoints,
        'headers': headers
    }
    
    # Initialize unified loader
    try:
        unified_loader = UnifiedDataLoaderAgent(api_config=api_config)
        
        print(f"✅ Unified Loader initialized")
        print(f"📍 Base URL: {base_url}")
        if api_key:
            print(f"🔑 API Key: {api_key[:8]}...")
        else:
            print(f"🔑 API Key: None (local server)")
        print(f"⏱️  Timeout: {timeout}s")
        
    except Exception as e:
        print(f"❌ Error initializing unified loader: {e}")
        return False
    
    # Test connection
    print("\n🔍 Testing API Connection...")
    if unified_loader._validate_api_connection():
        print("✅ API connection successful")
    else:
        print("❌ API connection failed")
        return False
    
    # Test individual endpoints
    print("\n📡 Testing Individual Endpoints...")
    endpoint_status = unified_loader.get_api_status()
    
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
    old_pricing = unified_loader._fetch_from_api(unified_loader.endpoints['old_pricing'], trade_ids=['TEST'], date='2024-01-01')
    if old_pricing is not None:
        print(f"✅ Old pricing: {len(old_pricing)} records")
    else:
        print("❌ Old pricing: Failed to fetch")
        return False
    
    # Test new pricing
    print("🔍 Testing new pricing endpoint...")
    new_pricing = unified_loader._fetch_from_api(unified_loader.endpoints['new_pricing'], trade_ids=['TEST'], date='2024-01-01')
    if new_pricing is not None:
        print(f"✅ New pricing: {len(new_pricing)} records")
    else:
        print("❌ New pricing: Failed to fetch")
        return False
    
    # Test trade metadata
    print("🔍 Testing trade metadata endpoint...")
    metadata = unified_loader._fetch_from_api(unified_loader.endpoints['trade_metadata'], trade_ids=['TEST'])
    if metadata is not None:
        print(f"✅ Trade metadata: {len(metadata)} records")
    else:
        print("❌ Trade metadata: Failed to fetch")
        return False
    
    # Test funding reference
    print("🔍 Testing funding reference endpoint...")
    funding = unified_loader._fetch_from_api(unified_loader.endpoints['funding_reference'], trade_ids=['TEST'])
    if funding is not None:
        print(f"✅ Funding reference: {len(funding)} records")
    else:
        print("❌ Funding reference: Failed to fetch")
        return False
    
    # Test complete data loading
    print("\n🔄 Testing Complete Data Loading...")
    try:
        df = unified_loader.load_data(source="api", trade_ids=['TEST'], date='2024-01-01')
        if df is not None and not df.empty:
            print(f"✅ Complete data loading: {len(df)} trades")
            print(f"📊 Columns: {list(df.columns)}")
        else:
            print("❌ Complete data loading: No data returned")
            return False
    except Exception as e:
        print(f"❌ Complete data loading failed: {e}")
        return False
    
    print("\n🎉 All API tests passed successfully!")
    return True

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test API connection for reconciliation system")
    parser.add_argument("--config", help="Path to API configuration JSON file")
    parser.add_argument("--base-url", help="API base URL")
    parser.add_argument("--api-key", help="API key for authentication")
    
    args = parser.parse_args()
    
    if not args.config and not args.base_url:
        print("❌ Please provide either --config or --base-url")
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