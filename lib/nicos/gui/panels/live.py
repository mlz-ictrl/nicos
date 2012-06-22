#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

from __future__ import with_statement

__version__ = "$Revision$"

import struct
from math import sin, radians, pi

from PyQt4.QtCore import Qt, QVariant, SIGNAL, SLOT
from PyQt4.QtCore import pyqtSignature as qtsig, QSize
from PyQt4.QtGui import QPrinter, QPrintDialog, QDialog, QMainWindow, \
     QMenu, QToolBar, QStatusBar, QSizePolicy, QListWidgetItem, QLabel, QFont, \
     QBrush, QPen, QComboBox, QVBoxLayout, QHBoxLayout, QFrame
from PyQt4.Qwt5 import QwtPlot, QwtPlotPicker, QwtPlotZoomer, QwtPlotCurve, \
     QwtPlotMarker, QwtSymbol

from nicos.gui.utils import loadUi, DlgUtils
from nicos.gui.panels import Panel
from nicos.gui.livewidget import LWWidget, LWData, Logscale, \
     MinimumMaximum, BrightnessContrast, Integrate, Histogram

DATATYPES = frozenset(('<I4', '<i4', '>I4', '>i4', '<I2', '<i2', '>I2', '>i2',
                       'I1', 'i1', 'f8', 'f4'))


class LiveDataPanel(Panel):
    panelName = 'Live data view'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'live.ui', 'panels')

        self._format = None
        self._runtime = 0
        self._no_direct_display = False
        self._range_active = False

        self.statusBar = QStatusBar(self)
        policy = self.statusBar.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.Fixed)
        self.statusBar.setSizePolicy(policy)
        self.statusBar.setSizeGripEnabled(False)
        self.layout().addWidget(self.statusBar)

        self.widget = LWWidget(self)
        self.widget.setAxisLabels('time channels', 'detectors')
        self.widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.widget.setKeepAspect(False)
        self.widget.setControls(Logscale | MinimumMaximum | BrightnessContrast |
                                Integrate | Histogram)
        self.widgetLayout.addWidget(self.widget)

        self.liveitem = QListWidgetItem('<Live>', self.fileList)
        self.liveitem.setData(32, '')
        self.liveitem.setData(33, '')

        self.splitter.restoreState(self.splitterstate)

        self.connect(client, SIGNAL('livedata'), self.on_client_livedata)
        self.connect(client, SIGNAL('liveparams'), self.on_client_liveparams)
        if client.connected:
            self.on_client_connected()
        self.connect(client, SIGNAL('connected'), self.on_client_connected)

        self.connect(self.actionLogScale, SIGNAL("toggled(bool)"),
                     self.widget, SLOT("setLog10(bool)"))
        self.connect(self.widget,
                     SIGNAL('customContextMenuRequested(const QPoint&)'),
                     self.on_widget_customContextMenuRequested)
        self.connect(self.widget,
                     SIGNAL('profileUpdate(int, int, void*, void*)'),
                     self.on_widget_profileUpdate)

        self._toftof_profile = None

    def setSettings(self, settings):
        self._instrument = settings.get('instrument', '')
        self.widget.setInstrumentOption(self._instrument)

    def loadSettings(self, settings):
        self.splitterstate = settings.value('splitter').toByteArray()

    def saveSettings(self, settings):
        settings.setValue('splitter', self.splitter.saveState())
        settings.setValue('geometry', QVariant(self.saveGeometry()))
        if self._toftof_profile:
            self._toftof_profile.close()

    def getMenus(self):
        self.menu = menu = QMenu('&Live data', self)
        menu.addAction(self.actionPrint)
        menu.addSeparator()
        menu.addAction(self.actionSetAsROI)
        menu.addAction(self.actionUnzoom)
        menu.addAction(self.actionLogScale)
        menu.addAction(self.actionNormalized)
        menu.addAction(self.actionLegend)
        return [menu]

    def getToolbars(self):
        bar = QToolBar('Live data')
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        #bar.addAction(self.actionSetAsROI)
        return [bar]

    def on_widget_customContextMenuRequested(self, point):
        self.menu.popup(self.mapToGlobal(point))

    def on_widget_profileUpdate(self, type, nbins, x, y):
        if self._instrument != 'toftof':
            return
        if self._toftof_profile is None:
            self._toftof_profile = ToftofProfileWindow(self)
        self._toftof_profile.update(type, nbins, x, y)
        self._toftof_profile.show()

    def on_client_connected(self):
        pass
    #     datapath = self.client.eval('session.experiment.datapath', [])
    #     caspath = path.join(datapath[0], 'cascade')
    #     if path.isdir(caspath):
    #         for fn in sorted(os.listdir(caspath)):
    #             if fn.endswith('.pad'):
    #                 self.add_to_flist(path.join(caspath, fn), 'pad', False)
    #             elif fn.endswith('tof'):
    #                 self.add_to_flist(path.join(caspath, fn), 'tof', False)

    def on_client_liveparams(self, params):
        tag, fname, dtype, nx, ny, nz, runtime = params
        self._runtime = runtime
        if dtype not in DATATYPES:
            self._format = None
            print 'Unsupported live data format:', params
            return
        self._format = dtype
        self._nx = nx
        self._ny = ny
        self._nz = nz

    def on_client_livedata(self, data):
        if self._format:
            self.widget.setData(
                LWData(self._nx, self._ny, self._nz, self._format, data))

    #@qtsig('')
    #def on_actionSetAsROI_triggered(self):
    #    zoom = self.widget.plot().getZoomer().zoomRect()

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
                                    Qt.MiddleButton)
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
        self.setContentsMargins(5, 5, 5, 5)
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
            info = self.panel.client.eval('m._detinfo_parsed, m._anglemap', None)
            if info is None:
                return self.showError('Cannot retrieve detector info.')
            self._lambda = self.panel.client.eval('chWL()', None)
            self._detinfo, self._anglemap = info
            self._inverse_anglemap = 0
            self._infowindow = QMainWindow(self)
            self._infolabel = QLabel(self._infowindow)
            self._infolabel.setTextFormat(Qt.RichText)
            self._infowindow.setCentralWidget(self._infolabel)
            self._infowindow.setContentsMargins(10, 10, 10, 10)
            self._inv_anglemap = [
                [entry for entry in self._detinfo[1:]
                 if entry[12] == self._anglemap[detnr]+1][0]
                for detnr in range(len(self._xs))
            ]

    def scaleChanged(self, scale):
        self.update(self._type, self._orig_nbins, self._orig_x, self._orig_y)

    def update(self, type, nbins, x, y):
        self._orig_x = x
        self._orig_y = y
        self._orig_nbins = nbins
        x.setsize(8 * nbins)
        y.setsize(8 * nbins)
        xs = struct.unpack('d' * nbins, x)
        ys = struct.unpack('d' * nbins, y)
        if type == 0:
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
                xs = [4*pi/self._lambda*
                      sin(radians(self._inv_anglemap[int(xi)][5]/2.))
                      for xi in xs]
        self._xs = xs
        self._ys = ys
        self.curve.setData(xs, ys)
        self.plot.setAxisAutoScale(QwtPlot.xBottom)
        self.plot.setAxisAutoScale(QwtPlot.yLeft)
        self.zoomer.setZoomBase(True)
        self._type = type
        if type == 0:
            self.setWindowTitle('Single detector view (time-channel integrated)')
            self.scaleframe.setVisible(True)
        elif type == 1:
            self.setWindowTitle('Time channel view (detector integrated)')
            self.scaleframe.setVisible(False)
        else:
            self.scaleframe.setVisible(False)

    def pickerSelected(self, point):
        if self._type != 0:
            return
        self._retrieve_detinfo()
        index = self.curve.closestPoint(self.picker.transform(point))[0]
        detentry = self._inv_anglemap[index]
        self.marker.setXValue(self._xs[index])
        self.marker.setYValue(self._ys[index])
        self.plot.replot()
        self._infowindow.show()
        entrynames = [
            'EntryNr', 'Rack', 'Plate', 'Pos', 'RPos',
            '2Theta', 'CableNr', 'CableType', 'CableLen', 'CableEmpty',
            'Card', 'Chan', 'Total', 'DetName', 'BoxNr', 'BoxChan']
        formats = ['%s', '%d', '%d', '%d', '%d', '%.3f', '%d', '%d', '%.2f',
                   '%d', '%d', '%d', '%d', '%r', '%d', '%d']
        empties = [1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
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
