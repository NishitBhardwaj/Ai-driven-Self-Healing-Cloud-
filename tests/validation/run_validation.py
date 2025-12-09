"""
Run System Validation
Main script to run all validation tests
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.validation.system_validation import SystemValidator
from tests.validation.continuous_validation import ContinuousValidator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run system validation"""
    logger.info("=" * 60)
    logger.info("AI-Driven Self-Healing Cloud - System Validation")
    logger.info("=" * 60)
    
    # Run comprehensive validation
    validator = SystemValidator()
    report = validator.validate_all()
    
    # Print results
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    print(f"Overall Status: {report.overall_status.upper()}")
    print(f"Total Tests: {report.total_tests}")
    print(f"Passed: {report.passed_tests}")
    print(f"Failed: {report.failed_tests}")
    print(f"Pass Rate: {report.summary['pass_rate']:.2%}")
    print(f"Duration: {report.summary['duration']:.2f}s")
    print("\n" + "-" * 60)
    print("Test Details:")
    print("-" * 60)
    
    for result in report.results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"\n[{status}] {result.test_name}")
        print(f"  {result.message}")
        print(f"  Duration: {result.duration:.2f}s")
    
    print("\n" + "=" * 60)
    
    # Exit with appropriate code
    if report.overall_status == "pass":
        sys.exit(0)
    elif report.overall_status == "partial":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()

