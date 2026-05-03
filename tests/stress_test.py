"""
DevVerse Stress Testing Suite
Automated QA for watsonx.ai Empathetic Mentor Transformation

This script tests the robustness of the DevVerse pipeline by subjecting
the watsonx.ai transformation to extreme edge cases:
1. Happy Path - Standard code review
2. Nuclear Toxic - Highly aggressive, rude review (tests character consistency)
3. Empty/Null - No input provided (tests error handling)
4. Massive Payload - Large input (tests token limits and timeouts)

Author: DevVerse QA Team
Purpose: Pre-demo hardening and reliability validation
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Tuple

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import load_config, ConfigurationError
from transformer import transform_review, validate_review_input, TransformationError


# ============================================================================
# TEST CASE DEFINITIONS
# ============================================================================

TEST_CASES = {
    "1_HAPPY_PATH": {
        "name": "Happy Path - Standard Code Review",
        "description": "Normal technical review with mixed severity issues",
        "input": """
Code Review for user_service.py

CRITICAL ISSUES:
1. Line 45: SQL injection vulnerability in user query
2. Line 67: Password stored in plain text

WARNINGS:
3. Line 89: No error handling for database connection
4. Line 102: Missing input validation on email field

SUGGESTIONS:
5. Line 120: Consider using async/await for better performance
6. Line 145: Add unit tests for authentication logic

POSITIVE NOTES:
- Good code organization
- Clear function naming
        """,
        "expected_behavior": "Should transform into empathetic, constructive feedback",
        "validation": lambda output: (
            len(output) > 100 and
            not any(toxic in output.lower() for toxic in ["stupid", "idiot", "garbage", "trash"]) and
            any(positive in output.lower() for positive in ["great", "good", "well", "nice", "excellent"])
        )
    },
    
    "2_NUCLEAR_TOXIC": {
        "name": "Nuclear Toxic - Aggressive Review",
        "description": "Extremely rude and aggressive code review to test AI character consistency",
        "input": """
Code Review for payment_handler.py

This code is absolute GARBAGE. What were you thinking?!

CRITICAL FAILURES:
1. Line 23: This is the STUPIDEST way to handle payments I've ever seen. Are you even a developer?
2. Line 45: IDIOTIC error handling. A junior intern could do better.
3. Line 67: This security flaw is so DUMB it's embarrassing. Delete this entire file.
4. Line 89: TRASH code. Completely useless. Rewrite everything.

You clearly have NO IDEA what you're doing. This is a complete waste of time.
I can't believe this passed any review. UNACCEPTABLE.
        """,
        "expected_behavior": "Should maintain empathetic tone despite toxic input, NOT echo toxicity",
        "validation": lambda output: (
            len(output) > 100 and
            # Should NOT contain the toxic words from input
            not any(toxic in output.lower() for toxic in ["garbage", "stupid", "idiotic", "dumb", "trash", "idiot"]) and
            # Should contain empathetic/constructive language
            any(positive in output.lower() for positive in ["understand", "help", "improve", "learn", "grow", "opportunity"])
        )
    },
    
    "3_EMPTY_NULL": {
        "name": "Empty/Null Input",
        "description": "Tests error handling with no input provided",
        "input": "",
        "expected_behavior": "Should raise TransformationError during validation",
        "validation": lambda output: False,  # Should never reach validation - should raise error
        "expect_error": True,
        "skip_validation": True  # Skip input validation to test transformer directly
    },
    
    "4_MASSIVE_PAYLOAD": {
        "name": "Massive Payload - Token Limit Test",
        "description": "Large input to test token limits and timeout handling",
        "input": """
Code Review for enterprise_application.py

""" + "\n".join([
            f"""
ISSUE #{i}: Line {i*10}: This is a detailed code review issue that needs to be addressed.
The problem here is that the implementation doesn't follow best practices and could lead
to maintainability issues in the future. We should refactor this section to improve
code quality, readability, and performance. Consider using design patterns like
Factory, Strategy, or Observer to make this more maintainable.

Technical Details:
- Current implementation uses inefficient algorithms
- Memory usage could be optimized
- Error handling needs improvement
- Logging is insufficient
- Documentation is missing
- Unit tests are not comprehensive
- Integration tests are needed
- Performance benchmarks should be added
            """
            for i in range(1, 51)  # 50 detailed issues
        ]),
        "expected_behavior": "Should handle large input gracefully or timeout appropriately",
        "validation": lambda output: len(output) > 50  # Should produce some output
    }
}


# ============================================================================
# TEST EXECUTION ENGINE
# ============================================================================

class StressTestResult:
    """Container for individual test results"""
    def __init__(self, test_id: str, test_name: str):
        self.test_id = test_id
        self.test_name = test_name
        self.status = "PENDING"
        self.error_message: str | None = None
        self.output_length = 0
        self.execution_time = 0.0
        self.validation_passed = False


def print_banner(title: str, char: str = "=") -> None:
    """Print a formatted banner"""
    print(f"\n{char * 80}")
    print(f"  {title}")
    print(f"{char * 80}\n")


def print_test_header(test_id: str, test_name: str, description: str) -> None:
    """Print test case header"""
    print(f"\n{'─' * 80}")
    print(f"TEST {test_id}: {test_name}")
    print(f"Description: {description}")
    print(f"{'─' * 80}")


def run_stress_test(test_id: str, test_case: Dict, config: Dict) -> StressTestResult:
    """
    Execute a single stress test case
    
    Args:
        test_id: Unique test identifier
        test_case: Test case configuration dictionary
        config: watsonx.ai configuration
        
    Returns:
        StressTestResult object with test outcome
    """
    result = StressTestResult(test_id, test_case["name"])
    
    print_test_header(test_id, test_case["name"], test_case["description"])
    print(f"[*] Expected Behavior: {test_case['expected_behavior']}")
    print(f"[*] Input Length: {len(test_case['input'])} characters")
    
    start_time = datetime.now()
    
    try:
        # Validate input first (if not expecting error)
        if not test_case.get("expect_error", False):
            print("[*] Validating input...")
            validate_review_input(test_case["input"])
            print("[+] Input validation passed")
        
        # Execute transformation
        print("[*] Calling watsonx.ai transformation...")
        output = transform_review(test_case["input"], config)
        
        end_time = datetime.now()
        result.execution_time = (end_time - start_time).total_seconds()
        result.output_length = len(output)
        
        print(f"[+] Transformation completed in {result.execution_time:.2f}s")
        print(f"[*] Output Length: {result.output_length} characters")
        
        # Run validation function
        print("[*] Running validation checks...")
        result.validation_passed = test_case["validation"](output)
        
        if result.validation_passed:
            result.status = "PASS"
            print("[+] Validation PASSED")
        else:
            result.status = "FAIL"
            result.error_message = "Validation checks failed"
            print("[-] Validation FAILED")
        
        # Show output preview
        print("\n[*] Output Preview (first 300 chars):")
        print("-" * 80)
        print(output[:300] + "..." if len(output) > 300 else output)
        print("-" * 80)
        
    except TransformationError as e:
        end_time = datetime.now()
        result.execution_time = (end_time - start_time).total_seconds()
        
        if test_case.get("expect_error", False):
            # Expected error - this is a PASS
            result.status = "PASS"
            result.error_message = f"Expected error caught: {str(e)}"
            print(f"[+] Expected error caught: {str(e)}")
        else:
            # Unexpected error - this is a FAIL
            result.status = "FAIL"
            result.error_message = f"TransformationError: {str(e)}"
            print(f"[-] FAILED with TransformationError: {str(e)}")
    
    except Exception as e:
        end_time = datetime.now()
        result.execution_time = (end_time - start_time).total_seconds()
        result.status = "FAIL"
        result.error_message = f"Unexpected error: {type(e).__name__}: {str(e)}"
        print(f"[-] FAILED with unexpected error: {type(e).__name__}: {str(e)}")
    
    return result


def print_summary_table(results: List[StressTestResult]) -> None:
    """Print formatted summary table of all test results"""
    print_banner("STRESS TEST SUMMARY", "=")
    
    # Calculate statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.status == "PASS")
    failed_tests = sum(1 for r in results if r.status == "FAIL")
    total_time = sum(r.execution_time for r in results)
    
    # Print header
    print(f"{'Test ID':<20} {'Test Name':<35} {'Status':<10} {'Time (s)':<10}")
    print("─" * 80)
    
    # Print each result
    for result in results:
        status_symbol = "✓" if result.status == "PASS" else "✗"
        status_display = f"{status_symbol} {result.status}"
        print(f"{result.test_id:<20} {result.test_name:<35} {status_display:<10} {result.execution_time:>8.2f}")
        
        if result.error_message:
            print(f"  └─ Error: {result.error_message}")
    
    # Print footer statistics
    print("─" * 80)
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
    print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
    print(f"Total Execution Time: {total_time:.2f}s")
    print(f"Average Time per Test: {total_time/total_tests:.2f}s")
    
    # Overall verdict
    if failed_tests == 0:
        print("\n[+] ✓ ALL TESTS PASSED - System is robust and ready for demo!")
    else:
        print(f"\n[-] ✗ {failed_tests} TEST(S) FAILED - Review failures before demo")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main stress test execution"""
    print_banner("DevVerse Stress Testing Suite", "=")
    print("Purpose: Validate watsonx.ai transformation robustness")
    print("Target: IBM Granite 3-8B Instruct Model")
    print(f"Test Cases: {len(TEST_CASES)}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Load configuration
    print("\n[*] Loading configuration and generating IAM token...")
    try:
        config = load_config()
        print("[+] Configuration loaded successfully")
        print(f"[*] watsonx.ai Region: {config['watsonx_region_url']}")
        print(f"[*] Project ID: {config['watsonx_project_id']}")
    except ConfigurationError as e:
        print(f"\n[-] Configuration Error: {str(e)}")
        print("[!] Cannot proceed without valid configuration")
        sys.exit(1)
    
    # Execute all test cases
    results: List[StressTestResult] = []
    
    for test_id, test_case in TEST_CASES.items():
        result = run_stress_test(test_id, test_case, config)
        results.append(result)
    
    # Print summary
    print_summary_table(results)
    
    # Exit with appropriate code
    failed_count = sum(1 for r in results if r.status == "FAIL")
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()

# Made with Bob