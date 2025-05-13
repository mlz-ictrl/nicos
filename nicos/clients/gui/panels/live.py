# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS livewidget with GR."""

import copy
import os
from collections import OrderedDict
from os import path
from uuid import uuid4

import numpy
from gr import COLORMAPS as GR_COLORMAPS

from nicos.clients.gui.dialogs.filesystem import FileFilterDialog
from nicos.clients.gui.panels.plot import PlotPanel
from nicos.clients.gui.utils import enumerateWithProgress, loadUi, uipath
from nicos.core.constants import FILE, LIVE
from nicos.core.errors import NicosError
from nicos.guisupport.livewidget import AXES, DATATYPES, IntegralLiveWidget, \
    LiveWidget, LiveWidget1D
from nicos.guisupport.qt import QActionGroup, QByteArray, QDialog, \
    QFileDialog, QListWidgetItem, QMenu, QPoint, QSizePolicy, QStatusBar, Qt, \
    QToolBar, QWidget, pyqtSignal, pyqtSlot
from nicos.guisupport.qtgr import MouseEvent
from nicos.guisupport.utils import waitCursor
from nicos.protocols.cache import cache_load
from nicos.utils import BoundedOrderedDict, ReaderRegistry, safeName

try:
    from nicos.utils.gammafilter import gam_rem_adp_log
except ImportError:
    gam_rem_adp_log = None

try:
    from colorcet import mapping_flipped as cet_mapping_flipped
except ImportError:
    cet_mapping_flipped = None

COLORMAPS = OrderedDict(GR_COLORMAPS)

FILENAME = Qt.ItemDataRole.UserRole
FILETYPE = Qt.ItemDataRole.UserRole + 1
FILETAG = Qt.ItemDataRole.UserRole + 2
FILEUID = Qt.ItemDataRole.UserRole + 3

DEFAULTS = dict(
    marks='solidcircle',
    offset=0,
    plotcount=1,
    colors='blue',
    markersize=1,
)


def readDataFromFile(filename, filetype):
    try:
        return ReaderRegistry.getReaderCls(filetype).fromfile(filename)
    except KeyError:
        raise NicosError('Unsupported file format %r' % filetype) from None


class LiveDataPanel(PlotPanel):
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
    * ``xscale`` - (default 'binary') - Scaling algorithm for the x-axis
      ('binary' or 'decimal')
    * ``yscale`` - (default 'binary') - Scaling algorithm for the y-axis
      ('binary' or 'decimal')
    * ``defaults`` (default []) - List of strings representing options to be
      set for every configured plot.
      These options cannot be set on a per-plot basis since they are global.
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
      * ``marks`` (default 'solidcircle') - Shape of the markers (if displayed).
        Possible values are:

          'dot', 'plus', 'asterrisk', 'circle', 'diagonalcross', 'solidcircle',
          'triangleup', 'solidtriangleup', 'triangledown', 'solidtriangledown',
          'square', 'solidsquare', 'bowtie', 'solidbowtie', 'hourglass',
          'solidhourglass', 'diamond', 'soliddiamond', 'star', 'solidstar',
          'triupdown', 'solidtriright', 'solidtrileft', 'hollowplus',
          'solidplus', 'pentagon', 'hexagon', 'heptagon', 'octagon', 'star4',
          'star5', 'star6', 'star7', 'star8', 'vline', 'hline', 'omark'

      * ``markersize`` (default 1) - Size of the markers (if displayed).
      * ``offset`` (default 0) - Offset for the X-axis labels of
        each curve in 1D plots.
      * ``colors`` (default ['blue']) - Color of the marks and lines
        (if displayed).
        If colors are set as a list the colors will be applied to the
        individual plots (and default back to blue when wrong/missing),
        for example:

        ['red', 'green']: The first plot will be red, the second green and
        the others will be blue (default).

        'red': all plots will be red.

      * ``use_cet`` (default False) - If True and the colorcet library is
        installed extend the available colormaps with the colorcet maps.

    A user-defined colormap file must be composed of three columns (R,G,B)
    normalised to 1 or in the range 0-255, e.g.:

    6.50e-01 8.07e-01 8.90e-01
    1.21e-01 4.70e-01 7.05e-01
    2.00e-01 6.27e-01 1.72e-01
    9.84e-01 6.03e-01 5.99e-01
    9.92e-01 7.49e-01 4.35e-01
    1.00e+00 4.98e-01 0.00e+00
    4.15e-01 2.39e-01 6.03e-01
    1.00e+00 1.00e+00 5.99e-01
    6.94e-01 3.49e-01 1.56e-01

    or

    255 255 255
    251 255 255
    86 215 255
    84 213 255
    80 209 255
    77 205 255
    0 0 8
    0 0 6
    0 0 0

    If less than 256 colors are provided the colors intensities are linear
    interpolated.
    """

    panelName = 'Live data view'

    ui = path.join(uipath, 'panels', 'live.ui')

    def __init__(self, parent, client, options):
        PlotPanel.__init__(self, parent, client, options)
        loadUi(self, self.ui)

        self._allowed_filetypes = set()
        self._allowed_detectors = set()
        self._range_active = False
        self._cachesize = 20
        self._livewidgets = {}  # livewidgets for rois: roi_key -> widget
        self._fileopen_filter = None
        self.widget = None
        self.menu = None
        self.unzoom = False
        self.lastSettingsIndex = None
        self._axis_labels = {}
        self._offset = 0
        self.xscale = options.get('xscale', 'binary')
        self.yscale = options.get('yscale', 'binary')

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.menuROI = QMenu(self)
        self.actionROI = self.menuROI.menuAction()
        self.actionROI.setText('&Region Of Interest')
        self.actionROI.setToolTip('Open region of interest in seperate window')
        self.actionROI.triggered.connect(self.on_actionROI_triggered)

        self.menuColormap = QMenu(self)
        self.actionColormap = self.menuColormap.menuAction()
        self.actionColormap.setText('&Colormap')
        self.actionColormap.setToolTip('Select colormap')
        self.actionColormap.triggered.connect(self.on_actionColormap_triggered)

        self.toolbar = QToolBar('Live data')
        self.toolbar.addAction(self.actionOpen)
        self.toolbar.addAction(self.actionPrint)
        self.toolbar.addAction(self.actionSavePlot)
        self.toolbar.addAction(self.actionAttachElog)
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
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

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
        self._allowed_filetypes = opt_filetypes & set(supported_filetypes)

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

        self._initControlsGUI()

        if options.get('use_cet', False) and cet_mapping_flipped:
            COLORMAPS.update(OrderedDict(
                {v: k for k, v in cet_mapping_flipped.items()}))

    def _initControlsGUI(self):
        pass

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
                item.setData(FILETYPE, '')
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

    def _initColormapMenu(self):
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

        def from_file():
            fname = QFileDialog.getOpenFileName(self, 'Open file')
            self.widget.surf.colormap = fname[0]
            self.toolbar.widgetForAction(self.actionColormap).setText(
                'Custom')

        action = self.menuColormap.addAction('From file')
        action.setStatusTip('Open new colormap')
        action.triggered.connect(from_file)
        self.actionsColormap.addAction(action)
        return activeCaption

    def initLiveWidget(self, widgetcls):
        if isinstance(self.widget, widgetcls):
            return

        # delete the old widget
        if self.widget:
            self.widgetLayout.removeWidget(self.widget)
            self.widget.deleteLater()

        # create a new one
        self.widget = widgetcls(self, xscale=self.xscale, yscale=self.yscale)
        self.currentPlot = self.widget.gr

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
        activeCaption = self._initColormapMenu()

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
            menu.addAction(self.actionAttachElog)
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

    @pyqtSlot()
    def on_actionAttachElog_triggered(self):
        self.attachElogDialogExec(
            safeName('data_' + self.fileList.currentItem().data(FILEUID))
        )

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

            # update with current data
            data = self.getDataFromItem(self.fileList.currentItem())
            if data is not None:
                widget.setData(data['dataarrays'], data.get('labels'))

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
        for w in list(self._livewidgets.values()):
            w.close()

    def _register_rois(self, detectors):
        self.rois.clear()
        self.actionROI.setVisible(False)
        self.actionsROI = QActionGroup(self)
        self.actionsROI.setExclusive(False)
        for detname in detectors:
            self.log.debug("checking rois for detector '%s'", detname)
            for tup in self.client.eval(detname + '.postprocess', ''):
                roi = tup[0]
                cachekey = roi + '/roi'
                # check whether this is a roi (cachekey exists).
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
                    del self._livewidgets[key]  # pylint: disable=unnecessary-dict-index-lookup
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
        elif key == self._detectorskey() and self.widget:
            self._register_rois(value)

    def _detectorskey(self):
        if self.detectorskey is None:
            self.detectorskey = self._query_detectorskey()
        return self.detectorskey

    def _query_detectorskey(self):
        try:
            return ('%s/detlist' % self.client.eval(
                'session.experiment.name')).lower()
        except AttributeError:
            pass

    def on_client_connected(self):
        self.client.tell('eventunmask', ['livedata'])
        self.detectorskey = self._query_detectorskey()

    def normalizeType(self, dtype):
        normalized_type = numpy.dtype(dtype).str
        if normalized_type not in DATATYPES:
            self.log.warning('Unsupported live data format: %s',
                             normalized_type)
            return
        return normalized_type

    def getIndexedUID(self, params, idx):
        return str(params['uid']) + '-' + str(idx)

    def _process_axis_labels(self, params, blobs):
        """Convert the raw axis label descriptions.
        tuple: `from, to`: Distribute labels equidistantly between the two
                           values.
        numbertype: `index into labels`: Actual labels are provided.
                                         Value is the starting index.
                                         Extract from first available blob.
                                         Remove said blob from list.
        None: `default`: Start at 0 with step width 1.

        Save the axis labels to the datacache.
        """

        CLASSIC = {'define': 'classic'}

        for i, datadesc in enumerate(params['datadescs']):
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
                # TODO: xoffset and yoffset ?
                labels[axis] += self._offset if axis == 'x' else 0
                titles[axis] = label.get('title')

            # save the labels in the datacache with uid as key
            uid = self.getIndexedUID(params, i)
            if uid not in self._datacache:
                self._datacache[uid] = {}

            self._datacache[uid]['labels'] = labels
            self._datacache[uid]['titles'] = titles

    def _process_livedata(self, params, data, idx):
        # ignore irrelevant data in liveOnly mode
        if self._liveOnlyIndex is not None and idx != self._liveOnlyIndex:
            return

        try:
            descriptions = params['datadescs']
        except KeyError:
            self.log.warning('Livedata with tag "Live" without '
                             '"datadescs" provided.')
            return

        # pylint: disable=len-as-condition
        if len(data):
            # we got live data with specified formats
            arrays = self.processDataArrays(
                params, idx, numpy.frombuffer(data, descriptions[idx]['dtype']))

            if arrays is None:
                return

            # cache and update displays
            uid = self.getIndexedUID(params, idx)
            self.setData(arrays, uid=uid, display=(idx == self._livechannel))
            self.liveitems[idx].setData(FILEUID, uid)

    def _process_filenames(self, params):
        # TODO: allow multiple fileformats?
        #       would need to modify input from DemonSession.notifyDataFile

        for i, filedesc in enumerate(params['filedescs']):
            # uids must match with uids in live events (_process_livedata)
            uid = self.getIndexedUID(params, i)
            name = filedesc['filename']
            filetype = filedesc.get('fileformat')
            self.add_to_flist(name, filetype, FILE, uid)
            try:
                # update display for selected live channel,
                # just cache otherwise
                self.setDataFromFile(
                    name, filetype, uid, display=(i == self._livechannel))
            except Exception as e:
                if uid in self._datacache:
                    # image is already cached
                    # suppress error message for cached image
                    self.log.debug(e)
                else:
                    # image is not cached and could not be loaded
                    self.log.exception(e)

    def on_client_livedata(self, params, blobs):
        self.log.debug('on_client_livedata: %r', params)
        # blobs is a list of data blobs and labels blobs
        if self._allowed_detectors \
                and params['det'] not in self._allowed_detectors:
            return

        self._applyPlotSettings(params)
        if params['tag'] == LIVE:
            datacount = len(params['datadescs'])
            self.setLiveItems(datacount)

            self._process_axis_labels(params, blobs[datacount:])

            for i, blob in enumerate(blobs[:datacount]):
                # update cache and display if selected channel is a live channel
                self._process_livedata(params, blob, i)
            if not datacount:
                self._process_livedata(params, [], 0)
        elif params['tag'] == FILE:
            self._process_filenames(params)

    def getDefaultLabels(self, size):
        return numpy.arange(size)

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

    def setData(self, arrays, labels=None, titles=None, uid=None, display=True):
        """Dispatch data array to corresponding live widgets.
        Cache array based on uid parameter. No caching if uid is ``None``.
        """
        if uid:
            if uid not in self._datacache:
                self.log.debug('add to cache: %s', uid)
                self._datacache[uid] = {}
            self._datacache[uid]['dataarrays'] = arrays
            if titles is None:
                titles = self._datacache[uid].get('titles')
            else:
                self._datacache[uid]['titles'] = titles
            if labels is None:
                labels = self._datacache[uid].get('labels')
            else:
                self._datacache[uid]['labels'] = labels
        if display:
            self._initLiveWidget(arrays[0])
            for widget in self._get_all_widgets():
                widget.setData(arrays, labels)
                widget.setTitles(titles)

    def setDataFromFile(self, filename, filetype, uid=None, display=True):
        """Load data array from file and dispatch to live widgets using
        ``setData``. Do not use caching if uid is ``None``.
        """
        array = readDataFromFile(filename, filetype)
        if array is not None:
            self.setData([array], uid=uid, display=display)
            return array.shape
        else:
            raise NicosError('Cannot read file %r' % filename)

    def processDataArrays(self, params, index, entry):
        """Check if the input 1D array has the expected amount of values.
        If the array is too small an Error is raised.
        If the size exceeds the expected amount it is truncated.

        Returns a list of arrays corresponding to the ``plotcount`` of
        ``index`` into ``datadescs`` of the current params"""

        datadesc = params['datadescs'][index]

        # representing the number of arrays with 'shape', in particular size
        # || shape ||
        count = datadesc.get('plotcount', DEFAULTS['plotcount'])
        shape = datadesc['shape']

        # ignore irrelevant data in liveOnly mode
        if self._liveOnlyIndex is not None and index != self._liveOnlyIndex:
            return

        # determine 1D array size
        arraysize = numpy.prod(shape)

        # check and split the input array `entry` into `count` arrays of size
        # `arraysize`
        if len(entry) != count * arraysize:
            self.log.warning('Expected data array with %d entries, got %d',
                             count * arraysize, len(entry))
            return
        arrays = numpy.split(entry, count)

        # reshape every array in the list
        for i, array in enumerate(arrays):
            arrays[i] = array.reshape(shape)
        return arrays

    def applyPlotSettings(self, params=None):
        if not self.widget or not isinstance(self.widget, LiveWidget1D):
            return

        if self._liveOnlyIndex is not None:
            index = self._liveOnlyIndex
        elif self.fileList.currentItem() not in self.liveitems:
            return
        else:
            index = self.fileList.currentRow()

        if isinstance(self.widget, LiveWidget1D):
            def getElement(l, index, default):
                try:
                    return l[index]
                except IndexError:
                    return default

            settings = getElement(self.plotsettings, index, DEFAULTS)

            if params and params['tag'] == LIVE:
                plotcount = params['datadescs'][index].get(
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
            filetype = item.data(FILETYPE)

            if path.isfile(filename):
                rawdata = readDataFromFile(filename, filetype)
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

    def _applyPlotSettings(self, params):
        self.applyPlotSettings(params)

        if self.unzoom and self.widget:
            self.on_actionUnzoom_triggered()

    def _show(self, params=None, data=None):
        """Show the provided data. If no data has been provided extract it
        from the datacache via the current item's uid.

        :param data: dictionary containing 'dataarrays' and 'labels'
        """

        if self.fileList.currentRow() == -1:
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
        self._applyPlotSettings(params)
        self.setData(arrays, labels, titles)

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

    def add_to_flist(self, filename, filetype, tag, uid=None, scroll=True):
        # liveonly mode doesn't display a filelist
        if self._liveOnlyIndex is not None:
            return
        # no duplicate filenames
        if any(self.fileList.item(i).data(FILENAME) == filename
               for i in range(self.fileList.count())):
            return

        shortname = path.basename(filename)
        item = QListWidgetItem(shortname)
        item.setData(FILENAME, filename)
        item.setData(FILETYPE, filetype)
        item.setData(FILETAG, tag)
        item.setData(FILEUID, uid)
        self.fileList.insertItem(self.fileList.count(), item)
        if uid:
            self.remove_obsolete_cached_files()
        if scroll:
            self.fileList.scrollToBottom()
        return item

    def on_fileList_currentItemChanged(self):
        item = self.fileList.currentItem()
        if item is None:
            return

        if item in self.liveitems and item.data(FILETAG) == 'live':
            # set _livechannel to show live image
            self._livechannel = int(item.data(FILENAME))
            self.log.debug('set livechannel: %d', self._livechannel)
        else:
            # no live channel selected
            self._livechannel = None
            self.log.debug('no direct display')

        self._show()

    @pyqtSlot()
    def on_actionOpen_triggered(self):
        """Open image file using registered reader classes."""
        ftypes = {ffilter: ftype
                  for ftype, ffilter in ReaderRegistry.filefilters()
                  if not self._allowed_filetypes
                  or ftype in self._allowed_filetypes}
        fdialog = FileFilterDialog(self, 'Open data files', '',
                                   ';;'.join(ftypes.keys()))
        if self._fileopen_filter:
            fdialog.selectNameFilter(self._fileopen_filter)
        if fdialog.exec() != QDialog.DialogCode.Accepted:
            return
        files = fdialog.selectedFiles()
        if not files:
            return
        self._fileopen_filter = fdialog.selectedNameFilter()
        filetype = ftypes[self._fileopen_filter]
        errors = []

        def _cacheFile(fn, filetype):
            uid = uuid4()
            # setDataFromFile may raise an `NicosException`, e.g.
            # if the file cannot be opened.
            try:
                self.setDataFromFile(fn, filetype, uid, display=False)
            except Exception as err:
                errors.append('%s: %s' % (fn, err))
            else:
                return self.add_to_flist(fn, filetype, FILE, uid)

        # load and display first item
        f = files.pop(0)
        item = _cacheFile(f, filetype)
        if item is not None:
            self.fileList.setCurrentItem(item)
        cachesize = self._cachesize - 1
        # add first `cachesize` files to cache
        for _, f in enumerateWithProgress(files[:cachesize],
                                          'Loading data files...',
                                          parent=fdialog):
            _cacheFile(f, filetype)
        # add further files to file list (open on request/itemClicked)
        for f in files[cachesize:]:
            self.add_to_flist(f, filetype, FILE)

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


class AutoScaleLiveWidget1D(LiveWidget1D):

    def __init__(self, parent=None, **kwargs):
        kwargs['xscale'] = 'decimal'
        LiveWidget1D.__init__(self, parent, **kwargs)

    def getYMax(self):
        minupperedge = 1
        if self._arrays is not None:
            minupperedge = max(array.max() for array in self._arrays)
            minupperedge *= 2.15 if self._logscale else 1.05
        return minupperedge

    def getYMin(self):
        maxloweredge = 0.09 if self._logscale else 0
        if self._arrays is not None:
            maxloweredge = min(array.min() for array in self._arrays)
            maxloweredge *= 0.5 if self._logscale else 0.95
        return maxloweredge

    def _getNewYRange(self):
        ymax = self.getYMax()
        ymin = self.getYMin()
        return ymin, ymax, ymax


class ImagingLiveWidget(LiveWidget):

    amin = 0
    amax = 65535

    def setViewRange(self, zmin, zmax):
        self.amin = zmin
        self.amax = zmax

    def updateZData(self):
        arr = self._arrays[0].ravel()
        if self._logscale:
            arr = numpy.ma.log10(arr).filled(-1)
        amin, amax = arr.min(), arr.max()
        smin = min(amax, max(self.amin, amin))
        smax = max(amin, min(amax, self.amax))

        if smin != smax:
            self.surf.z = 1000 + 255 / (smax - smin) * (
                numpy.clip(arr, smin, smax) - smin)
        elif smax > 0:
            self.surf.z = 1000 + 255 / smax * arr
        else:
            self.surf.z = 1000 + arr


class ImagingControls(QWidget):
    """Controls the filtering for the imaging instruments."""

    controlsui = path.join(uipath, 'panels', 'imagecontrols.ui')

    changed = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        loadUi(self, self.controlsui)
        pos = self.layout().indexOf(self.histoPlot)
        # delete the old widget
        if self.histoPlot:
            self.layout().removeWidget(self.histoPlot)
            self.histoPlot.deleteLater()
        self.histoPlot = AutoScaleLiveWidget1D(self)
        self.histoPlot.setLines(True)
        self.histoPlot.setColormap(COLORMAPS['GRAYSCALE'])
        self.layout().insertWidget(pos, self.histoPlot)

        for w in [self.brtSlider, self.brtSliderLabel, self.ctrSlider,
                  self.ctrSliderLabel, self.xsumButton, self.ysumButton,
                  self.operationSelector, self.filterSelector,
                  self.profileButton, self.profileHideButton, self.cyclicBox,
                  self.profileWidth, self.profileWidthLabel, self.profileBins,
                  self.profileBinsLabel, self.logscaleBox, self.grayscaleBox,
                  self.despeckleValue, self.gridBox]:
            w.setHidden(True)

        self.maxSlider.valueChanged[int].connect(self.maxSliderMoved)
        self.minSlider.valueChanged[int].connect(self.minSliderMoved)
        self.maxSlider.sliderReleased.connect(self.showData)
        self.minSlider.sliderReleased.connect(self.showData)

        if not gam_rem_adp_log:
            self.despeckleBox.hide()
            self.despeckleValues.hide()
        else:
            self.despeckleWarningLabel.hide()
        self.despeckleBox.toggled.connect(self.showData)
        self.darkfieldBox.toggled.connect(self.showData)
        self.normalizeBox.toggled.connect(self.showData)

        self.thr3Value.valueChanged.connect(self.showData)
        self.thr5Value.valueChanged.connect(self.showData)
        self.thr7Value.valueChanged.connect(self.showData)

        self.autoScaling.stateChanged[int].connect(self.setAutoScale)

    @pyqtSlot()
    def showData(self):
        self.changed.emit()

    @pyqtSlot(int)
    def setAutoScale(self, state):
        if state:
            self.showData()

    def minValue(self):
        return self.minSlider.value()

    def maxValue(self):
        return self.maxSlider.value()

    def maxSliderMoved(self, value):
        if self.minSlider.value() > value:
            self.minSlider.setValue(value)

    def minSliderMoved(self, value):
        if self.maxSlider.value() < value:
            self.maxSlider.setValue(value)

    def setData(self, data, labels=None):
        if labels is None:
            labels = {}
        binnings = labels.get('x')
        if binnings is not None:
            _min, _max = round(binnings[0]), round(binnings[-1])
        else:
            _min, _max = 0, 65535
        self.minSlider.setMinimum(_min)
        self.maxSlider.setMinimum(_min)
        self.minSlider.setMaximum(_max)
        self.maxSlider.setMaximum(_max)
        self.histoPlot.setData(data, labels)

    def autoScale(self):
        return self.autoScaling.checkState()

    def setRange(self, minValue, maxValue):
        if self.maxValue() > minValue:
            self.minSlider.setSliderPosition(minValue)
            self.maxSlider.setSliderPosition(maxValue)
        else:
            self.maxSlider.setSliderPosition(maxValue)
            self.minSlider.setSliderPosition(minValue)

    def darkFieldData(self):
        return readDataFromFile(self.darkfieldFile.text(), 'fits')

    def normalizedData(self):
        return readDataFromFile(self.normalizedFile.text(), 'fits')

    def setDataRoot(self, dataroot):
        self.darkfieldFile.setText(path.join(dataroot, 'current',
                                             'currentdarkimage.fits'))
        self.normalizedFile.setText(path.join(dataroot, 'current',
                                              'currentopenbeamimage.fits'))

    def handleData(self, image):
        gammafilter = self.despeckleBox.checkState()
        if gammafilter:
            image = self._applyGammaFilter(image)
        darkfield = self.darkfieldBox.checkState()
        if darkfield:
            try:
                di = self.darkFieldData()
                if gammafilter:
                    di = self._applyGammaFilter(di)
            except FileNotFoundError:
                di = numpy.zeros(image.shape)
            image = numpy.subtract(image, di)
        if self.normalizeBox.checkState():
            try:
                ob = self.normalizedData()
                if gammafilter:
                    ob = self._applyGammaFilter(ob)
            except FileNotFoundError:
                ob = numpy.ones(image.shape)
            if darkfield:
                ob = numpy.subtract(ob, di)
                # set 0's to 1's to avoid division by 0 errors
                ob += (ob == 0).astype(ob.dtype)
            ob = numpy.array(ob, dtype=numpy.float64)
            image = numpy.divide(image, ob)
        return image

    def _applyGammaFilter(self, image):
        return gam_rem_adp_log(image, self.thr3Value.value(),
                               self.thr5Value.value(),
                               self.thr7Value.value(), 0.8)


class ImagingLiveDataPanel(LiveDataPanel):
    """
    Options:

    * ``spectra`` (default False) - Display summation in X and Y direction
    """

    def __init__(self, parent, client, options):
        if 'xscale' not in options:
            options['xscale'] = 'decimal'
        if 'yscale' not in options:
            options['yscale'] = 'decimal'
        LiveDataPanel.__init__(self, parent, client, options)
        self._spectra = options.get('spectra', False)
        self._initLiveWidget(None)

    def _initControlsGUI(self):
        self.controls = ImagingControls(self)
        self.splitter.addWidget(self.controls)
        self.controls.changed.connect(self.showData)

        self.histogram = None
        self._livechannel = -1

    def _showHistogram(self, data):
        if data is None:
            return
        arrays = data.get('dataarrays', [])
        if not arrays:
            return data

        arrs = [self.controls.handleData(img) for img in arrays]
        histogram, binedges = numpy.histogram(arrs[0].flatten(), 1024)
        self.controls.setData(histogram.reshape((1, histogram.size)),
                              labels={'x': binedges[:-1]})

        if self.controls.autoScale():
            cdf = histogram.cumsum()
            cdf_normalized = cdf.astype(numpy.float64) / cdf.max()
            maxValue = round(binedges[numpy.argmax(cdf_normalized > 0.99)])
            minValue = round(binedges[numpy.argmax(cdf_normalized > 0.01)])
            self.controls.setRange(minValue, maxValue)
        else:
            minValue = self.controls.minValue()
            maxValue = self.controls.maxValue()
        if self.widget:
            self.widget.setViewRange(minValue, maxValue)
        newdata = copy.deepcopy(data)
        newdata['dataarrays'] = arrs
        return newdata

    @pyqtSlot()
    def showData(self):
        idx = self.fileList.currentRow()
        if idx == -1:
            return
        with waitCursor():
            data = self.getDataFromItem(self.fileList.item(idx))
            data = self._showHistogram(data)
        LiveDataPanel._show(self, None, data)

    def _show(self, params=None, data=None):
        self.showData()

    def _initLiveWidget(self, array):
        if self._spectra:
            self.initLiveWidget(IntegralLiveWidget)
        else:
            self.initLiveWidget(ImagingLiveWidget)
        # Set the grayscale as default
        for action in self.actionsColormap.actions():
            if action.data().upper() == 'GRAYSCALE':
                action.trigger()
                break

    def on_client_connected(self):
        LiveDataPanel.on_client_connected(self)
        datapath = self.client.eval('session.experiment.datapath', '')
        if not datapath or not path.isdir(datapath):
            return
        dataroot = self.client.eval('session.experiment.dataroot', '')
        if dataroot:
            self.controls.setDataRoot(dataroot)
        last_item = None
        for fn in sorted(os.listdir(datapath)):
            if fn.endswith('.fits'):
                last_item = self.add_to_flist(
                    path.join(datapath, fn), 'fits', FILE, scroll=False)
        if last_item:
            self.fileList.currentItemChanged.emit(self.liveitems[0], last_item)

    def _upgrade_last(self, item):
        last_item = self.liveitems[0]
        last_item.setData(FILENAME, item.data(FILENAME))
        last_item.setData(FILETYPE, item.data(FILETYPE))
        last_item.setData(FILETAG, item.data(FILETAG))
        self._show()

    def add_to_flist(self, filename, filetype, tag, uid=None, scroll=True):
        item = LiveDataPanel.add_to_flist(
            self, filename, filetype, tag, uid, scroll)
        self._upgrade_last(item)
        return item

    def setLiveItems(self, n):
        LiveDataPanel.setLiveItems(self, 1)
        self.liveitems[0].setText('<Last>')
