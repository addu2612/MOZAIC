import boto3
from typing import Dict, Any, List
from datetime import datetime, timedelta

async def test_cloudwatch_connection(credentials: Dict[str, Any]) -> bool:
    try:
        client = boto3.client(
            'cloudwatch',
            aws_access_key_id=credentials.get("aws_access_key_id"),
            aws_secret_access_key=credentials.get("aws_secret_access_key"),
            region_name=credentials.get("region", "us-east-1")
        )
        client.describe_alarms(MaxRecords=1)
        return True
    except Exception:
        return False

async def fetch_cloudwatch_logs(credentials: Dict[str, Any], log_group: str, hours: int = 1) -> List[Dict[str, Any]]:
    client = boto3.client(
        'logs',
        aws_access_key_id=credentials.get("aws_access_key_id"),
        aws_secret_access_key=credentials.get("aws_secret_access_key"),
        region_name=credentials.get("region")
    )
    
    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
    response = client.filter_log_events(
        logGroupName=log_group,
        startTime=start_time
    )
    
    return [
        {
            "timestamp": event['timestamp'],
            "message": event['message']
        }
        for event in response.get('events', [])
    ]

async def get_active_alarms(credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
    client = boto3.client(
        'cloudwatch',
        aws_access_key_id=credentials.get("aws_access_key_id"),
        aws_secret_access_key=credentials.get("aws_secret_access_key"),
        region_name=credentials.get("region")
    )
    
    response = client.describe_alarms(StateValue='ALARM')
    return [
        {
            "name": alarm['AlarmName'],
            "state": alarm['StateValue'],
            "reason": alarm.get('StateReason', '')
        }
        for alarm in response.get('MetricAlarms', [])
    ]