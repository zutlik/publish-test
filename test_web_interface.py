#!/usr/bin/env python3
"""
Web interface test for Script URL Generator
Starts the server and tests the web endpoints
"""

import os
import sys
import asyncio
import aiohttp
import json
import subprocess
import time
from datetime import datetime

# Set up environment variables
os.environ['SUPERVISOR_TOKEN'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmYjgwY2IwY2E4ZTk0MWRkYjgyZjQyY2NiNWMxOGFmOSIsImlhdCI6MTc1MDQ2OTY3OSwiZXhwIjoyMDY1ODI5Njc5fQ.XoqTkWZZ6jeaoIvJbTeF-4-exWtKTeRSakFG3e1voTI'
os.environ['HASS_URL'] = 'https://hamer.duckdns.org:62343'
os.environ['TOKEN_EXPIRY_MINUTES'] = '10'
os.environ['MAX_TOKENS_PER_SCRIPT'] = '5'
os.environ['ENABLE_LOGGING'] = 'true'

# Modify main.py to use port 8081
def modify_main_for_test():
    """Temporarily modify main.py to use port 8081"""
    with open('main.py', 'r') as f:
        content = f.read()
    
    # Replace port 8080 with 8081
    modified_content = content.replace('port=8080', 'port=8081')
    
    with open('main_test.py', 'w') as f:
        f.write(modified_content)
    
    return 'main_test.py'

async def test_health_endpoint():
    """Test health check endpoint"""
    print("🏥 Testing health endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8081/health') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Health check passed: {data}")
                    return True
                else:
                    print(f"   ✗ Health check failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ✗ Health check error: {e}")
        return False

async def test_scripts_endpoint():
    """Test scripts listing endpoint"""
    print("\n📜 Testing scripts endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8081/api/scripts') as response:
                if response.status == 200:
                    scripts = await response.json()
                    print(f"   ✓ Found {len(scripts)} scripts")
                    
                    # Look for test script
                    test_script = 'script.yuval_phone_notification_test_script'
                    found = any(s['entity_id'] == test_script for s in scripts)
                    
                    if found:
                        print(f"   ✓ Test script found: {test_script}")
                        return True
                    else:
                        print(f"   ⚠ Test script not found in API response")
                        return False
                else:
                    print(f"   ✗ Scripts endpoint failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ✗ Scripts endpoint error: {e}")
        return False

async def test_generate_endpoint():
    """Test URL generation endpoint"""
    print("\n🔗 Testing URL generation endpoint...")
    
    try:
        payload = {
            "script_id": "script.yuval_phone_notification_test_script"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:8081/api/generate',
                json=payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ URL generated successfully")
                    print(f"   ✓ Token: {data['token'][:20]}...")
                    print(f"   ✓ URL: {data['url'][:50]}...")
                    print(f"   ✓ Expires in: {data['expires_in_minutes']} minutes")
                    
                    return data['url'], data['token']
                else:
                    error_data = await response.text()
                    print(f"   ✗ URL generation failed: HTTP {response.status}")
                    print(f"   Error: {error_data}")
                    return None, None
    except Exception as e:
        print(f"   ✗ URL generation error: {e}")
        return None, None

async def test_trigger_endpoint(url, token):
    """Test script triggering via generated URL"""
    print(f"\n🚀 Testing trigger endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    if 'successfully' in content.lower():
                        print("   ✓ Script triggered successfully via URL")
                        return True
                    elif 'already been used' in content.lower():
                        print("   ✓ Token correctly marked as used")
                        return True
                    else:
                        print("   ⚠ Unexpected response content")
                        return False
                else:
                    print(f"   ✗ Trigger failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ✗ Trigger error: {e}")
        return False

async def test_tokens_endpoint():
    """Test tokens debug endpoint"""
    print("\n🔍 Testing tokens endpoint...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8081/api/tokens') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✓ Active tokens: {data['active_tokens']}")
                    print(f"   ✓ Token list retrieved")
                    return True
                else:
                    print(f"   ✗ Tokens endpoint failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ✗ Tokens endpoint error: {e}")
        return False

async def test_main_page():
    """Test main page loads correctly"""
    print("\n🌐 Testing main page...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8081/') as response:
                if response.status == 200:
                    content = await response.text()
                    if 'Script URL Generator' in content:
                        print("   ✓ Main page loads correctly")
                        return True
                    else:
                        print("   ✗ Main page content incorrect")
                        return False
                else:
                    print(f"   ✗ Main page failed: HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ✗ Main page error: {e}")
        return False

async def main():
    """Main test function"""
    print("🌐 Script URL Generator - Web Interface Test")
    print("=" * 60)
    
    # Modify main.py for testing
    test_main_file = modify_main_for_test()
    
    # Start the server
    print("🚀 Starting server on port 8081...")
    process = subprocess.Popen([sys.executable, test_main_file])
    
    # Wait for server to start
    print("   Waiting for server to start...")
    time.sleep(5)
    
    try:
        # Test health endpoint
        if not await test_health_endpoint():
            print("❌ Health check failed")
            return
        
        # Test main page
        if not await test_main_page():
            print("❌ Main page test failed")
            return
        
        # Test scripts endpoint
        if not await test_scripts_endpoint():
            print("❌ Scripts endpoint failed")
            return
        
        # Test URL generation
        url, token = await test_generate_endpoint()
        if not url:
            print("❌ URL generation failed")
            return
        
        # Test trigger endpoint
        if not await test_trigger_endpoint(url, token):
            print("❌ Trigger endpoint failed")
            return
        
        # Test tokens endpoint
        if not await test_tokens_endpoint():
            print("❌ Tokens endpoint failed")
            return
        
        print("\n" + "=" * 60)
        print("🎉 All web interface tests passed!")
        print("\n📋 Summary:")
        print("   ✓ Health endpoint works")
        print("   ✓ Main page loads correctly")
        print("   ✓ Scripts API works")
        print("   ✓ URL generation API works")
        print("   ✓ Script triggering works")
        print("   ✓ Tokens debug endpoint works")
        print("\n🌐 Web interface is fully functional!")
        print("   Access at: http://localhost:8081")
        
    finally:
        # Clean up
        print("\n🛑 Stopping server...")
        process.terminate()
        process.wait()
        
        # Clean up test file
        if os.path.exists('main_test.py'):
            os.remove('main_test.py')

if __name__ == '__main__':
    asyncio.run(main()) 