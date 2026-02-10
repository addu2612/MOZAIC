#!/usr/bin/env python3
"""
Synthetic Log Generator - Main Orchestrator
Generates hyper-realistic logs across Kubernetes, Sentry, CloudWatch, and Grafana
"""
import argparse
import json
import gzip
import yaml
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Import generators
from generators.kubernetes_generator import KubernetesLogGenerator
from generators.sentry_generator import SentryLogGenerator
from generators.cloudwatch_generator import CloudWatchLogGenerator
from generators.grafana_generator import GrafanaLogGenerator

# Import utilities
from utils.timestamp_utils import TimestampGenerator
from utils.correlation_engine import CorrelationEngine
from utils.realistic_data import realistic_data

# Import scenarios
from scenarios.incident_scenarios import IncidentScenarioGenerator
from scenarios.normal_operations import NormalOperationsGenerator

class SyntheticLogOrchestrator:
    """Main orchestrator for synthetic log generation"""
    
    def __init__(self, config_dir: str = 'config', output_dir: str = 'output'):
        self.config_dir = config_dir
        self.output_dir = output_dir
        
        # Load configurations
        print("Loading configurations...")
        self.services_config = self._load_yaml(f'{config_dir}/services_config.yaml')
        self.incident_patterns = self._load_yaml(f'{config_dir}/incident_patterns.yaml')
        self.generation_config = self._load_yaml(f'{config_dir}/generation_config.yaml')
        
        # Initialize generators
        print("Initializing generators...")
        self.k8s_gen = KubernetesLogGenerator(self.services_config)
        self.sentry_gen = SentryLogGenerator(self.services_config)
        self.cw_gen = CloudWatchLogGenerator(self.services_config)
        self.grafana_gen = GrafanaLogGenerator(self.services_config)
        
        # Initialize correlation engine
        self.corr_engine = CorrelationEngine()
        
        # Initialize scenario generators
        self.incident_gen = IncidentScenarioGenerator(
            self.k8s_gen, self.sentry_gen, self.cw_gen, self.grafana_gen, self.corr_engine
        )
        
        service_names = list(self.services_config.get('services', {}).keys())
        self.normal_gen = NormalOperationsGenerator(
            self.k8s_gen, self.sentry_gen, self.cw_gen, self.grafana_gen, service_names
        )
        
        # Create output directories
        self._create_output_dirs()
        
        print("✓ Initialization complete!\n")
    
    def _load_yaml(self, filepath: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    def _create_output_dirs(self):
        """Create output directory structure"""
        dirs = [
            f'{self.output_dir}/kubernetes',
            f'{self.output_dir}/sentry',
            f'{self.output_dir}/cloudwatch',
            f'{self.output_dir}/grafana',
            f'{self.output_dir}/correlation'
        ]
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        start_date: datetime,
        end_date: datetime,
        compress: bool = True,
        verbose: bool = True
    ):
        """Main generation workflow"""
        
        print(f"Generating logs from {start_date} to {end_date}")
        print(f"Duration: {(end_date - start_date).total_seconds() / 3600:.1f} hours")
        print(f"Compress: {compress}\n")
        
        # Initialize timestamp generator
        ts_gen = TimestampGenerator(start_date, end_date)
        
        # Storage for all logs
        all_logs = {
            'kubernetes': [],
            'sentry': [],
            'cloudwatch': [],
            'grafana': []
        }
        
        # Generation statistics
        stats = {
            'total_logs': 0,
            'incidents': 0,
            'normal_batches': 0
        }
        
        # Calculate incident schedule
        incident_schedule = self._generate_incident_schedule(
            start_date, end_date
        )
        
        print(f"Scheduled {len(incident_schedule)} incidents\n")
        print("="*60)
        print("Generating logs...")
        print("="*60 + "\n")
        
        # Generate normal operations
        current_time = start_date
        incident_idx = 0
        
        while current_time < end_date:
            # Check if we should inject an incident
            if incident_idx < len(incident_schedule):
                next_incident_time, incident_type, duration = incident_schedule[incident_idx]
                
                if current_time >= next_incident_time:
                    # Generate incident
                    if verbose:
                        print(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] Injecting {incident_type} incident (duration: {duration}min)")
                    
                    incident_logs = self._generate_incident(
                        next_incident_time, incident_type, duration
                    )
                    
                    # Append incident logs
                    for source in all_logs:
                        all_logs[source].extend(incident_logs[source])
                    
                    stats['incidents'] += 1
                    stats['total_logs'] += sum(len(incident_logs[s]) for s in all_logs)
                    
                    # Skip ahead past incident
                    current_time = next_incident_time + timedelta(minutes=duration)
                    incident_idx += 1
                    continue
            
            # Generate normal operation logs
            traffic_mult = ts_gen.get_traffic_multiplier(current_time)
            seasonal_mult = ts_gen.get_seasonal_multiplier(current_time)
            
            # Calculate logs per minute based on traffic
            base_logs_per_min = self.generation_config['generation']['normal_logs_per_minute']
            logs_this_batch = int(base_logs_per_min * traffic_mult * seasonal_mult / 60)
            
            normal_logs = self.normal_gen.generate_normal_logs(
                current_time, log_count=max(1, logs_this_batch)
            )
            
            # Append normal logs
            for source in all_logs:
                all_logs[source].extend(normal_logs[source])
            
            stats['normal_batches'] += 1
            stats['total_logs'] += sum(len(normal_logs[s]) for s in all_logs)
            
            # Progress update
            if stats['normal_batches'] % 100 == 0 and verbose:
                progress = (current_time - start_date).total_seconds() / (end_date - start_date).total_seconds()
                print(f"Progress: {progress*100:.1f}% | Logs: {stats['total_logs']:,} | Incidents: {stats['incidents']}")
            
            # Advance time
            current_time = ts_gen.generate_next_timestamp()
        
        print("\n" + "="*60)
        print("Generation complete!")
        print("="*60 + "\n")
        
        # Write outputs
        print("Writing outputs...")
        self._write_outputs(all_logs, start_date, end_date, compress)
        
        # Write correlation metadata
        self._write_correlation_metadata()
        
        # Print statistics
        self._print_statistics(stats, all_logs)
    
    def _generate_incident_schedule(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[tuple]:
        """Generate schedule of when incidents should occur"""
        
        schedule = []
        duration_hours = (end_date - start_date).total_seconds() / 3600
        
        # Get incident configuration
        incident_config = self.generation_config['generation']['incidents']
        total_incidents = incident_config.get('total_count', 50)
        
        # Scale based on duration
        scaled_incidents = int(total_incidents * (duration_hours / 720))  # 720 hours = 30 days
        
        # Get available incident types
        incidents = self.incident_patterns['incidents']
        
        for _ in range(scaled_incidents):
            # Random time within range
            offset_hours = random.uniform(0, duration_hours)
            incident_time = start_date + timedelta(hours=offset_hours)
            
            # Select incident type based on probability
            incident_type = random.choices(
                list(incidents.keys()),
                weights=[incidents[t].get('probability', 0.05) for t in incidents.keys()]
            )[0]
            
            # Get duration range
            duration_range = incidents[incident_type].get('duration_minutes', [10, 60])
            duration = random.randint(duration_range[0], duration_range[1])
            
            schedule.append((incident_time, incident_type, duration))
        
        # Sort by time
        schedule.sort(key=lambda x: x[0])
        
        return schedule
    
    def _generate_incident(
        self,
        start_time: datetime,
        incident_type: str,
        duration_minutes: int
    ) -> Dict[str, List]:
        """Generate a specific incident"""
        
        # Get incident configuration
        incident_config = self.incident_patterns['incidents'].get(incident_type, {})
        affected_services = incident_config.get('affected_services', ['user-service'])
        service = random.choice(affected_services)
        
        # Generate based on incident type
        if incident_type == 'memory_leak':
            return self.incident_gen.generate_memory_leak_incident(
                start_time, service, duration_minutes
            )
        elif incident_type == 'deployment_failure':
            return self.incident_gen.generate_deployment_failure_incident(
                start_time, service, duration_minutes
            )
        elif incident_type == 'database_connection_pool_exhaustion':
            return self.incident_gen.generate_database_connection_pool_exhaustion(
                start_time, service, duration_minutes
            )
        else:
            # Generic incident using correlation engine
            incident = self.corr_engine.create_incident(
                incident_type, start_time, duration_minutes,
                incident_config.get('severity', 'high'),
                [service]
            )
            
            return {
                'kubernetes': self.k8s_gen.generate_for_incident(incident),
                'sentry': self.sentry_gen.generate_for_incident(incident),
                'cloudwatch': self.cw_gen.generate_for_incident(incident),
                'grafana': self.grafana_gen.generate_for_incident(incident)
            }
    
    def _write_outputs(
        self,
        all_logs: Dict[str, List],
        start_date: datetime,
        end_date: datetime,
        compress: bool
    ):
        """Write logs to output files"""
        
        date_str = start_date.strftime('%Y-%m-%d')
        
        for source, logs in all_logs.items():
            if not logs:
                continue
            
            filename = f'{self.output_dir}/{source}/logs_{date_str}.jsonl'
            if compress:
                filename += '.gz'
            
            print(f"Writing {source}: {len(logs):,} entries -> {filename}")
            
            if compress:
                with gzip.open(filename, 'wt') as f:
                    for log in logs:
                        f.write(json.dumps(log) + '\n')
            else:
                with open(filename, 'w') as f:
                    for log in logs:
                        f.write(json.dumps(log) + '\n')
    
    def _write_correlation_metadata(self):
        """Write incident correlation metadata"""
        
        metadata = {
            'incidents': [
                {
                    'incident_id': inc.incident_id,
                    'incident_type': inc.incident_type,
                    'start_time': inc.start_time.isoformat(),
                    'end_time': inc.end_time.isoformat(),
                    'severity': inc.severity,
                    'affected_services': inc.affected_services,
                    'correlation_id': inc.correlation_id,
                    'event_count': len(inc.events)
                }
                for inc in self.corr_engine.incidents
            ]
        }
        
        filepath = f'{self.output_dir}/correlation/incidents.json'
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Correlation metadata: {filepath}")
    
    def _print_statistics(self, stats: Dict, all_logs: Dict[str, List]):
        """Print generation statistics"""
        
        print("\n" + "="*60)
        print("GENERATION STATISTICS")
        print("="*60)
        print(f"Total logs generated: {stats['total_logs']:,}")
        print(f"Incidents generated: {stats['incidents']}")
        print(f"Normal operation batches: {stats['normal_batches']}")
        print()
        print("Logs by source:")
        for source, logs in all_logs.items():
            print(f"  {source:15s}: {len(logs):,}")
        print("="*60 + "\n")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Generate synthetic logs for MOZAIC project'
    )
    
    # Time range
    parser.add_argument('--start-date', type=str, default='2024-01-01',
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=None,
                       help='Number of days to generate')
    parser.add_argument('--hours', type=int, default=None,
                       help='Number of hours to generate')
    
    # Configuration
    parser.add_argument('--config-dir', type=str, default='config',
                       help='Configuration directory')
    parser.add_argument('--output-dir', type=str, default='output',
                       help='Output directory')
    
    # Options
    parser.add_argument('--no-compress', action='store_true',
                       help='Do not compress output files')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal output')
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    
    # Parse dates
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    
    if args.end_date:
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
    elif args.days:
        end_date = start_date + timedelta(days=args.days)
    elif args.hours:
        end_date = start_date + timedelta(hours=args.hours)
    else:
        # Default to 1 day
        end_date = start_date + timedelta(days=1)
    
    print("\n" + "="*60)
    print("MOZAIC Synthetic Log Generator")
    print("="*60 + "\n")
    
    # Initialize orchestrator
    orchestrator = SyntheticLogOrchestrator(
        config_dir=args.config_dir,
        output_dir=args.output_dir
    )
    
    # Generate logs
    orchestrator.generate(
        start_date=start_date,
        end_date=end_date,
        compress=not args.no_compress,
        verbose=not args.quiet
    )
    
    print("✓ Generation complete!\n")
    print(f"Output directory: {args.output_dir}/")
    print()

if __name__ == '__main__':
    main()
