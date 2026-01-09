import docker
from typing import Dict, Any, List

async def test_docker_connection(credentials: Dict[str, Any]) -> bool:
    try:
        client = docker.DockerClient(base_url=credentials.get("base_url", "unix://var/run/docker.sock"))
        client.ping()
        return True
    except Exception:
        return False

async def fetch_container_logs(credentials: Dict[str, Any], container_id: str) -> str:
    client = docker.DockerClient(base_url=credentials.get("base_url"))
    container = client.containers.get(container_id)
    return container.logs().decode('utf-8')

async def get_container_stats(credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
    client = docker.DockerClient(base_url=credentials.get("base_url"))
    containers = client.containers.list()
    return [
        {
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "image": c.image.tags[0] if c.image.tags else "unknown"
        }
        for c in containers
    ]