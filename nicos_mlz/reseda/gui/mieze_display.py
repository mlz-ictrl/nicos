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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Classes to display Mieze data from Cascade detector."""

from math import pi
from os import path

import numpy as np
from gr.pygr import ErrorBar

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.clients.gui.widgets.plotting import NicosPlotCurve
from nicos.guisupport.livewidget import LiveWidget1D
from nicos.guisupport.plots import GRCOLORS, GRMARKS, MaskedPlotCurve
from nicos.guisupport.qt import QSize, QSizePolicy, QWidget
from nicos.protocols.cache import cache_load
from nicos.utils import findResource

from nicos_mlz.reseda.utils import MiezeFit

my_uipath = path.dirname(__file__)

COLOR_BLUE = GRCOLORS['blue']

DOT_MARKER = GRMARKS['dot']


class MiniPlot(LiveWidget1D):

    client = None

    def __init__(self, parent=None, **kwds):
        LiveWidget1D.__init__(self, parent, **kwds)
        self.setTitles({'x': 'time slots', 'y': 'summed counts'})
        self.axes.resetCurves()
        self._curves = [
            MaskedPlotCurve([0], [1], linecolor=GRCOLORS['blue'],
                            markertype=DOT_MARKER, linetype=None),
            NicosPlotCurve([0], [.1], linecolor=COLOR_BLUE,
                           markertype=DOT_MARKER),
        ]
        self._curves[0].markersize = 3
        for curve in self._curves:
            self.axes.addCurves(curve)
        # Disable creating a mouse selection to zoom
        self.gr.setMouseSelectionEnabled(False)

    def sizeHint(self):
        return QSize(120, 120)

    def reset(self):
        self.plot.reset()


class FoilWidget(QWidget):

    fitter = MiezeFit()

    def __init__(self, name='unknown', parent=None, **kwds):
        QWidget.__init__(self, parent)
        loadUi(self, findResource('nicos_mlz/reseda/gui/mieze_display_foil.ui'))
        # set name
        self.name = name
        self.groupBox.setTitle(name)

        # insert plot widget + store reference
        self.plotwidget = MiniPlot(self)
        self.plotwidget.setSizePolicy(QSizePolicy.MinimumExpanding,
                                      QSizePolicy.MinimumExpanding)
        self.verticalLayout.insertWidget(0, self.plotwidget)
        self.do_update([(0, 0, 0, 0), (0, 0, 0, 0), [0] * 16] * 2)

    def do_update(self, data, roi=False):
        popt, perr, counts = data[int(roi) * 3:int(roi) * 3 + 3]
        avg, contrast, freq, phase = popt
        davg, dcontrast, dfreq, dphase = perr

        # data contains a list [avg, avgErr, contrast, contrastErr,
        # freq, freErr, phase, phaseErr, 16 * counts]
        self.avg_value.setText('%.0f' % abs(avg))
        self.avg_error.setText('%.1f' % davg)
        self.contrast_value.setText('%.2f' % abs(contrast))
        self.contrast_error.setText('%.3f' % dcontrast)
        self.freq_value.setText('%.2f' % freq)
        self.freq_error.setText('%.3f' % dfreq)
        self.phase_value.setText('%.2f' % (phase + pi if contrast < 0
                                           else phase))
        self.phase_error.setText('%.3f' % dphase)

        # now update plot
        datacurve, fitcurve = self.plotwidget._curves
        fitcurve.x = np.arange(-0.5, 16.5, 0.1)
        fitcurve.y = self.fitter.fit_model(fitcurve.x, avg, contrast, phase)
        datacurve.x = np.arange(0, 16, 1)
        datacurve.y = np.array(counts)
        datacurve.errorBar1 = ErrorBar(datacurve.x, datacurve.y,
                                       np.sqrt(datacurve.y),
                                       markercolor=datacurve.markercolor)
        self.plotwidget.reset()
        self.plotwidget.update()


class MiezePanel(Panel):
    """Panel to display mieze data from cascade detector.

    options:
        * foils - list of foils to be displayed, the order gives the position
                  where it will be displayed. First foil in most left, most
                  top position. Next in the same row. If the number of entries
                  is greater than the number of the columns the next row will
                  be used.
                  default: [7, 6, 5, 0, 1, 2]
        * columns - number of columns, where foil data can be displayed
                    default: 3
        * rows - number of rows, where foil data can be displayed
                 default: 2
    """

    panelName = 'Cascade Mieze display'
    bar = None
    menu = None

    _do_updates = True
    _data = None

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_mlz/reseda/gui/mieze_display.ui'))
        self.mywidgets = []
        self.foils = options.get('foils', [7, 6, 5, 0, 1, 2])
        self.columns = options.get('columns', 3)
        self.rows = options.get('rows', 2)
        for foil, x, y in zip(self.foils, self.rows * list(range(self.columns)),
                              sum([self.columns * [i] for i in
                                   range(self.rows)], [])):
            foilwidget = FoilWidget(name='Foil %d' % foil, parent=self)
            self.mywidgets.append(foilwidget)
            self.gridLayout.addWidget(foilwidget, y, x)
        self.client.cache.connect(self.on_client_cache)
        self.client.connected.connect(self.on_client_connected)

    def _init_data(self):
        data = self.client.getCacheKey('psd_channel/_foildata')
        if data:
            self._data = data[1]
        self.do_update()

    def on_client_connected(self):
        if self._data is None:
            self._init_data()

    def on_LiveCheckBox_toggled(self, toggle):
        self._do_updates = toggle
        if toggle:
            self._init_data()

    def do_update(self):
        if self._do_updates and self._data:
            for d, w in zip(self._data, self.mywidgets):
                w.do_update(d, self.roiCheckBox.isChecked())

    def on_client_cache(self, data):
        _time, key, _op, value = data
        if key == 'psd_channel/_foildata':
            self._data = cache_load(value)
            self.do_update()
