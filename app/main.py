import sys
from PySide6.QtWidgets import QApplication
from app.config import Config
from app.core.theme_manager import ThemeManager

def main():
    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Lab Sheet Generator V2.0.0")
    app.setOrganizationName("University Tools")
    
    # Register all templates (IMPORTANT!)
    from app.templates import classic_template, sliit_template
    
    # Initialize configuration
    config = Config()
    config_data = config.load_config()
    
    # Apply theme
    theme_manager = ThemeManager()
    if config_data:
        theme_manager.set_theme(config_data.get('theme', 'light'))
    app.setStyleSheet(theme_manager.get_stylesheet())
    
    # Check if first run
    if config.is_first_run():
        from app.ui.setup_window import SetupWindow
        from app.ui.main_window import MainWindow
        
        setup_window = SetupWindow(config)
        main_window = None
        
        def on_setup_complete(config_data):
            nonlocal main_window
            main_window = MainWindow(config)
            main_window.show()
        
        setup_window.setup_complete.connect(on_setup_complete)
        setup_window.show()
    else:
        from app.ui.main_window import MainWindow
        main_window = MainWindow(config)
        main_window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())