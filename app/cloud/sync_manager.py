"""
Sync Manager for Lab Sheet Generator V3.0
Handles synchronization of configuration between local storage and OneDrive
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SyncManager:
    """
    Manages synchronization of configuration between local and OneDrive.
    Implements a simple "cloud wins" merge strategy.
    """
    
    def __init__(self, config, onedrive_client):
        """
        Initialize sync manager.
        
        Args:
            config: Config instance (local configuration manager)
            onedrive_client: OneDriveClient instance
        """
        self.config = config
        self.onedrive = onedrive_client
        self.sync_status_file = config.config_dir / ".sync_status.json"
        
        logger.info("Sync manager initialized")
    
    def sync_to_cloud(self) -> bool:
        """
        Upload local configuration to OneDrive.
        
        Returns:
            bool: True if successful
        """
        try:
            if not self.onedrive.is_authenticated():
                logger.error("Cannot sync to cloud: not authenticated")
                return False
            
            # Load local config
            local_config = self.config.load_config()
            if not local_config:
                logger.warning("No local config to sync")
                return False
            
            # Ensure folder structure exists
            self.onedrive.ensure_folder_structure()
            
            # Upload config to OneDrive
            logger.info("Syncing configuration to OneDrive...")
            success = self.onedrive.upload_json(
                "LabSheets/.config/user_config.json",
                local_config
            )
            
            if success:
                # Update sync status
                self._update_sync_status("to_cloud")
                logger.info("Configuration synced to OneDrive successfully")
                return True
            else:
                logger.error("Failed to sync configuration to OneDrive")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing to cloud: {e}")
            return False
    
    def sync_from_cloud(self) -> bool:
        """
        Download configuration from OneDrive and merge with local.
        Cloud config wins in case of conflicts.
        
        Returns:
            bool: True if successful
        """
        try:
            if not self.onedrive.is_authenticated():
                logger.error("Cannot sync from cloud: not authenticated")
                return False
            
            # Download cloud config
            logger.info("Downloading configuration from OneDrive...")
            cloud_config = self.onedrive.download_json(
                "LabSheets/.config/user_config.json"
            )
            
            if cloud_config is None:
                logger.warning("No cloud config found - first sync?")
                # If no cloud config, upload local config
                return self.sync_to_cloud()
            
            # Load local config
            local_config = self.config.load_config()
            
            # Merge configs (cloud wins)
            merged_config = self._merge_configs(local_config, cloud_config)
            
            # Save merged config locally
            logger.info("Saving merged configuration locally...")
            self.config.save_config(
                student_name=merged_config['student_name'],
                student_id=merged_config['student_id'],
                modules=merged_config['modules'],
                global_output_path=merged_config.get('global_output_path'),
                theme=merged_config.get('theme', 'light'),
                default_template=merged_config.get('default_template', 'classic')
            )
            
            # Update sync status
            self._update_sync_status("from_cloud")
            logger.info("Configuration synced from OneDrive successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing from cloud: {e}")
            return False
    
    def _merge_configs(
        self,
        local: Optional[Dict[str, Any]],
        cloud: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge local and cloud configs.
        Cloud config wins in case of conflicts.
        
        Args:
            local: Local configuration dict (or None)
            cloud: Cloud configuration dict
            
        Returns:
            Merged configuration dict
        """
        if not local:
            logger.info("No local config - using cloud config as-is")
            return cloud
        
        # Cloud wins - but we can preserve local-only settings if needed
        merged = cloud.copy()
        
        # Preserve local theme preference if not in cloud
        if 'theme' not in merged and 'theme' in local:
            merged['theme'] = local['theme']
        
        # Preserve local global_output_path if not in cloud
        if 'global_output_path' not in merged and 'global_output_path' in local:
            merged['global_output_path'] = local['global_output_path']
        
        logger.info("Configs merged (cloud wins strategy)")
        return merged
    
    def _update_sync_status(self, sync_type: str):
        """
        Update sync status file with timestamp.
        
        Args:
            sync_type: Type of sync ("to_cloud" or "from_cloud")
        """
        try:
            status = {
                'last_sync_type': sync_type,
                'last_sync_time': datetime.now().isoformat()
            }
            
            self.sync_status_file.write_text(json.dumps(status, indent=2))
            
        except Exception as e:
            logger.warning(f"Failed to update sync status: {e}")
    
    def get_last_sync_info(self) -> Optional[Dict[str, str]]:
        """
        Get information about the last sync.
        
        Returns:
            Dict with sync info or None
        """
        try:
            if not self.sync_status_file.exists():
                return None
            
            return json.loads(self.sync_status_file.read_text())
            
        except Exception as e:
            logger.warning(f"Failed to read sync status: {e}")
            return None
    
    def sync_logo(self, logo_path: Path) -> bool:
        """
        Upload logo to OneDrive.
        
        Args:
            logo_path: Path to local logo file
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.onedrive.is_authenticated():
                logger.error("Cannot sync logo: not authenticated")
                return False
            
            if not logo_path.exists():
                logger.error(f"Logo file not found: {logo_path}")
                return False
            
            # Upload logo
            logger.info("Syncing logo to OneDrive...")
            result = self.onedrive.upload_file(
                logo_path,
                f"LabSheets/.config/{logo_path.name}"
            )
            
            if result:
                logger.info("Logo synced to OneDrive successfully")
                return True
            else:
                logger.error("Failed to sync logo to OneDrive")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing logo: {e}")
            return False
    
    def download_logo(self, logo_name: str = "SLIIT.png") -> bool:
        """
        Download logo from OneDrive to local config directory.
        
        Args:
            logo_name: Name of logo file
            
        Returns:
            bool: True if successful
        """
        try:
            if not self.onedrive.is_authenticated():
                logger.error("Cannot download logo: not authenticated")
                return False
            
            local_logo_path = self.config.config_dir / logo_name
            
            # Download logo
            logger.info("Downloading logo from OneDrive...")
            success = self.onedrive.download_file(
                f"LabSheets/.config/{logo_name}",
                local_logo_path
            )
            
            if success:
                logger.info("Logo downloaded from OneDrive successfully")
                return True
            else:
                logger.error("Failed to download logo from OneDrive")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading logo: {e}")
            return False
