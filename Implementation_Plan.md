# Implementation Plan

## Phase 1: Project Setup & Architecture
- [x] Create directory structure with modular package layout
- [x] Define data models (ConversionTask, AppSettings with enums)
- [x] Implement singleton ConfigManager with JSON persistence
- [x] Set up logging infrastructure (file + console)

## Phase 2: Core Logic Layer
- [x] FileService: HEIC discovery, path validation, output path generation
- [x] ImageProcessor: Resize, rotate, flip, EXIF orientation, crop
- [x] MetadataHandler: EXIF extraction/preservation, GPS, ICC profiles
- [x] HeicConverter: Open HEIC with pillow-heif, apply transforms, save output
- [x] ExportService: Save to JPG, PNG, WEBP, TIFF, BMP, PDF
- [x] PdfService: Multipage PDF creation from image list

## Phase 3: Batch Processing
- [x] ConversionWorker (QRunnable): Per-task conversion with progress
- [x] BatchProcessor (QObject): QThreadPool management, signal forwarding
- [x] Cancel, retry failed, progress tracking

## Phase 4: UI - Widgets
- [x] DropArea: Custom-painted drag-and-drop zone with visual feedback
- [x] FileListWidget: File list with add/remove/clear, status indicators
- [x] ImagePreviewWidget: QGraphicsView-based zoom/pan, fit-to-window
- [x] ComparisonView: Before/after comparison with draggable divider
- [x] ProgressPanel: Progress bar, ETA calculation, cancel/retry buttons
- [x] ConversionLog: HTML-colored log with auto-scroll and export
- [x] SettingsPanel: Scrollable form for all conversion options

## Phase 5: UI - Dialogs & Main Window
- [x] SettingsDialog: Application preferences (theme, language, threads)
- [x] AboutDialog: Application information
- [x] MainWindow: QSplitter layout, menus, toolbar, status bar
- [x] Keyboard shortcuts (Ctrl+O, Ctrl+R, Ctrl+T, etc.)

## Phase 6: Theming & Styling
- [x] Comprehensive QSS light theme (Windows 11/Fluent style)
- [x] Comprehensive QSS dark theme with palette support
- [x] Theme toggle from menu and toolbar
- [x] Consistent widget styling across all components

## Phase 7: Advanced Features
- [x] Before/after image comparison with split view
- [x] EXIF orientation auto-application
- [x] Filename templates with {name} and {counter}
- [x] Custom output folder with overwrite option
- [x] Window geometry persistence

## Phase 8: Packaging & Documentation
- [x] requirements.txt with version pins
- [x] README.md with architecture and usage
- [x] Implementation_Plan.md
- [x] PyInstaller spec for Windows executable

## Future Enhancements
- [ ] Multi-language support (i18n)
- [ ] Plugin system for custom export formats
- [ ] Thumbnail gallery view
- [ ] Batch rename preview
- [ ] Drag-and-drop reordering in file list
- [ ] GPU-accelerated image processing
- [ ] Auto-update mechanism
