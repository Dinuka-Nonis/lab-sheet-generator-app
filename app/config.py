import json
import os
from pathlib import Path

class Config:
    """Handles loading and saving user configuration."""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.logo_file = self.config_dir / "logo.png"
        self._ensure_config_dir()
        
    def _get_config_dir(self):
        """Get the configuration directory path based on OS."""
        if os.name == 'nt':  # Windows
            base = Path(os.getenv('APPDATA', ''))
        else:  # macOS/Linux
            base = Path.home() / '.config'
        
        return base / 'LabSheetGenerator'
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def is_first_run(self):
        """Check if this is the first time running the app."""
        return not self.config_file.exists()
    
    def save_config(self, student_name, student_id, modules):
        """
        Save user configuration to file.
        
        Args:
            student_name: Student's full name
            student_id: Student ID number
            modules: List of dicts with 'name' and 'code' keys
        """
        config_data = {
            'student_name': student_name,
            'student_id': student_id,
            'modules': modules
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
    
    def load_config(self):
        """
        Load user configuration from file.
        
        Returns:
            dict: Configuration data or None if not found
        """
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def save_logo(self, logo_path):
        """
        Copy the logo file to the config directory.
        
        Args:
            logo_path: Path to the source logo file
        """
        import shutil
        shutil.copy2(logo_path, self.logo_file)
    
    def get_logo_path(self):
        """
        Get the path to the saved logo.
        
        Returns:
            Path object or None if logo doesn't exist
        """
        if self.logo_file.exists():
            return self.logo_file
        return None
    
    def reset_config(self):
        """Delete all configuration data."""
        if self.config_file.exists():
            self.config_file.unlink()
        if self.logo_file.exists():
            self.logo_file.unlink()