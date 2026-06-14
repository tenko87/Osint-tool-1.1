import os
import random
import asyncio
from modules.username import scan_username
from modules.email import scan_email

PROXY_POOL_URL = os.getenv("PROXY_POOL_URL", "")

def generate_isolated_proxy_string() -> dict:
    if not PROXY_POOL_URL:
        return {}

    try:
        protocol, remainder = PROXY_POOL_URL.split("://")
        auth_block, network_block = remainder.split("@")
        username, password = auth_block.split(":")
        
        session_modifier = random.randint(100000, 999999)
        rotated_username = f"{username}-session-{session_modifier}"
        
        reconstructed_url = f"{protocol}://{rotated_username}:{password}@{network_block}"
        return {
            "http://": reconstructed_url,
            "https://": reconstructed_url
        }
    except Exception:
        return {
            "http://": PROXY_POOL_URL,
            "https://": PROXY_POOL_URL
        }

async def run_parallel_investigation(target: str, scan_type: str) -> dict:
    sanitized_target = target.strip()
    
    if scan_type == "username":
        proxy_config = generate_isolated_proxy_string()
        username_task = asyncio.create_task(scan_username(sanitized_target, proxy_config))
        results = await asyncio.gather(username_task)
        return {
            "target": sanitized_target,
            "type": "username",
            "matches": results[0]
        }
        
    elif scan_type == "email":
        platforms = ["amazon", "linkedin", "twitter", "spotify"]
        tasks = []
        
        for platform in platforms:
            proxy_config = generate_isolated_proxy_string()
            tasks.append(asyncio.create_task(scan_email(sanitized_target, platform, proxy_config)))
            
        completed_scrapes = await asyncio.gather(*tasks)
        normalized_matches = [match for match in completed_scrapes if match is not None]
        return {
            "target": sanitized_target,
            "type": "email",
            "matches": normalized_matches
        }
        
    return {"error": "Invalid engine execution context encountered."}
