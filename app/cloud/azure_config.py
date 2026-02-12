"""
Azure Configuration for Lab Sheet Generator V3.0
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

# Load environment variables
load_dotenv(env_file)

# Get Azure Client ID from environment
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")


def get_client_id() -> str:
    """
    Get the Azure Client ID from environment variables.
    
    Returns:
        str: Client ID
        
    Raises:
        ValueError: If CLIENT_ID not configured
    """
    if not AZURE_CLIENT_ID or AZURE_CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        raise ValueError(
            "❌ Azure Client ID not configured!\n\n"
            "Please follow these steps:\n"
            "1. Copy .env.example to .env\n"
            "2. Edit .env and add your Client ID\n"
            "3. Get Client ID from: https://portal.azure.com\n\n"
            "See AZURE_SETUP_GUIDE.md for detailed instructions"
        )
    
    return AZURE_CLIENT_ID


def is_configured() -> bool:
    """
    Check if Azure Client ID is properly configured.
    
    Returns:
        bool: True if configured
    """
    return (
        AZURE_CLIENT_ID is not None and 
        AZURE_CLIENT_ID != "YOUR_CLIENT_ID_HERE" and
        len(AZURE_CLIENT_ID) > 0
    )


def get_debug_mode() -> bool:
    """
    Check if debug mode is enabled.
    
    Returns:
        bool: True if debug mode is on
    """
    return os.getenv("DEBUG_MODE", "false").lower() == "true"