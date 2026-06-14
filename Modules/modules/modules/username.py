import httpx
from maigret.lib import MaigretEngine
from maigret.submit import MaigretDatabase

async def scan_username(username: str, proxy_mounts: dict) -> list:
    normalized_records = []
    
    db = MaigretDatabase()
    db.load_from_file() 
    
    target_sites = ["GitHub", "Reddit", "Twitter", "Keybase", "Basecamp"]
    sites_to_check = {name: db.sites_dict[name] for name in target_sites if name in db.sites_dict}
    
    if not sites_to_check:
        sites_to_check = dict(list(db.sites_dict.items())[:15])

    async with httpx.AsyncClient(proxies=proxy_mounts, timeout=10.0, verify=False) as client:
        engine = MaigretEngine(client=client, db=db)
        
        for site_name, site_data in sites_to_check.items():
            try:
                result = await engine.check_username(username, site_data)
                if result and result.is_found:
                    normalized_records.append({
                        "platform": site_name,
                        "url": result.url,
                        "status": "Verified Active Account"
                    })
            except Exception:
                continue
                
    return normalized_records
  
