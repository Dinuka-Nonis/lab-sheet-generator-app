"""
Configuration Manager for Lab Sheet Generator V2.0.0
Enhanced with theme and template preferences
"""

import json
import os
from pathlib import Path


class Config:
    """Handles loading and saving user configuration."""
    
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.logo_file = self.config_dir / "SLIIT.png"
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
    
    def _get_default_output_dir(self):
        """Get the default output directory."""
        from app.utils.paths import get_output_dir
        return str(get_output_dir())
    
    def save_config(self, student_name, student_id, modules, global_output_path=None,
                    theme='light', default_template='classic'):
        """
        Save user configuration to file.
        
        Args:
            student_name: Student's full name
            student_id: Student ID number
            modules: List of dicts with enhanced fields (name, code, sheet_type, template, etc.)
            global_output_path: Default output path (optional)
            theme: UI theme preference ('light' or 'dark')
            default_template: Default template ID to use
        """
        config_data = {
            'version': '2.0.0',  # Config version for future migrations
            'student_name': student_name,
            'student_id': student_id,
            'modules': modules,
            'global_output_path': global_output_path or self._get_default_output_dir(),
            'theme': theme,
            'default_template': default_template
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=4)
    
    def load_config(self):
        """
        Load user configuration from file with migration for old formats.
        
        Returns:
            dict: Configuration data or None if not found
        """
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # MIGRATION: Add default values for missing fields
            if 'version' not in config:
                config['version'] = '1.0.0'  # Assume old version
            
            if 'global_output_path' not in config:
                config['global_output_path'] = self._get_default_output_dir()
            
            if 'theme' not in config:
                config['theme'] = 'light'
            
            if 'default_template' not in config:
                config['default_template'] = 'classic'
            
            # Migrate modules to new format
            for module in config.get('modules', []):
                # Add sheet_type if missing
                if 'sheet_type' not in module:
                    module['sheet_type'] = 'Practical'
                
                # Add custom_sheet_type if missing
                if 'custom_sheet_type' not in module:
                    module['custom_sheet_type'] = None
                
                # Add output_path if missing
                if 'output_path' not in module:
                    module['output_path'] = None
                
                # Add use_zero_padding if missing
                if 'use_zero_padding' not in module:
                    module['use_zero_padding'] = True
                
                # NEW: Add template preference if missing
                if 'template' not in module:
                    module['template'] = config.get('default_template', 'classic')
            
            return config
            
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
    
    def update_theme(self, theme):
        """
        Update theme preference.
        
        Args:
            theme: Theme name ('light' or 'dark')
        """
        config = self.load_config()
        if config:
            config['theme'] = theme
            self.save_config(
                config['student_name'],
                config['student_id'],
                config['modules'],
                config['global_output_path'],
                theme,
                config.get('default_template', 'classic')
            )
    
    def update_default_template(self, template_id):
        """
        Update default template preference.
        
        Args:
            template_id: Template ID
        """
        config = self.load_config()
        if config:
            config['default_template'] = template_id
            self.save_config(
                config['student_name'],
                config['student_id'],
                config['modules'],
                config['global_output_path'],
                config.get('theme', 'light'),
                template_id
            )
    
    def reset_config(self):
        """Delete all configuration data."""
        if self.config_file.exists():
            self.config_file.unlink()
        if self.logo_file.exists():
            self.logo_file.unlink()