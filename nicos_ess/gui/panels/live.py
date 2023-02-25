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

from enum import Enum

import numpy as np
import pyqtgraph as pg
from pyqtgraph import AxisItem, GraphicsView, HistogramLUTItem, ImageItem, \
    PlotWidget, ViewBox, mkPen
from pyqtgraph.graphicsItems.ROI import ROI

from nicos.clients.gui.panels import Panel
from nicos.core.constants import LIVE
from nicos.guisupport.livewidget import AXES, DATATYPES
from nicos.guisupport.qt import QFrame, QGroupBox, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QScrollArea, QSize, QSizePolicy, QSplitter, Qt, \
    QTabWidget, QVBoxLayout, QWidget, pyqtProperty, pyqtSignal, pyqtSlot
from nicos.utils.loggers import NicosLogger

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")
pg.setConfigOptions(antialias=True)


class HistogramItem(HistogramLUTItem):
    def __init__(
        self,
        image=None,
        fillHistogram=True,
        levelMode="mono",
        gradientPosition="right",
        orientation="vertical",
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
            "bottom", linkView=self.vb, maxTickLength=-10, parent=self
        )
        self.axis_2 = AxisItem(
            "left", linkView=self.vb, maxTickLength=-30, parent=self
        )
        self.layout.addItem(self.axis_2, 0, 0)
        self.layout.addItem(self.vb, 0, 1)
        self.layout.addItem(self.axis, 1, 1)
        self.layout.addItem(self.gradient, 2, 1)

        self.vb.setMaximumHeight(1000)

    def imageChanged(self, autoLevel=False, autoRange=False, bins=None):
        if self.imageItem() is None:
            return

        if self.levelMode != "mono":
            self.log.error("Only mono images are supported")
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
        background = kargs.pop("background", "default")
        GraphicsView.__init__(
            self, parent, useOpenGL=False, background=background
        )
        self.item = HistogramItem(*args, **kargs)
        self.setCentralItem(self.item)

        self.orientation = kargs.get("orientation", "vertical")
        if self.orientation == "vertical":
            self.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Expanding,
            )
            self.setMinimumWidth(95)
        else:
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred,
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
            self,
            pos=[0, 0],
            size=size,
            rotatable=False,
            *args,
            **kwargs,
        )
        self.addScaleHandle([1, 1], [0, 0])


class CrossROI:
    def __init__(self):
        pen = mkPen((6, 21, 191, 150), width=3)
        hover_pen = mkPen((6, 21, 191, 255), width=3)
        self.vertical_line = pg.InfiniteLine(
            pos=10,
            angle=90,
            movable=True,
            pen=pen,
            hoverPen=hover_pen,
        )
        self.horizontal_line = pg.InfiniteLine(
            pos=10, angle=0, movable=True, pen=pen, hoverPen=hover_pen
        )


class LineView(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, parent=None, name="", *args):
        QWidget.__init__(self, parent, *args)
        self.name = name
        self.setMinimumSize(150, 150)

        self.ui = QHBoxLayout(self)
        self.plot = PlotWidget()
        self.plotItem = self.plot.plot(pen=mkPen("k", width=2))
        self.plot.showGrid(x=True, y=True, alpha=0.2)
        self.view = self.plot.getViewBox()
        self.ui.addWidget(self.plot)
        self.setLayout(self.ui)

    def set_data(self, arrays, labels):
        self.plotItem.setData(y=arrays[0], x=np.arange(0, len(arrays[0])))

    def mousePressEvent(self, ev):
        self.clicked.emit(self.name)


class ImageViewController(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.plotwidget = parent
        self.build_ui()

    def initialize_ui(self):
        self.ui = QVBoxLayout()
        self.setLayout(self.ui)

    def build_hist_frame(self):
        self.hist_frame = QFrame()
        self.hist_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        self.hist_max_level_le = QLineEdit()
        self.hist_max_level_le.setText("1")
        self.hist_max_level_le.setMaximumWidth(100)
        self.hist_max_level_le.returnPressed.connect(
            self.update_hist_max_level
        )

        self.hist_min_level_le = QLineEdit()
        self.hist_min_level_le.setText("0")
        self.hist_min_level_le.setMaximumWidth(100)
        self.hist_min_level_le.returnPressed.connect(
            self.update_hist_min_level
        )

        hist_settings_hbox = QHBoxLayout()
        hist_min_level_label = QLabel("Level low")
        hist_settings_hbox.addWidget(
            hist_min_level_label, alignment=Qt.AlignRight
        )
        hist_settings_hbox.addWidget(
            self.hist_min_level_le, alignment=Qt.AlignLeft
        )
        hist_max_level_label = QLabel("Level high")
        hist_settings_hbox.addWidget(
            hist_max_level_label, alignment=Qt.AlignRight
        )
        hist_settings_hbox.addWidget(
            self.hist_max_level_le, alignment=Qt.AlignLeft
        )
        hist_autoscale_btn = QPushButton("Autoscale")
        hist_autoscale_btn.clicked.connect(self.single_shot_autoscale)
        hist_settings_hbox.addWidget(
            hist_autoscale_btn, alignment=Qt.AlignLeft
        )

        self.hist_frame.setLayout(hist_settings_hbox)

    def build_ui(self):
        self.initialize_ui()
        self.build_hist_frame()

        hbox = QHBoxLayout()

        roi_btn = QPushButton("Box ROI")
        roi_btn.clicked.connect(self.roi_clicked)
        hbox.addWidget(roi_btn)

        roi_crosshair_btn = QPushButton("Cross ROI")
        roi_crosshair_btn.clicked.connect(self.roi_crosshair_clicked)
        hbox.addWidget(roi_crosshair_btn)

        hbox.addWidget(self.hist_frame)

        self.ui.addLayout(hbox)

    def single_shot_autoscale(self):
        self.plotwidget.autolevel_complete = False
        self.plotwidget.update_image()

    def update_hist_max_level(self):
        self.plotwidget.settings_histogram.sigLevelsChanged.disconnect(
            self.plotwidget.update_hist_levels_text
        )
        hist_min, _ = self.plotwidget.image_item.getLevels()
        self.plotwidget.image_item.setLevels(
            [hist_min, float(self.hist_max_level_le.text())]
        )
        self.plotwidget.settings_histogram.sigLevelsChanged.connect(
            self.plotwidget.update_hist_levels_text
        )

    def update_hist_min_level(self):
        self.plotwidget.settings_histogram.sigLevelsChanged.disconnect(
            self.plotwidget.update_hist_levels_text
        )
        _, hist_max = self.plotwidget.image_item.getLevels()
        self.plotwidget.image_item.setLevels(
            [float(self.hist_min_level_le.text()), hist_max]
        )
        self.plotwidget.settings_histogram.sigLevelsChanged.connect(
            self.plotwidget.update_hist_levels_text
        )

    def roi_clicked(self):
        if self.plotwidget.roi_active:
            self.plotwidget.hide_roi()
        else:
            self.plotwidget.show_roi()
        self.update_roi_view()

    def roi_crosshair_clicked(self):
        if self.plotwidget.roi_crosshair_active:
            self.plotwidget.hide_crosshair_roi()
        else:
            self.plotwidget.show_crosshair_roi()
        self.update_roi_view()

    def update_roi_view(self):
        if self.plotwidget.roi_crosshair_active or self.plotwidget.roi_active:
            self.plotwidget.show_roi_plotwidgets()
        else:
            self.plotwidget.hide_roi_plotwidgets()


class ImageView(QWidget):
    sigTimeChanged = pyqtSignal(object, object)
    sigProcessingChanged = pyqtSignal(object)
    clicked = pyqtSignal(str)

    def __init__(self, parent=None, name="", *args):
        QWidget.__init__(self, parent, *args)
        self.parent = parent
        self.name = name

        self.log = NicosLogger("ImageView")
        self.log.parent = parent.log.parent

        self.roi_active = False
        self.roi_crosshair_active = False
        self.saved_roi_state = None
        self.autolevel_complete = False
        self.image = None
        self.axes = {"t": None, "x": 0, "y": 1, "c": None}

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
        self.graphics_view = GraphicsView()
        self.scene = self.graphics_view.scene()
        self.view = ViewBox()
        self.view.invertY()
        self.view.setAspectLocked(True)
        self.graphics_view.setCentralItem(self.view)

    def build_image_controller_tab(self):
        self.image_view_controller = ImageViewController(self)

    def build_main_image_item(self):
        self.image_item = ImageItem()
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
        self.roi.handles[0]["item"].pen = mkPen((255, 125, 0), width=2)
        self.roi.handles[0]["item"].hoverPen = mkPen((255, 175, 90), width=2)
        self.roi.handles[0]["item"].currentPen = mkPen((255, 125, 0), width=2)
        self.roi.setZValue(20)
        self.view.addItem(self.roi)
        self.saved_roi_state = self.roi.saveState()

    def build_histograms(self):
        self.settings_histogram = HistogramWidget(
            orientation="horizontal"
        )
        self.settings_histogram.gradient.loadPreset("viridis")
        self.settings_histogram.item.log = self.log
        self.settings_histogram.item.setImageItem(self.image_item)

        self.histogram_image_item = ImageItem()
        self.roi_histogram = HistogramWidget(
            orientation="horizontal",
            remove_regions=True,
        )
        self.roi_histogram.item.log = self.log
        self.roi_histogram.item.setImageItem(self.histogram_image_item)

    def build_plots(self):
        self.left_plot = PlotWidget()
        self.bottom_plot = PlotWidget()
        self.left_plot.setYLink(self.view)
        self.bottom_plot.setXLink(self.view)

        self.full_vert_trace = self.left_plot.plot(pen=mkPen("k", width=0.5))
        self.left_crosshair_roi = self.left_plot.plot(
            pen=mkPen((6, 21, 191), width=1)
        )
        self.left_roi_trace = self.left_plot.plot(pen=mkPen((200, 15, 15), width=2))
        self.left_plot.plotItem.invertY()
        self.left_plot.plotItem.invertX()
        self.left_plot.showGrid(x=True, y=True, alpha=0.2)

        self.full_hori_trace = self.bottom_plot.plot(pen=mkPen("k", width=0.5))
        self.bottom_crosshair_roi = self.bottom_plot.plot(
            pen=mkPen((6, 21, 191), width=1)
        )
        self.bottom_roi_trace = self.bottom_plot.plot(
            pen=mkPen((200, 15, 15), width=2)
        )
        self.bottom_plot.plotItem.invertY()
        self.bottom_plot.showGrid(x=True, y=True, alpha=0.2)

    def build_ui(self):
        self.filler_widget = QFrame()
        self.filler_layout = QVBoxLayout()
        self.filler_layout.addStretch()
        self.filler_widget.setLayout(self.filler_layout)

        self.splitter_vert_1 = QSplitter(Qt.Vertical)
        self.splitter_vert_1.addWidget(self.roi_histogram)
        self.splitter_vert_1.addWidget(self.left_plot)
        self.splitter_vert_1.addWidget(self.filler_widget)

        self.splitter_vert_2 = QSplitter(Qt.Vertical)
        self.splitter_vert_2.addWidget(self.settings_histogram)
        self.splitter_vert_2.addWidget(self.graphics_view)
        self.splitter_vert_2.addWidget(self.bottom_plot)

        self.splitter_hori_1 = QSplitter(Qt.Horizontal)
        self.splitter_hori_1.addWidget(self.splitter_vert_1)
        self.splitter_hori_1.addWidget(self.splitter_vert_2)

        self.splitter_vert_3 = QSplitter(Qt.Vertical)
        self.splitter_vert_3.addWidget(self.image_view_controller)
        self.splitter_vert_3.addWidget(self.splitter_hori_1)

        self.splitter_hori_1.setSizes([100, 500])
        self.splitter_vert_1.setSizes([100, 500, 100])
        self.splitter_vert_2.setSizes([100, 500, 100])
        self.splitter_vert_3.setSizes([50, 1000])

        self.ui.addWidget(self.splitter_vert_3)

        self.setLayout(self.ui)

    def setup_connections(self):
        self.image_item.sigImageChanged.connect(self.update_trace)
        self.settings_histogram.sigLevelsChanged.connect(
            self.update_hist_levels_text
        )

        self.splitter_vert_1.splitterMoved.connect(
            lambda x: self.splitter_moved(self.splitter_vert_1)
        )
        self.splitter_vert_2.splitterMoved.connect(
            lambda x: self.splitter_moved(self.splitter_vert_2)
        )

    def hide_crosshair_roi(self, ignore_connections=False):
        self.roi_crosshair_active = False
        self.left_crosshair_roi.setVisible(False)
        self.bottom_crosshair_roi.setVisible(False)
        self.left_crosshair_roi.hide()
        self.bottom_crosshair_roi.hide()
        self.crosshair_roi.vertical_line.hide()
        self.crosshair_roi.horizontal_line.hide()
        if ignore_connections:
            return
        self.image_item.sigImageChanged.disconnect(self.crosshair_roi_changed)
        self.crosshair_roi.vertical_line.sigPositionChanged.disconnect(
            self.crosshair_roi_changed
        )
        self.crosshair_roi.horizontal_line.sigPositionChanged.disconnect(
            self.crosshair_roi_changed
        )

    def show_crosshair_roi(self, ignore_connections=False):
        self.roi_crosshair_active = True
        self.left_crosshair_roi.setVisible(True)
        self.bottom_crosshair_roi.setVisible(True)
        self.left_crosshair_roi.show()
        self.bottom_crosshair_roi.show()
        self.crosshair_roi.vertical_line.show()
        self.crosshair_roi.horizontal_line.show()
        if ignore_connections:
            return
        self.image_item.sigImageChanged.connect(self.crosshair_roi_changed)
        self.crosshair_roi.vertical_line.sigPositionChanged.connect(
            self.crosshair_roi_changed
        )
        self.crosshair_roi.horizontal_line.sigPositionChanged.connect(
            self.crosshair_roi_changed
        )

    def hide_roi(self, ignore_connections=False):
        self.roi_active = False
        self.saved_roi_state = self.roi.saveState()
        self.roi.setSize(10)
        self.left_roi_trace.setVisible(False)
        self.bottom_roi_trace.setVisible(False)
        self.left_roi_trace.hide()
        self.bottom_roi_trace.hide()
        self.roi.hide()
        self.roi_histogram.item.plot.hide()
        if ignore_connections:
            return
        self.roi.sigRegionChanged.disconnect(self.roi_changed)
        self.image_item.sigImageChanged.disconnect(self.roi_changed)

    def show_roi(self, ignore_connections=False):
        self.roi_active = True
        self.roi.setState(self.saved_roi_state)
        self.left_roi_trace.setVisible(True)
        self.bottom_roi_trace.setVisible(True)
        self.left_roi_trace.show()
        self.bottom_roi_trace.show()
        self.roi.show()
        self.roi_histogram.item.plot.show()
        if ignore_connections:
            return
        self.roi.sigRegionChanged.connect(self.roi_changed)
        self.image_item.sigImageChanged.connect(self.roi_changed)

    def show_roi_plotwidgets(self):
        if self.roi_active or self.roi_crosshair_active:
            self.left_plot.setMouseEnabled(True, True)
            self.bottom_plot.setMouseEnabled(True, True)
            self.left_plot.show()
            self.bottom_plot.show()
            self.filler_widget.show()
            self.roi_histogram.show()

        if self.roi_crosshair_active and not self.roi_active:
            self.roi_histogram.item.plot.hide()
            self.left_roi_trace.hide()
            self.bottom_roi_trace.hide()
        elif self.roi_crosshair_active and not self.roi_active:
            self.crosshair_roi.vertical_line.hide()
            self.crosshair_roi.horizontal_line.hide()

    def hide_roi_plotwidgets(self):
        self.left_plot.setMouseEnabled(False, False)
        self.bottom_plot.setMouseEnabled(False, False)
        self.left_plot.hide()
        self.bottom_plot.hide()
        self.filler_widget.hide()
        self.roi_histogram.hide()

    def mousePressEvent(self, event):
        self.clicked.emit(self.name)

    def set_data(self, arrays, labels):
        self.set_image(
            (np.flipud(np.array(arrays[0])).T).astype(np.float64),
            autoLevels=False,
        )

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
        slice_point_y = min([max_y - 1, max([0, h_val])])
        slice_point_x = min([max_x - 1, max([0, v_val])])

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

        if self.image_item.axisOrder == "col-major":
            axes = (self.axes["x"], self.axes["y"])
        else:
            axes = (self.axes["y"], self.axes["x"])

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

        data_x = data.mean(axis=self.axes["y"])
        data_y = data.mean(axis=self.axes["x"])

        x_ref, y_ref = np.floor(coords[0][0][0]), np.floor(coords[1][0][0])

        coords_x = coords[:, :, 0] - coords[:, 0:1, 0]
        coords_y = coords[:, 0, :] - coords[:, 0, 0:1]
        xvals = (coords_x**2).sum(axis=0) ** 0.5 + x_ref
        yvals = (coords_y**2).sum(axis=0) ** 0.5 + y_ref

        self.bottom_roi_trace.setData(x=xvals, y=data_x)
        self.left_roi_trace.setData(y=yvals, x=data_y)

    def set_image(self, image, autoLevels=True):
        self.image_item.setImage(
            self.get_processed_image(image), autoLevels=autoLevels
        )

    def update_image(self):
        self.image_item.setImage(
            self.get_processed_image(self.raw_image), autoLevels=False
        )

    def get_processed_image(self, image):
        """Returns the image data after it has been processed by any normalization options in use."""
        self.raw_image = np.copy(image)

        if not self.autolevel_complete:
            flat_im = np.sort(image.flatten())
            ll, hl = int(len(flat_im) * 0.05), int(len(flat_im) * 0.95)
            use_min, use_max = flat_im[[ll, hl]]
            self.image_item.setLevels([use_min, use_max])
            self.autolevel_complete = True
        return image


class LiveDataPanel(Panel):
    panelName = "Live data view"
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
        self.view_splitter = QSplitter(Qt.Horizontal)

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
                "Unsupported live data format: %s", normalized_type
            )
            return
        return normalized_type

    def process_data_arrays(self, params, index, entry):
        """Check if the input 1D array has the expected amount of values.
        If the array is too small an Error is raised.
        If the size exceeds the expected amount it is truncated.

        Returns a list of arrays corresponding to the ``plotcount`` of
        ``index`` into ``datadescs`` of the current params"""

        datadesc = params["datadescs"][index]

        # representing the number of arrays with 'shape', in particular size
        # || shape ||
        count = datadesc.get("plotcount", 1)
        shape = datadesc["shape"]

        # ignore irrelevant data in liveOnly mode
        if self._liveOnlyIndex is not None and index != self._liveOnlyIndex:
            return

        # determine 1D array size
        arraysize = np.product(shape)

        # check and split the input array `entry` into `count` arrays of size
        # `arraysize`
        if len(entry) != count * arraysize:
            self.log.warning(
                "Expected data array with %d entries, got %d",
                count * arraysize,
                len(entry),
            )
            return
        arrays = np.split(entry, count)

        # reshape every array in the list
        for i, array in enumerate(arrays):
            arrays[i] = array.reshape(shape)
        return arrays

    def _process_livedata(self, params, data, idx):
        # ignore irrelevant data in liveOnly mode
        if self._liveOnlyIndex is not None and idx != self._liveOnlyIndex:
            return
        try:
            descriptions = params["datadescs"]
        except KeyError:
            self.log.warning(
                'Livedata with tag "Live" without ' '"datadescs" provided.'
            )
            return

        # pylint: disable=len-as-condition
        if len(data):
            # we got live data with specified formats
            arrays = self.process_data_arrays(
                params,
                idx,
                np.frombuffer(data, descriptions[idx]["dtype"]),
            )

            if arrays is None:
                return

            # cache and update displays
            if len(arrays[0].shape) == 1:
                if self.plotwidget.isVisible():
                    self.plotwidget.hide()
                if not self.plotwidget_1d.isVisible():
                    self.plotwidget_1d.show()
                self.plotwidget_1d.set_data(arrays, [])
            else:
                if self.plotwidget_1d.isVisible():
                    self.plotwidget_1d.hide()
                if not self.plotwidget.isVisible():
                    self.plotwidget.show()
                self.plotwidget.set_data(arrays, [])

    def on_client_livedata(self, params, blobs):
        self.log.debug("on_client_livedata: %r", params)
        # blobs is a list of data blobs and labels blobs
        if (
            self._allowed_detectors
            and params["det"] not in self._allowed_detectors
        ):
            return

        if params["tag"] == LIVE:
            datacount = len(params["datadescs"])
            for i, blob in enumerate(blobs[:datacount]):
                self._process_livedata(params, blob, i)

            if not datacount:
                self._process_livedata(params, [], 0)

    def on_client_connected(self):
        self.client.tell("eventunmask", ["livedata"])
        self.detectorskey = self._query_detectorskey()

    def _detectorskey(self):
        if self.detectorskey is None:
            self.detectorskey = self._query_detectorskey()
        return self.detectorskey

    def _query_detectorskey(self):
        try:
            return (
                "%s/detlist" % self.client.eval("session.experiment.name")
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
    CLASSIC = {"define": "classic"}
    labels = {}
    titles = {}
    for size, axis in zip(reversed(datadesc["shape"]), AXES):
        # if the 'labels' key does not exist or does not have the right
        # axis key set default to 'classic'.
        label = datadesc.get("labels", {"x": CLASSIC, "y": CLASSIC}).get(
            axis, CLASSIC
        )

        if label["define"] == "range":
            start = label.get("start", 0)
            size = label.get("length", 1)
            step = label.get("step", 1)
            end = start + step * size
            labels[axis] = np.arange(start, end, step)
        elif label["define"] == "array":
            index = label.get("index", 0)
            labels[axis] = np.frombuffer(
                blobs[index], label.get("dtype", "<i4")
            )
        else:
            labels[axis] = np.array(range(size))
        labels[axis] += offset if axis == "x" else 0
        titles[axis] = label.get("title")

    return labels, titles


def process_data_arrays(index, params, data):
    """Returns a list of arrays corresponding to the ``count`` of
    ``index`` into ``datadescs`` of the current params"""
    datadesc = params["datadescs"][index]
    count = datadesc.get("count", 1)
    shape = datadesc["shape"]

    # determine 1D array size
    arraysize = np.product(shape)
    arrays = np.split(data[: count * arraysize], count)

    # reshape every array in the list
    for i, array in enumerate(arrays):
        arrays[i] = array.reshape(shape)
    return arrays


def process_livedata(widget, data, params, labels, idx):
    descriptions = params["datadescs"]

    # pylint: disable=len-as-condition
    if len(data):
        arrays = process_data_arrays(
            idx,
            params,
            np.frombuffer(data, descriptions[idx]["dtype"]),
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
        self._previews = []

    def add_preview(self, name):
        self._previews_to_index[name] = len(self._previews)
        self._previews.append(name)

    def update_cache(self, params, blobs):
        self._params_cache = params
        self._blobs_cache = blobs

    def get_preview_name(self, index):
        return self._previews[index]

    def get_preview_data(self, name):
        ch = self._previews_to_index[name]
        if self._params_cache and self._blobs_cache:
            params = dict(self._params_cache)
            params["datadescs"] = [params["datadescs"][ch]]
            return params, [self._blobs_cache[ch]]
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
    Implements a LiveDataPanel that shows all the detectors in a side area.
    Each detector can be set as the one to be displayed in the main plot with a
    click on it.

    Options:

    * ``default_detector`` -- the default detector to be displayed in the main
    widget
    """

    panelName = "MultidetectorLiveDataView"

    def __init__(self, parent, client, options):
        self._detector_selected = options.get("default_detector", "")
        self._detectors = {}
        self._previews = {}
        self._plotwidget_settings = {}
        LiveDataPanel.__init__(self, parent, client, options)

        self.tab_widget = QTabWidget()

        self.scroll_content = QWidget()
        self.scroll_content.setMaximumWidth(250)
        self.scroll_content.setLayout(QVBoxLayout())

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        self.tab_widget.addTab(self.scroll, "Previews")

        self.view_splitter.addWidget(self.tab_widget)
        self.view_splitter.setSizes([600, 600, 100])
        self.view_splitter.setStretchFactor(0, 1)
        self.view_splitter.setStretchFactor(1, 1)
        self.view_splitter.setStretchFactor(2, 0)

        client.disconnected.connect(self.on_client_disconnected)
        client.setup.connect(self.on_client_setup)
        client.cache.connect(self.on_client_cache)
        self.plotwidget.settings_histogram.item.sigLookupTableChanged.connect(
            self.lut_changed
        )
        self.plotwidget.settings_histogram.item.sigLevelsChanged.connect(
            self.levels_changed
        )

    def save_plotsettings(self, is_2d):
        if self.plotwidget.name == "":
            return

        self._plotwidget_settings[self.plotwidget.name] = {}
        if is_2d:
            self._plotwidget_settings[self.plotwidget.name][
                "saved_roi_state"
            ] = self.plotwidget.roi.saveState()
            self._plotwidget_settings[self.plotwidget.name][
                "saved_lut_state"
            ] = self.plotwidget.settings_histogram.item.gradient.saveState()
            self._plotwidget_settings[self.plotwidget.name][
                "saved_levels"
            ] = self.plotwidget.image_item.getLevels()

    def restore_plotsettings(self, is_2d):
        if self.plotwidget.name not in self._plotwidget_settings.keys():
            return

        if is_2d:
            self.plotwidget.roi.setState(
                self._plotwidget_settings[self.plotwidget.name][
                    "saved_roi_state"
                ]
            )
            self.plotwidget.settings_histogram.item.gradient.restoreState(
                self._plotwidget_settings[self.plotwidget.name][
                    "saved_lut_state"
                ]
            )
            self.plotwidget.image_item.setLevels(
                self._plotwidget_settings[self.plotwidget.name]["saved_levels"]
            )

    def lut_changed(self):
        for name, preview in self._previews.items():
            if preview.widget.name == self.plotwidget.name:
                current_gradient_state = (
                    self.plotwidget.settings_histogram.item.gradient.saveState()
                )
                preview.widget.settings_histogram.item.gradient.restoreState(
                    current_gradient_state
                )

    def levels_changed(self):
        for name, preview in self._previews.items():
            if preview.widget.name == self.plotwidget.name:
                current_image_levels = self.plotwidget.image_item.getLevels()
                preview.widget.image_item.setLevels(current_image_levels)

    def on_client_connected(self):
        LiveDataPanel.on_client_connected(self)
        self._cleanup_existing_previews()

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

        for preview in previews:
            name = preview.widget().name
            self._previews[name] = Preview(name, det_name, preview)
            self._detectors[det_name].add_preview(name)
            preview.widget().clicked.connect(self.on_preview_clicked)
            self.scroll_content.layout().addWidget(preview)

    def on_client_setup(self):
        self._cleanup_existing_previews()

    def highlight_selected_preview(self, selected):
        for name, preview in self._previews.items():
            if name == selected:
                preview.show()
            else:
                preview.hide()

    def _populate_previews(self):
        """
        Populates the preview widget with all the available detectors.
        """
        detectors = set(self.find_detectors())
        if not detectors:
            return
        for detector in detectors:
            self._detectors[detector] = DetContainer(detector)
            self.create_previews_for_detector(detector)
        self._display_first_detector()

    def _display_first_detector(self):
        if self._previews:
            first_preview = next(iter(self._previews.values()))
            first_preview.widget.clicked.emit(first_preview.name)
            if isinstance(first_preview.widget, LineView):
                self.plotwidget_1d.name = first_preview.name
            elif isinstance(first_preview.widget, ImageView):
                self.plotwidget.name = first_preview.name

    def on_client_cache(self, data):
        # Clear the previews if the list of detectors being used changes
        _, key, _, _ = data
        if key == "exp/detlist":
            self._cleanup_existing_previews()

    def on_client_livedata(self, params, blobs):
        """
        Updates the previews and the selected main image.

        :param params: data parameters
        :param blobs: data array
        """
        det_name = params["det"]

        if not self._previews:
            self._populate_previews()

        self.set_preview_data(params, blobs)

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
        """
        :return: a list with the name of all the configured detectors.
        """
        state = self.client.ask("getstatus")
        if not state:
            return []
        detlist = self.client.getCacheKey("exp/detlist")
        if not detlist:
            return []
        return [
            det
            for det in detlist[1]
            if self.client.eval(f"{det}.arrayInfo()", [])
        ]

    def create_preview_widgets(self, det_name):
        """
        :param det_name: detector name
        :return: a list of preview widgets
        """
        array_info = self.client.eval(f"{det_name}.arrayInfo()", ())
        previews = []

        for info in array_info:
            if len(info.shape) == 1:
                widget = LineView(name=info.name, parent=self)
                widget.view.setMouseEnabled(False, False)
                widget.plot.getPlotItem().hideAxis("bottom")
                widget.plot.getPlotItem().hideAxis("left")
            else:
                widget = ImageView(name=info.name, parent=self)
                widget.view.setMouseEnabled(False, False)
                widget.splitter_hori_1.setHandleWidth(0)
                widget.image_view_controller.hide()
                widget.settings_histogram.hide()
                widget.hide_roi(ignore_connections=True)
                widget.hide_crosshair_roi(ignore_connections=True)
                widget.hide_roi_plotwidgets()
            previews.append(LiveWidgetWrapper(title=info.name, widget=widget))
        return previews

    def set_preview_data(self, params, blobs):
        """
        Plots the data in the corresponding preview.
        :param params: data parameters
        :param blobs: data array
        """
        parent = params["det"]
        self._detectors[parent].update_cache(params, blobs)

        for index, datadesc in enumerate(params["datadescs"]):
            normalized_type = self.normalize_type(datadesc["dtype"])
            name = self._detectors[parent].get_preview_name(index)
            widget = self._previews[name].widget
            labels, _ = process_axis_labels(datadesc, blobs)
            if self._has_plot_changed_dimensionality(widget, labels):
                # Previews are no longer correct widget types
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
        return (isinstance(widget, LineView) and "y" in labels) or (
            not isinstance(widget, LineView) and "y" not in labels
        )

    def on_preview_clicked(self, det_name):
        """
        Set the main display to show data of the corresponding preview widget
        :param det_name: detector name
        """
        self._detector_selected = det_name
        parent = self._previews[det_name].detector
        pars, blob = self._detectors[parent].get_preview_data(
            self._detector_selected
        )

        is_2d = isinstance(self._previews[det_name].widget, ImageView)

        if is_2d:
            switched_plot = det_name != self.plotwidget.name
        else:
            switched_plot = det_name != self.plotwidget_1d.name

        if is_2d:
            self.plotwidget.view.enableAutoRange()
            self.plotwidget.name = det_name
        else:
            self.plotwidget_1d.view.enableAutoRange()
            self.plotwidget_1d.name = det_name

        self.save_plotsettings(is_2d=is_2d)
        if switched_plot:
            self.restore_plotsettings(is_2d=is_2d)

        if pars and blob:
            LiveDataPanel.on_client_livedata(self, pars, blob)
        self.highlight_selected_preview(det_name)

    def on_closed(self):
        """
        Clear the previews.
        """
        for item in layout_iterator(self.scroll_content.layout()):
            item.widget().deleteLater()
            del item
        LiveDataPanel.on_closed(self)
