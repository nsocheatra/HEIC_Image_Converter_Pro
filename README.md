# HEIC Image Converter Pro

A professional desktop application for converting HEIC/HEIF images to popular formats.

## Features

- **Modern UI**: Fluent/Windows 11 style with responsive layout
- **Light/Dark Themes**: Fully themed with QSS, toggleable at any time
- **Drag & Drop**: Drop files or folders directly onto the application
- **Batch Processing**: Convert multiple files simultaneously with QThreadPool
- **Multiple Formats**: Export to JPG, PNG, WEBP, TIFF, BMP, and PDF
- **Metadata Preservation**: EXIF, GPS, ICC color profiles, and orientation
- **Image Preview**: Zoom, pan, fit-to-window, and before/after comparison
- **Adjustable Quality**: Fine-tune JPEG and WebP compression quality
- **Transformations**: Resize, rotate, flip, and custom filename templates
- **Output Options**: Same folder, custom folder, or ask every time
- **Detailed Progress**: Progress bar with ETA, cancel, retry, and conversion log
- **Settings Persistence**: All preferences saved to JSON
- **Error Handling**: Comprehensive error handling and logging

## Requirements

- Python 3.12+
- PySide6 >= 6.6.0
- Pillow >= 10.2.0
- pillow-heif >= 0.16.0

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m heic_converter_pro.main
```

Or navigate to the project root and run:

```bash
python -m heic_converter_pro.main
```

## Building Executable

Use PyInstaller to create a standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller heic_converter_pro.spec
```

The executable will be created in the `dist/` directory.

## Architecture

```
heic_converter_pro/
├── main.py                 # Application entry point
├── app/
│   ├── main_window.py     # Main window with menus, toolbar, statusbar
│   ├── config.py          # Configuration management (singleton)
│   ├── logger.py          # Logging setup
│   ├── core/
│   │   ├── converter.py       # HEIC to format conversion logic
│   │   ├── image_processor.py # Image transformations
│   │   ├── metadata.py        # EXIF, GPS, ICC handling
│   │   └── batch_processor.py # QThreadPool batch processing
│   ├── services/
│   │   ├── file_service.py    # File system operations
│   │   ├── export_service.py  # Image export to various formats
│   │   └── pdf_service.py     # PDF generation
│   ├── ui/
│   │   ├── widgets/
│   │   │   ├── image_preview.py   # Zoomable image viewer
│   │   │   ├── progress_panel.py  # Progress bar with ETA
│   │   │   ├── conversion_log.py  # Conversion log widget
│   │   │   ├── file_list.py       # File list with context menu
│   │   │   ├── drop_area.py       # Drag & drop zone
│   │   │   └── settings_panel.py  # Conversion settings
│   │   └── dialogs/
│   │       ├── settings_dialog.py # Application settings
│   │       └── about_dialog.py    # About dialog
│   └── models/
│       ├── conversion_task.py # Task data model
│       └── settings.py        # Settings data model
```

## License

MIT
