"""
Cloud API Client for Lab Sheet Generator Desktop App
Handles all communication with the cloud service
"""

import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class CloudAPIClient:
    """Client for communicating with cloud service."""
    
    def __init__(self, base_url: str, config_dir: Path):
        """
        Initialize API client.
        
        Args:
            base_url: Cloud service URL (e.g., "https://your-app.onrender.com")
            config_dir: Directory for storing API key
        """
        self.base_url = base_url.rstrip('/') if base_url else 'http://localhost:5000'
        self.config_dir = config_dir
        self.api_key_file = config_dir / ".cloud_api_key"
        self.api_key = self._load_api_key()
        self.user_info = None

        # If we already have a saved API key, silently fetch the profile
        # so the menu shows the real name instead of "User"
        if self.api_key:
            try:
                resp = self._request('GET', '/api/user/profile')
                # Profile returns {'success': True, 'user': {...}}
                # Store just the user dict for easy access
                self.user_info = resp.get('user', resp)
            except Exception:
                pass  # Offline or error — stay silent, still considered logged in
    
    def _load_api_key(self) -> Optional[str]:
        """Load API key from disk."""
        try:
            if self.api_key_file.exists():
                return self.api_key_file.read_text().strip()
        except Exception as e:
            logger.error(f"Error loading API key: {e}")
        return None
    
    def _save_api_key(self, api_key: str):
        """Save API key to disk."""
        try:
            self.api_key_file.write_text(api_key)
            logger.info("API key saved")
        except Exception as e:
            logger.error(f"Error saving API key: {e}")
    
    def _normalize_url(self, url: str) -> str:
        """Auto-upgrade http to https for PythonAnywhere."""
        if url.startswith('http://') and 'pythonanywhere.com' in url:
            url = 'https://' + url[7:]
            logger.info(f"Auto-upgraded to HTTPS: {url}")
        return url

    def _request(self, method: str, endpoint: str, data: Dict = None, timeout: int = 30) -> Dict:
        """Make API request with automatic http→https handling."""
        url = self._normalize_url(f"{self.base_url}{endpoint}")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'LabSheetGenerator/3.0'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        logger.info(f"{method} {url}")
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=timeout,
                allow_redirects=True
            )
        except requests.exceptions.SSLError:
            # If HTTPS fails, try HTTP
            http_url = url.replace('https://', 'http://')
            logger.warning(f"HTTPS failed, trying HTTP: {http_url}")
            response = requests.request(
                method=method,
                url=http_url,
                headers=headers,
                json=data,
                timeout=timeout,
                allow_redirects=True
            )
        
        if response.status_code == 403:
            raise Exception(
                f"403 Forbidden — PythonAnywhere blocked the request.\n"
                f"Make sure your cloud service is reloaded on PythonAnywhere."
            )
        
        response.raise_for_status()
        return response.json()


    # ========================================
    # Authentication
    # ========================================
    
    def register(self, name: str, student_id: str, email: str, password: str) -> Dict:
        """
        Register new user.
        
        Args:
            name: Student name
            student_id: Student ID
            email: Email address (university email for receiving notifications)
            password: Password
            
        Returns:
            Response dict with user info and API key
        """
        return self._request('POST', '/api/register', {
            'name': name,
            'student_id': student_id,
            'email': email,
            'password': password
        })
    
    def login(self, student_id: str, password: str) -> bool:
        """
        Login and store API key.
        
        Args:
            student_id: Student ID
            password: Password
        
        Returns:
            bool: True if successful
        """
        try:
            result = self._request('POST', '/api/login', {
                'student_id': student_id,
                'password': password
            })
            
            if result.get('success') and 'api_key' in result:
                self.api_key = result['api_key']
                self.user_info = result.get('user')
                self._save_api_key(self.api_key)
                logger.info(f"Logged in as {student_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise
    
    def logout(self):
        """Logout (clear API key)."""
        self.api_key = None
        self.user_info = None
        if self.api_key_file.exists():
            self.api_key_file.unlink()
        logger.info("Logged out")
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.api_key is not None
    
    def get_profile(self) -> Dict:
        """Get current user profile."""
        return self._request('GET', '/api/user/profile')
    
    # ========================================
    # Modules
    # ========================================
    
    def get_modules(self) -> List[Dict]:
        """Get user's modules."""
        result = self._request('GET', '/api/modules')
        return result.get('modules', [])
    
    def create_module(self, code: str, name: str, template: str = 'classic', 
                     sheet_type: str = 'Practical', **kwargs) -> Dict:
        """
        Create new module.
        
        Args:
            code: Module code (e.g., "IT2030")
            name: Module name
            template: Template name ('classic' or 'sliit')
            sheet_type: Sheet type ('Practical', 'Tutorial', etc.)
            **kwargs: Additional module settings
            
        Returns:
            Created module dict
        """
        data = {
            'code': code,
            'name': name,
            'template': template,
            'sheet_type': sheet_type,
            **kwargs
        }
        result = self._request('POST', '/api/modules', data)
        return result.get('module', {})
    
    def update_module(self, module_id: int, **kwargs) -> Dict:
        """Update module."""
        result = self._request('PUT', f'/api/modules/{module_id}', kwargs)
        return result.get('module', {})
    
    def delete_module(self, module_id: int) -> bool:
        """Delete module."""
        result = self._request('DELETE', f'/api/modules/{module_id}')
        return result.get('success', False)
    
    # ========================================
    # Schedules
    # ========================================
    
    def get_schedules(self) -> List[Dict]:
        """Get user's schedules."""
        result = self._request('GET', '/api/schedules')
        return result.get('schedules', [])
    
    def create_schedule(self, module_id: int, day_of_week: int, 
                       lab_time: str, start_practical: int = 1,
                       end_practical: Optional[int] = None,
                       skip_dates: Optional[List[str]] = None) -> Dict:
        """
        Create new schedule.
        
        Args:
            module_id: ID of module to schedule
            day_of_week: Day of week (0=Monday, 6=Sunday)
            lab_time: Time of lab (e.g., "14:00")
            start_practical: Starting practical number
            end_practical: Ending practical number (optional)
            skip_dates: List of dates to skip in ISO format (optional)
            
        Returns:
            Created schedule dict
        """
        data = {
            'module_id': module_id,
            'day_of_week': day_of_week,
            'lab_time': lab_time,
            'start_practical': start_practical
        }
        
        if end_practical is not None:
            data['end_practical'] = end_practical
        
        if skip_dates:
            data['skip_dates'] = skip_dates
        
        result = self._request('POST', '/api/schedules', data)
        return result.get('schedule', {})
    
    def update_schedule(self, schedule_id: int, **kwargs) -> Dict:
        """Update schedule."""
        result = self._request('PUT', f'/api/schedules/{schedule_id}', kwargs)
        return result.get('schedule', {})
    
    def delete_schedule(self, schedule_id: int) -> bool:
        """Delete schedule."""
        result = self._request('DELETE', f'/api/schedules/{schedule_id}')
        return result.get('success', False)
    
    def pause_schedule(self, schedule_id: int) -> bool:
        """Pause a schedule."""
        result = self.update_schedule(schedule_id, status='paused')
        return result is not None
    
    def resume_schedule(self, schedule_id: int) -> bool:
        """Resume a paused schedule."""
        result = self.update_schedule(schedule_id, status='active')
        return result is not None
    
    # ========================================
    # History
    # ========================================
    
    def get_generation_history(self) -> List[Dict]:
        """Get generation history."""
        result = self._request('GET', '/api/history')
        return result.get('history', [])
    
    # ========================================
    # Sync
    # ========================================
    
    def sync_modules_from_local(self, local_modules: List[Dict]) -> Dict:
        """
        Sync local modules to cloud.
        
        Args:
            local_modules: List of local module configs
            
        Returns:
            Sync result
        """
        synced = []
        errors = []
        
        for module in local_modules:
            try:
                # Check if module exists on cloud
                cloud_modules = self.get_modules()
                existing = next(
                    (m for m in cloud_modules if m['code'] == module['module_code']),
                    None
                )
                
                if existing:
                    # Update existing
                    self.update_module(
                        existing['id'],
                        name=module['module_name'],
                        template=module.get('template', 'classic'),
                        sheet_type=module.get('sheet_type', 'Practical')
                    )
                else:
                    # Create new
                    self.create_module(
                        code=module['module_code'],
                        name=module['module_name'],
                        template=module.get('template', 'classic'),
                        sheet_type=module.get('sheet_type', 'Practical')
                    )
                
                synced.append(module['module_code'])
                
            except Exception as e:
                logger.error(f"Error syncing module {module.get('module_code')}: {e}")
                errors.append(str(e))
        
        return {
            'synced': synced,
            'errors': errors,
            'success': len(errors) == 0
        }
    
    def test_connection(self) -> bool:
        """Test connection to cloud service."""
        try:
            url = self._normalize_url(f"{self.base_url}/")
            response = requests.get(
                url,
                timeout=25,
                allow_redirects=True,
                headers={'User-Agent': 'LabSheetGenerator/3.0'}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False