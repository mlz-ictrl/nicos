#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
from os import path
from collections import OrderedDict
from uuid import uuid4

import numpy

from PyQt4.QtGui import QStatusBar, QSizePolicy, QListWidgetItem, QMenu, \
    QToolBar, QActionGroup, QFileDialog
from PyQt4.QtCore import QByteArray, QPoint, Qt, SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig
from gr import COLORMAPS as GR_COLORMAPS
from qtgr.events import GUIConnector
from qtgr.events.mouse import MouseEvent

from nicos.utils import BoundedOrderedDict
from nicos.clients.gui.utils import loadUi, enumerateWithProgress
from nicos.clients.gui.panels import Panel
from nicos.core.errors import NicosError
from nicos.guisupport.livewidget import IntegralLiveWidget, LiveWidget, \
    LiveWidget1D, DATATYPES
from nicos.protocols.cache import cache_load
from nicos.utils import ReaderRegistry
from nicos.pycompat import iteritems

COLORMAPS = OrderedDict(GR_COLORMAPS)

FILENAME = Qt.UserRole
FILEFORMAT = Qt.UserRole + 1
FILETAG = Qt.UserRole + 2
FILEUID = Qt.UserRole + 3


class LiveDataPanel(Panel):
    panelName = 'Live data view'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'live.ui', 'panels')

        self._allowed_tags = set()
        self._allowed_detectors = set()
        self._ignore_livedata = False  # ignore livedata, e.g. wrong detector
        self._last_tag = None
        self._last_fname = None
        self._last_format = None
        self._runtime = 0
        self._no_direct_display = False
        self._range_active = False
        self._cachesize = 20
        self._livewidgets = {}  # livewidgets for rois: roi_key -> widget
        self._fileopen_filter = None
        self.widget = None

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.toolbar = QToolBar('Live data')
        self.toolbar.addAction(self.actionOpen)
        self.toolbar.addAction(self.actionPrint)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionLogScale)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionKeepRatio)
        self.toolbar.addAction(self.actionUnzoom)
        self.toolbar.addAction(self.actionColormap)
        self.toolbar.addAction(self.actionMarkCenter)

        # self.widget.setControls(Logscale | MinimumMaximum | BrightnessContrast |
        #                         Integrate | Histogram)

        self.liveitem = QListWidgetItem('<Live>', self.fileList)
        self.liveitem.setData(FILENAME, '')
        self.liveitem.setData(FILEFORMAT, '')

        self.splitter.restoreState(self.splitterstate)

        if hasattr(self.window(), 'closed'):
            self.window().closed.connect(self.on_closed)
        self.connect(client, SIGNAL('livedata'), self.on_client_livedata)
        self.connect(client, SIGNAL('liveparams'), self.on_client_liveparams)
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('cache'), self.on_cache)

        self.rois = {}
        self.detectorskey = None

    def initLiveWidget(self, widgetcls):
        if isinstance(self.widget, widgetcls):
            return

        if self.widget:
            self.widgetLayout.removeWidget(self.widget)
        self.widget = widgetcls(self)
        # set keep ratio defaults for new livewidget instances
        if isinstance(self.widget, LiveWidget1D):
            if self.actionKeepRatio.isChecked():
                self.actionKeepRatio.trigger()
        elif not self.actionKeepRatio.isChecked():
            self.actionKeepRatio.trigger()
        # apply current settings
        self.widget.setCenterMark(self.actionMarkCenter.isChecked())
        self.widget.logscale(self.actionLogScale.isChecked())
        guiConn = GUIConnector(self.widget.gr)
        guiConn.connect(MouseEvent.MOUSE_MOVE, self.on_mousemove_gr)

        self.menuColormap = QMenu(self)
        self.actionsColormap = QActionGroup(self)
        activeMap = self.widget.getColormap()
        for name, value in iteritems(COLORMAPS):
            caption = name.title()
            action = self.menuColormap.addAction(caption)
            action.setCheckable(True)
            if activeMap == value:
                action.setChecked(True)
                self.actionColormap.setText(caption)
            self.actionsColormap.addAction(action)
            action.triggered.connect(self.on_colormap_triggered)
        self.actionColormap.setMenu(self.menuColormap)
        self.widgetLayout.addWidget(self.widget)
        detectors = self.client.eval('session.experiment.detectors', [])
        self._register_rois(detectors)

    def setOptions(self, options):
        Panel.setOptions(self, options)
        # configure instrument specific behavior
        self._instrument = options.get('instrument', '')
        # self.widget.setInstrumentOption(self._instrument)
        # if self._instrument == 'toftof':
        #     self.widget.setAxisLabels('time channels', 'detectors')
        # elif self._instrument == 'imaging':
        #     self.widget.setControls(ShowGrid | Logscale | Grayscale |
        #                             Normalize | Darkfield | Despeckle |
        #                             CreateProfile | Histogram | MinimumMaximum)
        #     self.widget.setStandardColorMap(True, False)
        # configure allowed file types
        supported_filetypes = ReaderRegistry.filetypes()
        opt_filetypes = set(options.get('filetypes', supported_filetypes))
        self._allowed_tags = opt_filetypes & set(supported_filetypes)

        # configure allowed detector device names
        detectors = options.get('detectors')
        if detectors:
            self._allowed_detectors = set(detectors)

        # configure caching
        self._cachesize = options.get('cachesize', self._cachesize)
        if self._cachesize < 1:
            self._cachesize = 1  # always cache the last live image
        self._datacache = BoundedOrderedDict(maxlen=self._cachesize)
        # active connection
        if self.client.connected:
            self.on_client_connected()

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', b'', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('geometry', self.saveGeometry())

    def getMenus(self):
        self.menu = menu = QMenu('&Live data', self)
        menu.addAction(self.actionOpen)
        menu.addAction(self.actionPrint)
        menu.addSeparator()
        menu.addAction(self.actionKeepRatio)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionColormap)
        menu.addAction(self.actionMarkCenter)
        return [menu]

    def getToolbars(self):
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
        for widget in [self.widget] + self._livewidgets.values():
            widget.setColormap(COLORMAPS[action.text().upper()])
        name = action.text()
        self.actionColormap.setText(name[0] + name[1:].lower())

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
            for name, roi in iteritems(self.rois):
                widget.setROI(name, roi)
            width = max(region.x) - min(region.x)
            height = max(region.y) - min(region.y)
            if width > height:
                dwidth = 500
                dheight = 500 * height / width
            else:
                dheight = 500
                dwidth = 500 * width / height
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
        self.menuROI = QMenu(self)
        self.actionsROI = QActionGroup(self)
        self.actionsROI.setExclusive(False)
        for detname in detectors:
            self.log.debug('checking rois for detector \'%s\'', detname)
            for roi, _ in self.client.eval(detname + '.postprocess', ''):
                cachekey = roi + '/roi'
                key = cachekey.replace('/', '.')
                value = self.client.eval(key)
                self.on_roiChange(cachekey, value)
                self.log.debug('register roi: %s', roi)
                # create roi menu
                action = self.menuROI.addAction(roi)
                action.setCheckable(True)
                self.actionsROI.addAction(action)
                action.triggered.connect(self.on_roi_triggered)
                self.actionROI.setMenu(self.menuROI)
                if self.actionROI not in self.toolbar.actions():
                    self.toolbar.addAction(self.actionROI)
                    self.log.debug('add ROI menu')

    def on_actionROI_triggered(self):
        w = self.toolbar.widgetForAction(self.actionROI)
        self.actionROI.menu().popup(w.mapToGlobal(QPoint(0, w.height())))

    def on_roi_triggered(self):
        action = self.sender()
        roi = action.text()
        if action.isChecked():
            self.showRoiWindow(roi)
        else:
            self.closeRoiWindow(roi)

    def on_roiWindowClosed(self):
        widget = self.sender()
        if widget:
            key = None
            for key, w in iteritems(self._livewidgets):
                if w == widget:
                    self.log.debug('delete roi: %s', key)
                    del self._livewidgets[key]
                    break
            if key:
                roi = key.split('/')[0]
                for action in self.actionsROI.actions():
                    if action.text() == roi:
                        action.setChecked(False)
                        self.log.debug('uncheck roi: %s', roi)

    def on_roiChange(self, key, value):
        self.log.debug('on_roiChange: %s %s', key, (value,))
        self.rois[key] = value
        for widget in [self.widget] + self._livewidgets.values():
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
        self.client.tell('eventunmask', ['livedata', 'liveparams'])
        datapath = self.client.eval('session.experiment.datapath', '')
        if not datapath or not path.isdir(datapath):
            return
        if self._instrument == 'imaging':
            for fn in sorted(os.listdir(datapath)):
                if fn.endswith('.fits'):
                    self.add_to_flist(path.join(datapath, fn), '', 'fits',
                                      False)
        self.detectorskey = (self.client.eval('session.experiment.name')
                             + '/detlist').lower()

    def on_client_liveparams(self, params):
        # TODO: remove compatibility code
        if len(params) == 7:  # Protocol version < 16
            tag, fname, dtype, nx, ny, nz, runtime = params
            uid, det = None, None
        elif len(params) == 9:  # Protocol version >= 16
            tag, uid, det, fname, dtype, nx, ny, nz, runtime = params

        if self._allowed_detectors and det not in self._allowed_detectors:
            self._ignore_livedata = True
            return
        self._ignore_livedata = False
        self._runtime = runtime
        self._last_uid = uid
        if dtype:
            self._last_fname = None
            normalized_type = numpy.dtype(dtype).str
            if normalized_type not in DATATYPES:
                self._last_format = None
                self.log.warning('Unsupported live data format: %s', (params,))
                return
            self._last_format = normalized_type
        elif fname:
            self._last_fname = fname
            self._last_format = None
        self._last_tag = tag.lower()
        self._nx = nx
        self._ny = ny
        self._nz = nz

    def _initLiveWidget(self, array):
        """Initialize livewidget based on array's shape"""
        if len(array.shape) == 1:
            widgetcls = LiveWidget1D
        else:
            widgetcls = IntegralLiveWidget
        self.initLiveWidget(widgetcls)

    def setData(self, array, uid=None, display=True):
        """Dispatch data array to corresponding live widgets.
        Cache array based on uid parameter. No caching if uid is ``None``.
        """
        if uid:
            if uid not in self._datacache:
                self.log.debug('add to cache: %s', uid)
            self._datacache[uid] = array
        if display:
            self._initLiveWidget(array)
            for widget in [self.widget] + self._livewidgets.values():
                widget.setData(array)

    def setDataFromFile(self, filename, tag, uid=None, display=True):
        """Load data array from file and dispatch to live widgets using
        ``setData``. Do not use caching if uid is ``None``.
        """
        try:
            array = ReaderRegistry.getReaderCls(tag).fromfile(filename)
        except KeyError:
            raise NicosError('Unsupported fileformat %r' % tag)
        if array is not None:
            self.setData(array, uid, display=display)
        else:
            raise NicosError('Cannot read file %r' % filename)

    def on_client_livedata(self, data):
        # but display it right now only if on <Live> setting and no ignore
        if self._no_direct_display or self._ignore_livedata:
            return

        # always allow live data
        if self._last_tag in self._allowed_tags or self._last_tag == 'live':
            if len(data) and self._last_format:  # pylint: disable=len-as-condition
                # we got live data with a specified format
                array = numpy.frombuffer(data, self._last_format)
                if self._nz > 1:
                    array = array.reshape((self._nz, self._ny, self._nx))
                elif self._ny > 1:
                    array = array.reshape((self._ny, self._nx))
                self.setData(array, self._last_uid)
            elif self._last_fname:
                # we got no live data, but a filename with the data
                # filename corresponds to full qualififed path here
                self.add_to_flist(self._last_fname, self._last_format,
                                  self._last_tag, self._last_uid)
                try:
                    self.setDataFromFile(self._last_fname,
                                         self._last_tag,
                                         self._last_uid)
                except Exception as e:
                    if self._last_uid in self._datacache:
                        # image is already cached
                        # suppress error message for cached image
                        self.log.debug(e)
                    else:
                        # image is not cached and could not be loaded
                        self.log.exception(e)

    def remove_obsolete_cached_files(self):
        """Removes outdated cached files from the file list or set cached flag
        to False if the file is still available on the filesystem.
        """
        cached_item_rows = []
        for row in range(self.fileList.count()):
            item = self.fileList.item(row)
            if item.data(FILEUID):
                cached_item_rows.append(row)
        if len(cached_item_rows) > self._cachesize:
            for row in cached_item_rows[0:-self._cachesize]:
                item = self.fileList.item(row)
                self.log.debug('remove from cache %s %s',
                               item.data(FILEUID), item.data(FILENAME))
                if path.isfile(item.data(FILENAME)):
                    item.setData(FILEUID, None)
                else:
                    self.fileList.takeItem(row)

    def add_to_flist(self, filename, fformat, ftag, uid=None, scroll=True):
        shortname = path.basename(filename)
        item = QListWidgetItem(shortname)
        item.setData(FILENAME, filename)
        item.setData(FILEFORMAT, fformat)
        item.setData(FILETAG, ftag)
        item.setData(FILEUID, uid)
        self.fileList.insertItem(self.fileList.count() - 1, item)
        if uid:
            self.remove_obsolete_cached_files()
        if scroll:
            self.fileList.scrollToBottom()
        return item

    def on_fileList_itemClicked(self, item):
        if item is None:
            return
        elif item == self.liveitem:
            self._no_direct_display = False
            return

        fname = item.data(FILENAME)
        ftag = item.data(FILETAG)
        uid = item.data(FILEUID)
        if not fname:
            # show always latest live image
            self._no_direct_display = False
            if self._last_fname and self._last_tag in self._allowed_tags:
                fname = self._last_fname
                ftag = self._last_tag
        else:
            # show image from file
            self._no_direct_display = True
        if uid:
            array = self._datacache.get(uid, None)
            if array is not None and array.size:
                self.setData(array)
                return
        self.setDataFromFile(fname, ftag)

    def on_fileList_currentItemChanged(self, item, previous):
        self.on_fileList_itemClicked(item)

    @qtsig('')
    def on_actionOpen_triggered(self):
        """Open image file using registered reader classes."""
        ftypes = dict((ffilter, ftype)
                      for ftype, ffilter in ReaderRegistry.filefilters())
        fdialog = QFileDialog(self, "Open data files", "",
                              ";;".join(ftypes.keys()))
        fdialog.setAcceptMode(QFileDialog.AcceptOpen)
        fdialog.setFileMode(QFileDialog.ExistingFiles)
        if self._fileopen_filter:
            fdialog.selectNameFilter(self._fileopen_filter)
        if fdialog.exec_() == QFileDialog.Accepted:
            self._fileopen_filter = fdialog.selectedNameFilter()
            tag = ftypes[self._fileopen_filter]
            files = fdialog.selectedFiles()
            if files:
                def _cacheFile(fn, tag):
                    uid = uuid4()
                    # setDataFromFile may raise an `NicosException`, e.g.
                    # if the file cannot be opened.
                    self.setDataFromFile(fn, tag, uid, display=False)
                    return self.add_to_flist(fn, None, tag, uid)

                # load and display first item
                f = files.pop(0)
                self.fileList.setCurrentItem(_cacheFile(f, tag))
                cachesize = self._cachesize - 1
                # add first `cachesize` files to cache
                for _, f in enumerateWithProgress(files[:cachesize],
                                                  "Loading data files...",
                                                  parent=fdialog):
                    _cacheFile(f, tag)
                # add further files to file list (open on request/itemClicked)
                for f in files[cachesize:]:
                    self.add_to_flist(f, None, tag)


    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.widget.unzoom()

    @qtsig('')
    def on_actionPrint_triggered(self):
        self.widget.printDialog()

    @qtsig('')
    def on_actionLogScale_triggered(self):
        for widget in [self.widget] + self._livewidgets.values():
            widget.logscale(self.actionLogScale.isChecked())

    @qtsig('')
    def on_actionMarkCenter_triggered(self):
        flag = self.actionMarkCenter.isChecked()
        for widget in [self.widget] + self._livewidgets.values():
            widget.setCenterMark(flag)

    @qtsig('')
    def on_actionKeepRatio_triggered(self):
        self.widget.gr.setAdjustSelection(self.actionKeepRatio.isChecked())
