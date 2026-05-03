"""
Transformer module for DevVerse Phase 2
Transforms technical code reviews into empathetic, mentor-style feedback using watsonx.ai
"""

import requests
from typing import Dict, Optional


class TransformationError(Exception):
    """Custom exception for transformation errors"""
    pass


# Empathy-driven system prompt for the AI mentor
MENTOR_SYSTEM_PROMPT = """You are an experienced, empathetic software engineering mentor reviewing code from junior developers. Your role is to transform technical code review feedback into constructive, encouraging guidance that:

1. **Acknowledges effort and positive aspects** - Start by recognizing what the developer did well
2. **Explains the "why" behind suggestions** - Help them understand the reasoning, not just the fix
3. **Provides learning opportunities** - Share relevant concepts, patterns, or best practices
4. **Uses encouraging language** - Frame feedback as growth opportunities, not criticisms
5. **Offers concrete examples** - Show how to improve with specific code examples when helpful
6. **Maintains professionalism** - Be supportive yet professional, like a trusted mentor

Transform the following technical code review into empathetic, mentor-style feedback that will help the developer grow:"""


def transform_review(raw_review_text: str, config: Dict[str, str]) -> str:
    """
    Transform technical code review into empathetic mentor-style feedback using watsonx.ai
    
    Args:
        raw_review_text: Raw technical review text from Bob or other source
        config: Configuration dictionary containing watsonx credentials and settings
        
    Returns:
        Transformed, empathetic review text
        
    Raises:
        TransformationError: If the API call fails or returns invalid data
    """
    try:
        # Construct the full endpoint URL (strip trailing slash to avoid double slashes)
        endpoint = f"{config['watsonx_region_url'].rstrip('/')}/ml/v1/text/generation?version=2023-05-29"
        
        # Prepare headers with IAM token
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['watsonx_iam_token']}"
        }
        
        # Add Project ID or Space ID to headers (use whichever is available)
        if config.get("watsonx_space_id"):
            headers["X-Deployment-Space-Id"] = config["watsonx_space_id"]
            print(f"[*] Using Deployment Space ID: {config['watsonx_space_id']}")
        elif config.get("watsonx_project_id"):
            headers["X-Project-Id"] = config["watsonx_project_id"]
            print(f"[*] Using Project ID: {config['watsonx_project_id']}")
        
        # Construct the full prompt with system context and user review
        full_prompt = f"{MENTOR_SYSTEM_PROMPT}\n\n---\n\nTechnical Review:\n{raw_review_text}\n\n---\n\nEmpathetic Mentor Feedback:"
        
        # Prepare the request payload for watsonx.ai
        payload = {
            "input": full_prompt,
            "parameters": {
                "decoding_method": "greedy",  # Deterministic output for consistency
                "max_new_tokens": 900,        # Allow comprehensive feedback
                "min_new_tokens": 50,         # Ensure meaningful response
                "stop_sequences": [],         # No special stop sequences
                "repetition_penalty": 1.1     # Slight penalty to avoid repetition
            },
            "model_id": "ibm/granite-3-8b-instruct"  # Granite 3-8B model
        }
        
        # Add project_id or space_id to payload (use whichever is available)
        if config.get("watsonx_space_id"):
            payload["space_id"] = config["watsonx_space_id"]
        elif config.get("watsonx_project_id"):
            payload["project_id"] = config["watsonx_project_id"]
        
        print(f"[*] Calling watsonx.ai with Granite 3-8B model...")
        print(f"[*] Input length: {len(raw_review_text)} characters")
        
        # Make the API request
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60  # 60 second timeout for generation
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse the response
        result = response.json()
        
        # Extract the generated text from the response
        if "results" in result and len(result["results"]) > 0:
            generated_text = result["results"][0]["generated_text"].strip()
            
            # Validate we got meaningful output
            if not generated_text:
                raise TransformationError("Received empty response from watsonx.ai")
            
            print(f"[+] Transformation successful!")
            print(f"[*] Output length: {len(generated_text)} characters")
            print(f"[*] Tokens generated: {result['results'][0].get('generated_token_count', 'N/A')}")
            
            return generated_text
        else:
            raise TransformationError("Invalid response format from watsonx.ai")
            
    except requests.exceptions.Timeout:
        raise TransformationError("Request to watsonx.ai timed out after 60 seconds")
    except requests.exceptions.RequestException as e:
        raise TransformationError(f"API request failed: {str(e)}")
    except KeyError as e:
        raise TransformationError(f"Missing expected field in response: {str(e)}")
    except Exception as e:
        raise TransformationError(f"Unexpected error during transformation: {str(e)}")


def validate_review_input(raw_review_text: str) -> bool:
    """
    Validate that the input review text is suitable for transformation
    
    Args:
        raw_review_text: The review text to validate
        
    Returns:
        True if valid, raises TransformationError if invalid
        
    Raises:
        TransformationError: If input is invalid
    """
    if not raw_review_text or not raw_review_text.strip():
        raise TransformationError("Review text cannot be empty")
    
    if len(raw_review_text) < 10:
        raise TransformationError("Review text is too short (minimum 10 characters)")
    
    if len(raw_review_text) > 10000:
        raise TransformationError("Review text is too long (maximum 10,000 characters)")
    
    return True


if __name__ == "__main__":
    # Test the transformer with a sample review
    from config import load_config
    
    try:
        config = load_config()
        
        # Sample technical review
        sample_review = """
        Code Review for user_authentication.py:
        
        Issues found:
        1. Line 45: Using plain text password storage - CRITICAL SECURITY ISSUE
        2. Line 67: No input validation on username field
        3. Line 89: Exception handling is too broad, catching all exceptions
        4. Line 102: SQL query is vulnerable to injection attacks
        5. Line 120: No rate limiting on login attempts
        
        Recommendations:
        - Implement bcrypt for password hashing
        - Add input sanitization
        - Use specific exception types
        - Use parameterized queries
        - Add rate limiting middleware
        """
        
        print("\n" + "="*60)
        print("Testing Transformer Module")
        print("="*60)
        
        validate_review_input(sample_review)
        transformed = transform_review(sample_review, config)
        
        print("\n" + "="*60)
        print("TRANSFORMED REVIEW:")
        print("="*60)
        print(transformed)
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n[-] Error: {str(e)}")

# Made with Bob
