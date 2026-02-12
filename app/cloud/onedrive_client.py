"""
OneDrive Client for Lab Sheet Generator V3.0
Handles OAuth 2.0 authentication and file operations via Microsoft Graph API
"""

import msal
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OneDriveClient:
    """
    OneDrive integration using Microsoft Graph API.
    Handles OAuth 2.0 authentication and file operations.
    """
    
    # Microsoft Graph API endpoints
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    AUTHORITY = "https://login.microsoftonline.com/common"
    
    # OAuth scopes needed
    SCOPES = [
        "Files.ReadWrite",      # Read/write OneDrive files
        "User.Read",            # Basic user info
    ]
    
    def __init__(self, client_id: str, config_dir: Path):
        """
        Initialize OneDrive client.
        
        Args:
            client_id: Azure AD application (client) ID
            config_dir: Directory for storing token cache
        """
        self.client_id = client_id
        self.config_dir = config_dir
        self.token_cache_file = config_dir / ".token_cache.bin"
        self.access_token = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create MSAL application
        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.AUTHORITY,
            token_cache=self._load_token_cache()
        )
        
        logger.info("OneDrive client initialized")
    
    def _load_token_cache(self) -> msal.SerializableTokenCache:
        """Load token cache from disk."""
        cache = msal.SerializableTokenCache()
        
        if self.token_cache_file.exists():
            try:
                cache.deserialize(self.token_cache_file.read_text())
                logger.info("Token cache loaded from disk")
            except Exception as e:
                logger.warning(f"Failed to load token cache: {e}")
        
        return cache
    
    def _save_token_cache(self):
        """Save token cache to disk."""
        if self.app.token_cache.has_state_changed:
            try:
                self.token_cache_file.write_text(
                    self.app.token_cache.serialize()
                )
                logger.info("Token cache saved to disk")
            except Exception as e:
                logger.error(f"Failed to save token cache: {e}")
    
    def authenticate_interactive(self) -> bool:
        """
        Perform interactive authentication (opens browser).
        Used for initial login.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # Try to get token from cache first
            accounts = self.app.get_accounts()
            
            if accounts:
                logger.info(f"Found {len(accounts)} cached account(s)")
                # Try silent authentication
                result = self.app.acquire_token_silent(
                    scopes=self.SCOPES,
                    account=accounts[0]
                )
                
                if result and "access_token" in result:
                    self.access_token = result["access_token"]
                    logger.info("Silent authentication successful")
                    return True
            
            # No cached token, do interactive login
            logger.info("Starting interactive authentication...")
            result = self.app.acquire_token_interactive(
                scopes=self.SCOPES,
                prompt="select_account"  # Let user choose account
            )
            
            if result and "access_token" in result:
                self.access_token = result["access_token"]
                self._save_token_cache()
                logger.info("Interactive authentication successful")
                return True
            
            # Authentication failed
            error = result.get("error_description", "Unknown error") if result else "No result"
            logger.error(f"Authentication failed: {error}")
            return False
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def authenticate_silent(self) -> bool:
        """
        Attempt silent authentication using cached tokens.
        Used by background scheduler.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            accounts = self.app.get_accounts()
            
            if not accounts:
                logger.warning("No cached accounts found for silent auth")
                return False
            
            result = self.app.acquire_token_silent(
                scopes=self.SCOPES,
                account=accounts[0]
            )
            
            if result and "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("Silent authentication successful")
                return True
            
            logger.warning("Silent authentication failed")
            return False
            
        except Exception as e:
            logger.error(f"Silent authentication error: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        return self.access_token is not None
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the authenticated user.
        
        Returns:
            User info dict or None if not authenticated
        """
        if not self.is_authenticated():
            logger.warning("Cannot get user info: not authenticated")
            return None
        
        try:
            url = f"{self.GRAPH_API_ENDPOINT}/me"
            headers = {'Authorization': f'Bearer {self.access_token}'}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def logout(self):
        """Clear all cached tokens."""
        accounts = self.app.get_accounts()
        
        for account in accounts:
            self.app.remove_account(account)
        
        self.access_token = None
        
        if self.token_cache_file.exists():
            self.token_cache_file.unlink()
        
        logger.info("Logged out successfully")
    
    def upload_file(
        self, 
        local_path: Path, 
        onedrive_path: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Upload a file to OneDrive.
        
        Args:
            local_path: Path to local file
            onedrive_path: Path in OneDrive (e.g., "LabSheets/Practical_01.docx")
            conflict_behavior: What to do if file exists ("replace", "fail", "rename")
            
        Returns:
            Dict with file metadata if successful, None otherwise
        """
        if not self.is_authenticated():
            logger.error("Cannot upload: not authenticated")
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            # Read file content
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            # Construct upload URL
            # Note: OneDrive paths use forward slashes
            upload_url = (
                f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/"
                f"{onedrive_path}:/content"
            )
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/octet-stream'
            }
            
            
            logger.info(f"Uploading file to OneDrive: {onedrive_path}")
            response = requests.put(
                upload_url,
                headers=headers,
                data=file_content
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"File uploaded successfully: {onedrive_path}")
                return response.json()
            else:
                logger.error(f"Upload failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return None
    
    def download_file(
        self,
        onedrive_path: str,
        local_path: Path
    ) -> bool:
        """
        Download a file from OneDrive.
        
        Args:
            onedrive_path: Path in OneDrive
            local_path: Where to save locally
            
        Returns:
            bool: True if successful
        """
        if not self.is_authenticated():
            logger.error("Cannot download: not authenticated")
            raise Exception("Not authenticated")
        
        try:
            # Get download URL
            url = (
                f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/"
                f"{onedrive_path}:/content"
            )
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            logger.info(f"Downloading file from OneDrive: {onedrive_path}")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                local_path.write_bytes(response.content)
                logger.info(f"File downloaded successfully: {local_path}")
                return True
            else:
                logger.error(f"Download failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False
    
    def upload_json(
        self,
        onedrive_path: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Upload JSON data directly to OneDrive.
        
        Args:
            onedrive_path: Path in OneDrive
            data: Dictionary to upload as JSON
            
        Returns:
            bool: True if successful
        """
        import tempfile
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            json.dump(data, f, indent=2)
            temp_path = Path(f.name)
        
        try:
            result = self.upload_file(temp_path, onedrive_path)
            return result is not None
        finally:
            temp_path.unlink()
    
    def download_json(
        self,
        onedrive_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Download and parse JSON file from OneDrive.
        
        Args:
            onedrive_path: Path in OneDrive
            
        Returns:
            Parsed JSON data or None
        """
        import tempfile
        
        with tempfile.NamedTemporaryFile(
            suffix='.json',
            delete=False
        ) as f:
            temp_path = Path(f.name)
        
        try:
            if self.download_file(onedrive_path, temp_path):
                return json.loads(temp_path.read_text())
            return None
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            return None
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def list_files(
        self,
        folder_path: str = ""
    ) -> Optional[List[Dict[str, Any]]]:
        """
        List files in OneDrive folder.
        
        Args:
            folder_path: Folder path (empty string for root)
            
        Returns:
            List of file metadata dicts or None
        """
        if not self.is_authenticated():
            logger.error("Cannot list files: not authenticated")
            raise Exception("Not authenticated")
        
        try:
            if folder_path:
                url = (
                    f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/"
                    f"{folder_path}:/children"
                )
            else:
                url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root/children"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json().get('value', [])
            else:
                logger.error(f"List failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"List error: {e}")
            return None
    
    def create_folder(
        self,
        folder_path: str
    ) -> bool:
        """
        Create a folder in OneDrive.
        
        Args:
            folder_path: Path of folder to create
            
        Returns:
            bool: True if successful
        """
        if not self.is_authenticated():
            logger.error("Cannot create folder: not authenticated")
            raise Exception("Not authenticated")
        
        try:
            # Split path into parent and folder name
            parts = folder_path.rstrip('/').split('/')
            folder_name = parts[-1]
            parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ""
            
            if parent_path:
                url = (
                    f"{self.GRAPH_API_ENDPOINT}/me/drive/root:/"
                    f"{parent_path}:/children"
                )
            else:
                url = f"{self.GRAPH_API_ENDPOINT}/me/drive/root/children"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail"
            }
            
            logger.info(f"Creating folder: {folder_path}")
            response = requests.post(url, headers=headers, json=data)
            
            # 201 = created, 409 = already exists (OK)
            if response.status_code in [201, 409]:
                logger.info(f"Folder ready: {folder_path}")
                return True
            else:
                logger.error(f"Create folder failed: {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Create folder error: {e}")
            return False
    
    def ensure_folder_structure(self):
        """
        Ensure the required folder structure exists in OneDrive.
        Creates: LabSheets/ and LabSheets/.config/
        
        Returns:
            bool: True if successful
        """
        try:
            # Create main LabSheets folder
            self.create_folder("LabSheets")
            
            # Create .config subfolder
            self.create_folder("LabSheets/.config")
            
            logger.info("OneDrive folder structure verified")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure folder structure: {e}")
            return False
