#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Jonas Petersson <jonas.petersson@ess.eu>
#
# *****************************************************************************
import h5py
import numpy as np

from nicos.guisupport.qt import QGroupBox, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton, QVBoxLayout, QWidget, QCheckBox, QComboBox, QGridLayout, \
    QSizePolicy, QFileDialog
from nicos_ess.gui.panels.live import \
    MultiLiveDataPanel as DefaultMultiLiveDataPanel, \
    layout_iterator, Preview, DEFAULT_TAB_WIDGET_MAX_WIDTH, \
    DEFAULT_TAB_WIDGET_MIN_WIDTH


class ADControl(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.parent = parent
        self.selected_device = None
        self.fields = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        settings_group = self.create_settings_group()
        layout.addWidget(settings_group)

        normal_group = self.create_normalisation_group()
        layout.addWidget(normal_group)

        acq_layout = self.create_acquisition_control()
        layout.addLayout(acq_layout)

        self.setLayout(layout)

    def create_settings_group(self):
        settings_group = QGroupBox('Settings')
        settings_group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        settings_layout = QGridLayout()
        settings_layout.setContentsMargins(5, 5, 5, 5)
        settings_layout.setHorizontalSpacing(5)
        settings_layout.setVerticalSpacing(10)

        disp_fields = [
            ('Detector:', self.create_detector_combo, 0),
            ('Acquisition Mode:', self.create_acq_mode_combo, 1),
            ('Number of Images:', self.create_num_images_field, 2),
            ('Acquisition Time [s]:', self.create_acquisition_time_field, 3),
            (
                'Acquisition Period [s]:',
                self.create_acquisition_period_field,
                4,
            ),
            ('Start index X:', self.create_start_x_field, 5),
            ('Start index Y:', self.create_start_y_field, 6),
            ('Size X:', self.create_size_x_field, 7),
            ('Size Y:', self.create_size_y_field, 8),
            ('Binning Factor:', self.create_binning_field, 9),
        ]

        for label_text, field_method, row in disp_fields:
            label = QLabel(label_text)
            field_widget = field_method()
            settings_layout.addWidget(label, row, 0)
            settings_layout.addWidget(field_widget, row, 1)

            if hasattr(field_widget, 'readback'):
                settings_layout.addWidget(field_widget.readback, row, 2)
                self.fields.append((field_widget, field_widget.readback))

        settings_layout.setRowStretch(len(disp_fields) + 1, 1)
        settings_layout.setColumnStretch(0, 1)
        settings_layout.setColumnStretch(1, 0)
        settings_layout.setColumnStretch(2, 0)

        settings_group.setLayout(settings_layout)
        return settings_group

    def create_normalisation_group(self):
        normal_group = QGroupBox('Normalisation')
        normal_group.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        normal_layout = QGridLayout()
        normal_layout.setContentsMargins(5, 5, 5, 5)
        normal_layout.setHorizontalSpacing(5)
        normal_layout.setVerticalSpacing(10)

        self.import_open_beam_button = QPushButton('Import Open Beam')
        self.import_open_beam_button.clicked.connect(
            self._load_image_as_openbeam
        )
        normal_layout.addWidget(self.import_open_beam_button, 0, 0)

        self.loaded_openbeam_label = QLabel('Loaded file:')
        self.loaded_openbeam_label.readback = QLabel('None')
        normal_layout.addWidget(self.loaded_openbeam_label, 1, 0)
        normal_layout.addWidget(self.loaded_openbeam_label.readback, 1, 1)

        self.open_beam_acquisition_time_label = QLabel('Acquisition Time')
        self.open_beam_acquisition_time_label.readback = QLabel('None')
        normal_layout.addWidget(self.open_beam_acquisition_time_label, 2, 0)
        normal_layout.addWidget(
            self.open_beam_acquisition_time_label.readback, 2, 1
        )

        self.open_beam_correction_cb = QCheckBox('Open Beam Correction')
        self.open_beam_correction_cb.clicked.connect(self._on_correction)
        self.display_open_beam_cb = QCheckBox('Display Open Beam')
        self.display_open_beam_cb.clicked.connect(
            self._on_preview_open_beam_image
        )
        normal_layout.addWidget(self.open_beam_correction_cb, 3, 0)
        normal_layout.addWidget(self.display_open_beam_cb, 3, 1)

        self.import_dark_button = QPushButton('Import Dark')
        self.import_dark_button.clicked.connect(self._load_image_as_dark)
        normal_layout.addWidget(self.import_dark_button, 4, 0)

        self.loaded_dark_label = QLabel('Loaded file:')
        self.loaded_dark_label.readback = QLabel('None')
        normal_layout.addWidget(self.loaded_dark_label, 5, 0)
        normal_layout.addWidget(self.loaded_dark_label.readback, 5, 1)

        self.dark_acquisition_time_label = QLabel('Acquisition Time')
        self.dark_acquisition_time_label.readback = QLabel('None')
        normal_layout.addWidget(self.dark_acquisition_time_label, 6, 0)
        normal_layout.addWidget(
            self.dark_acquisition_time_label.readback, 6, 1
        )

        self.dark_subtraction_cb = QCheckBox('Dark Subtraction')
        self.dark_subtraction_cb.clicked.connect(self._on_correction)
        self.display_dark_cb = QCheckBox('Display Dark')
        self.display_dark_cb.clicked.connect(self._on_preview_dark_image)
        normal_layout.addWidget(self.dark_subtraction_cb, 7, 0)
        normal_layout.addWidget(self.display_dark_cb, 7, 1)

        self.export_button = QPushButton('Export Image')
        self.export_button.clicked.connect(self._export_image)
        normal_layout.addWidget(self.export_button, 8, 1)

        normal_layout.setRowStretch(9, 1)

        normal_group.setLayout(normal_layout)
        return normal_group

    def create_acquisition_control(self):
        def create_button(name, text, callback, color=None):
            button = QPushButton(text)
            button.setSizePolicy(
                QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
            )
            if color:
                button.setStyleSheet(f'background-color: {color}')
            button.clicked.connect(callback)
            setattr(self, name, button)
            return button

        layout = QHBoxLayout()
        layout.addWidget(
            create_button(
                'start_acq_button',
                'Start Acquisition',
                self.on_acq_start,
                'rgba(0, 200, 0, 75%)',
            )
        )
        layout.addWidget(
            create_button(
                'stop_acq_button', 'Stop Acquisition', self.on_acq_stop
            )
        )
        return layout

    def create_detector_combo(self):
        self.detector_combo = self.create_combo_box(
            ['det666', 'det999'], self.on_detector_changed
        )
        return self.detector_combo

    def create_acq_mode_combo(self):
        self.acq_mode_combo = self.create_combo_box(
            ['single', 'multiple', 'continuous'], self.on_acq_mode_changed
        )
        self.on_acq_mode_changed(0)
        return self.acq_mode_combo

    def create_binning_field(self):
        self.binning_combo = self.create_combo_box(
            ['1x1', '2x2', '4x4'], self.on_binning_changed
        )
        self.on_binning_changed(0)
        return self.binning_combo

    def create_num_images_field(self):
        self.num_images_label = QLabel('Number of Images:')
        self.num_images = self.create_line_edit(
            'Set Value', self.on_num_images_changes
        )
        return self.num_images

    def create_acquisition_time_field(self):
        self.acquisition_time = self.create_line_edit(
            'Set Value', self.on_acquisition_time_changed
        )
        return self.acquisition_time

    def create_acquisition_period_field(self):
        self.acquisition_period = self.create_line_edit(
            'Set Value', self.on_acquisition_period_changed
        )
        return self.acquisition_period

    def create_start_x_field(self):
        self.start_x = self.create_line_edit(
            'Set Value', self.on_start_x_changed
        )
        return self.start_x

    def create_start_y_field(self):
        self.start_y = self.create_line_edit(
            'Set Value', self.on_start_y_changed
        )
        return self.start_y

    def create_size_x_field(self):
        self.size_x = self.create_line_edit(
            'Set Value', self.on_size_x_changed
        )
        return self.size_x

    def create_size_y_field(self):
        self.size_y = self.create_line_edit(
            'Set Value', self.on_size_y_changed
        )
        return self.size_y

    def create_combo_box(self, items, callback):
        combo_box = QComboBox()
        combo_box.setMinimumContentsLength(1)
        combo_box.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents
        )
        combo_box.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        combo_box.addItems(items)
        combo_box.currentIndexChanged.connect(callback)
        return combo_box

    def create_line_edit(self, placeholder, callback):
        line_edit = QLineEdit()
        line_edit.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        line_edit.setPlaceholderText(placeholder)
        line_edit.returnPressed.connect(callback)
        line_edit.readback = QLabel('Readback Value')
        return line_edit

    def _get_file_path(self, dialog_type, title):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        if dialog_type == 'save':
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                title,
                '',
                'HDF5 Files (*.h5 *.hdf *.hdf5);;All Files (*)',
                options=options,
            )
        elif dialog_type == 'open':
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                title,
                '',
                'HDF5 Files (*.h5 *.hdf *.hdf5);;All Files (*)',
                options=options,
            )
        else:
            raise ValueError('Invalid dialog_type')

        return file_path

    def _export_image(self):
        image = self.parent.plotwidget.raw_image
        if image is None:
            print('No image data to export.')
            return

        file_path = self._get_file_path('save', 'Save Image Data')
        if not file_path:
            print('No file path provided. Image data export canceled.')
            return

        with h5py.File(file_path, 'w') as hdf5_file:
            dataset = hdf5_file.create_dataset('image_data', data=image)
            dataset.attrs.create(
                name='acquisition_time',
                data=float(self.acquisition_time.readback.text()),
            )

        print(f'Image data exported to {file_path}')

    def _load_image(
        self,
        dialog_title,
        image_attribute,
        acquisition_time_attribute,
        label_attribute,
    ):
        file_path = self._get_file_path('open', dialog_title)
        if not file_path:
            print('No file path provided. Image data loading canceled.')
            return

        with h5py.File(file_path, 'r') as hdf5_file:
            dataset = hdf5_file['image_data']
            setattr(self, image_attribute, dataset[:])
            setattr(
                self,
                acquisition_time_attribute,
                dataset.attrs.get('acquisition_time', 'None'),
            )

        print(f'Image data loaded from {file_path}')
        getattr(self, label_attribute).readback.setText(file_path)
        getattr(self, acquisition_time_attribute + '_label').readback.setText(
            str(getattr(self, acquisition_time_attribute))
        )

    def _load_image_as_openbeam(self):
        self._load_image(
            'Load Image Data',
            'open_beam_image',
            'open_beam_acquisition_time',
            'loaded_openbeam_label',
        )

    def _load_image_as_dark(self):
        self._load_image(
            'Load Image Data',
            'dark_image',
            'dark_acquisition_time',
            'loaded_dark_label',
        )

    def _on_preview_image(self, state, display_other_cb, image, other_image):
        if state:
            display_other_cb.setChecked(False)
            self.parent.plotwidget.image_view_controller.disp_image = image
            self.parent.plotwidget.set_image(
                image, autoLevels=False, raw_update=False
            )
        else:
            if not display_other_cb.isChecked():
                self.parent.plotwidget.image_view_controller.disp_image = None
                self.parent.plotwidget.set_image(
                    other_image, autoLevels=False, raw_update=False
                )

    def _on_preview_dark_image(self, state):
        self._on_preview_image(
            state,
            self.display_open_beam_cb,
            self.dark_image,
            self.parent.plotwidget.raw_image,
        )

    def _on_preview_open_beam_image(self, state):
        self._on_preview_image(
            state,
            self.display_dark_cb,
            self.open_beam_image,
            self.parent.plotwidget.raw_image,
        )

    def _apply_corrections(self, image):
        corrected_image = np.copy(image)

        if self.dark_subtraction_cb.isChecked():
            corrected_image -= self.dark_image

        if self.open_beam_correction_cb.isChecked():
            diff = self.open_beam_image - (
                self.dark_image if self.dark_subtraction_cb.isChecked() else 0
            )
            non_zero_diff = np.where(diff != 0, diff, 1)
            corrected_image *= np.mean(diff) / non_zero_diff

        return corrected_image

    def _on_correction(self):
        if not (
            self.open_beam_correction_cb.isChecked()
            or self.dark_subtraction_cb.isChecked()
        ):
            self.parent.plotwidget.image_view_controller.disp_image = None
            self.parent.plotwidget.update_image()
            return

        raw_image = self.parent.plotwidget.raw_image
        if raw_image is None:
            print('No image data to apply correction.')
            self.parent.plotwidget.image_view_controller.disp_image = None
            return

        corrected_image = self._apply_corrections(raw_image)
        self.parent.plotwidget.image_view_controller.disp_image = (
            corrected_image
        )
        self.parent.plotwidget.set_image(
            corrected_image, autoLevels=False, raw_update=False
        )

    def on_detector_changed(self, index):
        self.selected_device = self.detector_combo.currentText()
        if not self.selected_device:
            return
        self.update_readback_values()
        for field, field_readback in self.fields:
            if isinstance(field, QLineEdit):
                field.setText(field_readback.text())

    def update_readback_values(self):
        if not self.selected_device:
            return

        param_info = self.parent.client.getDeviceParams(self.selected_device)
        if not param_info:
            return

        self._update_text_fields(param_info)
        self._update_start_acq_button_style(
            param_info.get('status', (None, None))[1]
        )
        self._highlight_differing_readback_values()

    def _update_text_fields(self, param_info):
        self.acquisition_time.readback.setText(
            str(param_info.get('acquiretime'))
        )
        self.acquisition_period.readback.setText(
            str(param_info.get('acquireperiod'))
        )
        self.start_x.readback.setText(str(param_info.get('startx')))
        self.start_y.readback.setText(str(param_info.get('starty')))
        self.size_x.readback.setText(str(param_info.get('sizex')))
        self.size_y.readback.setText(str(param_info.get('sizey')))
        self.num_images.readback.setText(str(param_info.get('numimages')))
        self.acq_mode_combo.setCurrentText(str(param_info.get('imagemode')))
        self.binning_combo.setCurrentText(str(param_info.get('binning')))

    def _update_start_acq_button_style(self, status):
        if status == '':
            return
        elif 'Done' in status or 'Idle' in status:
            self.start_acq_button.setStyleSheet(
                'background-color: rgba(0, 200, 0, 75%)'
            )
        elif 'Acquiring' in status:
            self.start_acq_button.setStyleSheet(
                'background-color: rgba(0, 0, 255, 60%)'
            )
        else:
            self.start_acq_button.setStyleSheet(
                'background-color: rgba(255, 0, 0, 60%)'
            )

    def _highlight_differing_readback_values(self):
        for input_field, readback_field in self.fields:
            if input_field.text() == '':
                continue

            if float(input_field.text()) != float(readback_field.text()):
                readback_field.setStyleSheet(
                    'background-color: rgba(255, 0, 0, 75%)'
                )
            else:
                readback_field.setStyleSheet(
                    'background-color: rgba(255, 255, 255, 0%)'
                )

    def _exec_command_if_device_selected(self, command_template, *args):
        if not self.selected_device:
            return
        command = command_template % ((self.selected_device,) + args)
        self.parent.exec_command(command)

    def on_acq_start(self):
        # Needed?
        self._exec_command_if_device_selected('%s.prepare()')
        # Don't set presets, run with config from here
        self._exec_command_if_device_selected('%s.doAcquire()')

    def on_acq_stop(self):
        self._exec_command_if_device_selected('%s.stop()')

    def on_acq_mode_changed(self, index):
        mode = str(self.acq_mode_combo.currentText())
        self._exec_command_if_device_selected('%s.imagemode = "%s"', mode)

    def on_binning_changed(self, index):
        binning = str(self.binning_combo.currentText())
        self._exec_command_if_device_selected('%s.binning = "%s"', binning)

    def on_acquisition_time_changed(self):
        acquisition_time = float(self.acquisition_time.text())
        self._exec_command_if_device_selected(
            '%s.acquiretime = %f', acquisition_time
        )

    def on_acquisition_period_changed(self):
        acquisition_period = float(self.acquisition_period.text())
        self._exec_command_if_device_selected(
            '%s.acquireperiod = %f', acquisition_period
        )

    def on_start_x_changed(self):
        start_x = int(self.start_x.text())
        self._exec_command_if_device_selected('%s.startx = %d', start_x)

    def on_start_y_changed(self):
        start_y = int(self.start_y.text())
        self._exec_command_if_device_selected('%s.starty = %d', start_y)

    def on_size_x_changed(self):
        size_x = int(self.size_x.text())
        self._exec_command_if_device_selected('%s.sizex = %d', size_x)

    def on_size_y_changed(self):
        size_y = int(self.size_y.text())
        self._exec_command_if_device_selected('%s.sizey = %d', size_y)

    def on_num_images_changes(self):
        num_images = int(self.num_images.text())
        self._exec_command_if_device_selected('%s.numimages = %d', num_images)


class MultiLiveDataPanel(DefaultMultiLiveDataPanel):
    def __init__(self, parent, client, options):
        DefaultMultiLiveDataPanel.__init__(self, parent, client, options)

        self.ad_controller = ADControl(self)
        self.tab_widget.addTab(self.ad_controller, 'Detector Control')
        self.connect_camera_controller_signals()

    def connect_camera_controller_signals(self):
        self.ad_controller.detector_combo.currentTextChanged.connect(
            self.on_ad_selected
        )

    def on_ad_selected(self, ad_name):
        if ad_name not in self._previews.keys():
            return
        self._change_detector_to_display(ad_name)

    def _cleanup_existing_previews(self):
        for item in layout_iterator(self.scroll_content.layout()):
            item.widget().deleteLater()
            del item
        self.ad_controller.detector_combo.clear()
        self._previews.clear()
        self._detectors.clear()

    def add_previews_to_layout(self, previews, det_name):
        for preview in previews:
            name = preview.widget().name
            self._previews[name] = Preview(name, det_name, preview)
            self._detectors[det_name].add_preview(name)
            if 'collector' in det_name.lower():
                self.ad_controller.detector_combo.addItem(name)
            preview.widget().clicked.connect(self.on_preview_clicked)
            self.scroll_content.layout().addWidget(preview)

    def set_tab_widget_width(self):
        self.tab_widget.setMaximumWidth(DEFAULT_TAB_WIDGET_MAX_WIDTH)
        self.tab_widget.setMinimumWidth(DEFAULT_TAB_WIDGET_MIN_WIDTH)

    def on_client_cache(self, data):
        _, key, _, _ = data
        self.ad_controller.update_readback_values()
        self.scroll.setMaximumWidth(self.ad_controller.size().width())
        if key == 'exp/detlist':
            self.ad_controller.detector_combo.clear()
            self._cleanup_existing_previews()
