"""
Configuration module for DevVerse Phase 2
Handles environment variables and IBM Cloud IAM token generation
"""

import os
import requests
from dotenv import load_dotenv
from typing import Dict, Optional

# Load environment variables from .env file
load_dotenv()


class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass


def get_iam_token(api_key: str) -> str:
    """
    Generate IBM Cloud IAM access token from API key
    
    Args:
        api_key: IBM Cloud API key
        
    Returns:
        IAM access token string
        
    Raises:
        ConfigurationError: If token generation fails
    """
    try:
        # IBM Cloud IAM token endpoint
        token_url = "https://iam.cloud.ibm.com/identity/token"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key
        }
        
        response = requests.post(token_url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data["access_token"]
        
    except requests.exceptions.RequestException as e:
        raise ConfigurationError(f"Failed to generate IAM token: {str(e)}")
    except KeyError:
        raise ConfigurationError("Invalid response format from IAM token endpoint")


def load_config() -> Dict[str, str]:
    """
    Load and validate all configuration from environment variables
    
    Returns:
        Dictionary containing all configuration values including IAM token
        
    Raises:
        ConfigurationError: If required environment variables are missing
    """
    # Required environment variables
    required_vars = {
        "WATSONX_API_KEY": "watsonx.ai API key",
        "WATSONX_REGION_URL": "watsonx.ai region URL",
        "ORCHESTRATE_API_KEY": "Orchestrate API key",
        "ORCHESTRATE_URL": "Orchestrate webhook URL",
        "SLACK_BOT_TOKEN": "Slack bot token",
        "SLACK_CHANNEL_ID": "Slack channel ID"
    }
    
    # Validate all required variables are present
    missing_vars = []
    for var_name, description in required_vars.items():
        if not os.getenv(var_name):
            missing_vars.append(f"{var_name} ({description})")
    
    # Check for either PROJECT_ID or SPACE_ID (at least one required)
    project_id = os.getenv("WATSONX_PROJECT_ID")
    space_id = os.getenv("WATSONX_SPACE_ID")
    
    if not project_id and not space_id:
        missing_vars.append("WATSONX_PROJECT_ID or WATSONX_SPACE_ID (at least one required)")
    
    if missing_vars:
        raise ConfigurationError(
            f"Missing required environment variables:\n" +
            "\n".join(f"  - {var}" for var in missing_vars)
        )
    
    # Load all configuration values (guaranteed to be non-None after validation)
    config: Dict[str, str] = {
        "watsonx_api_key": os.getenv("WATSONX_API_KEY", ""),
        "watsonx_project_id": project_id or "",
        "watsonx_space_id": space_id or "",
        "watsonx_region_url": os.getenv("WATSONX_REGION_URL", ""),
        "orchestrate_api_key": os.getenv("ORCHESTRATE_API_KEY", ""),
        "orchestrate_url": os.getenv("ORCHESTRATE_URL", ""),
        "orchestrate_agent_id": os.getenv("ORCHESTRATE_AGENT_ID", ""),
        "slack_bot_token": os.getenv("SLACK_BOT_TOKEN", ""),
        "slack_channel_id": os.getenv("SLACK_CHANNEL_ID", "")
    }
    
    # Generate IAM token for watsonx.ai authentication
    try:
        print("[*] Generating IAM token for watsonx.ai...")
        config["watsonx_iam_token"] = get_iam_token(config["watsonx_api_key"])
        print("[+] IAM token generated successfully")
    except ConfigurationError as e:
        raise ConfigurationError(f"Failed to initialize configuration: {str(e)}")
    
    return config


def get_watsonx_endpoint(config: Dict[str, str]) -> str:
    """
    Construct the full watsonx.ai text generation endpoint URL
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Full endpoint URL for text generation
    """
    base_url = config["watsonx_region_url"]
    return f"{base_url}/ml/v1/text/generation?version=2023-05-29"


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = load_config()
        print("\n[+] Configuration loaded successfully!")
        print(f"[*] watsonx.ai Region: {config['watsonx_region_url']}")
        print(f"[*] Project ID: {config['watsonx_project_id']}")
        print(f"[*] Orchestrate URL: {config['orchestrate_url']}")
        print(f"[*] Slack Channel: {config['slack_channel_id']}")
        print(f"[*] IAM Token: {config['watsonx_iam_token'][:20]}...")
    except ConfigurationError as e:
        print(f"\n[-] Configuration Error: {str(e)}")

# Made with Bob
