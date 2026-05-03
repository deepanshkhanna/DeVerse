"""
Main orchestrator for DevVerse Phase 2
Chains together: Configuration -> Transformation -> Delivery
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
from typing import Dict, Optional
from datetime import datetime

# Import our custom modules
from config import load_config, ConfigurationError
from transformer import transform_review, validate_review_input, TransformationError
from deliver import send_to_slack_direct, validate_delivery_input, DeliveryError
from deliver_orchestrate import send_to_orchestrate_agent


# Mock technical review from Bob (or any code review tool)
MOCK_TECHNICAL_REVIEW = """
Code Review for payment_processor.py

CRITICAL ISSUES:
1. Line 23: API key hardcoded in source code - SECURITY VULNERABILITY
2. Line 45: No error handling for network failures
3. Line 67: Race condition in transaction processing
4. Line 89: Using deprecated payment gateway API v1

WARNINGS:
5. Line 102: Inefficient database query (N+1 problem)
6. Line 134: Missing input validation for amount field
7. Line 156: No logging for failed transactions
8. Line 178: Timeout not configured for external API calls

SUGGESTIONS:
9. Line 201: Consider using async/await for better performance
10. Line 223: Add unit tests for edge cases
11. Line 245: Documentation missing for public methods
12. Line 267: Consider implementing retry logic with exponential backoff

POSITIVE NOTES:
- Good separation of concerns
- Clean function naming
- Proper use of type hints
"""


def print_banner(title: str) -> None:
    """Print a formatted banner for section headers"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def print_step(step_num: int, description: str) -> None:
    """Print a formatted step indicator"""
    print(f"\n{'─'*70}")
    print(f"STEP {step_num}: {description}")
    print(f"{'─'*70}\n")


def run_pipeline(use_mock: bool = True, custom_review: Optional[str] = None) -> bool:
    """
    Run the complete DevVerse pipeline
    
    Args:
        use_mock: If True, use the mock review; if False, use custom_review
        custom_review: Custom review text to process (if use_mock is False)
        
    Returns:
        True if pipeline completed successfully, False otherwise
    """
    try:
        print_banner("[*] DevVerse Phase 2 - Full Pipeline Execution")
        
        # ============================================================
        # STEP 1: Load Configuration
        # ============================================================
        print_step(1, "Loading Configuration & Generating IAM Token")
        
        config = load_config()
        
        print("[+] Configuration loaded successfully!")
        print(f"   • watsonx.ai Region: {config['watsonx_region_url']}")
        print(f"   • Project ID: {config['watsonx_project_id']}")
        print(f"   • Orchestrate URL: {config['orchestrate_url'][:50]}...")
        print(f"   • Slack Channel: {config['slack_channel_id']}")
        print(f"   • IAM Token: {config['watsonx_iam_token'][:30]}...")
        
        # ============================================================
        # STEP 2: Prepare Input Review
        # ============================================================
        print_step(2, "Preparing Input Review")
        
        if use_mock:
            raw_review = MOCK_TECHNICAL_REVIEW
            print("[*] Using mock technical review from Bob")
        else:
            if not custom_review:
                raise ValueError("Custom review text is required when use_mock=False")
            raw_review = custom_review
            print("[*] Using custom review text")
        
        print(f"   • Review length: {len(raw_review)} characters")
        print(f"   • Lines: {len(raw_review.splitlines())}")
        
        # Validate input
        validate_review_input(raw_review)
        print("[+] Input validation passed")
        
        # Display preview of raw review
        print("\n[*] Raw Review Preview (first 300 chars):")
        print("-" * 70)
        print(raw_review[:300] + "..." if len(raw_review) > 300 else raw_review)
        print("-" * 70)
        
        # ============================================================
        # STEP 3: Transform with watsonx.ai
        # ============================================================
        print_step(3, "Transforming Review with watsonx.ai (Granite 3-8B)")
        
        print("[*] Calling watsonx.ai API...")
        print(f"   • Model: ibm/granite-3-8b-instruct")
        print(f"   • Decoding: greedy")
        print(f"   • Max tokens: 900")
        
        transformed_review = transform_review(raw_review, config)
        
        print(f"\n[+] Transformation complete!")
        print(f"   • Output length: {len(transformed_review)} characters")
        print(f"   • Lines: {len(transformed_review.splitlines())}")
        
        # Display preview of transformed review
        print("\n[*] Transformed Review Preview (first 500 chars):")
        print("-" * 70)
        print(transformed_review[:500] + "..." if len(transformed_review) > 500 else transformed_review)
        print("-" * 70)
        
        # ============================================================
        # STEP 4: Deliver to Orchestrate → Slack
        # ============================================================
        print_step(4, "Delivering to watsonx Orchestrate → Slack")
        
        # Validate delivery input
        validate_delivery_input(transformed_review)
        print("[+] Delivery validation passed")
        
        # Prepare metadata
        metadata = {
            "reviewer": "Bob AI Assistant",
            "file": "payment_processor.py",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "issues_found": 12,
            "critical_issues": 4,
            "warnings": 4,
            "suggestions": 4,
            "pipeline_version": "Phase2-v1.0"
        }
        
        print("[*] Sending to Orchestrate Agent...")
        
        try:
            result = send_to_orchestrate_agent(transformed_review, config, metadata)
            print(f"\n[+] Delivered successfully via Orchestrate Agent!")
            print(f"   • Status: {result.get('status', 'success')}")
            print(f"   • Message: {result.get('message', 'Review delivered to Slack')}")
            
        except DeliveryError as e:
            print(f"\n[!] Orchestrate Agent delivery failed: {str(e)}")
            print("[*] Attempting direct Slack delivery as fallback...")
            
            result = send_to_slack_direct(transformed_review, config)
            print(f"\n[+] Delivered successfully via Slack API!")
            print(f"   • Message TS: {result.get('ts', 'N/A')}")
        
        # ============================================================
        # STEP 5: Pipeline Complete
        # ============================================================
        print_banner("[+] Pipeline Execution Complete!")
        
        print("[*] Summary:")
        print(f"   • Input: {len(raw_review)} chars -> Output: {len(transformed_review)} chars")
        print(f"   • Transformation: Technical -> Empathetic")
        print(f"   • Delivery: Orchestrate -> Slack Channel {config['slack_channel_id']}")
        print(f"   • Status: SUCCESS [+]")
        
        return True
        
    except ConfigurationError as e:
        print(f"\n[-] Configuration Error: {str(e)}")
        print("[!] Tip: Check your .env file and ensure all credentials are set")
        return False
        
    except TransformationError as e:
        print(f"\n[-] Transformation Error: {str(e)}")
        print("[!] Tip: Check watsonx.ai credentials and API connectivity")
        return False
        
    except DeliveryError as e:
        print(f"\n[-] Delivery Error: {str(e)}")
        print("[!] Tip: Check Orchestrate/Slack credentials and webhook URL")
        return False
        
    except Exception as e:
        print(f"\n[-] Unexpected Error: {str(e)}")
        print(f"[!] Error type: {type(e).__name__}")
        import traceback
        print("\n[*] Full traceback:")
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print_banner("DevVerse Phase 2: Python Implementation")
    print("Architecture: Bob (Mock) -> watsonx.ai -> Orchestrate -> Slack")
    print("Model: IBM Granite 3-8B Instruct")
    print("Purpose: Transform technical reviews into empathetic feedback")
    
    # Run the pipeline with mock data
    success = run_pipeline(use_mock=True)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

# Made with Bob
