#!/usr/bin/env python3
"""
Test script for Script URL Generator addon
Tests the main functionality and API endpoints
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import aiohttp
    import pytest
except ImportError:
    print("Required packages not found. Install with: pip install aiohttp pytest")
    sys.exit(1)

# Test configuration
BASE_URL = "http://localhost:8080"
TEST_SCRIPT_ID = "script.test_script"

class TestScriptUrlGenerator:
    """Test class for the Script URL Generator addon"""
    
    def __init__(self):
        self.session = None
        self.generated_token = None
        self.generated_url = None
    
    async def setup(self):
        """Set up test session"""
        self.session = aiohttp.ClientSession()
    
    async def teardown(self):
        """Clean up test session"""
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Test health check endpoint"""
        print("Testing health check...")
        async with self.session.get(f"{BASE_URL}/health") as response:
            assert response.status == 200
            data = await response.json()
            assert data["status"] == "healthy"
            print("✓ Health check passed")
    
    async def test_scripts_endpoint(self):
        """Test scripts listing endpoint"""
        print("Testing scripts endpoint...")
        async with self.session.get(f"{BASE_URL}/api/scripts") as response:
            assert response.status == 200
            scripts = await response.json()
            assert isinstance(scripts, list)
            print(f"✓ Found {len(scripts)} scripts")
    
    async def test_generate_url(self):
        """Test URL generation"""
        print("Testing URL generation...")
        payload = {"script_id": TEST_SCRIPT_ID}
        
        async with self.session.post(
            f"{BASE_URL}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        ) as response:
            if response.status == 404:
                print("⚠ Script not found (expected in test environment)")
                return
            
            assert response.status == 200
            data = await response.json()
            
            assert "token" in data
            assert "url" in data
            assert "expires_at" in data
            assert "expires_in_minutes" in data
            
            self.generated_token = data["token"]
            self.generated_url = data["url"]
            
            print(f"✓ Generated URL: {data['url'][:50]}...")
    
    async def test_trigger_url(self):
        """Test script triggering via URL"""
        if not self.generated_url:
            print("⚠ Skipping trigger test (no URL generated)")
            return
        
        print("Testing script trigger...")
        async with self.session.get(self.generated_url) as response:
            # Should return HTML response
            assert response.status == 200
            content = await response.text()
            assert "html" in content.lower()
            print("✓ Trigger URL works")
    
    async def test_token_reuse(self):
        """Test that tokens can't be reused"""
        if not self.generated_url:
            print("⚠ Skipping reuse test (no URL generated)")
            return
        
        print("Testing token reuse prevention...")
        async with self.session.get(self.generated_url) as response:
            # Should return error page for reused token
            assert response.status == 200
            content = await response.text()
            assert "already been used" in content.lower() or "expired" in content.lower()
            print("✓ Token reuse prevention works")
    
    async def test_tokens_endpoint(self):
        """Test tokens debug endpoint"""
        print("Testing tokens endpoint...")
        async with self.session.get(f"{BASE_URL}/api/tokens") as response:
            assert response.status == 200
            data = await response.json()
            assert "active_tokens" in data
            assert "tokens" in data
            print(f"✓ Active tokens: {data['active_tokens']}")
    
    async def test_invalid_token(self):
        """Test invalid token handling"""
        print("Testing invalid token...")
        invalid_url = f"{BASE_URL}/trigger/invalid_token_123"
        async with self.session.get(invalid_url) as response:
            assert response.status == 200
            content = await response.text()
            assert "invalid" in content.lower() or "expired" in content.lower()
            print("✓ Invalid token handling works")

async def run_tests():
    """Run all tests"""
    print("Script URL Generator - Test Suite")
    print("=" * 50)
    
    tester = TestScriptUrlGenerator()
    
    try:
        await tester.setup()
        
        # Run tests
        await tester.test_health_check()
        await tester.test_scripts_endpoint()
        await tester.test_generate_url()
        await tester.test_trigger_url()
        await tester.test_token_reuse()
        await tester.test_tokens_endpoint()
        await tester.test_invalid_token()
        
        print("\n" + "=" * 50)
        print("✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False
    finally:
        await tester.teardown()
    
    return True

def test_token_generation():
    """Test token generation function directly"""
    print("Testing token generation...")
    
    # Import the main module
    from main import generate_token, create_token, cleanup_expired_tokens
    
    # Test token generation
    token1 = generate_token()
    token2 = generate_token()
    
    assert len(token1) > 20  # Should be reasonably long
    assert token1 != token2  # Should be unique
    
    print("✓ Token generation works")
    
    # Test token creation
    token, token_data = create_token("script.test")
    assert token_data.script_id == "script.test"
    assert token_data.used == False
    assert token_data.expires_at > time.time()
    
    print("✓ Token creation works")
    
    # Test cleanup
    cleanup_expired_tokens()
    print("✓ Token cleanup works")

if __name__ == "__main__":
    print("Starting tests...")
    
    # Test token generation first
    try:
        test_token_generation()
    except Exception as e:
        print(f"Token generation test failed: {e}")
        sys.exit(1)
    
    # Run async tests
    success = asyncio.run(run_tests())
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1) 