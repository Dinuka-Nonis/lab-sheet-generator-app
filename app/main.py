import sys
from PySide6.QtWidgets import QApplication
from app.config import Config

def main():
    """Main entry point for the application."""
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Lab Sheet Generator")
    app.setOrganizationName("University Tools")
    
    # Initialize configuration
    config = Config()
    
    # Check if first run
    if config.is_first_run():
        print("First run detected - showing setup wizard")
        # TODO: Show setup UI
        # from app.ui.setup_ui import SetupWindow
        # setup_window = SetupWindow(config)
        # setup_window.show()
    else:
        print("Configuration found - showing main window")
        # TODO: Show main UI
        # from app.ui.main_ui import MainWindow
        # main_window = MainWindow(config)
        # main_window.show()
    
    # For now, just test the config system
    print(f"Config directory: {config.config_dir}")
    print(f"Config file: {config.config_file}")
    print(f"Logo file: {config.logo_file}")
    
    # Test saving and loading config
    test_modules = [
        {"name": "Programming Paradigms", "code": "SE2052"},
        {"name": "Data Structures", "code": "CS2001"},
    ]
    
    config.save_config(
        student_name="NONIS P.K.D.T.",
        student_id="IT23614130",
        modules=test_modules
    )
    
    loaded_config = config.load_config()
    print(f"\nLoaded config: {loaded_config}")
    
    return 0
    # return app.exec()  # Uncomment when UI is ready

if __name__ == "__main__":
    sys.exit(main())