"""
Timestamp Utilities
Handles realistic timestamp generation with patterns
"""
import random
from datetime import datetime, timedelta
from typing import List, Tuple
import math

class TimestampGenerator:
    """Generate realistic timestamps with various patterns"""
    
    def __init__(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date
        self.current_time = start_date
    
    def is_business_hours(self, dt: datetime) -> bool:
        """Check if timestamp is during business hours (9 AM - 6 PM)"""
        return 9 <= dt.hour < 18
    
    def is_peak_hours(self, dt: datetime) -> bool:
        """Check if timestamp is during peak hours"""
        return 9 <= dt.hour < 19
    
    def is_weekend(self, dt: datetime) -> bool:
        """Check if timestamp is on weekend"""
        return dt.weekday() >= 5
    
    def get_traffic_multiplier(self, dt: datetime) -> float:
        """Get traffic multiplier based on time of day and week"""
        multiplier = 1.0
        
        # Weekend reduction
        if self.is_weekend(dt):
            multiplier *= 0.6
        
        # Hour of day pattern
        hour = dt.hour
        if 0 <= hour < 6:
            multiplier *= 0.2  # Very low traffic
        elif 6 <= hour < 9:
            multiplier *= 0.6  # Morning ramp-up
        elif 9 <= hour < 12:
            multiplier *= 1.5  # Morning peak
        elif 12 <= hour < 14:
            multiplier *= 1.3  # Lunch hour
        elif 14 <= hour < 18:
            multiplier *= 1.6  # Afternoon peak
        elif 18 <= hour < 21:
            multiplier *= 1.0  # Evening
        elif 21 <= hour < 24:
            multiplier *= 0.5  # Late evening
        
        # Monday spike
        if dt.weekday() == 0:
            multiplier *= 1.3
        
        # Friday afternoon reduction
        if dt.weekday() == 4 and hour >= 15:
            multiplier *= 0.8
        
        return multiplier
    
    def get_seasonal_multiplier(self, dt: datetime) -> float:
        """Get seasonal traffic multiplier"""
        # Black Friday / Cyber Monday (late November)
        if dt.month == 11 and 23 <= dt.day <= 27:
            return 3.5
        
        # Holiday season (December)
        if dt.month == 12:
            return 2.5
        
        # Back to school (September)
        if dt.month == 9:
            return 1.5
        
        # Summer slowdown (July-August)
        if dt.month in [7, 8]:
            return 0.8
        
        return 1.0
    
    def generate_next_timestamp(self, base_interval_seconds: float = 0.06) -> datetime:
        """
        Generate next realistic timestamp
        Base interval: 0.06s = ~1000 logs/minute at normal traffic
        """
        # Apply traffic patterns
        traffic_mult = self.get_traffic_multiplier(self.current_time)
        seasonal_mult = self.get_seasonal_multiplier(self.current_time)
        
        # Calculate actual interval
        interval = base_interval_seconds / (traffic_mult * seasonal_mult)
        
        # Add some randomness (±30%)
        interval *= random.uniform(0.7, 1.3)
        
        # Advance time
        self.current_time += timedelta(seconds=interval)
        
        return self.current_time
    
    def generate_incident_timestamps(
        self, 
        start_time: datetime, 
        duration_minutes: int, 
        intensity: str = 'high'
    ) -> List[datetime]:
        """
        Generate timestamps for an incident period
        Returns list of timestamps with increased frequency
        """
        timestamps = []
        
        # Intensity determines log frequency
        intervals = {
            'low': 5.0,      # One log every 5 seconds
            'medium': 2.0,   # One log every 2 seconds
            'high': 0.5,     # Two logs per second
            'critical': 0.1  # Ten logs per second
        }
        
        base_interval = intervals.get(intensity, 1.0)
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        current = start_time
        while current <= end_time:
            timestamps.append(current)
            # Add randomness
            interval = base_interval * random.uniform(0.5, 1.5)
            current += timedelta(seconds=interval)
        
        return timestamps
    
    def generate_correlated_timestamp(
        self, 
        base_timestamp: datetime, 
        max_offset_seconds: int = 30
    ) -> datetime:
        """
        Generate a timestamp correlated with a base timestamp
        Used for cross-source incident correlation
        """
        offset = random.uniform(-max_offset_seconds, max_offset_seconds)
        return base_timestamp + timedelta(seconds=offset)
    
    def generate_degradation_pattern(
        self, 
        start_time: datetime, 
        degradation_minutes: int,
        failure_time: datetime
    ) -> List[Tuple[datetime, float]]:
        """
        Generate timestamps with degradation severity
        Returns list of (timestamp, severity) tuples
        """
        pattern = []
        
        current = start_time
        end = failure_time
        
        while current <= end:
            # Calculate severity (0.0 to 1.0) based on progress
            progress = (current - start_time).total_seconds() / (end - start_time).total_seconds()
            
            # Exponential degradation
            severity = math.pow(progress, 2)
            
            pattern.append((current, severity))
            
            # More frequent logs as severity increases
            interval = 60 * (1 - severity * 0.8)  # From 60s to 12s
            current += timedelta(seconds=interval * random.uniform(0.8, 1.2))
        
        return pattern
    
    def generate_burst_pattern(
        self, 
        center_time: datetime, 
        burst_duration_seconds: int = 60,
        burst_intensity: float = 10.0
    ) -> List[datetime]:
        """
        Generate a burst of timestamps
        Used for sudden spikes in activity
        """
        timestamps = []
        
        start = center_time - timedelta(seconds=burst_duration_seconds / 2)
        end = center_time + timedelta(seconds=burst_duration_seconds / 2)
        
        # Normal distribution of timestamps within burst
        num_events = int(burst_duration_seconds * burst_intensity)
        
        for _ in range(num_events):
            # Use normal distribution centered at burst center
            offset = random.gauss(0, burst_duration_seconds / 6)
            timestamp = center_time + timedelta(seconds=offset)
            
            if start <= timestamp <= end:
                timestamps.append(timestamp)
        
        return sorted(timestamps)
    
    def generate_periodic_pattern(
        self,
        start_time: datetime,
        end_time: datetime,
        period_seconds: int = 300,  # 5 minutes
        amplitude: float = 0.5
    ) -> List[Tuple[datetime, float]]:
        """
        Generate periodic pattern (e.g., for scheduled tasks, garbage collection)
        Returns list of (timestamp, intensity) tuples
        """
        pattern = []
        current = start_time
        phase = 0
        
        while current <= end_time:
            # Sinusoidal pattern
            intensity = 1.0 + amplitude * math.sin(2 * math.pi * phase)
            pattern.append((current, intensity))
            
            current += timedelta(seconds=period_seconds)
            phase += 1 / (86400 / period_seconds)  # Normalize to daily cycle
        
        return pattern
    
    def generate_cascading_failure_timestamps(
        self,
        initial_failure: datetime,
        num_cascades: int = 3,
        cascade_delay_minutes: List[int] = None
    ) -> List[datetime]:
        """
        Generate timestamps for cascading failures
        Each subsequent failure occurs after a delay
        """
        if cascade_delay_minutes is None:
            cascade_delay_minutes = [2, 5, 10]  # Default delays
        
        failure_times = [initial_failure]
        
        for i in range(min(num_cascades, len(cascade_delay_minutes))):
            delay = cascade_delay_minutes[i] * random.uniform(0.8, 1.2)
            next_failure = failure_times[-1] + timedelta(minutes=delay)
            failure_times.append(next_failure)
        
        return failure_times
    
    def generate_recovery_pattern(
        self,
        failure_time: datetime,
        recovery_type: str = 'gradual',
        recovery_duration_minutes: int = 30
    ) -> List[Tuple[datetime, float]]:
        """
        Generate recovery pattern after incident
        Returns list of (timestamp, health) tuples where health goes from 0.0 to 1.0
        """
        pattern = []
        
        if recovery_type == 'immediate':
            # Instant recovery
            pattern.append((failure_time, 0.0))
            pattern.append((failure_time + timedelta(seconds=1), 1.0))
        
        elif recovery_type == 'gradual':
            # Gradual recovery over specified duration
            current = failure_time
            end = failure_time + timedelta(minutes=recovery_duration_minutes)
            
            while current <= end:
                progress = (current - failure_time).total_seconds() / (end - failure_time).total_seconds()
                
                # Logarithmic recovery (fast at first, then slower)
                health = math.log(1 + progress * 9) / math.log(10)
                
                pattern.append((current, health))
                current += timedelta(seconds=30)  # Check every 30 seconds
        
        elif recovery_type == 'stepped':
            # Recovery in steps (e.g., as pods restart)
            steps = 5
            for i in range(steps + 1):
                timestamp = failure_time + timedelta(
                    minutes=recovery_duration_minutes * i / steps
                )
                health = i / steps
                pattern.append((timestamp, health))
        
        return pattern
    
    def add_jitter(self, timestamp: datetime, max_jitter_seconds: float = 1.0) -> datetime:
        """Add small random jitter to timestamp"""
        jitter = random.uniform(-max_jitter_seconds, max_jitter_seconds)
        return timestamp + timedelta(seconds=jitter)
    
    def format_timestamp(self, dt: datetime, format_type: str = 'iso') -> str:
        """Format timestamp in various formats"""
        if format_type == 'iso':
            return dt.isoformat() + 'Z'
        elif format_type == 'rfc3339':
            return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        elif format_type == 'unix':
            return str(int(dt.timestamp()))
        elif format_type == 'unix_ms':
            return str(int(dt.timestamp() * 1000))
        elif format_type == 'human':
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == 'kubernetes':
            return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        else:
            return dt.isoformat()
