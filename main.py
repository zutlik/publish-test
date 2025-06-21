#!/usr/bin/env python3
"""
Script URL Generator - Home Assistant Addon
Generates temporary, internet-accessible URLs to trigger Home Assistant scripts
"""

import asyncio
import json
import logging
import os
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import aiohttp
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Script URL Generator", version="1.0.0")

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuration
SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN")
HASS_URL = os.environ.get("HASS_URL", "http://supervisor/core")
TOKEN_EXPIRY_MINUTES = int(os.environ.get("TOKEN_EXPIRY_MINUTES", "10"))
MAX_TOKENS_PER_SCRIPT = int(os.environ.get("MAX_TOKENS_PER_SCRIPT", "5"))
ENABLE_LOGGING = os.environ.get("ENABLE_LOGGING", "true").lower() == "true"

# In-memory token store (in production, consider using Redis or database)
tokens: Dict[str, Dict] = {}

class TokenData(BaseModel):
    script_id: str
    created_at: float
    expires_at: float
    used: bool = False

class ScriptInfo(BaseModel):
    entity_id: str
    name: str
    friendly_name: str

async def get_hass_headers() -> Dict[str, str]:
    """Get headers for Home Assistant API requests"""
    return {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }

async def get_scripts() -> List[ScriptInfo]:
    """Fetch all available scripts from Home Assistant"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = await get_hass_headers()
            async with session.get(
                f"{HASS_URL}/api/states",
                headers=headers
            ) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch states: {response.status}")
                    return []
                
                states = await response.json()
                scripts = []
                
                for state in states:
                    if state["entity_id"].startswith("script."):
                        scripts.append(ScriptInfo(
                            entity_id=state["entity_id"],
                            name=state["entity_id"],
                            friendly_name=state["attributes"].get("friendly_name", state["entity_id"])
                        ))
                
                return sorted(scripts, key=lambda x: x.friendly_name.lower())
    except Exception as e:
        logger.error(f"Error fetching scripts: {e}")
        return []

def generate_token() -> str:
    """Generate a cryptographically secure token"""
    return secrets.token_urlsafe(32)

def create_token(script_id: str) -> Tuple[str, TokenData]:
    """Create a new token for a script"""
    token = generate_token()
    now = time.time()
    expires_at = now + (TOKEN_EXPIRY_MINUTES * 60)
    
    token_data = TokenData(
        script_id=script_id,
        created_at=now,
        expires_at=expires_at
    )
    
    tokens[token] = token_data.dict()
    
    # Clean up expired tokens
    cleanup_expired_tokens()
    
    return token, token_data

def cleanup_expired_tokens():
    """Remove expired tokens from memory"""
    now = time.time()
    expired_tokens = [
        token for token, data in tokens.items()
        if data["expires_at"] < now
    ]
    for token in expired_tokens:
        del tokens[token]

def get_token_data(token: str) -> Optional[TokenData]:
    """Get token data if valid and not expired"""
    if token not in tokens:
        return None
    
    data = tokens[token]
    if data["expires_at"] < time.time():
        del tokens[token]
        return None
    
    return TokenData(**data)

async def trigger_script(script_id: str) -> bool:
    """Trigger a script via Home Assistant API"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = await get_hass_headers()
            payload = {"entity_id": script_id}
            
            async with session.post(
                f"{HASS_URL}/api/services/script/turn_on",
                headers=headers,
                json=payload
            ) as response:
                success = response.status == 200
                if ENABLE_LOGGING:
                    logger.info(f"Script {script_id} triggered: {'SUCCESS' if success else 'FAILED'}")
                return success
    except Exception as e:
        logger.error(f"Error triggering script {script_id}: {e}")
        return False

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main addon interface"""
    scripts = await get_scripts()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "scripts": scripts}
    )

@app.post("/api/generate")
async def generate_url(request: Request):
    """Generate a temporary URL for a script"""
    try:
        data = await request.json()
        script_id = data.get("script_id")
        
        if not script_id:
            raise HTTPException(status_code=400, detail="script_id is required")
        
        # Check if script exists
        scripts = await get_scripts()
        script_exists = any(s.entity_id == script_id for s in scripts)
        if not script_exists:
            raise HTTPException(status_code=404, detail="Script not found")
        
        # Check token limit per script
        script_tokens = [t for t in tokens.values() if t["script_id"] == script_id and t["expires_at"] > time.time()]
        if len(script_tokens) >= MAX_TOKENS_PER_SCRIPT:
            raise HTTPException(
                status_code=429, 
                detail=f"Maximum tokens ({MAX_TOKENS_PER_SCRIPT}) reached for this script"
            )
        
        token, token_data = create_token(script_id)
        
        # Generate the trigger URL
        base_url = str(request.base_url).rstrip('/')
        trigger_url = f"{base_url}/trigger/{token}"
        
        if ENABLE_LOGGING:
            logger.info(f"Generated token for script {script_id}: {token[:8]}...")
        
        return {
            "token": token,
            "url": trigger_url,
            "expires_at": datetime.fromtimestamp(token_data.expires_at).isoformat(),
            "expires_in_minutes": TOKEN_EXPIRY_MINUTES
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/trigger/{token}")
async def trigger_script_url(token: str, request: Request):
    """Trigger a script via token URL"""
    # Get token data
    token_data = get_token_data(token)
    if not token_data:
        if ENABLE_LOGGING:
            logger.warning(f"Invalid or expired token attempted: {token[:8]}...")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Invalid or expired token"}
        )
    
    # Check if already used
    if token_data.used:
        if ENABLE_LOGGING:
            logger.warning(f"Token already used: {token[:8]}...")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Token has already been used"}
        )
    
    # Trigger the script
    success = await trigger_script(token_data.script_id)
    
    # Mark token as used
    tokens[token]["used"] = True
    
    if success:
        if ENABLE_LOGGING:
            logger.info(f"Script {token_data.script_id} successfully triggered via token {token[:8]}...")
        return templates.TemplateResponse(
            "success.html",
            {"request": request, "script_id": token_data.script_id}
        )
    else:
        if ENABLE_LOGGING:
            logger.error(f"Failed to trigger script {token_data.script_id} via token {token[:8]}...")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Failed to trigger script"}
        )

@app.get("/api/scripts")
async def api_scripts():
    """API endpoint to get available scripts"""
    scripts = await get_scripts()
    return [{"entity_id": s.entity_id, "name": s.friendly_name} for s in scripts]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/tokens")
async def api_tokens():
    """API endpoint to get active tokens (for debugging)"""
    cleanup_expired_tokens()
    return {
        "active_tokens": len(tokens),
        "tokens": [
            {
                "token": token[:8] + "...",
                "script_id": data["script_id"],
                "created_at": datetime.fromtimestamp(data["created_at"]).isoformat(),
                "expires_at": datetime.fromtimestamp(data["expires_at"]).isoformat(),
                "used": data["used"]
            }
            for token, data in tokens.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_level="info"
    ) 