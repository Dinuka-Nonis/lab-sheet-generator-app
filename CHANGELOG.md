# Changelog

All notable changes to Lab Sheet Generator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-27

### Added
- **Per-module output paths**: Each module can now have its own dedicated output folder
- **Configurable sheet types**: Choose from Practical, Lab, Worksheet, Tutorial, Assignment, Exercise, or Custom
- **Custom sheet type**: Enter your own terminology (e.g., "Problem Set", "Case Study")
- **Real-time filename preview**: See the exact filename before generating
- **Edit module functionality**: Modify existing modules without recreating them
- **Browse button**: Quick path selection during sheet generation
- **Visual indicators**: 📁 icon shows which modules have custom output paths
- **Module-specific settings display**: UI updates based on selected module
- **Enhanced module dialog**: Configure all settings in one place
- **Backward compatibility**: Automatic migration of old configuration files

### Changed
- **Relaxed module code validation**: Now accepts formats like SE2052, CSC1234, CS-2052, COMP101
- **Enhanced configuration structure**: Added new fields for module customization
- **Improved UI layout**: Better visibility of output paths and settings
- **Updated About dialog**: Added version history and new features section
- **Better error messages**: More helpful validation messages

### Fixed
- Module code validation rejecting valid university codes
- All lab sheets mixed in single output folder
- Inability to customize sheet terminology per module
- Output path not prominently displayed
- No way to organize files by module

### Technical
- Updated `config.py` with migration logic
- Enhanced `setup_ui.py` with new module dialog
- Improved `main_ui.py` with dynamic UI updates
- Relaxed validation in `validators.py`
- Added comprehensive hidden imports for PyInstaller

## [1.0.0] - 2025-12-03

### Added
- Initial release
- Student information management (name and ID)
- Module configuration (name and code)
- Automated lab sheet generation in .docx format
- University logo support
- Professional document formatting with blue header bar
- First-time setup wizard
- Configuration persistence (stored in AppData/config)
- Cross-platform support (Windows, macOS, Linux)
- Single global output directory
- Basic menu system (File, Settings, Help)
- Edit and reset configuration options
- PyInstaller build support

### Features
- Fixed "Practical" terminology
- Numbered lab sheets (01-99)
- Student name and ID on each sheet
- Module name and code display
- Horizontal separator line
- Times New Roman font
- Professional document layout

### Technical
- Built with PySide6 (Qt for Python)
- Uses python-docx for document generation
- Pillow for image processing
- JSON-based configuration
- Threaded document generation (non-blocking UI)

---

## Upgrade Notes

### From v1.0.0 to v1.1.0
- ✅ **Automatic migration** - Your existing config will be upgraded automatically
- ✅ **No data loss** - All your modules and settings are preserved
- ✅ **No action required** - Just run the new version!
- 📝 **Optional** - Edit your modules to set custom paths and sheet types


## Links

- [GitHub Repository](https://github.com/Dinuka-Nonis/lab-sheet-generator)
- [Issue Tracker](https://github.com/Dinuka-Nonis/lab-sheet-generator/issues)
- [Releases](https://github.com/Dinuka-Nonis/lab-sheet-generator/releases)
