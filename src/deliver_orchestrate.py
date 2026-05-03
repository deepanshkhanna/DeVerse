"""
Orchestrate Agent integration for DevVerse
Sends code reviews via watsonx Orchestrate Agent Chat API
"""

import requests
from typing import Dict, Optional
from datetime import datetime


class DeliveryError(Exception):
    """Custom exception for delivery errors"""
    pass


def send_to_orchestrate_agent(formatted_review: str, config: Dict[str, str], metadata: Optional[Dict] = None) -> Dict:
    """
    Send the formatted review to watsonx Orchestrate Agent for Slack delivery
    
    Uses the Agent Chat API to trigger the workflow that sends messages to Slack
    via OpenAPI-based webhook integration.
    
    Args:
        formatted_review: The empathetic, transformed review text
        config: Configuration dictionary containing Orchestrate credentials
        metadata: Optional metadata about the review (author, file, timestamp, etc.)
        
    Returns:
        Dictionary containing response data from Orchestrate
        
    Raises:
        DeliveryError: If the Agent API call fails
    """
    try:
        # Check if we have Agent ID configured
        agent_id = config.get('orchestrate_agent_id')
        if not agent_id:
            raise DeliveryError("ORCHESTRATE_AGENT_ID not configured in .env file")
        
        # Orchestrate Agent Chat API endpoint
        base_url = config['orchestrate_url'].rstrip('/')
        agent_url = f"{base_url}/api/v1/agents/{agent_id}/chat"
        
        # Prepare headers for Orchestrate Agent API
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {config['orchestrate_api_key']}"
        }
        
        # Format the message for Slack with nice formatting
        formatted_message = f"""📝 *DevVerse Code Review Feedback*

{formatted_review}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Powered by IBM watsonx.ai Granite 3-8B
⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
🎯 DevVerse - Empathy-Driven Code Reviews"""
        
        # Add metadata if provided
        if metadata:
            metadata_str = "\n".join([f"• {k}: {v}" for k, v in metadata.items()])
            formatted_message += f"\n\n*Metadata:*\n{metadata_str}"
        
        # Prepare the payload for Orchestrate Agent
        # The agent will call the workflow with this message
        payload = {
            "message": f"Send this code review to Slack: {formatted_message}",
            "context": {
                "source": "DevVerse",
                "type": "code_review",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        print(f"[*] Sending to watsonx Orchestrate Agent...")
        print(f"[*] Agent URL: {agent_url}")
        print(f"[*] Agent ID: {agent_id}")
        
        # Make the POST request to Orchestrate Agent
        response = requests.post(
            agent_url,
            headers=headers,
            json=payload,
            timeout=60  # 60 second timeout for agent processing
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
                "message": "Review sent to Orchestrate Agent"
            }
        
        print(f"[+] Delivery successful via Orchestrate Agent!")
        print(f"[*] Status Code: {response.status_code}")
        
        return result
        
    except requests.exceptions.Timeout:
        raise DeliveryError("Request to Orchestrate Agent timed out after 60 seconds")
    except requests.exceptions.HTTPError as e:
        # Extract error details if available
        error_detail = ""
        try:
            error_data = e.response.json()
            error_detail = f": {error_data.get('error', error_data.get('message', ''))}"
        except:
            error_detail = f": {e.response.text[:200]}"
        
        raise DeliveryError(f"HTTP {e.response.status_code} error from Orchestrate Agent{error_detail}")
    except requests.exceptions.RequestException as e:
        raise DeliveryError(f"Failed to connect to Orchestrate Agent: {str(e)}")
    except Exception as e:
        raise DeliveryError(f"Unexpected error during Orchestrate delivery: {str(e)}")


# Made with Bob