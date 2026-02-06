import aiohttp
from typing import Dict, Any, List

async def test_sentry_connection(credentials: Dict[str, Any]) -> bool:
    try:
        auth_token = credentials.get("auth_token")
        org_slug = credentials.get("org_slug")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://sentry.io/api/0/organizations/{org_slug}/projects/",
                headers={"Authorization": f"Bearer {auth_token}"}
            ) as response:
                return response.status == 200
    except Exception:
        return False

async def fetch_sentry_issues(credentials: Dict[str, Any], project_slug: str) -> List[Dict[str, Any]]:
    auth_token = credentials.get("auth_token")
    org_slug = credentials.get("org_slug")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://sentry.io/api/0/projects/{org_slug}/{project_slug}/issues/",
            headers={"Authorization": f"Bearer {auth_token}"}
        ) as response:
            if response.status == 200:
                issues = await response.json()
                return [
                    {
                        "id": issue['id'],
                        "title": issue['title'],
                        "level": issue['level'],
                        "count": issue['count']
                    }
                    for issue in issues
                ]
            return []