#!/usr/bin/env python3
"""
Comprehensive Test Runner for OmniFy Cloud Connect
Runs all test suites with proper configuration and reporting
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class TestRunner:
    """Comprehensive test runner for OmniFy"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.results_dir = self.project_root / "test-results"
        self.coverage_dir = self.project_root / "htmlcov"
        
        # Ensure results directory exists
        self.results_dir.mkdir(exist_ok=True)
        
        # Test suites configuration
        self.test_suites = {
            "unit": {
                "pattern": "test_*_service*.py",
                "markers": ["unit", "fast"],
                "description": "Unit tests for individual services"
            },
            "integration": {
                "pattern": "test_*_integration*.py",
                "markers": ["integration"],
                "description": "Integration tests for API endpoints"
            },
            "e2e": {
                "pattern": "test_e2e_*.py",
                "markers": ["e2e"],
                "description": "End-to-end user journey tests"
            },
            "performance": {
                "pattern": "test_performance_*.py",
                "markers": ["performance", "slow"],
                "description": "Performance and load tests"
            },
            "security": {
                "pattern": "test_security_*.py",
                "markers": ["security"],
                "description": "Security vulnerability tests"
            },
            "all": {
                "pattern": "test_*.py",
                "markers": [],
                "description": "All tests"
            }
        }
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Run a command and return results"""
        cwd = cwd or self.project_root
        
        print(f"Running: {' '.join(command)}")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timed out after 1 hour",
                "duration": 3600
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "duration": 0
            }
    
    def run_test_suite(self, suite_name: str, verbose: bool = False) -> Dict[str, Any]:
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}")
        
        suite_config = self.test_suites[suite_name]
        
        # Build pytest command
        command = ["python", "-m", "pytest"]
        
        if verbose:
            command.append("-vv")
        
        # Add markers if specified
        if suite_config["markers"]:
            markers = " or ".join(suite_config["markers"])
            command.extend(["-m", markers])
        
        # Add pattern if not running all tests
        if suite_name != "all":
            pattern = self.test_dir / suite_config["pattern"]
            command.append(str(pattern))
        else:
            command.append(str(self.test_dir))
        
        # Add output options
        command.extend([
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
            "--cov=backend",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-report=xml",
            "--cov-fail-under=80",
            f"--junitxml={self.results_dir}/junit-{suite_name}.xml",
            f"--html={self.results_dir}/report-{suite_name}.html",
            "--self-contained-html"
        ])
        
        print(f"\n{'='*60}")
        print(f"Running {suite_name.upper()} tests")
        print(f"Description: {suite_config['description']}")
        print(f"{'='*60}")
        
        result = self.run_command(command)
        
        # Save detailed results
        results_file = self.results_dir / f"results-{suite_name}.json"
        with open(results_file, "w") as f:
            json.dump({
                "suite": suite_name,
                "config": suite_config,
                "command": command,
                "result": result,
                "timestamp": time.time()
            }, f, indent=2)
        
        return result
    
    def run_all_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run all test suites"""
        print("🚀 Starting Comprehensive Test Suite for OmniFy Cloud Connect")
        print(f"📁 Test directory: {self.test_dir}")
        print(f"📊 Results directory: {self.results_dir}")
        
        overall_results = {
            "start_time": time.time(),
            "suites": {},
            "summary": {
                "total_suites": 0,
                "passed_suites": 0,
                "failed_suites": 0,
                "total_duration": 0
            }
        }
        
        # Run each test suite
        for suite_name in ["unit", "integration", "e2e", "performance", "security"]:
            print(f"\n🔄 Running {suite_name} tests...")
            
            suite_result = self.run_test_suite(suite_name, verbose)
            overall_results["suites"][suite_name] = suite_result
            overall_results["summary"]["total_suites"] += 1
            
            if suite_result["success"]:
                overall_results["summary"]["passed_suites"] += 1
                print(f"✅ {suite_name} tests PASSED ({suite_result['duration']:.2f}s)")
            else:
                overall_results["summary"]["failed_suites"] += 1
                print(f"❌ {suite_name} tests FAILED ({suite_result['duration']:.2f}s)")
                if suite_result["stderr"]:
                    print(f"Error: {suite_result['stderr']}")
            
            overall_results["summary"]["total_duration"] += suite_result["duration"]
        
        overall_results["end_time"] = time.time()
        overall_results["summary"]["total_duration"] = overall_results["end_time"] - overall_results["start_time"]
        
        # Save overall results
        results_file = self.results_dir / "overall-results.json"
        with open(results_file, "w") as f:
            json.dump(overall_results, f, indent=2)
        
        # Print summary
        self.print_summary(overall_results)
        
        return overall_results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print test results summary"""
        summary = results["summary"]
        
        print(f"\n{'='*60}")
        print("📊 TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total Suites: {summary['total_suites']}")
        print(f"Passed: {summary['passed_suites']} ✅")
        print(f"Failed: {summary['failed_suites']} ❌")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"Success Rate: {(summary['passed_suites']/summary['total_suites']*100):.1f}%")
        
        print(f"\n📁 Results saved to: {self.results_dir}")
        print(f"📊 Coverage report: {self.coverage_dir}/index.html")
        
        # Print individual suite results
        print(f"\n📋 Individual Suite Results:")
        for suite_name, suite_result in results["suites"].items():
            status = "✅ PASSED" if suite_result["success"] else "❌ FAILED"
            print(f"  {suite_name:12} {status:10} ({suite_result['duration']:.2f}s)")
        
        if summary["failed_suites"] > 0:
            print(f"\n❌ {summary['failed_suites']} test suite(s) failed. Check logs for details.")
            sys.exit(1)
        else:
            print(f"\n🎉 All test suites passed!")
    
    def run_coverage_report(self):
        """Generate comprehensive coverage report"""
        print("\n📊 Generating coverage report...")
        
        command = [
            "python", "-m", "coverage", "combine",
            "--rcfile=pytest.ini"
        ]
        
        result = self.run_command(command)
        
        if result["success"]:
            # Generate HTML report
            html_command = [
                "python", "-m", "coverage", "html",
                "--rcfile=pytest.ini"
            ]
            
            html_result = self.run_command(html_command)
            
            if html_result["success"]:
                print(f"✅ Coverage report generated: {self.coverage_dir}/index.html")
            else:
                print(f"❌ Failed to generate HTML coverage report: {html_result['stderr']}")
        else:
            print(f"❌ Failed to combine coverage data: {result['stderr']}")
    
    def run_specific_tests(self, test_pattern: str, verbose: bool = False):
        """Run specific tests matching a pattern"""
        print(f"🔍 Running tests matching pattern: {test_pattern}")
        
        command = [
            "python", "-m", "pytest",
            "-v" if verbose else "",
            str(self.test_dir / test_pattern),
            "--tb=short",
            "--strict-markers",
            "--disable-warnings"
        ]
        
        # Remove empty strings
        command = [c for c in command if c]
        
        result = self.run_command(command)
        
        if result["success"]:
            print(f"✅ Tests passed ({result['duration']:.2f}s)")
        else:
            print(f"❌ Tests failed ({result['duration']:.2f}s)")
            if result["stderr"]:
                print(f"Error: {result['stderr']}")
        
        return result

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OmniFy Cloud Connect Test Runner")
    parser.add_argument(
        "suite",
        nargs="?",
        choices=["unit", "integration", "e2e", "performance", "security", "all"],
        default="all",
        help="Test suite to run (default: all)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--pattern",
        help="Run tests matching specific pattern"
    )
    parser.add_argument(
        "--coverage-only",
        action="store_true",
        help="Only generate coverage report"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.coverage_only:
            runner.run_coverage_report()
        elif args.pattern:
            runner.run_specific_tests(args.pattern, args.verbose)
        elif args.suite == "all":
            runner.run_all_tests(args.verbose)
        else:
            result = runner.run_test_suite(args.suite, args.verbose)
            if result["success"]:
                print(f"✅ {args.suite} tests passed!")
            else:
                print(f"❌ {args.suite} tests failed!")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
