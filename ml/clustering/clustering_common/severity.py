from typing import Dict

GRAFANA_SEVERITY = {
    "high_error_rate": "P0",
    "cpu_spike": "P1",
    "memory_spike": "P1",
    "connection_pool_exhaustion": "P0",
    "cache_miss_spike": "P2",
    "gc_pressure": "P2",
    "traffic_spike": "P2",
    "slow_response": "P1",
}

K8S_SEVERITY = {
    "NodeNotReady": "P0",
    "NodeOutOfDisk": "P0",
    "DiskPressure": "P0",
    "FailedScheduling": "P1",
    "ImagePullBackOff": "P1",
    "ContainerCreateError": "P1",
    "BackOffRestartPod": "P1",
    "ReadinessProbeFailure": "P1",
    "LivenessProbeFailure": "P1",
    "FailedDetachVolume": "P1",
    "VolumeAttachFailed": "P1",
    "TLSHandshakeFailed": "P1",
    "DNSResolutionFailed": "P1",
    "AuthenticationFailed": "P0",
    "AuthorizationDenied": "P0",
    "ConfigMapNotFound": "P2",
    "ResourceQuotaExceeded": "P2",
    "TimeoutError": "P2",
    "InvalidImageName": "P2",
    "InvalidArgument": "P2",
    "AdmissionWebhookDenied": "P2",
    "InsufficientMemory": "P1",
}


def grafana_severity(anomaly_type: str) -> str:
    if not anomaly_type:
        return "P3"
    return GRAFANA_SEVERITY.get(anomaly_type, "P3")


def k8s_severity(error_type: str) -> str:
    if not error_type:
        return "P3"
    return K8S_SEVERITY.get(error_type, "P3")
