#  -*- coding: utf-8 -*-
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS livewidget with GR."""

import os
from collections import OrderedDict
from os import path
from uuid import uuid4

import numpy
from gr import COLORMAPS as GR_COLORMAPS

from nicos.clients.gui.dialogs.filesystem import FileFilterDialog
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import enumerateWithProgress, loadUi, uipath
from nicos.core.constants import FILE, LIVE
from nicos.core.errors import NicosError
from nicos.guisupport.livewidget import AXES, DATATYPES, IntegralLiveWidget, \
    LiveWidget, LiveWidget1D
from nicos.guisupport.qt import QActionGroup, QByteArray, QListWidgetItem, \
    QMenu, QPoint, QSizePolicy, QStatusBar, Qt, QToolBar, pyqtSlot
from nicos.guisupport.qtgr import MouseEvent
from nicos.protocols.cache import cache_load
from nicos.utils import BoundedOrderedDict, ReaderRegistry

COLORMAPS = OrderedDict(GR_COLORMAPS)

FILENAME = Qt.UserRole
FILEFORMAT = Qt.UserRole + 1
FILETAG = Qt.UserRole + 2
FILEUID = Qt.UserRole + 3

DEFAULTS = dict(
    marks='omark',
    offset=0,
    plotcount=1,
    colors='blue',
    markersize=1,
)


def readDataFromFile(filename, fileformat):
    try:
        return ReaderRegistry.getReaderCls(fileformat).fromfile(filename)
    except KeyError:
        raise NicosError('Unsupported fileformat %r' % fileformat) from None


class LiveDataPanel(Panel):
    """Provides a generic "detector live view".

    For most instruments, a specific panel must be implemented that takes care
    of the individual live display needs.

    Options:

    * ``filetypes`` (default []) - List of filename extensions whose content
      should be displayed.
    * ``detectors`` (default []) - List of detector devices whose data should
      be displayed. If not set data from all configured detectors will be
      shown.
    * ``cachesize`` (default 20) - Number of entries in the live data cache.
      The live data cache allows displaying of previously measured data.
    * ``liveonlyindex`` (default None) - Enable live only view. This disables
      interaction with the liveDataPanel and only displays the dataset of the
      set index.

    * ``defaults`` (default []) - List of strings representing options to be
      set for every configured plot.
      These options can not be set on a per plot basis since they are global.
      Options are as follows:

        * ``logscale`` - Switch the logarithic scale on.
        * ``center`` - Display the center lines for the image.
        * ``nolines`` - Display lines for the curve.
        * ``markers`` - Display symbols for data points.
        * ``unzoom`` - Unzoom the plot when new data is received.

    * ``plotsettings`` (default []) - List of dictionaries which contain
      settings for the individual datasets.

      Each entry will be applied to one of the detector's datasets.

      * ``plotcount`` (default 1) - Amount of plots in the dataset.
      * ``marks`` (default 'omark') - Shape of the markers (if displayed).
        Possible values are:

          'dot', 'plus', 'asterrisk', 'circle', 'diagonalcross', 'solidcircle',
          'triangleup', 'solidtriangleup', 'triangledown', 'solidtriangledown',
          'square', 'solidsquare', 'bowtie', 'solidbowtie', 'hourglass',
          'solidhourglass', 'diamond', 'soliddiamond', 'star', 'solidstar',
          'triupdown', 'solidtriright', 'solidtrileft', 'hollowplus',
          'solidplus', 'pentagon', 'hexagon', 'heptagon', 'octagon', 'star4',
          'star5', 'star6', 'star7', 'star8', 'vline', 'hline', 'omark'

      * ``markersize`` (default 1) - Size of the markers (if displayed).
      * ``offset`` (default 0) - Offset for the X axis labels of
        each curve in 1D plots.
      * ``colors`` (default ['blue']) - Color of the marks and lines
        (if displayed).
        If colors are set as a list the colors will be applied to the
        individual plots (and default back to blue when wrong/missing),
        for example:

        ['red', 'green']: The first plot will be red, the second green and
        the others will be blue (default).

        'red': all plots will be red.
    """

    panelName = 'Live data view'

    ui = f'{uipath}/panels/live.ui'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.ui)

        self._allowed_tags = set()
        self._allowed_detectors = set()
        self._runtime = 0
        self._range_active = False
        self._cachesize = 20
        self._livewidgets = {}  # livewidgets for rois: roi_key -> widget
        self._fileopen_filter = None
        self.widget = None
        self.menu = None
        self.unzoom = False
        self.lastSettingsIndex = None
        self._axis_labels = {}
        self.params = {}
        self._offset = 0

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.toolbar = QToolBar('Live data')
        self.toolbar.addAction(self.actionOpen)
        self.toolbar.addAction(self.actionPrint)
        self.toolbar.addAction(self.actionSavePlot)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionLogScale)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionKeepRatio)
        self.toolbar.addAction(self.actionUnzoom)
        self.toolbar.addAction(self.actionColormap)
        self.toolbar.addAction(self.actionMarkCenter)
        self.toolbar.addAction(self.actionROI)

        self._actions2D = [self.actionROI, self.actionColormap]
        self.setControlsEnabled(False)
        self.set2DControlsEnabled(False)

        # hide fileselection in liveonly mode
        self._liveOnlyIndex = options.get('liveonlyindex', None)
        if self._liveOnlyIndex is not None:
            self.pastFilesWidget.hide()
            self.statusBar.hide()
            # disable interactions with the plot
            self.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.liveitems = []
        self.setLiveItems(1)
        self._livechannel = 0

        self.splitter.setSizes([20, 80])
        self.splitter.restoreState(self.splitterstate)

        if hasattr(self.window(), 'closed'):
            self.window().closed.connect(self.on_closed)
        client.livedata.connect(self.on_client_livedata)
        client.connected.connect(self.on_client_connected)
        client.cache.connect(self.on_cache)

        self.rois = {}
        self.detectorskey = None
        # configure allowed file types
        supported_filetypes = ReaderRegistry.filetypes()
        opt_filetypes = set(options.get('filetypes', supported_filetypes))
        self._allowed_tags = opt_filetypes & set(supported_filetypes)

        # configure allowed detector device names
        detectors = options.get('detectors')
        if detectors:
            self._allowed_detectors = set(detectors)

        defaults = options.get('defaults', [])

        if 'logscale' in defaults:
            self.actionLogScale.setChecked(True)
        if 'center' in defaults:
            self.actionMarkCenter.setChecked(True)
        if 'nolines' not in defaults:
            self.actionLines.setChecked(True)
        if 'markers' in defaults:
            self.actionSymbols.setChecked(True)
        if 'unzoom' in defaults:
            self.unzoom = True

        self.plotsettings = options.get('plotsettings', [DEFAULTS])

        # configure caching
        self._cachesize = options.get('cachesize', self._cachesize)
        if self._cachesize < 1 or self._liveOnlyIndex is not None:
            self._cachesize = 1  # always cache the last live image
        self._datacache = BoundedOrderedDict(maxlen=self._cachesize)

    def setLiveItems(self, n):
        nitems = len(self.liveitems)
        if n < nitems:
            nfiles = self.fileList.count()
            for i in range(nitems - 1, n - 1, -1):
                self.liveitems.pop(i)
                self.fileList.takeItem(nfiles - nitems + i)
            if self._livechannel > n:
                self._livechannel = 0 if n > 0 else None
        else:
            for i in range(nitems, n):
                item = QListWidgetItem('<Live #%d>' % (i + 1))
                item.setData(FILENAME, i)
                item.setData(FILEFORMAT, '')
                item.setData(FILETAG, LIVE)
                self.fileList.insertItem(self.fileList.count(), item)
                self.liveitems.append(item)
            if self._liveOnlyIndex is not None:
                self.fileList.setCurrentRow(self._liveOnlyIndex)
        if n == 1:
            self.liveitems[0].setText('<Live>')
        else:
            self.liveitems[0].setText('<Live #1>')

    def set2DControlsEnabled(self, flag):
        if flag != self.actionKeepRatio.isChecked():
            self.actionKeepRatio.trigger()
        for action in self._actions2D:
            action.setVisible(flag)

    def setControlsEnabled(self, flag):
        for action in self.toolbar.actions():
            action.setEnabled(flag)
        self.actionOpen.setEnabled(True)  # File Open action always available

    def initLiveWidget(self, widgetcls):
        if isinstance(self.widget, widgetcls):
            return

        # delete the old widget
        if self.widget:
            self.widgetLayout.removeWidget(self.widget)
            self.widget.deleteLater()

        # create a new one
        self.widget = widgetcls(self)

        # enable/disable controls and set defaults for new livewidget instances
        self.setControlsEnabled(True)
        if isinstance(self.widget, LiveWidget1D):
            self.set2DControlsEnabled(False)
        else:
            self.set2DControlsEnabled(True)

        # apply current global settings
        self.widget.setCenterMark(self.actionMarkCenter.isChecked())
        self.widget.logscale(self.actionLogScale.isChecked())
        if isinstance(self.widget, LiveWidget1D):
            self.widget.setSymbols(self.actionSymbols.isChecked())
            self.widget.setLines(self.actionLines.isChecked())
        # liveonly mode does not display a status bar
        if self._liveOnlyIndex is None:
            self.widget.gr.cbm.addHandler(MouseEvent.MOUSE_MOVE,
                                          self.on_mousemove_gr)

        # handle menus
        self.menuColormap = QMenu(self)
        self.actionsColormap = QActionGroup(self)
        activeMap = self.widget.getColormap()
        activeCaption = None
        for name, value in COLORMAPS.items():
            caption = name.title()
            action = self.menuColormap.addAction(caption)
            action.setData(caption)
            action.setCheckable(True)
            if activeMap == value:
                action.setChecked(True)
                # update toolButton text later otherwise this may fail
                # depending on the setup and qt versions in use
                activeCaption = caption
            self.actionsColormap.addAction(action)
            action.triggered.connect(self.on_colormap_triggered)
        self.actionColormap.setMenu(self.menuColormap)

        # finish initiation
        self.widgetLayout.addWidget(self.widget)
        if activeCaption:
            self.toolbar.widgetForAction(self.actionColormap).setText(
                activeCaption)
        detectors = self.client.eval('session.experiment.detectors', [])
        self._register_rois(detectors)

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', '', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('geometry', self.saveGeometry())

    def getMenus(self):
        if self._liveOnlyIndex is not None:
            return []

        if not self.menu:
            menu = QMenu('&Live data', self)
            menu.addAction(self.actionOpen)
            menu.addAction(self.actionPrint)
            menu.addAction(self.actionSavePlot)
            menu.addSeparator()
            menu.addAction(self.actionKeepRatio)
            menu.addAction(self.actionUnzoom)
            menu.addAction(self.actionLogScale)
            menu.addAction(self.actionColormap)
            menu.addAction(self.actionMarkCenter)
            menu.addAction(self.actionROI)
            menu.addAction(self.actionSymbols)
            menu.addAction(self.actionLines)
            self.menu = menu
        return [self.menu]

    def _get_all_widgets(self):
        yield self.widget
        yield from self._livewidgets.values()

    def getToolbars(self):
        if self._liveOnlyIndex is not None:
            return []

        return [self.toolbar]

    def on_mousemove_gr(self, event):
        xyz = None
        if event.getWindow():  # inside plot
            xyz = self.widget.getZValue(event)
        if xyz:
            fmt = '(%g, %g)'  # x, y data 1D integral plots
            if len(xyz) == 3:
                fmt += ': %g'  # x, y, z data for 2D image plot
            self.statusBar.showMessage(fmt % xyz)
        else:
            self.statusBar.clearMessage()

    def on_actionColormap_triggered(self):
        w = self.toolbar.widgetForAction(self.actionColormap)
        m = self.actionColormap.menu()
        if m:
            m.popup(w.mapToGlobal(QPoint(0, w.height())))

    def on_colormap_triggered(self):
        action = self.actionsColormap.checkedAction()
        name = action.data()
        for widget in self._get_all_widgets():
            widget.setColormap(COLORMAPS[name.upper()])
        self.toolbar.widgetForAction(
            self.actionColormap).setText(name.title())

    @pyqtSlot()
    def on_actionLines_triggered(self):
        if self.widget and isinstance(self.widget, LiveWidget1D):
            self.widget.setLines(self.actionLines.isChecked())

    @pyqtSlot()
    def on_actionSymbols_triggered(self):
        if self.widget and isinstance(self.widget, LiveWidget1D):
            self.widget.setSymbols(self.actionSymbols.isChecked())

    def _getLiveWidget(self, roi):
        return self._livewidgets.get(roi + '/roi', None)

    def showRoiWindow(self, roikey):
        key = roikey + '/roi'
        widget = self._getLiveWidget(roikey)
        region = self.widget._rois[key]
        if not widget:
            widget = LiveWidget(None)
            widget.setWindowTitle(roikey)
            widget.setColormap(self.widget.getColormap())
            widget.setCenterMark(self.actionMarkCenter.isChecked())
            widget.logscale(self.actionLogScale.isChecked())
            widget.gr.setAdjustSelection(False)  # don't use adjust on ROIs
            for name, roi in self.rois.items():
                widget.setROI(name, roi)
            width = max(region.x) - min(region.x)
            height = max(region.y) - min(region.y)
            if width > height:
                dwidth = 500
                dheight = 500 * height // width
            else:
                dheight = 500
                dwidth = 500 * width // height
            widget.resize(dwidth, dheight)
            widget.closed.connect(self.on_roiWindowClosed)
        widget.setWindowForRoi(region)
        widget.update()
        widget.show()
        widget.activateWindow()
        self._livewidgets[key] = widget

    def closeRoiWindow(self, roi):
        widget = self._getLiveWidget(roi)
        if widget:
            widget.close()

    def on_closed(self):
        for w in self._livewidgets.values():
            w.close()

    def _register_rois(self, detectors):
        self.rois.clear()
        self.actionROI.setVisible(False)
        self.menuROI = QMenu(self)
        self.actionsROI = QActionGroup(self)
        self.actionsROI.setExclusive(False)
        for detname in detectors:
            self.log.debug('checking rois for detector \'%s\'', detname)
            for tup in self.client.eval(detname + '.postprocess', ''):
                roi = tup[0]
                cachekey = roi + '/roi'
                # check whether or not this is a roi (cachekey exists).
                keyval = self.client.getCacheKey(cachekey)
                if keyval:
                    self.on_roiChange(cachekey, keyval[1])
                    self.log.debug('register roi: %s', roi)
                    # create roi menu
                    action = self.menuROI.addAction(roi)
                    action.setData(roi)
                    action.setCheckable(True)
                    self.actionsROI.addAction(action)
                    action.triggered.connect(self.on_roi_triggered)
                    self.actionROI.setMenu(self.menuROI)
                    self.actionROI.setVisible(True)

    def on_actionROI_triggered(self):
        w = self.toolbar.widgetForAction(self.actionROI)
        self.actionROI.menu().popup(w.mapToGlobal(QPoint(0, w.height())))

    def on_roi_triggered(self):
        action = self.sender()
        roi = action.data()
        if action.isChecked():
            self.showRoiWindow(roi)
        else:
            self.closeRoiWindow(roi)

    def on_roiWindowClosed(self):
        widget = self.sender()
        if widget:
            key = None
            for key, w in self._livewidgets.items():
                if w == widget:
                    self.log.debug('delete roi: %s', key)
                    del self._livewidgets[key]
                    break
            if key:
                roi = key.rsplit('/', 1)[0]
                for action in self.actionsROI.actions():
                    if action.data() == roi:
                        action.setChecked(False)
                        self.log.debug('uncheck roi: %s', roi)

    def on_roiChange(self, key, value):
        self.log.debug('on_roiChange: %s %s', key, (value,))
        self.rois[key] = value
        for widget in self._get_all_widgets():
            widget.setROI(key, value)
        widget = self._livewidgets.get(key, None)
        if widget:
            widget.setWindowForRoi(self.widget._rois[key])

    def on_cache(self, data):
        _time, key, _op, svalue = data
        try:
            value = cache_load(svalue)
        except ValueError:
            value = None
        if key in self.rois:
            self.on_roiChange(key, value)
        elif key == self.detectorskey and self.widget:
            self._register_rois(value)

    def on_client_connected(self):
        self.client.tell('eventunmask', ['livedata'])
        self.detectorskey = (self.client.eval('session.experiment.name')
                             + '/detlist').lower()

    def normalizeType(self, dtype):
        normalized_type = numpy.dtype(dtype).str
        if normalized_type not in DATATYPES:
            self.log.warning('Unsupported live data format: %s',
                             normalized_type)
            return
        return normalized_type

    def getIndexedUID(self, idx):
        return str(self.params['uid']) + '-' + str(idx)

    def _process_axis_labels(self, blobs):
        """Convert the raw axis label descriptions.
        tuple: `from, to`: Distribute labels equidistantly between the two
                           values.
        numbertype: `index into labels`: Actual labels are provided.
                                         Value is the starting index.
                                         Extract from first available blob.
                                         Remove said blob from list.
        None: `default`: Start at 0 with stepwidth 1.

        Save the axis labels to the datacache.
        """

        CLASSIC = {'define': 'classic'}

        for i, datadesc in enumerate(self.params['datadescs']):
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
                    labels[axis] = self.getDefaultLabels(size)
                labels[axis] += self._offset if axis == 'x' else 0
                titles[axis] = label.get('title')

            # save the labels in the datacache with uid as key
            uid = self.getIndexedUID(i)
            if uid not in self._datacache:
                self._datacache[uid] = {}

            self._datacache[uid]['labels'] = labels
            self._datacache[uid]['titles'] = titles

    def _process_livedata(self, data, idx):
        # ignore irrelevant data in liveOnly mode
        if self._liveOnlyIndex is not None and idx != self._liveOnlyIndex:
            return

        if self.params['tag'] in self._allowed_tags \
                or self.params['tag'] == LIVE:
            try:
                descriptions = self.params['datadescs']
            except KeyError:
                self.log.warning('Livedata with tag "Live" without '
                                 '"datadescs" provided.')
                return

            # pylint: disable=len-as-condition
            if len(data):
                # we got live data with specified formats
                arrays = self.processDataArrays(
                    idx, numpy.frombuffer(data, descriptions[idx]['dtype']))

                if arrays is None:
                    return

                # put everythin into the cache
                uid = self.getIndexedUID(idx)
                self._datacache[uid]['dataarrays'] = arrays

                self.liveitems[idx].setData(FILEUID, uid)

    def _process_filenames(self):
        # TODO: allow multiple fileformats?
        #       would need to modify input from DemonSession.notifyDataFile

        number_of_items = self.fileList.count()
        for i, filedesc in enumerate(self.params['filedescs']):
            uid = self.getIndexedUID(number_of_items + i)
            name = filedesc['filename']
            tag = filedesc.get('fileformat')
            if tag is None or tag not in ReaderRegistry.filetypes():
                continue  # Ignore unregistered file types
            self.add_to_flist(name, tag, FILE, uid)
            try:
                # update display for selected live channel,
                # just cache otherwise
                self.setDataFromFile(
                    name, tag, uid, display=(i == self._livechannel))
            except Exception as e:
                if uid in self._datacache:
                    # image is already cached
                    # suppress error message for cached image
                    self.log.debug(e)
                else:
                    # image is not cached and could not be loaded
                    self.log.exception(e)

    def on_client_livedata(self, params, blobs):
        # blobs is a list of data blobs and labels blobs
        if self._allowed_detectors \
                and params['det'] not in self._allowed_detectors:
            return

        self.params = params
        self._runtime = params['time']
        if params['tag'] == LIVE:
            datacount = len(params['datadescs'])
            self.setLiveItems(datacount)

            self._process_axis_labels(blobs[datacount:])

            for i, blob in enumerate(blobs[:datacount]):
                self._process_livedata(blob, i)
            if not datacount:
                self._process_livedata([], 0)
        elif params['tag'] == FILE:
            self._process_filenames()

        self._show()

    def getDefaultLabels(self, size):
        return numpy.array(range(size))

    def convertLabels(self, labelinput):
        """Convert the input into a processable format"""

        for i, entry in enumerate(labelinput):
            if isinstance(entry, str):
                labelinput[i] = self.normalizeType(entry)

        return labelinput

    def _initLiveWidget(self, array):
        """Initialize livewidget based on array's shape"""
        if len(array.shape) == 1:
            widgetcls = LiveWidget1D
        else:
            widgetcls = IntegralLiveWidget
        self.initLiveWidget(widgetcls)

    def setDataFromFile(self, filename, tag, uid=None, display=True):
        """Load data array from file and dispatch to live widgets using
        ``setData``. Do not use caching if uid is ``None``.
        """
        array = readDataFromFile(filename, tag)
        if array is not None:
            if uid:
                if uid not in self._datacache:
                    self.log.debug('add to cache: %s', uid)
                self._datacache[uid] = {}
                self._datacache[uid]['dataarrays'] = [array]
            if display:
                self._initLiveWidget(array)
                for widget in self._get_all_widgets():
                    widget.setData(array)
#           self.setData([array], uid, display=display)
            return array.shape
        else:
            raise NicosError('Cannot read file %r' % filename)

    def processDataArrays(self, index, entry):
        """Check if the input 1D array has the expected amount of values.
        If the array is too small an Error is raised.
        If the size exceeds the expected amount it is truncated.

        Returns a list of arrays corresponding to the ``plotcount`` of
        ``index`` into ``datadescs`` of the current params"""

        datadesc = self.params['datadescs'][index]
        count = datadesc.get('plotcount', DEFAULTS['plotcount'])
        shape = datadesc['shape']

        # ignore irrelevant data in liveOnly mode
        if self._liveOnlyIndex is not None and index != self._liveOnlyIndex:
            return

        # determine 1D array size
        arraysize = numpy.product(shape)

        # check and split the input array
        if len(entry) < count * arraysize:
            self.log.warning('Expected dataarray with %d entries, got %d',
                             count * arraysize, len(entry))
            return
        arrays = numpy.split(entry[:count * arraysize], count)

        # reshape every array in the list
        for i, array in enumerate(arrays):
            arrays[i] = array.reshape(shape)
        return arrays

    def applyPlotSettings(self):
        if not self.widget or not isinstance(self.widget, LiveWidget1D):
            return

        if self._liveOnlyIndex is not None:
            index = self._liveOnlyIndex
        else:
            index = self.fileList.currentRow()

        if isinstance(self.widget, LiveWidget1D):
            def getElement(l, index, default):
                try:
                    return l[index]
                except IndexError:
                    return default

            settings = getElement(self.plotsettings, index, DEFAULTS)

            if self.params['tag'] == LIVE:
                plotcount = self.params['datadescs'][index].get(
                    'plotcount', DEFAULTS['plotcount'])
            else:
                plotcount = DEFAULTS['plotcount']
            marks = [settings.get('marks', DEFAULTS['marks'])]
            markersize = settings.get('markersize', DEFAULTS['markersize'])
            offset = settings.get('offset', DEFAULTS['offset'])
            colors = settings.get('colors', DEFAULTS['colors'])

            if isinstance(colors, list):
                if len(colors) > plotcount:
                    colors = colors[:plotcount]
                while len(colors) < plotcount:
                    colors.append(DEFAULTS['colors'])
            else:
                colors = [colors] * plotcount

            self.setOffset(offset)
            self.widget.setMarks(marks)
            self.widget.setMarkerSize(markersize)
            self.widget.setPlotCount(plotcount, colors)

    def setOffset(self, offset):
        self._offset = offset

    def getDataFromItem(self, item):
        """Extract and return the data associated with the item.
        If the data is in the cache return it.
        If the data is in a valid file extract it from there.
        """

        if item is None:
            return

        uid = item.data(FILEUID)
        # data is cached
        if uid and hasattr(self, '_datacache') and uid in self._datacache:
            return self._datacache[uid]
        # cache has cleared data or data has not been cached in the first place
        elif uid is None and item.data(FILETAG) == FILE:
            filename = item.data(FILENAME)
            fileformat = item.data(FILEFORMAT)

            if path.isfile(filename):
                rawdata = readDataFromFile(filename, fileformat)
                labels = {}
                titles = {}
                for axis, entry in zip(AXES, reversed(rawdata.shape)):
                    labels[axis] = numpy.arange(entry)
                    titles[axis] = axis
                data = {
                    'labels': labels,
                    'titles': titles,
                    'dataarrays': [rawdata]
                }
                return data
            # else:
            # TODO: mark for deletion on item changed?

    def _show(self, data=None):
        """Show the provided data. If no data has been provided extract it
        from the datacache via the current item's uid.

        :param data: dictionary containing 'dataarrays' and 'labels'
        """

        idx = self.fileList.currentRow()
        if idx == -1:
            self.fileList.setCurrentRow(0)
            return

        # no data has been provided, try to get it from the cache
        if data is None:
            data = self.getDataFromItem(self.fileList.currentItem())
            # still no data
            if data is None:
                return

        arrays = data.get('dataarrays', [])
        labels = data.get('labels', {})
        titles = data.get('titles', {})

        # if multiple datasets have to be displayed in one widget, they have
        # the same dimensions, so we only need the dimensions of one set
        self._initLiveWidget(arrays[0])
        self.applyPlotSettings()
        for widget in self._get_all_widgets():
            widget.setData(arrays, labels)
            widget.setTitles(titles)

        if self.unzoom and self.widget:
            self.on_actionUnzoom_triggered()

    def remove_obsolete_cached_files(self):
        """Remove or flag items which are no longer cached.
        The cache will delete items if it's size exceeds ´cachesize´.
        This checks the items in the filelist and their caching status,
        removing items with deleted associated files and flagging items
        with valid files to be reloaded if selected by the user.
        """

        for index in reversed(range(self.fileList.count())):
            item = self.fileList.item(index)
            uid = item.data(FILEUID)
            # is the uid still cached
            if uid and uid not in self._datacache:
                # does the file still exist on the filesystem
                if path.isfile(item.data(FILENAME)):
                    item.setData(FILEUID, None)
                else:
                    self.fileList.takeItem(index)

    def add_to_flist(self, filename, fformat, ftag, uid=None, scroll=True):
        # liveonly mode doesn't display a filelist
        if self._liveOnlyIndex is not None:
            return

        shortname = path.basename(filename)
        item = QListWidgetItem(shortname)
        item.setData(FILENAME, filename)
        item.setData(FILEFORMAT, fformat)
        item.setData(FILETAG, ftag)
        item.setData(FILEUID, uid)
        self.fileList.insertItem(self.fileList.count(), item)
        if uid:
            self.remove_obsolete_cached_files()
        if scroll:
            self.fileList.scrollToBottom()
        return item

    def on_fileList_currentItemChanged(self):
        self._show()

    @pyqtSlot()
    def on_actionOpen_triggered(self):
        """Open image file using registered reader classes."""
        ftypes = {ffilter: ftype
                  for ftype, ffilter in ReaderRegistry.filefilters()
                  if not self._allowed_tags or ftype in self._allowed_tags}
        fdialog = FileFilterDialog(self, "Open data files", "",
                                   ";;".join(ftypes.keys()))
        if self._fileopen_filter:
            fdialog.selectNameFilter(self._fileopen_filter)
        if fdialog.exec_() != fdialog.Accepted:
            return
        files = fdialog.selectedFiles()
        if not files:
            return
        self._fileopen_filter = fdialog.selectedNameFilter()
        tag = ftypes[self._fileopen_filter]
        errors = []

        def _cacheFile(fn, tag):
            uid = uuid4()
            # setDataFromFile may raise an `NicosException`, e.g.
            # if the file cannot be opened.
            try:
                self.setDataFromFile(fn, tag, uid, display=False)
            except Exception as err:
                errors.append('%s: %s' % (fn, err))
            else:
                return self.add_to_flist(fn, tag, FILE, uid)

        # load and display first item
        f = files.pop(0)
        item = _cacheFile(f, tag)
        if item is not None:
            self.fileList.setCurrentItem(item)
        cachesize = self._cachesize - 1
        # add first `cachesize` files to cache
        for _, f in enumerateWithProgress(files[:cachesize],
                                          "Loading data files...",
                                          parent=fdialog):
            _cacheFile(f, tag)
        # add further files to file list (open on request/itemClicked)
        for f in files[cachesize:]:
            self.add_to_flist(f, tag, FILE)

        if errors:
            self.showError('Some files could not be opened:\n\n' +
                           '\n'.join(errors))

    @pyqtSlot()
    def on_actionUnzoom_triggered(self):
        self.widget.unzoom()

    @pyqtSlot()
    def on_actionPrint_triggered(self):
        self.widget.printDialog()

    @pyqtSlot()
    def on_actionSavePlot_triggered(self):
        self.widget.savePlot()

    @pyqtSlot()
    def on_actionLogScale_triggered(self):
        for widget in self._get_all_widgets():
            widget.logscale(self.actionLogScale.isChecked())

    @pyqtSlot()
    def on_actionMarkCenter_triggered(self):
        flag = self.actionMarkCenter.isChecked()
        for widget in self._get_all_widgets():
            widget.setCenterMark(flag)

    @pyqtSlot()
    def on_actionKeepRatio_triggered(self):
        self.widget.gr.setAdjustSelection(self.actionKeepRatio.isChecked())


class ImagingLiveDataPanel(LiveDataPanel):

    def on_client_connected(self):
        LiveDataPanel.on_client_connected(self)
        datapath = self.client.eval('session.experiment.datapath', '')
        if not datapath or not path.isdir(datapath):
            return
        for fn in sorted(os.listdir(datapath)):
            if fn.endswith('.fits'):
                self.add_to_flist(path.join(datapath, fn), 'fits', FILE)

    def setLiveItems(self, n):
        pass  # No live entries for the imaging instruments
