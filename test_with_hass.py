#!/usr/bin/env python3
"""
Ready-to-run script for testing Script URL Generator with Home Assistant
Sets up environment and launches the server with your specific credentials
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

# Your Home Assistant credentials (replace with your actual values)
HASS_CONFIG = {
    'SUPERVISOR_TOKEN': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmYjgwY2IwY2E4ZTk0MWRkYjgyZjQyY2NiNWMxOGFmOSIsImlhdCI6MTc1MDQ2OTY3OSwiZXhwIjoyMDY1ODI5Njc5fQ.XoqTkWZZ6jeaoIvJbTeF-4-exWtKTeRSakFG3e1voTI',
    'HASS_URL': 'https://hamer.duckdns.org:62343',
    'TOKEN_EXPIRY_MINUTES': '10',
    'MAX_TOKENS_PER_SCRIPT': '5',
    'ENABLE_LOGGING': 'true'
}

def setup_environment():
    """Set up environment variables for Home Assistant connection"""
    print("🔧 Setting up environment variables...")
    
    for key, value in HASS_CONFIG.items():
        os.environ[key] = value
        print(f"   ✓ {key} = {value[:50]}{'...' if len(value) > 50 else ''}")
    
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = ['fastapi', 'uvicorn', 'aiohttp', 'jinja2']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ✗ {package} (missing)")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("   ✓ All dependencies found\n")
    return True

def test_hass_connection():
    """Test connection to Home Assistant"""
    print("🔗 Testing Home Assistant connection...")
    
    try:
        import aiohttp
        import asyncio
        
        async def test_connection():
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {HASS_CONFIG["SUPERVISOR_TOKEN"]}'}
                async with session.get(f'{HASS_CONFIG["HASS_URL"]}/api/', headers=headers) as response:
                    if response.status == 200:
                        return True
                    else:
                        print(f"   ✗ Connection failed: HTTP {response.status}")
                        return False
        
        result = asyncio.run(test_connection())
        if result:
            print("   ✓ Successfully connected to Home Assistant")
        else:
            print("   ✗ Failed to connect to Home Assistant")
            return False
            
    except Exception as e:
        print(f"   ✗ Connection error: {e}")
        return False
    
    print()
    return True

def find_test_script():
    """Find the test script in Home Assistant"""
    print("🔍 Looking for test script...")
    
    try:
        import aiohttp
        import asyncio
        
        async def find_script():
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {HASS_CONFIG["SUPERVISOR_TOKEN"]}'}
                async with session.get(f'{HASS_CONFIG["HASS_URL"]}/api/states', headers=headers) as response:
                    if response.status == 200:
                        states = await response.json()
                        scripts = [s for s in states if s['entity_id'].startswith('script.')]
                        
                        # Look for the specific test script
                        test_script = 'script.yuval_phone_notification_test_script'
                        found_script = next((s for s in scripts if s['entity_id'] == test_script), None)
                        
                        if found_script:
                            print(f"   ✓ Found test script: {test_script}")
                            print(f"      Name: {found_script['attributes'].get('friendly_name', test_script)}")
                            return True
                        else:
                            print(f"   ⚠ Test script '{test_script}' not found")
                            print(f"   Available scripts: {[s['entity_id'] for s in scripts[:5]]}")
                            if len(scripts) > 5:
                                print(f"   ... and {len(scripts) - 5} more")
                            return False
        
        result = asyncio.run(find_script())
        print()
        return result
        
    except Exception as e:
        print(f"   ✗ Error finding script: {e}")
        print()
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Script URL Generator server...")
    print("   URL: http://localhost:8080")
    print("   Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Start the server
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    """Main function"""
    print("🏠 Script URL Generator - Home Assistant Test")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path('main.py').exists():
        print("❌ Error: main.py not found. Please run this script from the addon directory.")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Test Home Assistant connection
    if not test_hass_connection():
        print("❌ Cannot connect to Home Assistant. Please check your credentials and network.")
        sys.exit(1)
    
    # Find test script
    find_test_script()
    
    # Start server
    start_server()

if __name__ == '__main__':
    main() 