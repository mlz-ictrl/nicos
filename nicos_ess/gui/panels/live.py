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

"""NICOS livewidget with pyqtgraph."""
from datetime import datetime
from enum import Enum

import numpy as np
import pyqtgraph as pg
from pyqtgraph import AxisItem, GraphicsView, HistogramLUTItem, ImageItem, \
    PlotWidget, ViewBox, mkPen, mkBrush, ColorMap
from pyqtgraph.graphicsItems.ROI import ROI

from nicos.clients.gui.panels import Panel
from nicos.core.constants import LIVE
from nicos.guisupport.livewidget import AXES, DATATYPES
from nicos.guisupport.qt import QFrame, QGroupBox, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QScrollArea, QSize, QSizePolicy, QSplitter, Qt, \
    QTabWidget, QVBoxLayout, QWidget, pyqtProperty, pyqtSignal, pyqtSlot, \
    QCheckBox
from nicos.utils.loggers import NicosLogger

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)


class HistogramItem(HistogramLUTItem):
    def __init__(
        self,
        image=None,
        fillHistogram=True,
        levelMode='mono',
        gradientPosition='right',
        orientation='vertical',
    ):
        HistogramLUTItem.__init__(
            self,
            image=image,
            fillHistogram=fillHistogram,
            levelMode=levelMode,
            gradientPosition=gradientPosition,
            orientation=orientation,
        )
        self.layout.removeItem(self.axis)
        self.layout.removeItem(self.vb)
        self.layout.removeItem(self.gradient)
        self.axis = AxisItem(
            'bottom', linkView=self.vb, maxTickLength=-10, parent=self
        )
        self.axis_2 = AxisItem(
            'left', linkView=self.vb, maxTickLength=-30, parent=self
        )
        self.layout.addItem(self.axis_2, 0, 0)
        self.layout.addItem(self.vb, 0, 1)
        self.layout.addItem(self.axis, 1, 1)
        self.layout.addItem(self.gradient, 2, 1)

        self.vb.setMaximumHeight(1000)

    def imageChanged(self, autoLevel=False, autoRange=False, bins=None):
        if self.imageItem() is None:
            return

        if self.levelMode != 'mono':
            self.log.error('Only mono images are supported')
            return

        for plt in self.plots[1:]:
            plt.setVisible(False)
        self.plots[0].setVisible(True)
        # plot one histogram for all image data
        if bins:
            h = self.imageItem().getHistogram(bins)
        else:
            h = self.imageItem().getHistogram()
        if h[0] is None:
            return
        self.plot.setData(*h)
        if autoLevel:
            mn = h[0][0]
            mx = h[0][-1]
            self.region.setRegion([mn, mx])
        else:
            mn, mx = self.imageItem().levels
            self.region.setRegion([mn, mx])


class HistogramWidget(GraphicsView):
    def __init__(self, parent=None, remove_regions=False, *args, **kargs):
        background = kargs.pop('background', 'default')
        GraphicsView.__init__(
            self, parent, useOpenGL=False, background=background
        )
        self.item = HistogramItem(*args, **kargs)
        self.setCentralItem(self.item)

        self.orientation = kargs.get('orientation', 'vertical')
        if self.orientation == 'vertical':
            self.setSizePolicy(
                QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding,
            )
            self.setMinimumWidth(95)
        else:
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred,
            )
            self.setMinimumHeight(95)

        if remove_regions:
            self.region.setVisible(False)
            self.item.plot.hide()
            for region in self.regions:
                self.vb.removeItem(region)
                del region
            self.vb.removeItem(self.gradient)

    def __getattr__(self, attr):
        return getattr(self.item, attr)


class PlotROI(ROI):
    def __init__(self, size, *args, **kwargs):
        ROI.__init__(
            self, pos=[0, 0], size=size, rotatable=False, *args, **kwargs,
        )
        self.addScaleHandle([1, 1], [0, 0])


class CrossROI:
    def __init__(self):
        pen = mkPen((6, 21, 191, 150), width=3)
        hover_pen = mkPen((6, 21, 191, 255), width=3)
        self.vertical_line = pg.InfiniteLine(
            pos=10, angle=90, movable=True, pen=pen, hoverPen=hover_pen,
        )
        self.horizontal_line = pg.InfiniteLine(
            pos=10, angle=0, movable=True, pen=pen, hoverPen=hover_pen
        )


class LineView(QWidget):
    clicked = pyqtSignal(str)
    data_changed = pyqtSignal(dict)

    def __init__(self, parent=None, name='', preview_mode=False, *args):
        super(LineView, self).__init__(parent, *args)

        self.name = name
        self.preview_mode = preview_mode
        self.data = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        hbox = QHBoxLayout()

        self.mode_checkbox = QCheckBox('Plot latest curve')
        self.mode_checkbox.setChecked(True)
        self.mode_checkbox.stateChanged.connect(self.toggle_mode)
        hbox.addWidget(self.mode_checkbox)

        self.clear_button = QPushButton('Clear curves')
        self.clear_button.clicked.connect(self.clear_data)
        hbox.addWidget(self.clear_button)

        self.log_checkbox = QCheckBox('Logarithmic mode')
        self.log_checkbox.stateChanged.connect(self.toggle_log_mode)
        hbox.addWidget(self.log_checkbox)

        if not self.preview_mode:
            layout.addLayout(hbox)

        splitter_widget = QSplitter(Qt.Orientation.Vertical)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        self.view = self.plot_widget.getViewBox()
        splitter_widget.addWidget(self.plot_widget)

        self.legend = self.plot_widget.addLegend(
            pen=mkPen('k', width=0.5), brush=mkBrush((0, 0, 0, 10)),
        )
        self.legend.hide()

        self.init_vertical_line()

        self.plot_widget_sliced = pg.PlotWidget(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')}
        )
        self.plot_widget_sliced.showGrid(x=True, y=True, alpha=0.2)
        self.plot_widget_sliced.hide()
        self.plot_sliced = self.plot_widget_sliced.plot(
            pen=mkPen('k', width=1)
        )
        splitter_widget.addWidget(self.plot_widget_sliced)

        layout.addWidget(splitter_widget)

        self.setLayout(layout)

    def init_vertical_line(self):
        self.vertical_line = pg.InfiniteLine(
            pos=10,
            angle=90,
            movable=True,
            pen=mkPen((6, 21, 191, 150), width=3),
            hoverPen=mkPen((6, 21, 191, 255), width=3),
        )
        self.view.addItem(self.vertical_line)
        self.vertical_line.hide()

        self.vertical_line.sigPositionChanged.connect(
            self.vertical_line_changed
        )

    @pyqtSlot()
    def vertical_line_changed(self):
        if not self.vertical_line.isVisible():
            return
        v_val = int(self.vertical_line.value())
        x_vals = []
        y_vals = []
        for data in self.data:
            x_data = data['curve'][0]
            if v_val < x_data[0] or v_val > x_data[-1]:
                continue
            idx = np.searchsorted(x_data, v_val)
            y_vals.append(data['curve'][1][idx])
            x_vals.append(data['timestamp'].timestamp())
        self.plot_sliced.setData(y=y_vals, x=x_vals)

    def toggle_mode(self, state):
        if state == Qt.Checked:
            self.plot_latest_curve()
            self.legend.hide()
            self.vertical_line.hide()
            self.plot_widget_sliced.hide()
        else:
            self.plot_all_curves()
            if not self.preview_mode:
                self.legend.show()
                self.vertical_line.show()
                self.plot_widget_sliced.show()
                self.vertical_line_changed()

    def toggle_log_mode(self, state):
        log_mode = state == Qt.Checked
        self.plot_widget.setLogMode(y=log_mode)
        self.plot_widget_sliced.setLogMode(y=log_mode)

    def clear_data(self):
        self.data = []
        self.plot_widget.clear()

    def generate_contrasting_color(self):
        color = pg.intColor(np.random.randint(0, 255), alpha=255)
        while color.red() + color.green() + color.blue() < 300:
            color = pg.intColor(np.random.randint(0, 255), alpha=255)
        return color

    def set_data(self, arrays, labels):
        y_data = arrays[0]
        x_data = labels['x']
        if self.data and np.array_equal(y_data, self.data[-1]['curve'][1]):
            return

        color = self.generate_contrasting_color()
        new_data = {
            'curve': (x_data, y_data),
            'timestamp': datetime.now(),
            'color': color,
        }
        self.data.append(new_data)
        self.move_vertical_line_within_bounds(
            lower_bound=x_data[0] + 1, upper_bound=x_data[-1]
        )
        self.data_changed.emit(self.save_state())

        self.mode_changed()

    def move_vertical_line_within_bounds(self, lower_bound, upper_bound):
        v_val = int(self.vertical_line.value())
        if v_val < lower_bound:
            self.vertical_line.setValue(lower_bound)
        elif v_val > upper_bound:
            self.vertical_line.setValue(upper_bound)

    def mode_changed(self):
        if self.mode_checkbox.isChecked():
            self.plot_latest_curve()
        else:
            self.plot_all_curves()

    def plot_latest_curve(self):
        self.plot_widget.clear()
        if self.data:
            latest_data = self.data[-1]
            self.plot_widget.plot(
                x=latest_data['curve'][0],
                y=latest_data['curve'][1],
                pen=mkPen('k'),
                name=latest_data['timestamp'].strftime('%Y/%m/%d, %H:%M:%S'),
            )

    def plot_all_curves(self):
        self.plot_widget.clear()
        for data in self.data:
            self.plot_widget.plot(
                x=data['curve'][0],
                y=data['curve'][1],
                pen=data['color'],
                name=data['timestamp'].strftime('%Y/%m/%d, %H:%M:%S'),
            )
        self.vertical_line_changed()

    def save_state(self):
        return {
            'data': self.data,
            'log_mode': self.log_checkbox.isChecked(),
            'plot_latest': self.mode_checkbox.isChecked(),
            'vertical_line_val': self.vertical_line.value(),
        }

    def restore_state(self, state):
        self.data = state['data']
        self.log_checkbox.setChecked(state['log_mode'])
        self.mode_checkbox.setChecked(state['plot_latest'])
        self.vertical_line.setValue(state['vertical_line_val'])

        if state['plot_latest']:
            self.plot_latest_curve()
        else:
            self.plot_all_curves()

    def mousePressEvent(self, ev):
        self.clicked.emit(self.name)


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [str(datetime.fromtimestamp(value)) for value in values]


class ImageViewController(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.plotwidget = parent
        self.disp_image = None
        self.build_ui()

    def initialize_ui(self):
        self.ui = QVBoxLayout()
        self.setLayout(self.ui)

    def build_hist_settings(self):
        self.hist_max_level_le = QLineEdit()
        self.hist_max_level_le.setText('1')
        self.hist_max_level_le.setMaximumWidth(100)
        self.hist_max_level_le.returnPressed.connect(
            self.update_hist_max_level
        )

        self.hist_min_level_le = QLineEdit()
        self.hist_min_level_le.setText('0')
        self.hist_min_level_le.setMaximumWidth(100)
        self.hist_min_level_le.returnPressed.connect(
            self.update_hist_min_level
        )

        hist_settings_hbox = QHBoxLayout()
        hist_min_level_label = QLabel('Level low')
        hist_settings_hbox.addWidget(
            hist_min_level_label, alignment=Qt.AlignmentFlag.AlignRight
        )
        hist_settings_hbox.addWidget(
            self.hist_min_level_le, alignment=Qt.AlignmentFlag.AlignLeft
        )
        hist_max_level_label = QLabel('Level high')
        hist_settings_hbox.addWidget(
            hist_max_level_label, alignment=Qt.AlignmentFlag.AlignRight
        )
        hist_settings_hbox.addWidget(
            self.hist_max_level_le, alignment=Qt.AlignmentFlag.AlignLeft
        )
        hist_autoscale_btn = QPushButton('Autoscale')
        hist_autoscale_btn.clicked.connect(self.single_shot_autoscale)
        hist_settings_hbox.addWidget(
            hist_autoscale_btn, alignment=Qt.AlignmentFlag.AlignLeft
        )

        return hist_settings_hbox

    def build_ui(self):
        self.initialize_ui()

        hbox = QHBoxLayout()

        self.log_cb = QCheckBox('Logarithmic mode')
        self.log_cb.stateChanged.connect(self.toggle_log_mode)
        hbox.addWidget(self.log_cb)

        self.roi_cb = QCheckBox('Box ROI')
        self.roi_cb.clicked.connect(self.roi_clicked)
        hbox.addWidget(self.roi_cb)

        self.roi_crosshair_cb = QCheckBox('Cross ROI')
        self.roi_crosshair_cb.clicked.connect(self.roi_crosshair_clicked)
        hbox.addWidget(self.roi_crosshair_cb)

        hist_settings = self.build_hist_settings()

        hbox.addLayout(hist_settings)

        self.ui.addLayout(hbox)

    def toggle_log_mode(self, state):
        log_mode = state == Qt.Checked
        self.plotwidget.left_plot.setLogMode(x=log_mode)
        self.plotwidget.bottom_plot.setLogMode(y=log_mode)
        self.plotwidget.toggle_log_mode(log_mode)
        self.plotwidget.update_image()

    def single_shot_autoscale(self):
        self.plotwidget.autolevel_complete = False
        self.plotwidget.update_image(self.disp_image)

    def update_hist_max_level(self):
        hist_min, _ = self.plotwidget.image_item.getLevels()
        self.plotwidget.image_item.setLevels(
            [hist_min, float(self.hist_max_level_le.text())]
        )
        self.plotwidget.settings_histogram.item.imageChanged()

    def update_hist_min_level(self):
        _, hist_max = self.plotwidget.image_item.getLevels()
        self.plotwidget.image_item.setLevels(
            [float(self.hist_min_level_le.text()), hist_max]
        )
        self.plotwidget.settings_histogram.item.imageChanged()

    def roi_clicked(self):
        if self.plotwidget.image_view_controller.roi_cb.isChecked():
            self.plotwidget.show_roi()
        else:
            self.plotwidget.hide_roi()
        self.update_roi_view()

    def roi_crosshair_clicked(self):
        if self.plotwidget.image_view_controller.roi_crosshair_cb.isChecked():
            self.plotwidget.show_crosshair_roi()
        else:
            self.plotwidget.hide_crosshair_roi()
        self.update_roi_view()

    def update_roi_view(self):
        if (
            self.plotwidget.image_view_controller.roi_cb.isChecked() or
            self.plotwidget.image_view_controller.roi_crosshair_cb.isChecked()
        ):
            self.plotwidget.show_roi_plotwidgets()
        else:
            self.plotwidget.hide_roi_plotwidgets()


class CustomImageItem(ImageItem):
    hoverData = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)
        self.hoverData.emit('')

    def hoverEvent(self, event):
        if event.isExit():
            self.hoverData.emit('')  # Clear any previous title
        else:
            pos = event.pos()
            i, j = pos.x(), pos.y()
            i, j = (
                int(np.clip(i, 0, self.image.shape[0] - 1)),
                int(np.clip(j, 0, self.image.shape[1] - 1)),
            )
            value = self.image[i, j]
            self.hoverData.emit(f'Coordinates: ({i}, {j}), Value: {value:.2f}')


class ImageView(QWidget):
    sigTimeChanged = pyqtSignal(object, object)
    sigProcessingChanged = pyqtSignal(object)
    clicked = pyqtSignal(str)

    def __init__(self, parent=None, name='', *args):
        QWidget.__init__(self, parent, *args)
        self.parent = parent
        self.name = name

        self.log = NicosLogger('ImageView')
        self.log.parent = parent.log.parent

        self.saved_roi_state = None
        self.log_mode = False
        self.saved_cm = None
        self.autolevel_complete = False
        self.image = None
        self.axes = {'t': None, 'x': 0, 'y': 1, 'c': None}

        self.initialize_ui()
        self.build_image_controller_tab()
        self.build_main_image_item()
        self.build_rois()
        self.build_histograms()
        self.build_plots()
        self.build_ui()

        self.setup_connections()

    def initialize_ui(self):
        self.ui = QVBoxLayout(self)
        self.hover_label = QLabel(self)
        self.graphics_view = GraphicsView()
        self.scene = self.graphics_view.scene()
        self.view = ViewBox()
        self.view.invertY()
        self.view.setAspectLocked(True)
        self.graphics_view.setCentralItem(self.view)

    def build_image_controller_tab(self):
        self.image_view_controller = ImageViewController(self)

    def build_main_image_item(self):
        self.image_item = CustomImageItem()
        self.image_item.setAutoDownsample(True)
        self.view.addItem(self.image_item)

    def build_rois(self):
        self.crosshair_roi = CrossROI()
        self.crosshair_roi.vertical_line.hide()
        self.crosshair_roi.horizontal_line.hide()
        self.view.addItem(self.crosshair_roi.vertical_line, ignoreBounds=True)
        self.view.addItem(
            self.crosshair_roi.horizontal_line, ignoreBounds=True
        )

        self.roi = PlotROI(
            50,
            pen=mkPen((200, 15, 15, 150), width=4),
            hoverPen=mkPen((200, 15, 15, 255), width=4),
        )
        self.roi.hide()
        self.roi.handles[0]['item'].pen = mkPen((255, 125, 0), width=2)
        self.roi.handles[0]['item'].hoverPen = mkPen((255, 175, 90), width=2)
        self.roi.handles[0]['item'].currentPen = mkPen((255, 125, 0), width=2)
        self.roi.setZValue(20)
        self.view.addItem(self.roi)
        self.saved_roi_state = self.roi.saveState()

    def build_histograms(self):
        self.settings_histogram = HistogramWidget(orientation='horizontal')
        self.settings_histogram.gradient.loadPreset('viridis')
        self.settings_histogram.item.log = self.log
        self.settings_histogram.item.setImageItem(self.image_item)

        self.histogram_image_item = ImageItem()
        self.roi_histogram = HistogramWidget(
            orientation='horizontal', remove_regions=True,
        )
        self.roi_histogram.item.log = self.log
        self.roi_histogram.item.setImageItem(self.histogram_image_item)

    def build_plots(self):
        self.left_plot = PlotWidget()
        self.bottom_plot = PlotWidget()
        self.left_plot.setYLink(self.view)
        self.bottom_plot.setXLink(self.view)

        self.full_vert_trace = self.left_plot.plot(pen=mkPen('k', width=0.5))
        self.left_crosshair_roi = self.left_plot.plot(
            pen=mkPen((6, 21, 191), width=1)
        )
        self.left_roi_trace = self.left_plot.plot(
            pen=mkPen((200, 15, 15), width=1)
        )
        self.left_plot.plotItem.invertY()
        self.left_plot.plotItem.invertX()
        self.left_plot.showGrid(x=True, y=True, alpha=0.2)

        self.full_hori_trace = self.bottom_plot.plot(pen=mkPen('k', width=0.5))
        self.bottom_crosshair_roi = self.bottom_plot.plot(
            pen=mkPen((6, 21, 191), width=1)
        )
        self.bottom_roi_trace = self.bottom_plot.plot(
            pen=mkPen((200, 15, 15), width=1)
        )
        self.bottom_plot.plotItem.invertY()
        self.bottom_plot.showGrid(x=True, y=True, alpha=0.2)

    def build_ui(self):
        self.filler_widget = QFrame()
        self.filler_layout = QVBoxLayout()
        self.filler_layout.addStretch()
        self.filler_widget.setLayout(self.filler_layout)

        self.splitter_vert_1 = QSplitter(Qt.Orientation.Vertical)
        self.splitter_vert_1.addWidget(self.roi_histogram)
        self.splitter_vert_1.addWidget(self.left_plot)
        self.splitter_vert_1.addWidget(self.filler_widget)

        self.splitter_vert_2 = QSplitter(Qt.Orientation.Vertical)
        self.splitter_vert_2.addWidget(self.settings_histogram)
        self.splitter_vert_2.addWidget(self.graphics_view)
        self.splitter_vert_2.addWidget(self.bottom_plot)

        self.splitter_hori_1 = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_hori_1.addWidget(self.splitter_vert_1)
        self.splitter_hori_1.addWidget(self.splitter_vert_2)

        self.splitter_vert_3 = QSplitter(Qt.Orientation.Vertical)
        self.splitter_vert_3.addWidget(self.image_view_controller)
        self.splitter_vert_3.addWidget(self.splitter_hori_1)

        self.splitter_hori_1.setSizes([100, 500])
        self.splitter_vert_1.setSizes([100, 500, 100])
        self.splitter_vert_2.setSizes([100, 500, 100])
        self.splitter_vert_3.setSizes([50, 1000])

        self.ui.addWidget(self.splitter_vert_3)
        self.ui.addWidget(self.hover_label)

        self.setLayout(self.ui)

    def setup_connections(self):
        self.image_item.sigImageChanged.connect(self.update_trace)
        self.image_item.hoverData.connect(self.set_hover_title)
        self.settings_histogram.sigLevelsChanged.connect(
            self.update_hist_levels_text
        )

        self.splitter_vert_1.splitterMoved.connect(
            lambda x: self.splitter_moved(self.splitter_vert_1)
        )
        self.splitter_vert_2.splitterMoved.connect(
            lambda x: self.splitter_moved(self.splitter_vert_2)
        )

    def set_crosshair_roi_visibility(self, visible, ignore_connections=False):
        self.roi_crosshair_active = visible
        self.left_crosshair_roi.setVisible(visible)
        self.bottom_crosshair_roi.setVisible(visible)

        for item in [
            self.left_crosshair_roi,
            self.bottom_crosshair_roi,
            self.crosshair_roi.vertical_line,
            self.crosshair_roi.horizontal_line,
        ]:
            item.setVisible(visible)

        if ignore_connections:
            return

        if visible:
            self.image_item.sigImageChanged.connect(self.crosshair_roi_changed)
            self.crosshair_roi.vertical_line.sigPositionChanged.connect(
                self.crosshair_roi_changed
            )
            self.crosshair_roi.horizontal_line.sigPositionChanged.connect(
                self.crosshair_roi_changed
            )
        else:
            self.image_item.sigImageChanged.disconnect(
                self.crosshair_roi_changed
            )
            self.crosshair_roi.vertical_line.sigPositionChanged.disconnect(
                self.crosshair_roi_changed
            )
            self.crosshair_roi.horizontal_line.sigPositionChanged.disconnect(
                self.crosshair_roi_changed
            )

    def set_roi_visibility(self, visible, ignore_connections=False):
        if visible:
            self.roi.setState(self.saved_roi_state)
        else:
            self.saved_roi_state = self.roi.saveState()
            self.roi.setSize(10)

        for item in [
            self.left_roi_trace,
            self.bottom_roi_trace,
            self.roi,
            self.roi_histogram.item.plot,
        ]:
            item.setVisible(visible)

        if ignore_connections:
            return

        if visible:
            self.roi.sigRegionChanged.connect(self.roi_changed)
            self.image_item.sigImageChanged.connect(self.roi_changed)
        else:
            self.roi.sigRegionChanged.disconnect(self.roi_changed)
            self.image_item.sigImageChanged.disconnect(self.roi_changed)

    def set_roi_plotwidgets_visibility(self, visible):
        for item in [
            self.left_plot,
            self.bottom_plot,
            self.filler_widget,
            self.roi_histogram,
        ]:
            item.setVisible(visible)

        self.left_plot.setMouseEnabled(visible, visible)
        self.bottom_plot.setMouseEnabled(visible, visible)

        if visible and (
            self.image_view_controller.roi_cb.isChecked()
            or self.image_view_controller.roi_crosshair_cb.isChecked()
        ):
            if not self.image_view_controller.roi_cb.isChecked():
                self.roi_histogram.item.plot.hide()
                self.left_roi_trace.hide()
                self.bottom_roi_trace.hide()
            if not self.image_view_controller.roi_crosshair_cb.isChecked():
                self.crosshair_roi.vertical_line.hide()
                self.crosshair_roi.horizontal_line.hide()

    def hide_crosshair_roi(self, ignore_connections=False):
        self.set_crosshair_roi_visibility(False, ignore_connections)

    def show_crosshair_roi(self, ignore_connections=False):
        self.set_crosshair_roi_visibility(True, ignore_connections)

    def hide_roi(self, ignore_connections=False):
        self.set_roi_visibility(False, ignore_connections)

    def show_roi(self, ignore_connections=False):
        self.set_roi_visibility(True, ignore_connections)

    def hide_roi_plotwidgets(self):
        self.set_roi_plotwidgets_visibility(False)

    def show_roi_plotwidgets(self):
        self.set_roi_plotwidgets_visibility(True)

    def mousePressEvent(self, event):
        self.clicked.emit(self.name)

    def toggle_log_mode(self, log_mode):
        self.log_mode = log_mode

        current_cm = self.settings_histogram.item.gradient.colorMap()

        if log_mode:
            self.saved_cm = current_cm
            new_cm = self._create_log_colormap(current_cm)
            self.settings_histogram.item.gradient.setColorMap(new_cm)
        else:
            self._restore_original_colormap()

    def _create_log_colormap(self, current_cm):
        colors = current_cm.getColors(mode='byte')
        pos = current_cm.pos
        new_pos = np.exp(np.linspace(-5, 0, 10))
        new_pos[0], new_pos[-1] = 0.0, 1.0
        new_colors = [
            [int(np.interp(x, pos, c)) for c in zip(*colors)]
            for x in np.linspace(0, 1, 10)
        ]

        return ColorMap(
            np.array(new_pos), np.array(new_colors, dtype=np.ubyte)
        )

    def _restore_original_colormap(self):
        if self.saved_cm is not None:
            self.settings_histogram.item.gradient.setColorMap(self.saved_cm)

    def set_data(self, arrays, labels):
        self.set_image(
            (np.array(arrays[0]).T).astype(np.float64), autoLevels=False,
        )

    def save_state(self):
        return {
            'saved_roi_state': self.roi.saveState(),
            'saved_lut_state': self.settings_histogram.item.gradient.saveState(),
            'saved_levels': self.image_item.getLevels(),
            'saved_cross_roi': (
                self.crosshair_roi.vertical_line.value(),
                self.crosshair_roi.horizontal_line.value(),
            ),
        }

    def restore_state(self, state):
        self.roi.setState(state['saved_roi_state'])
        self.settings_histogram.item.gradient.restoreState(
            state['saved_lut_state']
        )
        self.image_item.setLevels(state['saved_levels'])
        self.crosshair_roi.vertical_line.setValue(state['saved_cross_roi'][0])
        self.crosshair_roi.horizontal_line.setValue(
            state['saved_cross_roi'][1]
        )

    @pyqtSlot(str)
    def set_hover_title(self, title):
        self.hover_label.setText(title)

    @pyqtSlot()
    def update_trace(self):
        hori_y = self.image_item.image.mean(axis=1)
        vert_y = self.image_item.image.mean(axis=0)
        self.full_hori_trace.setData(y=hori_y, x=np.arange(0, len(hori_y)))
        self.full_vert_trace.setData(x=vert_y, y=np.arange(0, len(vert_y)))

    @pyqtSlot()
    def splitter_moved(self, sender):
        receiver = (
            self.splitter_vert_1
            if sender is self.splitter_vert_2
            else self.splitter_vert_2
        )
        receiver.blockSignals(True)
        receiver.setSizes(sender.sizes())
        receiver.blockSignals(False)

    @pyqtSlot()
    def update_hist_levels_text(self):
        hist_min, hist_max = self.image_item.getLevels()
        self.image_view_controller.hist_max_level_le.setText(
            str(round(hist_max, 5))
        )
        self.image_view_controller.hist_min_level_le.setText(
            str(round(hist_min, 5))
        )

    @pyqtSlot()
    def crosshair_roi_changed(self):
        # Extract image data from ROI
        if self.image_item.image is None:
            return

        max_x, max_y = self.image_item.image.shape
        h_val = int(self.crosshair_roi.horizontal_line.value())
        v_val = int(self.crosshair_roi.vertical_line.value())

        slice_point_y = min(max_y - 1, max(0, h_val))
        slice_point_x = min(max_x - 1, max(0, v_val))

        slice_x = self.image_item.image[slice_point_x, :]
        slice_y = self.image_item.image[:, slice_point_y]

        self.left_crosshair_roi.setData(
            y=np.arange(0, len(slice_x)), x=slice_x
        )
        self.bottom_crosshair_roi.setData(
            x=np.arange(0, len(slice_y)), y=slice_y
        )

    @pyqtSlot()
    def roi_changed(self):
        # Extract image data from ROI
        if self.image_item.image is None:
            return

        if self.image_item.axisOrder == 'col-major':
            axes = (self.axes['x'], self.axes['y'])
        else:
            axes = (self.axes['y'], self.axes['x'])

        data, coords = self.roi.getArrayRegion(
            self.image_item.image.view(np.ndarray),
            img=self.image_item,
            axes=axes,
            returnMappedCoords=True,
        )

        if data is None:
            return

        self.histogram_image_item.setImage(data, autoLevels=False)
        self.roi_histogram.item.imageChanged(bins=100)

        data_x = data.mean(axis=self.axes['y'])
        data_y = data.mean(axis=self.axes['x'])

        x_ref, y_ref = np.floor(coords[0][0][0]), np.floor(coords[1][0][0])

        coords_x = coords[:, :, 0] - coords[:, 0:1, 0]
        coords_y = coords[:, 0, :] - coords[:, 0, 0:1]
        xvals = (coords_x ** 2).sum(axis=0) ** 0.5 + x_ref
        yvals = (coords_y ** 2).sum(axis=0) ** 0.5 + y_ref

        self.bottom_roi_trace.setData(x=xvals, y=data_x)
        self.left_roi_trace.setData(y=yvals, x=data_y)

    def set_image(self, image, autoLevels=True, raw_update=True):
        self.image_item.setImage(
            self.get_processed_image(image, raw_update), autoLevels=autoLevels
        )

    def update_image(self, force_image=None):
        if force_image is None:
            use_image = self.raw_image
            raw_update = True
        else:
            use_image = force_image
            raw_update = False
        self.image_item.setImage(
            self.get_processed_image(use_image, raw_update=raw_update),
            autoLevels=False,
        )

    def get_processed_image(self, image, raw_update=True):
        if raw_update:
            self.raw_image = np.copy(image)

        if not self.autolevel_complete:
            flat_im = np.sort(image.flatten())
            ll, hl = int(len(flat_im) * 0.05), int(len(flat_im) * 0.95)
            use_min, use_max = flat_im[[ll, hl]]
            self.image_item.setLevels([use_min, use_max])
            self.autolevel_complete = True
        return image


class LiveDataPanel(Panel):
    panelName = 'Live data view'
    detectorskey = None
    _allowed_detectors = set()
    _liveOnlyIndex = None

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)

        self.plotwidget = ImageView(parent=self)
        self.plotwidget_1d = LineView(parent=self)

        self.initialize_ui()
        self.build_ui()
        self.setup_connections(client)

    def initialize_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

    def build_ui(self):
        self.plotwidget.hide()
        self.plotwidget_1d.hide()
        self.view_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.view_splitter.addWidget(self.plotwidget)
        self.view_splitter.addWidget(self.plotwidget_1d)
        self.view_splitter.setStretchFactor(0, 1)
        self.view_splitter.setStretchFactor(1, 1)
        self.layout().addWidget(self.view_splitter)

        self.plotwidget.hide_roi_plotwidgets()

    def setup_connections(self, client):
        client.livedata.connect(self.on_client_livedata)
        client.connected.connect(self.on_client_connected)

    def normalize_type(self, dtype):
        normalized_type = np.dtype(dtype).str
        if normalized_type not in DATATYPES:
            self.log.warning(
                'Unsupported live data format: %s', normalized_type
            )
            return
        return normalized_type

    def process_data_arrays(self, params, index, entry):
        """
        Check if the input 1D array has the expected amount of values.
        If the array is too small, a warning is raised.
        If the size exceeds the expected amount, it is truncated.
        Returns a list of arrays corresponding to the `plotcount` of
        `index` into `datadescs` of the current params.
        """

        datadesc = params['datadescs'][index]
        count = datadesc.get('plotcount', 1)
        shape = datadesc['shape']

        if self._liveOnlyIndex is not None and index != self._liveOnlyIndex:
            return

        arraysize = np.product(shape)

        if len(entry) != count * arraysize:
            self.log.warning(
                'Expected data array with %d entries, got %d',
                count * arraysize,
                len(entry),
            )
            return

        arrays = [
            entry[i * arraysize : (i + 1) * arraysize].reshape(shape)
            for i in range(count)
        ]

        return arrays

    def _process_livedata(self, params, data, idx, labels):
        # ignore irrelevant data in liveOnly mode
        if self._liveOnlyIndex is not None and idx != self._liveOnlyIndex:
            return
        try:
            descriptions = params['datadescs']
        except KeyError:
            self.log.warning(
                'Livedata with tag "Live" without ' '"datadescs" provided.'
            )
            return

        # pylint: disable=len-as-condition
        if len(data):
            # we got live data with specified formats
            arrays = self.process_data_arrays(
                params, idx, np.frombuffer(data, descriptions[idx]['dtype']),
            )

            if arrays is None:
                return

            # cache and update displays
            if len(arrays[0].shape) == 1:
                if self.plotwidget.isVisible():
                    self.plotwidget.hide()
                if not self.plotwidget_1d.isVisible():
                    self.plotwidget_1d.show()
                self.plotwidget_1d.set_data(arrays, labels)
            else:
                if self.plotwidget_1d.isVisible():
                    self.plotwidget_1d.hide()
                if not self.plotwidget.isVisible():
                    self.plotwidget.show()
                self.plotwidget.set_data(arrays, [])

    def update_widget_to_show(self, is_2d):
        if is_2d:
            if self.plotwidget_1d.isVisible():
                self.plotwidget_1d.hide()
            if not self.plotwidget.isVisible():
                self.plotwidget.show()
        else:
            if self.plotwidget.isVisible():
                self.plotwidget.hide()
            if not self.plotwidget_1d.isVisible():
                self.plotwidget_1d.show()

    def exec_command(self, command):
        self.client.tell('exec', command)

    def on_client_livedata(self, params, blobs):
        self.log.debug('on_client_livedata: %r', params)
        # blobs is a list of data blobs and labels blobs
        if (
            self._allowed_detectors
            and params['det'] not in self._allowed_detectors
        ):
            return

        if params['tag'] == LIVE:
            datacount = len(params['datadescs'])
            for index, datadesc in enumerate(params['datadescs']):
                labels, _ = process_axis_labels(datadesc, blobs[datacount:])
                for i, blob in enumerate(blobs[:datacount]):
                    self._process_livedata(params, blob, index, labels)

                if not datacount:
                    self._process_livedata(params, [], 0, {})

    def on_client_connected(self):
        self.client.tell('eventunmask', ['livedata'])
        self.detectorskey = self._query_detectorskey()

    def _detectorskey(self):
        if self.detectorskey is None:
            self.detectorskey = self._query_detectorskey()
        return self.detectorskey

    def _query_detectorskey(self):
        try:
            return (
                '%s/detlist' % self.client.eval('session.experiment.name')
            ).lower()
        except AttributeError:
            pass


class State(Enum):
    UNSELECTED = 0
    SELECTED = 1


class LiveWidgetWrapper(QGroupBox):
    def __init__(self, title, widget, parent=None):
        QGroupBox.__init__(self, title=title, parent=parent)
        self.state = State.UNSELECTED

        self.setContentsMargins(0, 0, 0, 0)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 5, 0, 0)
        self.setLayout(vbox)
        self.layout().addWidget(widget)

    def widget(self):
        return self.layout().itemAt(0).widget()

    def resizeEvent(self, event):
        # Maintain aspect ratio when resizing
        new_size = QSize(event.size().width(), event.size().width())
        self.resize(new_size)
        self.setMinimumHeight(event.size().width())

    @pyqtProperty(str)
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value.name
        self.refresh_widget()

    def refresh_widget(self):
        """
        Update the widget with a new stylesheet.
        """
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


def layout_iterator(layout):
    return (layout.itemAt(i) for i in range(layout.count()))


def get_detectors_in_layout(layout):
    return [item.widget().name for item in layout_iterator(layout)]


def process_axis_labels(datadesc, blobs, offset=0):
    """Convert the raw axis label descriptions.
    Similar to LiveDataPanel._process_axis_labels, but is flexible in datadesc.
    """
    CLASSIC = {'define': 'classic'}
    labels = {}
    titles = {}
    for size, axis in zip(reversed(datadesc['shape']), AXES):
        # if the 'labels' key does not exist or does not have the right
        # axis key set default to 'classic'.
        label = datadesc.get('labels', {'x': CLASSIC, 'y': CLASSIC}).get(
            axis, CLASSIC
        )
        if label['define'] == 'range':
            start = label.get('start', 0)
            size = label.get('length', 1)
            step = label.get('step', 1)
            end = start + step * size
            labels[axis] = np.arange(start, end, step)
        elif label['define'] == 'array':
            index = label.get('index', 0)
            labels[axis] = np.frombuffer(
                blobs[index], label.get('dtype', '<i4')
            )
        else:
            labels[axis] = np.array(range(size))
        labels[axis] += offset if axis == 'x' else 0
        titles[axis] = label.get('title')

    return labels, titles


def process_data_arrays(index, params, data):
    """Returns a list of arrays corresponding to the ``count`` of
    ``index`` into ``datadescs`` of the current params"""
    datadesc = params['datadescs'][index]
    count = datadesc.get('count', 1)
    shape = datadesc['shape']

    # determine 1D array size
    arraysize = np.product(shape)
    arrays = np.split(data[: count * arraysize], count)

    # reshape every array in the list
    for i, array in enumerate(arrays):
        arrays[i] = array.reshape(shape)
    return arrays


def process_livedata(widget, data, params, labels, idx):
    descriptions = params['datadescs']

    # pylint: disable=len-as-condition
    if len(data):
        arrays = process_data_arrays(
            idx, params, np.frombuffer(data, descriptions[idx]['dtype']),
        )
        if arrays is None:
            return
        widget.set_data(arrays, labels)


class DetContainer:
    """
    Container class for items related to a detector.
    """

    def __init__(self, name):
        self.name = name
        self._params_cache = {}
        self._blobs_cache = []
        self._previews_to_index = {}
        self._blobs_to_index = {}
        self._previews = []

    def add_preview(self, name):
        self._previews_to_index[name] = len(self._previews)
        self._previews.append(name)

    def update_cache(self, params, blobs):
        self._params_cache = params
        self._blobs_cache = blobs

    def update_blobs_to_index(self, name):
        if not self._params_cache:
            return

        self._blobs_to_index[name] = [self._previews_to_index[name]]
        for idx, datadesc in enumerate(self._params_cache['datadescs']):
            transferred_label_count = self._previews_to_index[name]
            for axis in datadesc['labels'].values():
                if axis['define'] != 'classic':
                    transferred_label_count += 1
                    self._blobs_to_index[name].append(transferred_label_count)

    def get_preview_name(self, index):
        return self._previews[index]

    def get_preview_data(self, name):
        self.update_blobs_to_index(name)
        ch = self._previews_to_index[name]
        if self._params_cache and self._blobs_cache:
            params = dict(self._params_cache)
            params['datadescs'] = [params['datadescs'][ch]]
            idx = self._blobs_to_index[name]
            return params, [*self._blobs_cache[idx[0] : idx[-1] + 1]]
        return None, None


class Preview:
    """
    Container class for items related to a preview.
    """

    def __init__(self, name, detector, widget):
        """
        :param name: name of the preview
        :param detector: the detector the preview belongs to
        :param widget: the preview widget.
        """
        self.name = name
        self.detector = detector
        self._widget = widget
        self._savestate = {}

    @property
    def widget(self):
        return self._widget.widget()

    def show(self):
        self._widget.state = State.SELECTED

    def hide(self):
        self._widget.state = State.UNSELECTED


class MultiLiveDataPanel(LiveDataPanel):
    """
    MultiLiveDataPanel is a class that extends the LiveDataPanel to handle
    multiple detectors and previews. It provides functionality for creating
    and managing detector previews, updating and displaying live data, and
    switching between 1D and 2D data views.
    The MultiLiveDataPanel shows all the detectors in a side area.
    Each detector can be set as the one to be displayed in the main plot with a
    click on it.
    Options:
    * ``default_detector`` -- the default detector to be displayed in the main
    widget
    """

    panelName = 'MultidetectorLiveDataView'

    def __init__(self, parent, client, options):
        self._detector_selected = options.get('default_detector', '')
        self._detectors = {}
        self._previews = {}
        self._plotwidget_settings = {}
        LiveDataPanel.__init__(self, parent, client, options)

        self.init_UI()
        self.connect_signals()

    def init_UI(self):
        self.tab_widget = QTabWidget()

        self.scroll_content = QWidget()
        self.scroll_content.setMaximumWidth(250)
        self.scroll_content.setLayout(QVBoxLayout())

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        self.tab_widget.addTab(self.scroll, 'Previews')

        self.view_splitter.addWidget(self.tab_widget)
        self.view_splitter.setSizes([600, 600, 100])
        self.view_splitter.setStretchFactor(0, 1)
        self.view_splitter.setStretchFactor(1, 1)
        self.view_splitter.setStretchFactor(2, 0)

    def connect_signals(self):
        self.connect_disconnected_signal()
        self.connect_setup_signal()
        self.connect_cache_signal()

        self.connect_histogram_signals()
        self.connect_plotwidget_1d_signals()

    def save_plotsettings(self, is_2d):
        widget_name = self.get_widget_name(is_2d)
        if not widget_name:
            return

        plot_settings = self.get_plot_settings(is_2d)
        self._plotwidget_settings[widget_name] = plot_settings

    def restore_plotsettings(self, is_2d):
        widget_name = self.get_widget_name(is_2d)
        if widget_name not in self._plotwidget_settings:
            return

        plot_settings = self._plotwidget_settings[widget_name]
        self.apply_plot_settings(is_2d, plot_settings)

    def apply_plot_settings(self, is_2d, plot_settings):
        if is_2d:
            self.plotwidget.restore_state(plot_settings)
        else:
            pass

    def get_widget_name(self, is_2d):
        if is_2d:
            return self.plotwidget.name
        else:
            return self.plotwidget_1d.name

    def get_plot_settings(self, is_2d):
        if is_2d:
            return self.plotwidget.save_state()
        else:
            return self.plotwidget_1d.save_state()

    def connect_disconnected_signal(self):
        self.client.disconnected.connect(self.on_client_disconnected)

    def connect_setup_signal(self):
        self.client.setup.connect(self.on_client_setup)

    def connect_cache_signal(self):
        self.client.cache.connect(self.on_client_cache)

    def connect_histogram_signals(self):
        self.plotwidget.settings_histogram.item.sigLookupTableChanged.connect(
            self.lut_changed
        )
        self.plotwidget.settings_histogram.item.sigLevelsChanged.connect(
            self.levels_changed
        )

    def connect_plotwidget_1d_signals(self):
        self.plotwidget_1d.clear_button.clicked.connect(self.plot_clear_data)
        self.plotwidget_1d.mode_checkbox.stateChanged.connect(
            self.plot_mode_changed
        )
        self.plotwidget_1d.log_checkbox.stateChanged.connect(
            self.plot_log_mode_changed
        )
        self.plotwidget_1d.vertical_line.sigPositionChangeFinished.connect(
            self.plot_vertical_line_changed
        )

    def update_previews(self, action, widget_name):
        for name, preview in self._previews.items():
            if preview.widget.name == widget_name:
                action(preview)

    def plot_mode_changed(self):
        current_plot_mode = self.plotwidget_1d.mode_checkbox.isChecked()
        action = lambda preview: preview.widget.mode_checkbox.setChecked(
            current_plot_mode
        )
        self.update_previews(action, self.plotwidget_1d.name)

    def plot_clear_data(self):
        action = lambda preview: preview.widget.clear_data()
        self.update_previews(action, self.plotwidget_1d.name)

    def plot_log_mode_changed(self):
        current_log_mode = self.plotwidget_1d.log_checkbox.isChecked()
        action = lambda preview: preview.widget.log_checkbox.setChecked(
            current_log_mode
        )
        self.update_previews(action, self.plotwidget_1d.name)

    def plot_vertical_line_changed(self):
        current_value = self.plotwidget_1d.vertical_line.value()
        action = lambda preview: preview.widget.vertical_line.setValue(
            current_value
        )
        self.update_previews(action, self.plotwidget_1d.name)

    def lut_changed(self):
        current_gradient_state = (
            self.plotwidget.settings_histogram.item.gradient.saveState()
        )
        action = lambda preview: \
            preview.widget.settings_histogram.item.gradient.restoreState(
                current_gradient_state
            )
        self.update_previews(action, self.plotwidget.name)

    def levels_changed(self):
        current_image_levels = self.plotwidget.image_item.getLevels()
        action = lambda preview: preview.widget.image_item.setLevels(
            current_image_levels
        )
        self.update_previews(action, self.plotwidget.name)

    def on_1d_data_changed(self, state):
        self.plotwidget_1d.clear_data()
        self.plotwidget_1d.restore_state(state)

    def on_client_connected(self):
        LiveDataPanel.on_client_connected(self)
        self._cleanup_existing_previews()
        if not self._previews:
            self._populate_previews()

    def on_client_disconnected(self):
        self._cleanup_existing_previews()

    def _cleanup_existing_previews(self):
        for item in layout_iterator(self.scroll_content.layout()):
            item.widget().deleteLater()
            del item
        self._previews.clear()
        self._detectors.clear()

    def create_previews_for_detector(self, det_name):
        previews = self.create_preview_widgets(det_name)
        self.add_previews_to_layout(previews, det_name)

    def add_previews_to_layout(self, previews, det_name):
        for preview in previews:
            name = preview.widget().name
            self._previews[name] = Preview(name, det_name, preview)
            self._detectors[det_name].add_preview(name)
            preview.widget().clicked.connect(self.on_preview_clicked)
            self.scroll_content.layout().addWidget(preview)

    def on_client_setup(self):
        self._cleanup_existing_previews()
        if not self._previews:
            self._populate_previews()

    def highlight_selected_preview(self, selected):
        for name, preview in self._previews.items():
            if name == selected:
                preview.show()
            else:
                preview.hide()

    def _populate_previews(self):
        detectors = set(self.find_detectors())
        if not detectors:
            return
        self.add_detectors_to_previews(detectors)
        self._display_first_detector()

    def add_detectors_to_previews(self, detectors):
        for detector in detectors:
            self._detectors[detector] = DetContainer(detector)
            self.create_previews_for_detector(detector)

    def _display_first_detector(self):
        if self._previews:
            first_preview = next(iter(self._previews.values()))
            self.display_preview(first_preview)

    def display_preview(self, preview):
        preview.widget.clicked.emit(preview.name)
        if isinstance(preview.widget, LineView):
            self.plotwidget_1d.name = preview.name
        elif isinstance(preview.widget, ImageView):
            self.plotwidget.name = preview.name

    def on_client_cache(self, data):
        _, key, _, _ = data
        if key == 'exp/detlist':
            self._cleanup_existing_previews()

    def on_client_livedata(self, params, blobs):
        det_name = params['det']

        if not self._previews:
            self._populate_previews()

        self.set_preview_data(params, blobs)
        self.update_selected_main_widget(det_name)

    def update_selected_main_widget(self, det_name):
        if (
            not self._detector_selected
            or self._detector_selected not in self._previews
        ):
            return

        if self._previews[self._detector_selected].detector == det_name:
            pars, blob = self._detectors[det_name].get_preview_data(
                self._detector_selected
            )
            LiveDataPanel.on_client_livedata(self, pars, blob)

    def find_detectors(self):
        return self._get_configured_detectors()

    def _get_configured_detectors(self):
        state = self.client.ask('getstatus')
        if not state:
            return []
        detlist = self.client.getCacheKey('exp/detlist')
        if not detlist:
            return []
        return [
            det
            for det in detlist[1]
            if self.client.eval(f'{det}.arrayInfo()', [])
        ]

    def create_preview_widgets(self, det_name):
        array_info = self.client.eval(f'{det_name}.arrayInfo()', ())
        previews = [self._create_preview_widget(info) for info in array_info]
        return previews

    def _create_preview_widget(self, info):
        if len(info.shape) == 1:
            return self._create_line_view_preview_widget(info)
        else:
            return self._create_image_view_preview_widget(info)

    def _create_line_view_preview_widget(self, info):
        widget = LineView(name=info.name, parent=self, preview_mode=True)
        widget.view.setMouseEnabled(False, False)
        widget.plot_widget.getPlotItem().hideAxis('bottom')
        widget.plot_widget.getPlotItem().hideAxis('left')
        widget.plot_widget_sliced.hide()
        widget.data_changed.connect(self.on_1d_data_changed)
        return LiveWidgetWrapper(title=info.name, widget=widget)

    def _create_image_view_preview_widget(self, info):
        widget = ImageView(name=info.name, parent=self)
        widget.view.setMouseEnabled(False, False)
        widget.splitter_hori_1.setHandleWidth(0)
        widget.image_view_controller.hide()
        widget.settings_histogram.hide()
        widget.hover_label.hide()
        widget.hide_roi(ignore_connections=True)
        widget.hide_crosshair_roi(ignore_connections=True)
        widget.hide_roi_plotwidgets()
        return LiveWidgetWrapper(title=info.name, widget=widget)

    def set_preview_data(self, params, blobs):
        self._update_and_process_preview_data(params, blobs)

    def _update_and_process_preview_data(self, params, blobs):
        parent = params['det']
        self._detectors[parent].update_cache(params, blobs)
        datacount = len(params['datadescs'])

        for index, datadesc in enumerate(params['datadescs']):
            normalized_type = self.normalize_type(datadesc['dtype'])
            name = self._detectors[parent].get_preview_name(index)
            widget = self._previews[name].widget
            labels, _ = process_axis_labels(datadesc, blobs[datacount:])
            if self._has_plot_changed_dimensionality(widget, labels):
                self._cleanup_existing_previews()
                return
            process_livedata(
                widget,
                np.frombuffer(blobs[index], normalized_type),
                params,
                labels,
                index,
            )

    def _has_plot_changed_dimensionality(self, widget, labels):
        return (isinstance(widget, LineView) and 'y' in labels) or (
            not isinstance(widget, LineView) and 'y' not in labels
        )

    def on_preview_clicked(self, det_name):
        self._change_detector_to_display(det_name)

    def _change_detector_to_display(self, det_name):
        self._detector_selected = det_name
        parent = self._previews[det_name].detector
        pars, blob = self._detectors[parent].get_preview_data(
            self._detector_selected
        )
        is_2d = isinstance(self._previews[det_name].widget, ImageView)
        switched_plot = self._check_switched_plot(det_name, is_2d)

        self.save_plotsettings(is_2d=is_2d)
        self._update_plot_widget_name(det_name, is_2d)
        if switched_plot:
            self._handle_switched_plot(det_name, is_2d, pars, blob)

        self.highlight_selected_preview(det_name)

    def _check_switched_plot(self, det_name, is_2d):
        if self.plotwidget.isVisible() and not is_2d:
            return True
        elif self.plotwidget_1d.isVisible() and is_2d:
            return True
        elif is_2d:
            return det_name != self.plotwidget.name
        else:
            return det_name != self.plotwidget_1d.name

    def _update_plot_widget_name(self, det_name, is_2d):
        if is_2d:
            self.plotwidget.view.enableAutoRange()
            self.plotwidget.name = det_name
        else:
            self.plotwidget_1d.view.enableAutoRange()
            self.plotwidget_1d.name = det_name

    def _handle_switched_plot(self, det_name, is_2d, pars, blob):
        self.restore_plotsettings(is_2d=is_2d)
        if is_2d:
            if pars and blob:
                LiveDataPanel.on_client_livedata(self, pars, blob)
        else:
            self.plotwidget_1d.clear_data()
            preview_state = self._previews[det_name].widget.save_state()
            self.plotwidget_1d.restore_state(preview_state)
            LiveDataPanel.update_widget_to_show(self, is_2d=is_2d)

    def on_closed(self):
        self._clear_previews()
        LiveDataPanel.on_closed(self)

    def _clear_previews(self):
        for item in layout_iterator(self.scroll_content.layout()):
            item.widget().deleteLater()
            del item

    def on_closed(self):
        self._clear_previews()
        LiveDataPanel.on_closed(self)

    def _clear_previews(self):
        for item in layout_iterator(self.scroll_content.layout()):
            item.widget().deleteLater()
            del item
