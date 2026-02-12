"""
Schedule Manager for Lab Sheet Generator V3.0
Handles CRUD operations and calculations for schedules
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta, time
import json
import logging

from app.scheduler.models import Schedule

logger = logging.getLogger(__name__)


class ScheduleManager:
    """
    Manages lab sheet generation schedules.
    Handles creation, updates, deletion, and next generation time calculations.
    """
    
    def __init__(self, config, onedrive_client=None):
        """
        Initialize schedule manager.
        
        Args:
            config: Config instance
            onedrive_client: Optional OneDriveClient for cloud sync
        """
        self.config = config
        self.onedrive = onedrive_client
        self.schedules_file = config.config_dir / "schedules.json"
        self.schedules: List[Schedule] = []
        
        # Load existing schedules
        self.load_schedules()
        
        logger.info(f"Schedule manager initialized with {len(self.schedules)} schedule(s)")
    
    def load_schedules(self) -> bool:
        """
        Load schedules from local file.
        
        Returns:
            bool: True if loaded successfully
        """
        try:
            if not self.schedules_file.exists():
                logger.info("No schedules file found - starting fresh")
                self.schedules = []
                return True
            
            with open(self.schedules_file, 'r') as f:
                data = json.load(f)
            
            self.schedules = [Schedule.from_dict(s) for s in data.get('schedules', [])]
            logger.info(f"Loaded {len(self.schedules)} schedule(s) from file")
            return True
            
        except Exception as e:
            logger.error(f"Error loading schedules: {e}")
            self.schedules = []
            return False
    
    def save_schedules(self) -> bool:
        """
        Save schedules to local file.
        
        Returns:
            bool: True if saved successfully
        """
        try:
            data = {
                'version': '3.0.0',
                'last_updated': datetime.now().isoformat(),
                'schedules': [s.to_dict() for s in self.schedules]
            }
            
            with open(self.schedules_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.schedules)} schedule(s) to file")
            return True
            
        except Exception as e:
            logger.error(f"Error saving schedules: {e}")
            return False
    
    def sync_to_cloud(self) -> bool:
        """
        Sync schedules to OneDrive.
        
        Returns:
            bool: True if synced successfully
        """
        if not self.onedrive or not self.onedrive.is_authenticated():
            logger.warning("Cannot sync schedules: OneDrive not available")
            return False
        
        try:
            # Ensure schedules are saved locally first
            self.save_schedules()
            
            # Upload to OneDrive
            logger.info("Syncing schedules to OneDrive...")
            success = self.onedrive.upload_file(
                self.schedules_file,
                "LabSheets/.config/schedules.json"
            )
            
            if success:
                logger.info("Schedules synced to OneDrive successfully")
                return True
            else:
                logger.error("Failed to sync schedules to OneDrive")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing schedules to cloud: {e}")
            return False
    
    def create_schedule(
        self,
        module_code: str,
        module_name: str,
        day_of_week: int,
        lab_time: time,
        **kwargs
    ) -> Schedule:
        """
        Create a new schedule.
        
        Args:
            module_code: Module code
            module_name: Module name
            day_of_week: Day of week (0-6)
            lab_time: Lab time
            **kwargs: Additional schedule parameters
            
        Returns:
            Schedule: Created schedule
        """
        schedule = Schedule(
            id=Schedule.generate_id(),
            module_code=module_code,
            module_name=module_name,
            day_of_week=day_of_week,
            lab_time=lab_time,
            **kwargs
        )
        
        self.schedules.append(schedule)
        self.save_schedules()
        
        logger.info(f"Created schedule: {module_code} - {schedule.get_day_name()} {schedule.get_formatted_time()}")
        
        # Sync to cloud if available
        if self.onedrive:
            self.sync_to_cloud()
        
        return schedule
    
    def get_all_schedules(self) -> List[Schedule]:
        """Get all schedules."""
        return self.schedules
    
    def get_schedule_by_id(self, schedule_id: str) -> Optional[Schedule]:
        """Get schedule by ID."""
        for schedule in self.schedules:
            if schedule.id == schedule_id:
                return schedule
        return None
    
    def get_active_schedules(self) -> List[Schedule]:
        """Get only active schedules."""
        return [s for s in self.schedules if s.is_active()]
    
    def update_schedule(self, schedule: Schedule) -> bool:
        """
        Update an existing schedule.
        
        Args:
            schedule: Updated schedule
            
        Returns:
            bool: True if updated successfully
        """
        for i, s in enumerate(self.schedules):
            if s.id == schedule.id:
                schedule.last_updated_at = datetime.now().isoformat()
                self.schedules[i] = schedule
                self.save_schedules()
                
                logger.info(f"Updated schedule: {schedule.module_code}")
                
                # Sync to cloud
                if self.onedrive:
                    self.sync_to_cloud()
                
                return True
        
        logger.warning(f"Schedule not found for update: {schedule.id}")
        return False
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """
        Delete a schedule.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            bool: True if deleted successfully
        """
        for i, schedule in enumerate(self.schedules):
            if schedule.id == schedule_id:
                deleted = self.schedules.pop(i)
                self.save_schedules()
                
                logger.info(f"Deleted schedule: {deleted.module_code}")
                
                # Sync to cloud
                if self.onedrive:
                    self.sync_to_cloud()
                
                return True
        
        logger.warning(f"Schedule not found for deletion: {schedule_id}")
        return False
    
    def pause_schedule(self, schedule_id: str) -> bool:
        """Pause a schedule."""
        schedule = self.get_schedule_by_id(schedule_id)
        if schedule:
            schedule.pause()
            self.save_schedules()
            
            if self.onedrive:
                self.sync_to_cloud()
            
            logger.info(f"Paused schedule: {schedule.module_code}")
            return True
        return False
    
    def resume_schedule(self, schedule_id: str) -> bool:
        """Resume a schedule."""
        schedule = self.get_schedule_by_id(schedule_id)
        if schedule:
            schedule.resume()
            self.save_schedules()
            
            if self.onedrive:
                self.sync_to_cloud()
            
            logger.info(f"Resumed schedule: {schedule.module_code}")
            return True
        return False
    
    def calculate_next_generation_time(self, schedule: Schedule) -> datetime:
        """
        Calculate when the next lab sheet should be generated.
        
        Args:
            schedule: Schedule to calculate for
            
        Returns:
            datetime: Next generation time
        """
        now = datetime.now()
        current_day = now.weekday()  # 0 = Monday
        target_day = schedule.day_of_week
        
        # Calculate days until next lab
        days_until_lab = (target_day - current_day) % 7
        
        # If it's the same day, check if lab time has passed
        if days_until_lab == 0:
            lab_datetime = now.replace(
                hour=schedule.lab_time.hour,
                minute=schedule.lab_time.minute,
                second=0,
                microsecond=0
            )
            
            # If lab time already passed today, schedule for next week
            if now >= lab_datetime:
                days_until_lab = 7
        
        # Calculate next lab date and time
        next_lab = now + timedelta(days=days_until_lab)
        next_lab = next_lab.replace(
            hour=schedule.lab_time.hour,
            minute=schedule.lab_time.minute,
            second=0,
            microsecond=0
        )
        
        # Subtract "generate before" time
        next_generation = next_lab - timedelta(minutes=schedule.generate_before_minutes)
        
        return next_generation
    
    def get_next_generation_time_str(self, schedule: Schedule) -> str:
        """
        Get next generation time as formatted string.
        
        Args:
            schedule: Schedule
            
        Returns:
            str: Formatted time string
        """
        next_time = self.calculate_next_generation_time(schedule)
        
        # Calculate time until generation
        time_until = next_time - datetime.now()
        
        if time_until.total_seconds() < 0:
            return "Overdue!"
        elif time_until.days > 7:
            return next_time.strftime('%B %d at %I:%M %p')
        elif time_until.days > 0:
            return f"In {time_until.days} days ({next_time.strftime('%a %I:%M %p')})"
        elif time_until.seconds > 3600:
            hours = int(time_until.seconds / 3600)
            return f"In {hours} hour{'s' if hours > 1 else ''}"
        else:
            minutes = int(time_until.seconds / 60)
            return f"In {minutes} minute{'s' if minutes > 1 else ''}"
    
    def increment_practical_number(self, schedule_id: str) -> bool:
        """
        Increment practical number for a schedule.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            bool: True if incremented successfully
        """
        schedule = self.get_schedule_by_id(schedule_id)
        if schedule:
            schedule.increment_practical_number()
            self.save_schedules()
            
            if self.onedrive:
                self.sync_to_cloud()
            
            logger.info(f"Incremented practical number for {schedule.module_code} to {schedule.current_practical_number}")
            return True
        return False
    
    def add_skip_date(self, schedule_id: str, date_str: str) -> bool:
        """
        Add a skip date to a schedule.
        
        Args:
            schedule_id: Schedule ID
            date_str: Date to skip (ISO format)
            
        Returns:
            bool: True if added successfully
        """
        schedule = self.get_schedule_by_id(schedule_id)
        if schedule:
            if date_str not in schedule.skip_dates:
                schedule.skip_dates.append(date_str)
                schedule.last_updated_at = datetime.now().isoformat()
                self.save_schedules()
                
                if self.onedrive:
                    self.sync_to_cloud()
                
                logger.info(f"Added skip date {date_str} to {schedule.module_code}")
                return True
        return False