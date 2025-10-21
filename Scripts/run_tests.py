#!/usr/bin/env python3
"""
OmniFy Test Runner
Comprehensive test execution script for all test types
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Exit code: {result.returncode}")
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    
    return result.returncode == 0

def run_unit_tests():
    """Run unit tests"""
    command = "pytest tests/test_backend_services.py -m unit -v --cov=backend --cov-report=term-missing"
    return run_command(command, "Unit Tests")

def run_integration_tests():
    """Run integration tests"""
    command = "pytest tests/test_api_integration.py -m integration -v --cov=backend --cov-report=term-missing"
    return run_command(command, "Integration Tests")

def run_performance_tests():
    """Run performance tests"""
    command = "pytest tests/test_performance.py -m performance -v --tb=short"
    return run_command(command, "Performance Tests")

def run_security_tests():
    """Run security tests"""
    commands = [
        ("bandit -r backend/ -f json -o security-report.json", "Security Scan (Bandit)"),
        ("safety check --json --output safety-report.json", "Dependency Security Check"),
        ("pytest tests/ -m security -v", "Security Tests")
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success

def run_load_tests():
    """Run load tests"""
    command = "pytest tests/test_performance.py -m load -v --tb=short"
    return run_command(command, "Load Tests")

def run_stress_tests():
    """Run stress tests"""
    command = "pytest tests/test_performance.py -m stress -v --tb=short"
    return run_command(command, "Stress Tests")

def run_code_quality_checks():
    """Run code quality checks"""
    commands = [
        ("black --check backend/", "Code Formatting Check (Black)"),
        ("isort --check-only backend/", "Import Sorting Check (isort)"),
        ("flake8 backend/", "Linting Check (Flake8)"),
        ("mypy backend/ --ignore-missing-imports", "Type Checking (MyPy)")
    ]
    
    success = True
    for command, description in commands:
        if not run_command(command, description):
            success = False
    
    return success

def run_all_tests():
    """Run all tests"""
    test_suites = [
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
        ("Performance Tests", run_performance_tests),
        ("Security Tests", run_security_tests),
        ("Load Tests", run_load_tests),
        ("Stress Tests", run_stress_tests),
        ("Code Quality Checks", run_code_quality_checks)
    ]
    
    results = {}
    total_start_time = time.time()
    
    print(f"\n{'='*80}")
    print("OMNIFY COMPREHENSIVE TEST SUITE")
    print(f"{'='*80}")
    
    for suite_name, suite_func in test_suites:
        print(f"\n{'='*60}")
        print(f"Starting: {suite_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        success = suite_func()
        end_time = time.time()
        
        results[suite_name] = {
            "success": success,
            "duration": end_time - start_time
        }
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{suite_name}: {status} ({end_time - start_time:.2f}s)")
    
    total_end_time = time.time()
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUITE SUMMARY")
    print(f"{'='*80}")
    
    passed = 0
    failed = 0
    
    for suite_name, result in results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{suite_name:<25} {status:<10} {result['duration']:>8.2f}s")
        
        if result["success"]:
            passed += 1
        else:
            failed += 1
    
    print(f"{'='*80}")
    print(f"Total Duration: {total_end_time - total_start_time:.2f}s")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed > 0:
        print(f"\n❌ {failed} test suite(s) failed!")
        sys.exit(1)
    else:
        print(f"\n✅ All test suites passed!")
        sys.exit(0)

def generate_coverage_report():
    """Generate comprehensive coverage report"""
    command = "pytest tests/ --cov=backend --cov-report=html --cov-report=xml --cov-report=term-missing"
    return run_command(command, "Coverage Report Generation")

def run_specific_test(test_path):
    """Run specific test file"""
    command = f"pytest {test_path} -v"
    return run_command(command, f"Specific Test: {test_path}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="OmniFy Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--security", action="store_true", help="Run security tests only")
    parser.add_argument("--load", action="store_true", help="Run load tests only")
    parser.add_argument("--stress", action="store_true", help="Run stress tests only")
    parser.add_argument("--quality", action="store_true", help="Run code quality checks only")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--test", type=str, help="Run specific test file")
    parser.add_argument("--all", action="store_true", help="Run all tests (default)")
    
    args = parser.parse_args()
    
    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(project_root)
    os.environ["TESTING"] = "true"
    
    # Run specific test suites
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.performance:
        success = run_performance_tests()
    elif args.security:
        success = run_security_tests()
    elif args.load:
        success = run_load_tests()
    elif args.stress:
        success = run_stress_tests()
    elif args.quality:
        success = run_code_quality_checks()
    elif args.coverage:
        success = generate_coverage_report()
    elif args.test:
        success = run_specific_test(args.test)
    else:
        # Default: run all tests
        run_all_tests()
        return
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
