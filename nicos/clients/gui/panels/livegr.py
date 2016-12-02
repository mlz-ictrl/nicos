#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

import numpy

from PyQt4.QtGui import QStatusBar, QSizePolicy, QListWidgetItem, QMenu, \
    QToolBar, QActionGroup
from PyQt4.QtCore import QByteArray, QPoint, Qt, SIGNAL
from PyQt4.QtCore import pyqtSignature as qtsig
from gr import COLORMAPS as GR_COLORMAPS

from nicos.clients.gui.utils import loadUi
from nicos.clients.gui.panels import Panel
from nicos.guisupport.livewidget import LiveWidget, Data, DATATYPES, FILETYPES
from nicos.protocols.cache import cache_load

COLORMAPS = OrderedDict(GR_COLORMAPS)

FILENAME = Qt.UserRole
FILEFORMAT = Qt.UserRole + 1
FILETAG = Qt.UserRole + 2


class LiveDataPanel(Panel):
    panelName = 'Live data view'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'live.ui', 'panels')

        self._allowed_tags = set()
        self._last_tag = None
        self._last_fname = None
        self._last_format = None
        self._runtime = 0
        self._no_direct_display = False
        self._range_active = False

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.widget = LiveWidget(self)

        self.menuColormap = QMenu(self)
        self.actionsColormap = QActionGroup(self)
        activeMap = self.widget.getColormap()
        for name, value in COLORMAPS.iteritems():
            caption = name[0] + name[1:].lower()
            action = self.menuColormap.addAction(caption)
            action.setCheckable(True)
            if activeMap == value:
                action.setChecked(True)
                self.actionColormap.setText(caption)
            self.actionsColormap.addAction(action)
            action.triggered.connect(self.on_colormap_triggered)
        self.actionColormap.setMenu(self.menuColormap)

        self.toolbar = QToolBar('Live data')
        self.toolbar.addAction(self.actionPrint)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionLogScale)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionUnzoom)
        self.toolbar.addAction(self.actionColormap)

        # self.widget.setControls(Logscale | MinimumMaximum | BrightnessContrast |
        #                         Integrate | Histogram)
        self.widgetLayout.addWidget(self.widget)

        self.liveitem = QListWidgetItem('<Live>', self.fileList)
        self.liveitem.setData(FILENAME, '')
        self.liveitem.setData(FILEFORMAT, '')

        self.splitter.restoreState(self.splitterstate)

        self.connect(client, SIGNAL('livedata'), self.on_client_livedata)
        self.connect(client, SIGNAL('liveparams'), self.on_client_liveparams)
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('cache'), self.on_cache)

        self.roikeys = []
        self.detectorskey = None

    def setOptions(self, options):
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
        opt_filetypes = set(options.get('filetypes', FILETYPES))
        self._allowed_tags = opt_filetypes & set(FILETYPES)
        if self.client.connected:
            self.on_client_connected()

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', b'', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('geometry', self.saveGeometry())

    def getMenus(self):
        self.menu = menu = QMenu('&Live data', self)
        menu.addAction(self.actionPrint)
        menu.addSeparator()
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionColormap)
        return [menu]

    def getToolbars(self):
        bar = QToolBar('Live data')
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionColormap)
        return [self.toolbar]

    def on_actionColormap_triggered(self):
        w = self.toolbar.widgetForAction(self.actionColormap)
        self.actionColormap.menu().popup(w.mapToGlobal(QPoint(0, w.height())))

    def on_colormap_triggered(self):
        action = self.actionsColormap.checkedAction()
        self.widget.setColormap(COLORMAPS[action.text().upper()])
        name = action.text()
        self.actionColormap.setText(name[0] + name[1:].lower())


    def _register_rois(self, detectors):
        self.roikeys = []
        for detname in detectors:
            self.log.debug('checking rois for detector \'%s\'', detname)
            for roi, _ in self.client.eval(detname + '.postprocess', ''):
                cachekey = roi + '/roi'
                self.roikeys.append(cachekey)
                key = cachekey.replace('/', '.')
                value = self.client.eval(key)
                self.on_roiChange(cachekey, value)
                self.log.debug('register roi: %s', roi)

    def on_roiChange(self, key, value):
        self.log.debug('on_roiChange: %s %s', key, (value,))
        self.widget.setROI(key, value)

    def on_cache(self, data):
        _time, key, _op, svalue = data
        try:
            value = cache_load(svalue)
        except ValueError:
            value = None
        if key in self.roikeys:
            self.on_roiChange(key, value)
        elif key == self.detectorskey:
            self._register_rois(value)

    def on_client_connected(self):
        self.client.tell('eventunmask', ['livedata', 'liveparams'])
        datapath = self.client.eval('session.experiment.datapath', '')
        if not path.isdir(datapath):
            return
        if self._instrument == 'imaging':
            for fn in sorted(os.listdir(datapath)):
                if fn.endswith('.fits'):
                    self.add_to_flist(path.join(datapath, fn), '', 'fits',
                                      False)
        self.detectorskey = (self.client.eval('session.experiment.name')
                             + '/detlist').lower()
        detectors = self.client.eval('session.experiment.detectors', [])
        self._register_rois(detectors)

    def on_client_liveparams(self, params):
        tag, fname, dtype, nx, ny, nz, runtime = params
        self._runtime = runtime
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

    def on_client_livedata(self, data):
        if self._last_fname and path.isfile(self._last_fname) and \
                        self._last_tag in self._allowed_tags:
            # in the case of a filename, we add it to the list
            self.add_to_flist(self._last_fname, self._last_format,
                              self._last_tag)
        # but display it right now only if on <Live> setting
        if self._no_direct_display:
            return
        # always allow live data
        if self._last_tag in self._allowed_tags or self._last_tag == 'live':
            if len(data) and self._last_format:
                # we got live data with a specified format
                self.widget.setData(
                    Data(self._nx, self._ny, self._nz, self._last_format, data))
            elif self._last_fname:
                # we got no live data, but a filename with the data
                self.widget.setData(Data.fromfile(self._last_fname,
                                                  self._last_tag))

    def add_to_flist(self, filename, fformat, ftag, scroll=True):
        shortname = path.basename(filename)
        item = QListWidgetItem(shortname)
        item.setData(FILENAME, filename)
        item.setData(FILEFORMAT, fformat)
        item.setData(FILETAG, ftag)
        self.fileList.insertItem(self.fileList.count() - 1, item)
        if scroll:
            self.fileList.scrollToBottom()

    def on_fileList_itemClicked(self, item):
        if item is None:
            return
        elif item == self.liveitem:
            self._no_direct_display = False
            return

        fname = item.data(FILENAME)
        ftag = item.data(FILETAG)
        if not fname:
            # show always latest live image
            self._no_direct_display = False
            if self._last_fname and self._last_tag in self._allowed_tags:
                fname = self._last_fname
                ftag = self._last_tag
        else:
            # show image from file
            self._no_direct_display = True
        self.widget.setData(Data.fromfile(fname, ftag))

    def on_fileList_currentItemChanged(self, item, previous):
        self.on_fileList_itemClicked(item)

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.widget.unzoom()

    @qtsig('')
    def on_actionPrint_triggered(self):
        self.widget.printDialog()
