from kubernetes import client, config
from kubernetes.client.rest import ApiException
from typing import Dict, Any, List
import base64

async def test_k8s_connection(credentials: Dict[str, Any]) -> bool:
    try:
        kubeconfig = credentials.get("kubeconfig")
        config.load_kube_config_from_dict(kubeconfig)
        v1 = client.CoreV1Api()
        v1.list_namespace(limit=1)
        return True
    except Exception:
        return False

async def fetch_pod_logs(credentials: Dict[str, Any], namespace: str, pod_name: str) -> str:
    config.load_kube_config_from_dict(credentials.get("kubeconfig"))
    v1 = client.CoreV1Api()
    return v1.read_namespaced_pod_log(name=pod_name, namespace=namespace)

async def get_pod_events(credentials: Dict[str, Any], namespace: str) -> List[Dict[str, Any]]:
    config.load_kube_config_from_dict(credentials.get("kubeconfig"))
    v1 = client.CoreV1Api()
    events = v1.list_namespaced_event(namespace=namespace)
    return [
        {
            "type": event.type,
            "reason": event.reason,
            "message": event.message,
            "timestamp": event.last_timestamp
        }
        for event in events.items
    ]