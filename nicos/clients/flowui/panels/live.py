# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************
from enum import Enum

import numpy

from nicos.clients.flowui import uipath
from nicos.clients.flowui.panels import get_icon
from nicos.clients.gui.panels.live import LiveDataPanel as DefaultLiveDataPanel
from nicos.guisupport.livewidget import AXES, \
    LiveWidget as DefaultLiveWidget, LiveWidget1D as DefaultLiveWidget1D
from nicos.guisupport.qt import QComboBox, QGroupBox, QListWidget, QSize, Qt, \
    QToolBar, QVBoxLayout, pyqtProperty, pyqtSignal


class State(Enum):
    UNSELECTED = 0
    SELECTED = 1


class LiveDataPanel(DefaultLiveDataPanel):
    def __init__(self, parent, client, options):
        DefaultLiveDataPanel.__init__(self, parent, client, options)
        self.toolbar = self.createPanelToolbar()
        self.layout().setMenuBar(self.toolbar)
        self.set_icons()

    def createPanelToolbar(self):
        toolbar = QToolBar('Live data')
        toolbar.addAction(self.actionOpen)
        toolbar.addAction(self.actionPrint)
        toolbar.addAction(self.actionSavePlot)
        toolbar.addSeparator()
        toolbar.addAction(self.actionLogScale)
        toolbar.addSeparator()
        toolbar.addAction(self.actionKeepRatio)
        toolbar.addAction(self.actionUnzoom)
        toolbar.addAction(self.actionColormap)
        toolbar.addAction(self.actionMarkCenter)
        toolbar.addAction(self.actionROI)
        return toolbar

    def set_icons(self):
        self.actionPrint.setIcon(get_icon('print-24px.svg'))
        self.actionSavePlot.setIcon(get_icon('save-24px.svg'))
        self.actionUnzoom.setIcon(get_icon('zoom_out-24px.svg'))
        self.actionOpen.setIcon(get_icon('folder_open-24px.svg'))

    def getToolbars(self):
        return []


class LiveWidget(DefaultLiveWidget):
    """
    Add a 'name' attribute to LiveWidget and emit 'clicked' signal when clicked
    """

    clicked = pyqtSignal(str)

    def __init__(self, name, parent=None, **kwargs):
        DefaultLiveWidget.__init__(self, parent, **kwargs)
        self.setMinimumSize(150, 150)
        self.name = name

    def mousePressEvent(self, event):
        self.clicked.emit(self.name)


class LiveWidget1D(DefaultLiveWidget1D):
    """
    Add a 'name' attribute to LiveWidget1D and emit 'clicked' signal when
    clicked
    """

    clicked = pyqtSignal(str)

    def __init__(self, name='', parent=None, **kwargs):
        DefaultLiveWidget1D.__init__(self, parent, **kwargs)
        self.setMinimumSize(150, 150)
        self.name = name

    def mousePressEvent(self, event):
        self.clicked.emit(self.name)


class LiveWidgetWrapper(QGroupBox):
    def __init__(self, title, widget, parent=None):
        QGroupBox.__init__(self, title=title, parent=parent)
        self.state = State.UNSELECTED

        self.setContentsMargins(0, 0, 0, 0)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
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
        label = datadesc.get(
            'labels', {'x': CLASSIC, 'y': CLASSIC}).get(axis, CLASSIC)

        if label['define'] == 'range':
            start = label.get('start', 0)
            size = label.get('length', 1)
            step = label.get('step', 1)
            end = start + step * size
            labels[axis] = numpy.arange(start, end, step)
        elif label['define'] == 'array':
            index = label.get('index', 0)
            labels[axis] = numpy.frombuffer(blobs[index],
                                            label.get('dtype', '<i4'))
        else:
            labels[axis] = numpy.array(range(size))
        labels[axis] += offset if axis == 'x' else 0
        titles[axis] = label.get('title')

    return labels, titles


def processDataArrays(index, params, data):
    """Returns a list of arrays corresponding to the ``count`` of
    ``index`` into ``datadescs`` of the current params"""
    datadesc = params['datadescs'][index]
    count = datadesc.get('count', 1)
    shape = datadesc['shape']

    # determine 1D array size
    arraysize = numpy.product(shape)
    arrays = numpy.split(data[:count * arraysize], count)

    # reshape every array in the list
    for i, array in enumerate(arrays):
        arrays[i] = array.reshape(shape)
    return arrays


def process_livedata(widget, data, params, labels, idx):
    descriptions = params['datadescs']

    # pylint: disable=len-as-condition
    if len(data):
        arrays = processDataArrays(
            idx, params, numpy.frombuffer(data,descriptions[idx]['dtype']))
        if arrays is None:
            return
        widget.setData(arrays, labels)


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
            params['datadescs'] = [params['datadescs'][ch]]
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
    panelName = 'MultidetectorLiveDataView'
    ui = f'{uipath}/panels/ui_files/live.ui'

    def __init__(self, parent, client, options):
        self.fileList = QListWidget()
        self.tb_fileList = QComboBox()
        self._detector_selected = options.get('default_detector', '')
        self._detectors = {}
        self._previews = {}
        LiveDataPanel.__init__(self, parent, client, options)
        self.layout().setMenuBar(self.toolbar)
        self.scroll.setWidgetResizable(True)
        self.scrollContent.setLayout(QVBoxLayout())
        client.disconnected.connect(self.on_client_disconnected)
        client.setup.connect(self.on_client_setup)
        client.cache.connect(self.on_client_cache)

    def on_client_connected(self):
        DefaultLiveDataPanel.on_client_connected(self)
        self._cleanup_existing_previews()

    def on_client_disconnected(self):
        self._cleanup_existing_previews()

    def _cleanup_existing_previews(self):
        for item in layout_iterator(self.scrollContent.layout()):
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
            self.scrollContent.layout().addWidget(preview)

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

    def on_client_cache(self, data):
        # Clear the previews if the list of detectors being used changes
        (_, key, _, _) = data
        if key == 'exp/detlist':
            self._cleanup_existing_previews()

    def on_client_livedata(self, params, blobs):
        """
        Updates the previews and the selected main image.

        :param params: data parameters
        :param blobs: data array
        """
        det_name = params['det']

        if not self._previews:
            self._populate_previews()

        self.set_preview_data(params, blobs)

        if not self._detector_selected or \
                self._detector_selected not in self._previews:
            return

        if self._previews[self._detector_selected].detector == det_name:
            pars, blob = self._detectors[det_name].get_preview_data(
                self._detector_selected)
            DefaultLiveDataPanel.on_client_livedata(self, pars, blob)

    def find_detectors(self):
        """
        :return: a list with the name of all the configured detectors.
        """
        state = self.client.ask('getstatus')
        if not state:
            return []
        detlist = self.client.getCacheKey('exp/detlist')
        if not detlist:
            return []
        return [det for det in detlist[1]
                if self.client.eval(f'{det}.arrayInfo()', [])]

    def create_preview_widgets(self, det_name):
        """
        :param det_name: detector name
        :return: a list of preview widgets
        """
        array_info = self.client.eval(f'{det_name}.arrayInfo()', ())
        previews = []

        for info in array_info:
            if len(info.shape) == 1:
                widget = LiveWidget1D(name=info.name, parent=self)
                widget.setLines(True)
            else:
                widget = LiveWidget(name=info.name, parent=self)
            widget.gr.keepRatio = True
            widget.gr.setAttribute(Qt.WA_TransparentForMouseEvents)
            previews.append(LiveWidgetWrapper(title=info.name, widget=widget))
        return previews

    def set_preview_data(self, params, blobs):
        """
        Plots the data in the corresponding preview.
        :param params: data parameters
        :param blobs: data array
        """
        parent = params['det']
        self._detectors[parent].update_cache(params, blobs)

        for index, datadesc in enumerate(params['datadescs']):
            normalized_type = self.normalizeType(datadesc['dtype'])
            name = self._detectors[parent].get_preview_name(index)
            widget = self._previews[name].widget
            labels, _ = process_axis_labels(datadesc, blobs)
            if self._has_plot_changed_dimensionality(widget, labels):
                # Previews are no longer correct widget types
                self._cleanup_existing_previews()
                return
            process_livedata(widget,
                             numpy.frombuffer(blobs[index], normalized_type),
                             params, labels, index)

    def _has_plot_changed_dimensionality(self, widget, labels):
        return (isinstance(widget, LiveWidget1D) and 'y' in labels) or \
               (not isinstance(widget, LiveWidget1D) and 'y' not in labels)

    def on_preview_clicked(self, det_name):
        """
        Set the main display to show data of the corresponding preview widget
        :param det_name: detector name
        """
        self._detector_selected = det_name
        parent = self._previews[det_name].detector
        pars, blob = self._detectors[parent].get_preview_data(
            self._detector_selected)

        if pars and blob:
            DefaultLiveDataPanel.on_client_livedata(self, pars, blob)

        self.highlight_selected_preview(det_name)

    def on_closed(self):
        """
        Clear the previews.
        """
        for item in layout_iterator(self.scrollContent.layout()):
            item.widget().deleteLater()
            del item
        DefaultLiveDataPanel.on_closed(self)
