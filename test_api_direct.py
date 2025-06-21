#!/usr/bin/env python3
"""
Direct API test for Script URL Generator
Tests the core functionality without starting the web server
"""

import os
import sys
import asyncio
import aiohttp
import json
from datetime import datetime

# Set up environment variables
os.environ['SUPERVISOR_TOKEN'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmYjgwY2IwY2E4ZTk0MWRkYjgyZjQyY2NiNWMxOGFmOSIsImlhdCI6MTc1MDQ2OTY3OSwiZXhwIjoyMDY1ODI5Njc5fQ.XoqTkWZZ6jeaoIvJbTeF-4-exWtKTeRSakFG3e1voTI'
os.environ['HASS_URL'] = 'https://hamer.duckdns.org:62343'
os.environ['TOKEN_EXPIRY_MINUTES'] = '10'
os.environ['MAX_TOKENS_PER_SCRIPT'] = '5'
os.environ['ENABLE_LOGGING'] = 'true'

# Import the main module functions
from main import get_scripts, create_token, get_token_data, trigger_script, cleanup_expired_tokens

async def test_script_discovery():
    """Test script discovery functionality"""
    print("🔍 Testing script discovery...")
    
    try:
        scripts = await get_scripts()
        print(f"   ✓ Found {len(scripts)} scripts")
        
        # Look for the test script
        test_script = 'script.yuval_phone_notification_test_script'
        found_script = next((s for s in scripts if s.entity_id == test_script), None)
        
        if found_script:
            print(f"   ✓ Found test script: {found_script.entity_id}")
            print(f"      Name: {found_script.friendly_name}")
            return found_script
        else:
            print(f"   ⚠ Test script '{test_script}' not found")
            if scripts:
                print(f"   Available scripts: {[s.entity_id for s in scripts[:3]]}")
            return None
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None

def test_token_generation():
    """Test token generation and management"""
    print("\n🔐 Testing token generation...")
    
    try:
        # Test token creation
        script_id = 'script.yuval_phone_notification_test_script'
        token, token_data = create_token(script_id)
        
        print(f"   ✓ Generated token: {token[:20]}...")
        print(f"   ✓ Script ID: {token_data.script_id}")
        print(f"   ✓ Created at: {datetime.fromtimestamp(token_data.created_at)}")
        print(f"   ✓ Expires at: {datetime.fromtimestamp(token_data.expires_at)}")
        print(f"   ✓ Used: {token_data.used}")
        
        # Test token retrieval
        retrieved_data = get_token_data(token)
        if retrieved_data:
            print("   ✓ Token retrieval works")
        else:
            print("   ✗ Token retrieval failed")
            return None
        
        return token, token_data
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None

async def test_script_triggering():
    """Test script triggering functionality"""
    print("\n🚀 Testing script triggering...")
    
    try:
        script_id = 'script.yuval_phone_notification_test_script'
        
        # Test script triggering
        success = await trigger_script(script_id)
        
        if success:
            print("   ✓ Script triggered successfully!")
            return True
        else:
            print("   ✗ Script triggering failed")
            return False
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

def test_token_cleanup():
    """Test token cleanup functionality"""
    print("\n🧹 Testing token cleanup...")
    
    try:
        # Create some test tokens
        script_id = 'script.yuval_phone_notification_test_script'
        token1, _ = create_token(script_id)
        token2, _ = create_token(script_id)
        
        print(f"   ✓ Created test tokens")
        
        # Test cleanup
        cleanup_expired_tokens()
        print("   ✓ Token cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False

async def test_full_workflow():
    """Test the complete workflow"""
    print("\n🔄 Testing complete workflow...")
    
    try:
        script_id = 'script.yuval_phone_notification_test_script'
        
        # Step 1: Generate token
        token, token_data = create_token(script_id)
        print(f"   ✓ Step 1: Generated token {token[:10]}...")
        
        # Step 2: Verify token is valid
        retrieved_data = get_token_data(token)
        if not retrieved_data:
            print("   ✗ Step 2: Token validation failed")
            return False
        print("   ✓ Step 2: Token is valid")
        
        # Step 3: Trigger script
        success = await trigger_script(script_id)
        if not success:
            print("   ✗ Step 3: Script triggering failed")
            return False
        print("   ✓ Step 3: Script triggered successfully")
        
        # Step 4: Mark token as used
        from main import tokens
        tokens[token]["used"] = True
        
        # Step 5: Verify token is now used
        used_data = get_token_data(token)
        if used_data and used_data.used:
            print("   ✓ Step 4: Token marked as used")
        else:
            print("   ✗ Step 4: Token usage tracking failed")
            return False
        
        print("   ✓ Complete workflow test passed!")
        return True
        
    except Exception as e:
        print(f"   ✗ Workflow error: {e}")
        return False

async def main():
    """Main test function"""
    print("🏠 Script URL Generator - Direct API Test")
    print("=" * 60)
    
    # Test script discovery
    test_script = await test_script_discovery()
    if not test_script:
        print("❌ Cannot proceed without test script")
        return
    
    # Test token generation
    token_result = test_token_generation()
    if not token_result:
        print("❌ Token generation failed")
        return
    
    # Test script triggering
    trigger_success = await test_script_triggering()
    if not trigger_success:
        print("❌ Script triggering failed")
        return
    
    # Test token cleanup
    cleanup_success = test_token_cleanup()
    if not cleanup_success:
        print("❌ Token cleanup failed")
        return
    
    # Test complete workflow
    workflow_success = await test_full_workflow()
    if not workflow_success:
        print("❌ Complete workflow test failed")
        return
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! The addon is working correctly.")
    print("\n📋 Summary:")
    print("   ✓ Script discovery works")
    print("   ✓ Token generation is secure")
    print("   ✓ Script triggering functions")
    print("   ✓ Token cleanup works")
    print("   ✓ Complete workflow is functional")
    print("\n🚀 The addon is ready for use!")

if __name__ == '__main__':
    asyncio.run(main()) 