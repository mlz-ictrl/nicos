#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************

"""NICOS livewidget 2D data plot window/panel."""

import os
import struct

import numpy

from os import path
from math import sin, radians, pi

from PyQt4.QtGui import QPrinter, QPrintDialog, QDialog, QMainWindow, \
    QMenu, QToolBar, QStatusBar, QSizePolicy, QListWidgetItem, QLabel, QFont, \
    QBrush, QPen, QComboBox, QVBoxLayout, QHBoxLayout, QFrame
from PyQt4.Qwt5 import QwtPlot, QwtPlotPicker, QwtPlotZoomer, QwtPlotCurve, \
    QwtPlotMarker, QwtSymbol
from PyQt4.QtCore import QByteArray, Qt, SIGNAL, SLOT
from PyQt4.QtCore import pyqtSignature as qtsig, QSize

from nicos.utils import BoundedOrderedDict
from nicos.clients.gui.utils import loadUi, DlgUtils
from nicos.clients.gui.panels import Panel

from nicoslivewidget import LWWidget, LWData, Logscale, MinimumMaximum, \
    BrightnessContrast, Integrate, Histogram, TYPE_FITS, ShowGrid, Grayscale, \
    Normalize, Darkfield, Despeckle, CreateProfile, TYPE_RAW, TYPE_TIFF

# the empty string means: no live data is coming, only the filename is important
DATATYPES = frozenset(('<u4', '<i4', '>u4', '>i4', '<u2', '<i2', '>u2', '>i2',
                       'u1', 'i1', 'f8', 'f4', ''))

FILETYPES = {'fits': TYPE_FITS, 'raw': TYPE_RAW, 'tiff': TYPE_TIFF, 'TIFF': TYPE_TIFF}


class LiveDataPanel(Panel):
    panelName = 'Live data view'
    bar = None
    menu = None

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
        self._cachesize = 20
        self._datacache = BoundedOrderedDict(maxlen=self._cachesize)
        self._datapathok = False

        self.statusBar = QStatusBar(self, sizeGripEnabled=False)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.widget = LWWidget(self)
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.widget.setControls(Logscale | MinimumMaximum | BrightnessContrast |
                                Integrate | Histogram)
        self.widgetLayout.addWidget(self.widget)

        self.liveitem = QListWidgetItem('<Live>', self.fileList)
        self.liveitem.setData(32, '')
        self.liveitem.setData(33, '')

        self.splitter.restoreState(self.splitterstate)

        self.connect(client, SIGNAL('livedata'), self.on_client_livedata)
        self.connect(client, SIGNAL('liveparams'), self.on_client_liveparams)
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('setup'), self.on_client_connected)

        self.connect(self.actionLogScale, SIGNAL("toggled(bool)"),
                     self.widget, SLOT("setLog10(bool)"))
        self.connect(self.widget,
                     SIGNAL('customContextMenuRequested(const QPoint&)'),
                     self.on_widget_customContextMenuRequested)
        self.connect(self.widget,
                     SIGNAL('profileUpdate(int, int, void*, void*)'),
                     self.on_widget_profileUpdate)

        self._toftof_profile = None

    def setOptions(self, options):
        Panel.setOptions(self, options)
        # configure instrument specific behavior
        self._instrument = options.get('instrument', '')
        self.widget.setInstrumentOption(self._instrument)
        if self._instrument == 'toftof':
            self.widget.setAxisLabels('time channels', 'detectors')
        elif self._instrument == 'imaging':
            self.widget.setControls(ShowGrid | Logscale | Grayscale |
                                    Normalize | Darkfield | Despeckle |
                                    CreateProfile | Histogram | MinimumMaximum)
        elif self._instrument == 'laue':
            self.widget.setControls(ShowGrid | Grayscale |
                                    Darkfield | Despeckle |
                                    CreateProfile | Histogram | MinimumMaximum)
            self.widget.setStandardColorMap(True, False)
        if self._instrument == 'dns':
            self.widget.setKeepAspect(False)
        else:
            self.widget.setKeepAspect(True)
        # configure allowed file types
        opt_filetypes = options.get('filetypes', list(FILETYPES))
        self._allowed_tags = set(opt_filetypes) & set(FILETYPES)

        # configure caching
        self._showcached = options.get('showcached', False)
        self._cachesize = options.get('cachesize', 20)
        if self._cachesize < 1:
            self._cachesize = 1  # always cache the last live image
        self._datacache = BoundedOrderedDict(maxlen=self._cachesize)
        if self.client.connected:
            self.on_client_connected()

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter', '', QByteArray)

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('geometry', self.saveGeometry())
        if self._toftof_profile:
            self._toftof_profile.close()

    def getMenus(self):
        if not self.menu:
            menu = QMenu('&Live data', self)
            menu.addAction(self.actionPrint)
            menu.addSeparator()
            menu.addAction(self.actionSetAsROI)
            menu.addAction(self.actionUnzoom)
            menu.addAction(self.actionLogScale)
            menu.addAction(self.actionNormalized)
            menu.addAction(self.actionLegend)
            self.menu = menu
        return [self.menu]

    def getToolbars(self):
        if not self.bar:
            bar = QToolBar('Live data')
            bar.addAction(self.actionPrint)
            bar.addSeparator()
            bar.addAction(self.actionLogScale)
            bar.addSeparator()
            bar.addAction(self.actionUnzoom)
            # bar.addAction(self.actionSetAsROI)
            self.bar = bar
        return [self.bar]

    def on_widget_customContextMenuRequested(self, point):
        self.menu.popup(self.mapToGlobal(point))

    def on_widget_profileUpdate(self, proftype, nbins, x, y):
        if self._instrument != 'toftof':
            return
        if self._toftof_profile is None:
            self._toftof_profile = ToftofProfileWindow(self)
        self._toftof_profile.update(proftype, nbins, x, y)
        self._toftof_profile.show()

    def on_client_connected(self):
        datapath = self.client.eval('session.experiment.datapath', '')
        if not datapath or not path.isdir(datapath):
            self._showcached = True  # always show  cached data if datapath is not accessible
            return
        if self._instrument == 'imaging':
            for fn in sorted(os.listdir(datapath)):
                if fn.endswith('.fits'):
                    self.add_to_flist(path.join(datapath, fn), '', 'fits', False)

    def on_client_liveparams(self, params):
        tag, fname, dtype, nx, ny, nz, runtime = params
        self._runtime = runtime
        normalized_type = numpy.dtype(dtype).str if dtype != '' else ''
        if not fname and normalized_type not in DATATYPES:
            self._last_format = self._last_fname = None
            self.log.warning('Unsupported live data format: %s' % (params,))
            return
        self._last_tag = tag.lower()
        self._last_fname = fname
        self._last_format = normalized_type
        self._nx = nx
        self._ny = ny
        self._nz = nz

    def on_client_livedata(self, data):
        d = None
        if self._last_fname:
            if path.isfile(self._last_fname) and self._last_tag in self._allowed_tags:
                # in the case of a filename, we add it to the list
                self.add_to_flist(self._last_fname, self._last_format, self._last_tag)
                d = LWData(self._last_fname)
            elif len(data) and self._last_format and self._last_tag in self._allowed_tags or self._last_tag == 'live':
                d = LWData(self._nx, self._ny, self._nz, self._last_format, data)
                self._datacache[self._last_fname] = (self._nx, self._ny, self._nz, self._last_format, data)
                if self._showcached:
                    self.add_to_flist(self._last_fname, self._last_format, self._last_tag, cached=True)
        # always allow live data
        if self._last_tag == 'live':
            if len(data) and self._last_format:
                # we got live data with a specified format
                d = LWData(self._nx, self._ny, self._nz, self._last_format, data)
        # but display it right now only if on <Live> setting
        if self._no_direct_display or not d:
            return
        self.widget.setData(d)

    def add_to_flist(self, filename, fformat, ftag, cached=False, scroll=True):
        shortname = path.basename(filename)
        item = QListWidgetItem(shortname)
        item.setData(32, filename)
        item.setData(33, fformat)
        item.setData(34, ftag)
        item.setData(35, cached)
        self.fileList.insertItem(self.fileList.count() - 1, item)
        if cached:
            self.del_obsolete_cached_data()

        if scroll:
            self.fileList.scrollToBottom()

    def del_obsolete_cached_data(self):
        cached_item_rows = list()
        for row in range(self.fileList.count()):
            item = self.fileList.item(row)
            if item.data(35):
                cached_item_rows.append(row)
        if len(cached_item_rows) > self._cachesize:
            for row in cached_item_rows[0:-self._cachesize]:
                self.fileList.takeItem(row)

    def on_fileList_itemClicked(self, item):
        if item is None:
            return
        fname = item.data(32)
        ftag = item.data(34)
        cached = item.data(35)
        if fname == '':
            # show always latest live image
            if self._no_direct_display:
                self._no_direct_display = False
                d = None
                if self._last_fname and path.isfile(self._last_fname) and \
                   self._last_tag in self._allowed_tags:
                    d = LWData(self._last_fname)
                elif len(self._datacache):
                    val = self._datacache.getlast()
                    d = LWData(*val)
                if d:
                    self.widget.setData(d)
        else:
            # show image from file
            self._no_direct_display = True
            if fname and str(ftag) in self._allowed_tags or str(ftag) == 'live':
                if cached:
                    d = self._datacache.get(fname, None)
                    if d:
                        self.widget.setData(LWData(*d))
                else:
                    self.widget.setData(LWData(fname))

    def on_fileList_currentItemChanged(self, item, previous):
        self.on_fileList_itemClicked(item)

    @qtsig('')
    def on_actionUnzoom_triggered(self):
        self.widget.plot().getZoomer().zoom(0)

    @qtsig('')
    def on_actionPrint_triggered(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOrientation(QPrinter.Landscape)
        printer.setOutputFileName('')
        if QPrintDialog(printer, self).exec_() == QDialog.Accepted:
            self.widget.plot().print_(printer)
            self.statusBar.showMessage('Plot successfully printed to %s.' %
                                       str(printer.printerName()))


class ToftofProfileWindow(QMainWindow, DlgUtils):
    def __init__(self, parent):
        QMainWindow.__init__(self, parent)
        DlgUtils.__init__(self, 'Live data')
        self.panel = parent
        layout1 = QVBoxLayout()
        self.plot = QwtPlot(self)
        layout1.addWidget(self.plot)
        self.curve = QwtPlotCurve()
        self.curve.setRenderHint(QwtPlotCurve.RenderAntialiased)
        self.curve.attach(self.plot)
        self.marker = QwtPlotMarker()
        self.marker.attach(self.plot)
        self.markerpen = QPen(Qt.red)
        self.marker.setSymbol(QwtSymbol(QwtSymbol.Ellipse, QBrush(),
                                        self.markerpen, QSize(7, 7)))
        self.zoomer = QwtPlotZoomer(self.plot.canvas())
        self.zoomer.setMousePattern(QwtPlotZoomer.MouseSelect3,
                                    Qt.NoButton)
        self.picker = QwtPlotPicker(self.plot.canvas())
        self.picker.setSelectionFlags(QwtPlotPicker.PointSelection |
                                      QwtPlotPicker.ClickSelection)
        self.picker.setMousePattern(QwtPlotPicker.MouseSelect1,
                                    Qt.MidButton)
        self.connect(self.picker, SIGNAL('selected(const QwtDoublePoint&)'),
                     self.pickerSelected)
        layout2 = QHBoxLayout()
        layout2.addWidget(QLabel('Scale:', self))
        self.scale = QComboBox(self)
        self.scale.addItems(['Single detectors, sorted by angle',
                             'Scattering angle 2theta (deg)',
                             'Q value (A-1)'])
        self.connect(self.scale, SIGNAL('currentIndexChanged(int)'),
                     self.scaleChanged)
        layout2.addWidget(self.scale)
        layout2.addStretch()
        self.scaleframe = QFrame(self)
        self.scaleframe.setLayout(layout2)
        self.scaleframe.setVisible(False)
        layout1.addWidget(self.scaleframe)
        mainframe = QFrame(self)
        mainframe.setLayout(layout1)
        self.setCentralWidget(mainframe)
        self.setContentsMargins(6, 6, 6, 6)
        plotfont = QFont(self.font())
        plotfont.setPointSize(plotfont.pointSize() * 0.7)
        self.plot.setAxisFont(QwtPlot.xBottom, plotfont)
        self.plot.setAxisFont(QwtPlot.yLeft, plotfont)
        self.plot.setCanvasBackground(Qt.white)
        self.resize(800, 200)

        self._detinfo = None
        self._anglemap = None
        self._infowindow = None
        self._infolabel = None
        self._xs = self._ys = None
        self._type = None

    def _retrieve_detinfo(self):
        if self._detinfo is None:
            info = self.panel.client.eval('det._detinfo_parsed, '
                                          'det._anglemap', None)
            if not info:
                return self.showError('Cannot retrieve detector info.')
            self._lambda = self.panel.client.eval('chWL()', None)
            if not self._lambda:
                return self.showError('Cannot retrieve wavelength.')
            self._detinfo, self._anglemap = info
            self._inverse_anglemap = 0
            self._infowindow = QMainWindow(self)
            self._infolabel = QLabel(self._infowindow)
            self._infolabel.setTextFormat(Qt.RichText)
            self._infowindow.setCentralWidget(self._infolabel)
            self._infowindow.setContentsMargins(10, 10, 10, 10)
            self._inv_anglemap = [
                [entry for entry in self._detinfo[1:]
                 if entry[12] == self._anglemap[detnr] + 1][0]
                for detnr in range(len(self._xs))
            ]

    def scaleChanged(self, scale):
        self.update(self._type, self._orig_nbins, self._orig_x, self._orig_y)

    def update(self, proftype, nbins, x, y):
        self._orig_x = x
        self._orig_y = y
        self._orig_nbins = nbins
        x.setsize(8 * nbins)
        y.setsize(8 * nbins)
        xs = struct.unpack('d' * nbins, x)
        ys = struct.unpack('d' * nbins, y)
        if proftype == 0:
            if self.scale.currentIndex() == 0:
                xs = xs
            elif self.scale.currentIndex() == 1:
                self._retrieve_detinfo()
                xs = [self._inv_anglemap[int(xi)][5] for xi in xs]
            else:
                self._retrieve_detinfo()
                if self._lambda is None:
                    self.showError('Could not determine wavelength.')
                    self.scale.setCurrentIndex(1)
                    return
                xs = [4 * pi / self._lambda *
                      sin(radians(self._inv_anglemap[int(xi)][5] / 2.))
                      for xi in xs]
        self._xs = xs
        self._ys = ys
        self.curve.setData(xs, ys)
        self.plot.setAxisAutoScale(QwtPlot.xBottom)
        self.plot.setAxisAutoScale(QwtPlot.yLeft)
        self.marker.setVisible(False)
        self.zoomer.setZoomBase(True)
        self._type = proftype
        if proftype == 0:
            self.setWindowTitle('Single detector view (time-channel integrated)')
            self.scaleframe.setVisible(True)
        elif proftype == 1:
            self.setWindowTitle('Time channel view (detector integrated)')
            self.scaleframe.setVisible(False)
        else:
            self.scaleframe.setVisible(False)

    def pickerSelected(self, point):
        if self._type != 0:
            return
        self._retrieve_detinfo()
        index = self.curve.closestPoint(self.picker.transform(point))[0]
        detentry = self._inv_anglemap[index][:]
        detentry.append(self._xs[index])
        detentry.append(self._ys[index])
        self.marker.setXValue(self._xs[index])
        self.marker.setYValue(self._ys[index])
        self.marker.setVisible(True)
        self.plot.replot()
        self._infowindow.show()
        entrynames = [
            'EntryNr', 'Rack', 'Plate', 'Pos', 'RPos',
            '2Theta', 'CableNr', 'CableType', 'CableLen', 'CableEmpty',
            'Card', 'Chan', 'Total', 'DetName', 'BoxNr', 'BoxChan',
            'XValue', 'Counts']
        formats = ['%s', '%d', '%d', '%d', '%d', '%.3f', '%d', '%d', '%.2f',
                   '%d', '%d', '%d', '%d', '%r', '%d', '%d', '%s', '%d']
        empties = [1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0]
        self._infolabel.setText(
            'Detector info:<br><table>' +
            ''.join('<tr><td>%s</td><td></td><td>%s</td></tr>%s' %
                    (name, format % value, '<tr></tr>' if empty else '')
                    for (name, format, empty, value)
                    in zip(entrynames, formats, empties, detentry)) +
            '</table>')

    def closeEvent(self, event):
        if self._infowindow:
            self._infowindow.close()
