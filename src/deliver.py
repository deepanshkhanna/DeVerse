"""
Delivery module for DevVerse Phase 2
Sends transformed reviews to watsonx Orchestrate for Slack delivery
"""

import requests
from typing import Dict, Optional
from datetime import datetime


class DeliveryError(Exception):
    """Custom exception for delivery errors"""
    pass


def send_to_orchestrate(formatted_review: str, config: Dict[str, str], metadata: Optional[Dict] = None) -> Dict:
    """
    Send the formatted review to watsonx Orchestrate webhook for Slack delivery
    
    Args:
        formatted_review: The empathetic, transformed review text
        config: Configuration dictionary containing Orchestrate credentials
        metadata: Optional metadata about the review (author, file, timestamp, etc.)
        
    Returns:
        Dictionary containing response data from Orchestrate
        
    Raises:
        DeliveryError: If the webhook call fails
    """
    try:
        # Prepare headers for Orchestrate API
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {config['orchestrate_api_key']}"
        }
        
        # Prepare the payload for Orchestrate
        # The webhook will forward this to Slack
        payload = {
            "review_content": formatted_review,
            "channel_id": config["slack_channel_id"],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "DevVerse-Phase2"
        }
        
        # Add optional metadata if provided
        if metadata:
            payload["metadata"] = metadata
        
        print(f"[*] Sending to watsonx Orchestrate...")
        print(f"[*] Webhook URL: {config['orchestrate_url'][:50]}...")
        print(f"[*] Target Slack Channel: {config['slack_channel_id']}")
        
        # Make the POST request to Orchestrate webhook
        response = requests.post(
            config["orchestrate_url"],
            headers=headers,
            json=payload,
            timeout=30  # 30 second timeout
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse response
        try:
            result = response.json()
        except ValueError:
            # If response is not JSON, create a simple result
            result = {
                "status": "success",
                "status_code": response.status_code,
                "message": "Review delivered successfully"
            }
        
        print(f"[+] Delivery successful!")
        print(f"[*] Status Code: {response.status_code}")
        
        return result
        
    except requests.exceptions.Timeout:
        raise DeliveryError("Request to Orchestrate timed out after 30 seconds")
    except requests.exceptions.HTTPError as e:
        # Extract error details if available
        error_detail = ""
        try:
            error_data = e.response.json()
            error_detail = f": {error_data.get('error', error_data.get('message', ''))}"
        except:
            error_detail = f": {e.response.text[:200]}"
        
        raise DeliveryError(f"HTTP {e.response.status_code} error from Orchestrate{error_detail}")
    except requests.exceptions.RequestException as e:
        raise DeliveryError(f"Failed to connect to Orchestrate: {str(e)}")
    except Exception as e:
        raise DeliveryError(f"Unexpected error during delivery: {str(e)}")


def send_to_slack_direct(formatted_review: str, config: Dict[str, str]) -> Dict:
    """
    Alternative: Send directly to Slack (bypassing Orchestrate)
    Use this as a fallback if Orchestrate is unavailable
    
    Args:
        formatted_review: The empathetic, transformed review text
        config: Configuration dictionary containing Slack credentials
        
    Returns:
        Dictionary containing response data from Slack
        
    Raises:
        DeliveryError: If the Slack API call fails
    """
    try:
        # Slack Web API endpoint for posting messages
        slack_url = "https://slack.com/api/chat.postMessage"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['slack_bot_token']}"
        }
        
        # Format the message with header and footer
        formatted_message = f"""📝 *Code Review Feedback*

{formatted_review}

---
_Delivered by DevVerse • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC_
_Powered by IBM watsonx.ai Granite 3-8B_"""
        
        # Use simple text payload (no blocks to avoid formatting issues)
        payload = {
            "channel": config["slack_channel_id"],
            "text": formatted_message
        }
        
        print(f"[*] Sending directly to Slack (fallback mode)...")
        
        response = requests.post(
            slack_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        if not result.get("ok"):
            raise DeliveryError(f"Slack API error: {result.get('error', 'Unknown error')}")
        
        print(f"[+] Delivered to Slack successfully!")
        return result
        
    except requests.exceptions.RequestException as e:
        raise DeliveryError(f"Failed to send to Slack: {str(e)}")
    except Exception as e:
        raise DeliveryError(f"Unexpected error during Slack delivery: {str(e)}")


def validate_delivery_input(formatted_review: str) -> bool:
    """
    Validate that the review content is suitable for delivery
    
    Args:
        formatted_review: The review text to validate
        
    Returns:
        True if valid, raises DeliveryError if invalid
        
    Raises:
        DeliveryError: If input is invalid
    """
    if not formatted_review or not formatted_review.strip():
        raise DeliveryError("Review content cannot be empty")
    
    if len(formatted_review) < 10:
        raise DeliveryError("Review content is too short (minimum 10 characters)")
    
    # Slack has a message limit of ~40,000 characters
    if len(formatted_review) > 40000:
        raise DeliveryError("Review content exceeds Slack's message limit (40,000 characters)")
    
    return True


if __name__ == "__main__":
    # Test the delivery module
    from config import load_config
    
    try:
        config = load_config()
        
        # Sample transformed review
        sample_review = """
        Hey there! 👋 I've reviewed your authentication code, and I can see you've put good effort into building this feature. Let me share some thoughts that will help make it even better:

        **What You Did Well:**
        - Clear function structure and naming
        - Good attempt at organizing the authentication flow
        
        **Growth Opportunities:**
        
        1. **Password Security** (Line 45): Right now, passwords are stored in plain text, which is a critical security risk. Let's use bcrypt for hashing - it's specifically designed for passwords and includes built-in salt generation. Here's how:
        
        ```python
        import bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        ```
        
        2. **Input Validation** (Line 67): Adding validation on the username field will prevent potential security issues. Consider using a library like `validators` or regex patterns to ensure usernames meet your requirements.
        
        3. **Exception Handling** (Line 89): Catching all exceptions can hide bugs. Try catching specific exceptions like `ValueError` or `DatabaseError` - this makes debugging much easier!
        
        4. **SQL Injection Protection** (Line 102): Great that you're thinking about database queries! Let's use parameterized queries to prevent SQL injection. Your ORM likely supports this out of the box.
        
        5. **Rate Limiting** (Line 120): Adding rate limiting on login attempts protects against brute force attacks. Libraries like `Flask-Limiter` make this straightforward.
        
        These improvements will significantly strengthen your code's security posture. Want to pair program on implementing any of these? I'm here to help! 🚀
        """
        
        print("\n" + "="*60)
        print("Testing Delivery Module")
        print("="*60)
        
        validate_delivery_input(sample_review)
        
        # Test metadata
        metadata = {
            "reviewer": "Bob AI",
            "file": "user_authentication.py",
            "lines_reviewed": 150,
            "issues_found": 5
        }
        
        result = send_to_orchestrate(sample_review, config, metadata)
        
        print("\n" + "="*60)
        print("DELIVERY RESULT:")
        print("="*60)
        print(result)
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n[-] Error: {str(e)}")

# Made with Bob
