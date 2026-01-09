import aiohttp
from typing import Dict, Any, List

async def test_grafana_connection(credentials: Dict[str, Any]) -> bool:
    try:
        url = credentials.get("url")
        api_key = credentials.get("api_key")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{url}/api/health",
                headers={"Authorization": f"Bearer {api_key}"}
            ) as response:
                return response.status == 200
    except Exception:
        return False

async def fetch_grafana_alerts(credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
    url = credentials.get("url")
    api_key = credentials.get("api_key")
    
    print(f"Fetching from Grafana: {url}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{url}/api/v1/provisioning/alert-rules",  # Updated endpoint
            headers={"Authorization": f"Bearer {api_key}"}
        ) as response:
            print(f"Grafana response status: {response.status}")
            if response.status == 200:
                alerts = await response.json()
                print(f"Grafana alerts found: {len(alerts)}")
                print(f"Alerts data: {alerts}")
                return [
                    {
                        "id": alert.get('uid', alert.get('id')),
                        "name": alert.get('title', alert.get('name', 'Unknown')),
                        "state": alert.get('state', 'unknown')
                    }
                    for alert in alerts
                ]
            else:
                error = await response.text()
                print(f"Grafana error: {error}")
            return []