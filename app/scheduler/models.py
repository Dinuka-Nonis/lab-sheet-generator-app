"""
Schedule data models for Lab Sheet Generator V3.0
Defines structure for automated lab sheet generation schedules
"""

from dataclasses import dataclass, asdict
from datetime import datetime, time
from typing import List, Optional
import uuid


@dataclass
class Schedule:
    """
    Represents a lab sheet generation schedule.
    
    Attributes:
        id: Unique identifier (UUID)
        module_code: Module code (e.g., "CS2023")
        module_name: Module name (e.g., "Operating Systems")
        day_of_week: Day of week (0=Monday, 6=Sunday)
        lab_time: Time of lab session (e.g., time(10, 0) for 10:00 AM)
        generate_before_minutes: How many minutes before lab to generate (default 60)
        current_practical_number: Current practical number (auto-increments)
        auto_increment: Whether to auto-increment practical number
        use_zero_padding: Whether to use zero padding (e.g., "01" vs "1")
        template_id: Template to use (e.g., "classic", "sliit")
        sheet_type: Type of sheet (e.g., "Practical", "Lab")
        status: Schedule status ("active", "paused", "disabled")
        skip_dates: List of dates to skip (ISO format strings)
        repeat_mode: Whether to repeat last practical instead of incrementing
        upload_to_onedrive: Whether to upload generated sheets to OneDrive
        send_confirmation: Whether to send email confirmation
        created_at: Creation timestamp
        last_generated_at: Last generation timestamp
        last_updated_at: Last update timestamp
    """
    
    id: str
    module_code: str
    module_name: str
    day_of_week: int  # 0-6 (Monday-Sunday)
    lab_time: time
    generate_before_minutes: int = 60
    current_practical_number: int = 1
    auto_increment: bool = True
    use_zero_padding: bool = True
    template_id: str = "classic"
    sheet_type: str = "Practical"
    status: str = "active"  # active, paused, disabled
    skip_dates: List[str] = None
    repeat_mode: bool = False
    upload_to_onedrive: bool = True
    send_confirmation: bool = True
    created_at: str = None
    last_generated_at: str = None
    last_updated_at: str = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.skip_dates is None:
            self.skip_dates = []
        
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        
        if self.last_updated_at is None:
            self.last_updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert time object to string
        data['lab_time'] = self.lab_time.strftime('%H:%M')
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Schedule':
        """Create Schedule from dictionary."""
        # Convert time string to time object
        if isinstance(data.get('lab_time'), str):
            time_parts = data['lab_time'].split(':')
            data['lab_time'] = time(int(time_parts[0]), int(time_parts[1]))
        
        # Handle missing fields for backwards compatibility
        data.setdefault('skip_dates', [])
        data.setdefault('repeat_mode', False)
        data.setdefault('upload_to_onedrive', True)
        data.setdefault('send_confirmation', True)
        
        return cls(**data)
    
    @staticmethod
    def generate_id() -> str:
        """Generate unique schedule ID."""
        return str(uuid.uuid4())
    
    def get_day_name(self) -> str:
        """Get human-readable day name."""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[self.day_of_week]
    
    def get_formatted_time(self) -> str:
        """Get formatted time string."""
        return self.lab_time.strftime('%I:%M %p')
    
    def get_practical_number_str(self) -> str:
        """Get practical number as string with optional zero padding."""
        if self.use_zero_padding:
            return f"{self.current_practical_number:02d}"
        return str(self.current_practical_number)
    
    def increment_practical_number(self):
        """Increment practical number if auto_increment is enabled."""
        if self.auto_increment and not self.repeat_mode:
            self.current_practical_number += 1
            self.last_updated_at = datetime.now().isoformat()
    
    def update_last_generated(self):
        """Update last generation timestamp."""
        self.last_generated_at = datetime.now().isoformat()
        self.last_updated_at = datetime.now().isoformat()
    
    def is_active(self) -> bool:
        """Check if schedule is active."""
        return self.status == "active"
    
    def pause(self):
        """Pause the schedule."""
        self.status = "paused"
        self.last_updated_at = datetime.now().isoformat()
    
    def resume(self):
        """Resume the schedule."""
        self.status = "active"
        self.last_updated_at = datetime.now().isoformat()
    
    def disable(self):
        """Disable the schedule."""
        self.status = "disabled"
        self.last_updated_at = datetime.now().isoformat()