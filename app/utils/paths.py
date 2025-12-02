from pathlib import Path
import os

def get_output_dir():
    """
    Get the default output directory for generated lab sheets.
    Creates the directory if it doesn't exist.
    
    Returns:
        Path: Path to the output directory
    """
    # Default to Documents/LabSheets
    if os.name == 'nt':  # Windows
        docs = Path(os.getenv('USERPROFILE', '')) / 'Documents'
    else:  # macOS/Linux
        docs = Path.home() / 'Documents'
    
    output_dir = docs / 'LabSheets'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir

def get_app_data_dir():
    """
    Get the application data directory.
    
    Returns:
        Path: Path to the app data directory
    """
    if os.name == 'nt':  # Windows
        return Path(os.getenv('APPDATA', ''))
    else:  # macOS/Linux
        return Path.home() / '.config'