from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QSlider,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QScrollArea,
    QGridLayout,
)

from heic_converter_pro.app.config import ConfigManager
from heic_converter_pro.app.models.settings import (
    AppSettings,
    ExportFormat,
    OutputMode,
)

logger = logging.getLogger(__name__)


class SettingsPanel(QWidget):
    settings_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._config = ConfigManager()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.frameShape().NoFrame)

        scroll_content = QWidget()
        self._main_layout = QVBoxLayout(scroll_content)
        self._main_layout.setSpacing(12)

        self._build_output_group()
        self._build_quality_group()
        self._build_resize_group()
        self._build_transform_group()
        self._build_metadata_group()
        self._build_enhance_group()
        self._build_filename_group()
        self._build_advanced_group()

        self._main_layout.addStretch()

        scroll.setWidget(scroll_content)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("Conversion Settings")
        header_font = QFont()
        header_font.setPointSize(11)
        header_font.setBold(True)
        header.setFont(header_font)
        outer_layout.addWidget(header)

        outer_layout.addWidget(scroll)

    def _build_output_group(self) -> None:
        group = QGroupBox("Output Format")
        layout = QFormLayout(group)

        self._format_combo = QComboBox()
        for fmt in ExportFormat:
            self._format_combo.addItem(fmt.value.upper(), fmt.value)
        self._format_combo.currentIndexChanged.connect(self._on_setting_changed)
        layout.addRow("Format:", self._format_combo)

        self._output_mode_combo = QComboBox()
        self._output_mode_combo.addItem("Same as source", OutputMode.SAME_FOLDER.value)
        self._output_mode_combo.addItem("Custom folder", OutputMode.CUSTOM_FOLDER.value)
        self._output_mode_combo.addItem("Ask every time", OutputMode.ASK_EVERY.value)
        self._output_mode_combo.currentIndexChanged.connect(self._on_output_mode_changed)
        layout.addRow("Output to:", self._output_mode_combo)

        output_folder_layout = QHBoxLayout()
        self._output_folder_edit = QLineEdit()
        self._output_folder_edit.setPlaceholderText("Select output folder...")
        self._output_folder_edit.setEnabled(False)
        output_folder_layout.addWidget(self._output_folder_edit)

        self._browse_btn = QPushButton("Browse")
        self._browse_btn.setEnabled(False)
        self._browse_btn.clicked.connect(self._browse_output_folder)
        output_folder_layout.addWidget(self._browse_btn)
        layout.addRow("Folder:", output_folder_layout)

        self._overwrite_cb = QCheckBox("Overwrite existing files")
        self._overwrite_cb.stateChanged.connect(self._on_setting_changed)
        layout.addRow("", self._overwrite_cb)

        self._main_layout.addWidget(group)

    def _build_quality_group(self) -> None:
        group = QGroupBox("Quality")
        layout = QFormLayout(group)

        jpeg_layout = QHBoxLayout()
        self._jpeg_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self._jpeg_quality_slider.setRange(1, 100)
        self._jpeg_quality_slider.valueChanged.connect(self._on_jpeg_quality_changed)
        jpeg_layout.addWidget(self._jpeg_quality_slider)
        self._jpeg_quality_label = QLabel("95")
        self._jpeg_quality_label.setMinimumWidth(30)
        jpeg_layout.addWidget(self._jpeg_quality_label)
        layout.addRow("JPEG Quality:", jpeg_layout)

        webp_layout = QHBoxLayout()
        self._webp_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self._webp_quality_slider.setRange(1, 100)
        self._webp_quality_slider.valueChanged.connect(self._on_webp_quality_changed)
        webp_layout.addWidget(self._webp_quality_slider)
        self._webp_quality_label = QLabel("90")
        self._webp_quality_label.setMinimumWidth(30)
        webp_layout.addWidget(self._webp_quality_label)
        layout.addRow("WebP Quality:", webp_layout)

        self._main_layout.addWidget(group)

    def _build_resize_group(self) -> None:
        group = QGroupBox("Resize")
        layout = QGridLayout(group)

        self._resize_cb = QCheckBox("Enable resize")
        self._resize_cb.stateChanged.connect(self._on_setting_changed)
        layout.addWidget(self._resize_cb, 0, 0, 1, 2)

        layout.addWidget(QLabel("Width:"), 1, 0)
        self._resize_width_spin = QSpinBox()
        self._resize_width_spin.setRange(1, 10000)
        self._resize_width_spin.setValue(1920)
        self._resize_width_spin.setEnabled(False)
        self._resize_width_spin.valueChanged.connect(self._on_setting_changed)
        layout.addWidget(self._resize_width_spin, 1, 1)

        layout.addWidget(QLabel("Height:"), 2, 0)
        self._resize_height_spin = QSpinBox()
        self._resize_height_spin.setRange(1, 10000)
        self._resize_height_spin.setValue(1080)
        self._resize_height_spin.setEnabled(False)
        self._resize_height_spin.valueChanged.connect(self._on_setting_changed)
        layout.addWidget(self._resize_height_spin, 2, 1)

        self._keep_aspect_cb = QCheckBox("Keep aspect ratio")
        self._keep_aspect_cb.setChecked(True)
        self._keep_aspect_cb.setEnabled(False)
        self._keep_aspect_cb.stateChanged.connect(self._on_setting_changed)
        layout.addWidget(self._keep_aspect_cb, 3, 0, 1, 2)

        self._resize_cb.stateChanged.connect(
            lambda checked: (
                self._resize_width_spin.setEnabled(checked),
                self._resize_height_spin.setEnabled(checked),
                self._keep_aspect_cb.setEnabled(checked),
            )
        )

        self._main_layout.addWidget(group)

    def _build_transform_group(self) -> None:
        group = QGroupBox("Transform")
        layout = QFormLayout(group)

        rotation_layout = QHBoxLayout()
        self._rotation_spin = QSpinBox()
        self._rotation_spin.setRange(0, 360)
        self._rotation_spin.setSuffix("°")
        self._rotation_spin.setSingleStep(90)
        self._rotation_spin.valueChanged.connect(self._on_setting_changed)
        rotation_layout.addWidget(self._rotation_spin)
        self._rotate_90_cw = QPushButton("90° CW")
        self._rotate_90_cw.clicked.connect(
            lambda: self._rotation_spin.setValue((self._rotation_spin.value() + 90) % 360)
        )
        rotation_layout.addWidget(self._rotate_90_cw)
        self._rotate_90_ccw = QPushButton("90° CCW")
        self._rotate_90_ccw.clicked.connect(
            lambda: self._rotation_spin.setValue((self._rotation_spin.value() - 90) % 360)
        )
        rotation_layout.addWidget(self._rotate_90_ccw)
        layout.addRow("Rotation:", rotation_layout)

        self._flip_h_cb = QCheckBox("Flip horizontally")
        self._flip_h_cb.stateChanged.connect(self._on_setting_changed)
        layout.addRow("", self._flip_h_cb)
        self._flip_v_cb = QCheckBox("Flip vertically")
        self._flip_v_cb.stateChanged.connect(self._on_setting_changed)
        layout.addRow("", self._flip_v_cb)

        self._brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self._brightness_slider.setRange(0, 200)
        self._brightness_slider.setValue(100)
        self._brightness_slider.valueChanged.connect(self._on_setting_changed)
        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(self._brightness_slider)
        self._brightness_label = QLabel("1.0")
        brightness_layout.addWidget(self._brightness_label)
        layout.addRow("Brightness:", brightness_layout)
        self._brightness_slider.valueChanged.connect(
            lambda v: self._brightness_label.setText(f"{v/100:.1f}")
        )

        self._contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self._contrast_slider.setRange(0, 300)
        self._contrast_slider.setValue(100)
        self._contrast_slider.valueChanged.connect(self._on_setting_changed)
        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(self._contrast_slider)
        self._contrast_label = QLabel("1.0")
        contrast_layout.addWidget(self._contrast_label)
        layout.addRow("Contrast:", contrast_layout)
        self._contrast_slider.valueChanged.connect(
            lambda v: self._contrast_label.setText(f"{v/100:.1f}")
        )

        self._sharpness_slider = QSlider(Qt.Orientation.Horizontal)
        self._sharpness_slider.setRange(0, 300)
        self._sharpness_slider.setValue(100)
        self._sharpness_slider.valueChanged.connect(self._on_setting_changed)
        sharpness_layout = QHBoxLayout()
        sharpness_layout.addWidget(self._sharpness_slider)
        self._sharpness_label = QLabel("1.0")
        sharpness_layout.addWidget(self._sharpness_label)
        layout.addRow("Sharpness:", sharpness_layout)
        self._sharpness_slider.valueChanged.connect(
            lambda v: self._sharpness_label.setText(f"{v/100:.1f}")
        )

        self._saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self._saturation_slider.setRange(0, 300)
        self._saturation_slider.setValue(100)
        self._saturation_slider.valueChanged.connect(self._on_setting_changed)
        saturation_layout = QHBoxLayout()
        saturation_layout.addWidget(self._saturation_slider)
        self._saturation_label = QLabel("1.0")
        saturation_layout.addWidget(self._saturation_label)
        layout.addRow("Saturation:", saturation_layout)
        self._saturation_slider.valueChanged.connect(
            lambda v: self._saturation_label.setText(f"{v/100:.1f}")
        )

        gamma_layout = QHBoxLayout()
        self._gamma_slider = QSlider(Qt.Orientation.Horizontal)
        self._gamma_slider.setRange(10, 300)
        self._gamma_slider.setValue(100)
        self._gamma_slider.valueChanged.connect(self._on_setting_changed)
        gamma_layout.addWidget(self._gamma_slider)
        self._gamma_label = QLabel("1.0")
        gamma_layout.addWidget(self._gamma_label)
        layout.addRow("Gamma:", gamma_layout)
        self._gamma_slider.valueChanged.connect(
            lambda v: self._gamma_label.setText(f"{v/100:.1f}")
        )

        self._auto_enhance_cb = QCheckBox("Auto enhance")
        self._auto_enhance_cb.stateChanged.connect(self._on_setting_changed)
        layout.addRow("", self._auto_enhance_cb)

        blur_layout = QHBoxLayout()
        self._blur_spin = QSpinBox()
        self._blur_spin.setRange(0, 50)
        self._blur_spin.setValue(0)
        self._blur_spin.valueChanged.connect(self._on_setting_changed)
        blur_layout.addWidget(self._blur_spin)
        blur_layout.addWidget(QLabel("px"))
        layout.addRow("Blur:", blur_layout)

        self._main_layout.addWidget(group)

    def _build_enhance_group(self) -> None:
        group = QGroupBox("Watermark & Border")
        layout = QFormLayout(group)

        self._watermark_edit = QLineEdit()
        self._watermark_edit.setPlaceholderText("Watermark text (leave empty to disable)")
        self._watermark_edit.textChanged.connect(self._on_setting_changed)
        layout.addRow("Text:", self._watermark_edit)

        self._watermark_pos = QComboBox()
        self._watermark_pos.addItems(["top_left", "top_right", "bottom_left", "bottom_right", "center"])
        self._watermark_pos.currentIndexChanged.connect(self._on_setting_changed)
        layout.addRow("Position:", self._watermark_pos)

        opacity_layout = QHBoxLayout()
        self._watermark_opacity = QSlider(Qt.Orientation.Horizontal)
        self._watermark_opacity.setRange(0, 255)
        self._watermark_opacity.setValue(128)
        self._watermark_opacity.valueChanged.connect(self._on_setting_changed)
        opacity_layout.addWidget(self._watermark_opacity)
        self._watermark_opacity_label = QLabel("128")
        opacity_layout.addWidget(self._watermark_opacity_label)
        layout.addRow("Opacity:", opacity_layout)
        self._watermark_opacity.valueChanged.connect(
            lambda v: self._watermark_opacity_label.setText(str(v))
        )

        border_layout = QHBoxLayout()
        self._border_spin = QSpinBox()
        self._border_spin.setRange(0, 100)
        self._border_spin.setValue(0)
        self._border_spin.setSuffix(" px")
        self._border_spin.valueChanged.connect(self._on_setting_changed)
        border_layout.addWidget(self._border_spin)
        layout.addRow("Border:", border_layout)

        self._main_layout.addWidget(group)

    def _build_metadata_group(self) -> None:
        group = QGroupBox("Metadata")
        layout = QVBoxLayout(group)

        self._preserve_exif_cb = QCheckBox("Preserve EXIF data")
        self._preserve_exif_cb.setChecked(True)
        self._preserve_exif_cb.stateChanged.connect(self._on_setting_changed)
        layout.addWidget(self._preserve_exif_cb)

        self._preserve_gps_cb = QCheckBox("Preserve GPS data")
        self._preserve_gps_cb.setChecked(True)
        self._preserve_gps_cb.stateChanged.connect(self._on_setting_changed)
        layout.addWidget(self._preserve_gps_cb)

        self._preserve_icc_cb = QCheckBox("Preserve ICC color profile")
        self._preserve_icc_cb.setChecked(True)
        self._preserve_icc_cb.stateChanged.connect(self._on_setting_changed)
        layout.addWidget(self._preserve_icc_cb)

        self._preserve_orientation_cb = QCheckBox("Auto-apply EXIF orientation")
        self._preserve_orientation_cb.setChecked(True)
        self._preserve_orientation_cb.stateChanged.connect(self._on_setting_changed)
        layout.addWidget(self._preserve_orientation_cb)

        self._main_layout.addWidget(group)

    def _build_filename_group(self) -> None:
        group = QGroupBox("Filename Template")
        layout = QFormLayout(group)

        self._template_edit = QLineEdit("{name}_converted")
        self._template_edit.setPlaceholderText("{name} and {counter} supported")
        self._template_edit.textChanged.connect(self._on_setting_changed)
        layout.addRow("Template:", self._template_edit)

        help_label = QLabel("Use {name} for original filename, {counter} for numbering")
        help_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addRow("", help_label)

        self._main_layout.addWidget(group)

    def _build_advanced_group(self) -> None:
        group = QGroupBox("Advanced")
        layout = QFormLayout(group)

        self._threads_spin = QSpinBox()
        self._threads_spin.setRange(1, 32)
        self._threads_spin.setValue(4)

        self._keep_original_cb = QCheckBox("Keep original files after conversion")
        self._keep_original_cb.setChecked(True)
        self._keep_original_cb.stateChanged.connect(self._on_setting_changed)
        layout.addRow("", self._keep_original_cb)
        self._threads_spin.valueChanged.connect(self._on_setting_changed)
        layout.addRow("Max threads:", self._threads_spin)

        self._main_layout.addWidget(group)

    def _load_settings(self) -> None:
        settings = self._config.get()

        idx = self._format_combo.findData(settings.export_format.value)
        if idx >= 0:
            self._format_combo.setCurrentIndex(idx)

        idx = self._output_mode_combo.findData(settings.output_mode.value)
        if idx >= 0:
            self._output_mode_combo.setCurrentIndex(idx)

        self._output_folder_edit.setText(settings.custom_output_folder)
        self._overwrite_cb.setChecked(settings.overwrite_existing)

        self._jpeg_quality_slider.setValue(settings.jpeg_quality)
        self._webp_quality_slider.setValue(settings.webp_quality)

        self._resize_cb.setChecked(settings.resize_enabled)
        self._resize_width_spin.setValue(settings.resize_width)
        self._resize_height_spin.setValue(settings.resize_height)
        self._keep_aspect_cb.setChecked(settings.resize_keep_aspect)

        self._rotation_spin.setValue(settings.rotation)
        self._flip_h_cb.setChecked(settings.flip_horizontal)
        self._flip_v_cb.setChecked(settings.flip_vertical)
        self._brightness_slider.setValue(int(settings.brightness * 100))
        self._brightness_label.setText(f"{settings.brightness:.1f}")
        self._contrast_slider.setValue(int(settings.contrast * 100))
        self._contrast_label.setText(f"{settings.contrast:.1f}")
        self._sharpness_slider.setValue(int(settings.sharpness * 100))
        self._sharpness_label.setText(f"{settings.sharpness:.1f}")
        self._saturation_slider.setValue(int(settings.saturation * 100))
        self._saturation_label.setText(f"{settings.saturation:.1f}")
        self._gamma_slider.setValue(int(settings.gamma * 100))
        self._gamma_label.setText(f"{settings.gamma:.1f}")
        self._auto_enhance_cb.setChecked(settings.auto_enhance)
        self._blur_spin.setValue(settings.blur_radius)
        self._watermark_edit.setText(settings.watermark_text)
        idx = self._watermark_pos.findText(settings.watermark_position)
        if idx >= 0:
            self._watermark_pos.setCurrentIndex(idx)
        self._watermark_opacity.setValue(settings.watermark_opacity)
        self._watermark_opacity_label.setText(str(settings.watermark_opacity))
        self._border_spin.setValue(settings.border_width)
        self._keep_original_cb.setChecked(settings.keep_original)

        self._preserve_exif_cb.setChecked(settings.preserve_exif)
        self._preserve_gps_cb.setChecked(settings.preserve_gps)
        self._preserve_icc_cb.setChecked(settings.preserve_icc)
        self._preserve_orientation_cb.setChecked(settings.preserve_orientation)

        self._template_edit.setText(settings.filename_template)
        self._threads_spin.setValue(settings.max_threads)
        self._keep_original_cb.setChecked(settings.keep_original)

    def apply_settings(self) -> None:
        settings = self._config.get()
        settings.export_format = ExportFormat(self._format_combo.currentData())
        settings.output_mode = OutputMode(self._output_mode_combo.currentData())
        settings.custom_output_folder = self._output_folder_edit.text()
        settings.overwrite_existing = self._overwrite_cb.isChecked()
        settings.jpeg_quality = self._jpeg_quality_slider.value()
        settings.webp_quality = self._webp_quality_slider.value()
        settings.resize_enabled = self._resize_cb.isChecked()
        settings.resize_width = self._resize_width_spin.value()
        settings.resize_height = self._resize_height_spin.value()
        settings.resize_keep_aspect = self._keep_aspect_cb.isChecked()
        settings.rotation = self._rotation_spin.value()
        settings.flip_horizontal = self._flip_h_cb.isChecked()
        settings.flip_vertical = self._flip_v_cb.isChecked()
        settings.brightness = self._brightness_slider.value() / 100.0
        settings.contrast = self._contrast_slider.value() / 100.0
        settings.sharpness = self._sharpness_slider.value() / 100.0
        settings.saturation = self._saturation_slider.value() / 100.0
        settings.gamma = self._gamma_slider.value() / 100.0
        settings.auto_enhance = self._auto_enhance_cb.isChecked()
        settings.blur_radius = self._blur_spin.value()
        settings.watermark_text = self._watermark_edit.text()
        settings.watermark_position = self._watermark_pos.currentText()
        settings.watermark_opacity = self._watermark_opacity.value()
        settings.border_width = self._border_spin.value()
        settings.keep_original = self._keep_original_cb.isChecked()
        settings.preserve_exif = self._preserve_exif_cb.isChecked()
        settings.preserve_gps = self._preserve_gps_cb.isChecked()
        settings.preserve_icc = self._preserve_icc_cb.isChecked()
        settings.preserve_orientation = self._preserve_orientation_cb.isChecked()
        settings.filename_template = self._template_edit.text()
        settings.max_threads = self._threads_spin.value()
        settings.keep_original = self._keep_original_cb.isChecked()
        self._config.save()

    def _on_setting_changed(self) -> None:
        self.settings_changed.emit()

    def _on_jpeg_quality_changed(self, value: int) -> None:
        self._jpeg_quality_label.setText(str(value))
        self._on_setting_changed()

    def _on_webp_quality_changed(self, value: int) -> None:
        self._webp_quality_label.setText(str(value))
        self._on_setting_changed()

    def _on_output_mode_changed(self, index: int) -> None:
        mode = self._output_mode_combo.itemData(index)
        is_custom = mode == OutputMode.CUSTOM_FOLDER.value
        self._output_folder_edit.setEnabled(is_custom)
        self._browse_btn.setEnabled(is_custom)
        self._on_setting_changed()

    def _browse_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self._output_folder_edit.setText(folder)
            self._on_setting_changed()
