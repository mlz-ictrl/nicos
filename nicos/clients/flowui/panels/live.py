# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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

import numpy

from nicos.clients.flowui import uipath
from nicos.clients.flowui.panels import get_icon
from nicos.clients.gui.panels.live import LiveDataPanel as DefaultLiveDataPanel
from nicos.guisupport.livewidget import AXES, \
    LiveWidget as DefaultLiveWidget, LiveWidget1D as DefaultLiveWidget1D
from nicos.guisupport.qt import QComboBox, QGroupBox, QListWidget, QSize, Qt, \
    QToolBar, QVBoxLayout, pyqtSignal


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

    def __init__(self, name, parent=None):
        DefaultLiveWidget.__init__(self, parent)
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

    def __init__(self, name='', parent=None):
        DefaultLiveWidget1D.__init__(self, parent)
        self.setMinimumSize(150, 150)
        self.name = name

    def mousePressEvent(self, event):
        self.clicked.emit(self.name)


class LiveWidgetWrapper(QGroupBox):
    def __init__(self, title, parent=None):
        QGroupBox.__init__(self, title=title, parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def set_live_widget(self, widget):
        self.layout().addWidget(widget)

    def widget(self):
        return self.layout().itemAt(0).widget()

    def resizeEvent(self, event):
        # Maintain aspect ratio when resizing
        new_size = QSize(event.size().width(), event.size().width())
        self.resize(new_size)


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
        self._previews = dict()
        self._previews_cache = dict()
        LiveDataPanel.__init__(self, parent, client, options)
        self.layout().setMenuBar(self.toolbar)
        self.scroll.setWidgetResizable(True)
        self.scrollContent.setLayout(QVBoxLayout())
        client.disconnected.connect(self.on_client_disconnected)
        client.setup.connect(self.on_client_setup)
        client.cache.connect(self.on_client_cache)

    def on_client_connected(self):
        DefaultLiveDataPanel.on_client_connected(self)
        self.on_client_setup()

    def on_client_disconnected(self):
        for item in layout_iterator(self.scrollContent.layout()):
            item.widget().deleteLater()
            del item

    def add_detector_to_preview(self, detname):
        previews = self.create_preview(detname)
        self._previews_cache.update({detname: {'params': {}, 'blobs': []}})
        for preview in previews:
            preview.widget().clicked.connect(self.on_preview_clicked)
            self._previews[preview.widget().name] = preview
            self.scrollContent.layout().addWidget(preview)

    def on_client_setup(self):
        """
        The object populates the checkbox with all the available detectors.
        If this method is called after a reconnection, destroys the content
        of the detector group before reallocating.
        :return: None
        """
        detectors = set(self.find_detectors())
        self.on_client_disconnected()
        for detector in detectors:
            self.add_detector_to_preview(detector)

    def on_client_cache(self, data):
        # Update the preview if the list of detectors being used changes
        (_, key, _, _) = data
        if key == 'exp/detlist':
            self.on_client_setup()

    def on_client_livedata(self, params, blobs):
        """
        If the blob comes from a detector that has been selected in the
        checkbox update the preview.
        If in addition the detector is the one selected to provide the main
        image updates the view.
        :param params: data parameters
        :param blobs: data array
        :return: None
        """
        det_name = params['det']
        if [preview for preview in self._previews if preview.startswith(
                det_name)]:
            self.set_preview_data(params, blobs)

        detector_selected = '-'.join(self._detector_selected.split('-')[:-1])
        if det_name == detector_selected:
            channel = int(self._detector_selected.split('-')[-1])
            param = dict(params)
            param['datadescs'] = [param['datadescs'][channel]]
            blob = [blobs[channel]]
            DefaultLiveDataPanel.on_client_livedata(self, param, blob)

    def find_detectors(self):
        """
        Returns a list with all the devices of type Detector.
        :return: a list with the name of all the configured detectors.
        """
        state = self.client.ask('getstatus')
        if not state:
            return {}
        detlist = self.client.getCacheKey('exp/detlist')[1]
        return [det for det in detlist if self.client.eval(f'{det}.arrayInfo('
                                                           f')', [])]

    def create_preview(self, detname):
        """
        Return a widget to be used for the detector preview.
        :param detname: detector name
        :return: a LiveWidget
        """
        array_desc = self.client.eval(f'{detname}.arrayInfo()', [])
        widgets = []
        for channel_id in range(len(array_desc)):
            if len(array_desc[channel_id].shape) == 1:
                widget = LiveWidget1D(name=f'{detname}-{channel_id}',
                                      parent=self)
            else:
                widget = LiveWidget(name=f'{detname}-{channel_id}', parent=self)
            widget.gr.keepRatio = True
            widget.gr.setAttribute(Qt.WA_TransparentForMouseEvents)
            if len(array_desc) > 1:
                title = f'{detname}-ch:{channel_id}'
            else:
                title = f'{detname}'
            superwidget = LiveWidgetWrapper(title=title)
            superwidget.set_live_widget(widget)
            widgets.append(superwidget)
        return widgets

    def set_preview_data(self, params, blobs):
        """
        Plots the data in the corresponding preview.
        :param params: data parameters
        :param blobs: data array
        :return: None
        """
        detname = params['det']

        self._previews_cache[detname]['params'] = params
        self._previews_cache[detname]['blobs'] = blobs

        for index, datadesc in enumerate(params['datadescs']):
            normalized_type = self.normalizeType(datadesc['dtype'])
            widget = self._previews[f'{detname}-{index}'].widget()
            labels, _ = process_axis_labels(datadesc, blobs)
            process_livedata(widget,
                             numpy.frombuffer(blobs[index], normalized_type),
                             params, labels, index)

    def on_preview_clicked(self, detname):
        """
        Set the main display to show data of the corresponding preview widget
        :param detname: detector name
        :return:
        """
        self._detector_selected = detname

        cached_name = '-'.join(detname.split('-')[:-1])
        if cached_name not in self._previews_cache:
            return
        params = self._previews_cache[cached_name].get('params', [])
        blobs = self._previews_cache[cached_name].get('blobs', [])

        if params and blobs:
            ch = int(detname.split('-')[-1])
            pars = dict(params)

            pars['datadescs'] = [pars['datadescs'][ch]]
            DefaultLiveDataPanel.on_client_livedata(self, pars, [blobs[ch]])

    def on_closed(self):
        """
        Clear the preview.
        :return: None
        """
        for item in layout_iterator(self.scrollContent.layout()):
            item.widget().deleteLater()
            del item
        DefaultLiveDataPanel.on_closed(self)
