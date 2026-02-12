import sys
from PySide6.QtWidgets import QApplication
from app.config import Config
from app.core.theme_manager import ThemeManager


def main():
    """Main entry point for the application."""
    
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Lab Sheet Generator V3.0")
    app.setOrganizationName("University Tools")
    
    # Register all templates (IMPORTANT: This must happen before any template usage)
    from app.templates import classic_template, sliit_template
    
    # Apply theme (V2.0 uses light theme only)
    theme_manager = ThemeManager()
    app.setStyleSheet(theme_manager.get_stylesheet())
    
    # Initialize configuration
    config = Config()
    
    # Check if first run
    if config.is_first_run():
        from app.ui.setup_window import SetupWindow
        from app.ui.main_window import MainWindow
        
        setup_window = SetupWindow(config)
        main_window = None  # Will be created after setup
        
        def on_setup_complete(config_data):
            """Called when setup is complete - open main window."""
            nonlocal main_window
            main_window = MainWindow(config)
            main_window.show()
            setup_window.close()
        
        setup_window.setup_complete.connect(on_setup_complete)
        setup_window.show()
    else:
        from app.ui.main_window import MainWindow
        main_window = MainWindow(config)
        main_window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())