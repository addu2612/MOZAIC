#!/usr/bin/env python3
"""
Validation script to check if the synthetic log generator is set up correctly
"""
import sys
import os

def check_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {filepath}")
        return True
    else:
        print(f"✗ {filepath} - MISSING")
        return False

def main():
    print("Validating Synthetic Log Generator Setup...\n")
    
    all_good = True
    
    print("Configuration Files:")
    all_good &= check_file_exists("config/services_config.yaml")
    all_good &= check_file_exists("config/incident_patterns.yaml")
    all_good &= check_file_exists("config/generation_config.yaml")
    
    print("\nUtility Modules:")
    all_good &= check_file_exists("utils/__init__.py")
    all_good &= check_file_exists("utils/realistic_data.py")
    all_good &= check_file_exists("utils/timestamp_utils.py")
    all_good &= check_file_exists("utils/correlation_engine.py")
    
    print("\nGenerator Modules:")
    all_good &= check_file_exists("generators/__init__.py")
    all_good &= check_file_exists("generators/kubernetes_generator.py")
    
    print("\n--- TODO (Need to Implement) ---")
    print("☐ generators/sentry_generator.py")
    print("☐ generators/cloudwatch_generator.py")
    print("☐ generators/grafana_generator.py")
    print("☐ main.py")
    
    print("\nDocumentation:")
    check_file_exists("README.md")
    check_file_exists("IMPLEMENTATION_COMPLETE.md")
    check_file_exists("COMPLETE_SUMMARY.md")
    check_file_exists("requirements.txt")
    
    print("\n" + "="*60)
    if all_good:
        print("✓ All existing files validated successfully!")
        print("📝 See IMPLEMENTATION_COMPLETE.md for next steps")
        print("⏱️  Estimated completion time: 5-8 hours")
    else:
        print("✗ Some files are missing. Please check the package.")
    print("="*60)
    
    # Test imports
    print("\nTesting imports...")
    try:
        from utils.realistic_data import realistic_data
        print("✓ realistic_data imported successfully")
        print(f"  Sample IP: {realistic_data.generate_ip_address()}")
        print(f"  Sample trace ID: {realistic_data.generate_trace_id()}")
    except Exception as e:
        print(f"✗ Failed to import realistic_data: {e}")
        all_good = False
    
    try:
        from utils.timestamp_utils import TimestampGenerator
        from datetime import datetime
        tg = TimestampGenerator(datetime.now(), datetime.now())
        print("✓ TimestampGenerator imported successfully")
        print(f"  Traffic multiplier (now): {tg.get_traffic_multiplier(datetime.now()):.2f}x")
    except Exception as e:
        print(f"✗ Failed to import TimestampGenerator: {e}")
        all_good = False
    
    try:
        from utils.correlation_engine import CorrelationEngine
        ce = CorrelationEngine()
        print("✓ CorrelationEngine imported successfully")
    except Exception as e:
        print(f"✗ Failed to import CorrelationEngine: {e}")
        all_good = False
    
    try:
        from generators.kubernetes_generator import KubernetesLogGenerator
        print("✓ KubernetesLogGenerator imported successfully")
    except Exception as e:
        print(f"✗ Failed to import KubernetesLogGenerator: {e}")
        all_good = False
    
    print("\n" + "="*60)
    if all_good:
        print("🎉 Setup validation PASSED!")
        print("Ready to implement remaining generators and main.py")
    else:
        print("❌ Setup validation FAILED")
        print("Please fix the issues above before continuing")
    print("="*60)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
