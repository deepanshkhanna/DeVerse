"""
watsonx.ai API Diagnostic Tool
Helps debug 403 Forbidden errors by testing different configurations

This script will:
1. Test IAM token generation
2. Test API endpoint connectivity
3. Try different model IDs
4. Provide detailed error information
"""

import sys
import os
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import load_config, get_iam_token, ConfigurationError


def print_banner(title: str) -> None:
    """Print formatted banner"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_iam_token(api_key: str) -> tuple[bool, str]:
    """Test IAM token generation"""
    print("[*] Testing IAM token generation...")
    try:
        token = get_iam_token(api_key)
        print(f"[+] IAM token generated successfully")
        print(f"[*] Token preview: {token[:30]}...")
        return True, token
    except Exception as e:
        print(f"[-] IAM token generation failed: {str(e)}")
        return False, ""


def test_model_access(config: dict, model_id: str) -> tuple[bool, str]:
    """Test access to a specific model"""
    print(f"\n[*] Testing model: {model_id}")
    
    endpoint = f"{config['watsonx_region_url'].rstrip('/')}/ml/v1/text/generation?version=2023-05-29"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['watsonx_iam_token']}"
    }
    
    # Test with project_id in header
    headers_with_project = headers.copy()
    headers_with_project["X-Project-Id"] = config["watsonx_project_id"]
    
    payload = {
        "input": "Hello, this is a test.",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 50
        },
        "model_id": model_id,
        "project_id": config["watsonx_project_id"]
    }
    
    try:
        print(f"[*] Sending request to: {endpoint}")
        print(f"[*] Using project_id: {config['watsonx_project_id']}")
        
        response = requests.post(
            endpoint,
            headers=headers_with_project,
            json=payload,
            timeout=30
        )
        
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"[+] SUCCESS! Model {model_id} is accessible")
            result = response.json()
            if "results" in result and len(result["results"]) > 0:
                generated = result["results"][0]["generated_text"]
                print(f"[*] Generated text: {generated[:100]}...")
            return True, "Success"
        else:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f": {error_data}"
            except:
                error_msg += f": {response.text[:200]}"
            
            print(f"[-] FAILED: {error_msg}")
            return False, error_msg
            
    except Exception as e:
        error_msg = f"Exception: {type(e).__name__}: {str(e)}"
        print(f"[-] FAILED: {error_msg}")
        return False, error_msg


def test_alternative_authentication(config: dict) -> None:
    """Test alternative authentication methods"""
    print("\n[*] Testing alternative authentication methods...")
    
    endpoint = f"{config['watsonx_region_url'].rstrip('/')}/ml/v1/text/generation?version=2023-05-29"
    
    # Method 1: Project ID in URL parameter
    print("\n[1] Testing with project_id as URL parameter...")
    endpoint_with_param = f"{endpoint}&project_id={config['watsonx_project_id']}"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config['watsonx_iam_token']}"
    }
    
    payload = {
        "input": "Test",
        "parameters": {"decoding_method": "greedy", "max_new_tokens": 20},
        "model_id": "ibm/granite-3-8b-instruct"
    }
    
    try:
        response = requests.post(endpoint_with_param, headers=headers, json=payload, timeout=30)
        print(f"[*] Status: {response.status_code}")
        if response.status_code == 200:
            print("[+] Method 1 WORKS!")
        else:
            print(f"[-] Method 1 failed: {response.text[:200]}")
    except Exception as e:
        print(f"[-] Method 1 exception: {str(e)}")


def main():
    """Main diagnostic routine"""
    print_banner("watsonx.ai API Diagnostic Tool")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("Purpose: Debug 403 Forbidden errors\n")
    
    # Load configuration
    print("[*] Loading configuration...")
    try:
        config = load_config()
        print("[+] Configuration loaded")
        print(f"[*] Region: {config['watsonx_region_url']}")
        print(f"[*] Project ID: {config['watsonx_project_id']}")
    except ConfigurationError as e:
        print(f"[-] Configuration error: {str(e)}")
        sys.exit(1)
    
    # Test IAM token
    print_banner("Step 1: IAM Token Test")
    success, token = test_iam_token(config['watsonx_api_key'])
    if not success:
        print("\n[!] Cannot proceed without valid IAM token")
        sys.exit(1)
    
    # Test different models
    print_banner("Step 2: Model Access Tests")
    
    models_to_test = [
        "ibm/granite-3-8b-instruct",
        "ibm/granite-13b-chat-v2",
        "meta-llama/llama-3-70b-instruct",
        "ibm/granite-20b-multilingual"
    ]
    
    results = {}
    for model in models_to_test:
        success, msg = test_model_access(config, model)
        results[model] = (success, msg)
    
    # Test alternative auth methods
    print_banner("Step 3: Alternative Authentication Methods")
    test_alternative_authentication(config)
    
    # Summary
    print_banner("DIAGNOSTIC SUMMARY")
    print("Model Access Results:")
    print("-" * 80)
    
    working_models = []
    for model, (success, msg) in results.items():
        status = "✓ WORKS" if success else "✗ FAILS"
        print(f"{status:10} | {model}")
        if not success:
            print(f"           | Error: {msg}")
        else:
            working_models.append(model)
    
    print("-" * 80)
    
    if working_models:
        print(f"\n[+] SUCCESS! {len(working_models)} model(s) are accessible:")
        for model in working_models:
            print(f"    - {model}")
        print("\n[*] Recommendation: Update transformer.py to use one of these models")
    else:
        print("\n[-] CRITICAL: No models are accessible!")
        print("\n[!] Possible issues:")
        print("    1. API key doesn't have Watson Machine Learning permissions")
        print("    2. Project ID is incorrect or inaccessible")
        print("    3. Region mismatch between project and API endpoint")
        print("    4. Account doesn't have watsonx.ai access")
        print("\n[*] Next steps:")
        print("    1. Verify API key has 'Editor' role on Watson Machine Learning")
        print("    2. Confirm project ID in IBM Cloud console")
        print("    3. Check project region matches WATSONX_REGION_URL")


if __name__ == "__main__":
    main()

# Made with Bob