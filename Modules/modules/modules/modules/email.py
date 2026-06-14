import httpx
import importlib

async def scan_email(email: str, platform_name: str, proxy_mounts: dict) -> dict:
    try:
        module_path = f"holehe.modules.{platform_name}"
        target_module = importlib.import_module(module_path)
    except ImportError:
        return None

    async with httpx.AsyncClient(proxies=proxy_mounts, timeout=12.0, verify=False) as client:
        try:
            outbound_session = client
            results_matrix = {}
            await target_module.check(email, outbound_session, results_matrix)
            
            if platform_name in results_matrix:
                data = results_matrix[platform_name]
                if data.get("exists"):
                    return {
                        "platform": platform_name.capitalize(),
                        "exists": True,
                        "rate_limit": data.get("rateLimit", False),
                        "info": data.get("others", "No external attributes surfaced.")
                    }
        except Exception:
            return None
            
    return {
        "platform": platform_name.capitalize(),
        "exists": False,
        "rate_limit": False,
        "info": "No matched record targets discovered."
    }
  
