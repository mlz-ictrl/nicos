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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

from PyQt4.QtGui import QFont

from nicos.clients.gui.utils import DlgUtils


class Fitter(object):
    pass


class NicosPlot(DlgUtils):
    def __init__(self, window, timeaxis=False):
        DlgUtils.__init__(self, 'Plot')
        self.window = window
        self.plotcurves = []
        self.normalized = False
        self.has_secondary = False
        self.show_all = False
        self.timeaxis = timeaxis

        self.fits = 0
        self.fittype = None
        self.fitparams = None
        self.fitstage = 0
        self.fitPicker = None
        self.fitcallbacks = [None, None]

        font = self.window.user_font
        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)
        self.setFonts(font, bold, larger)

    def setFonts(self, font, bold, larger):
        raise NotImplementedError

    def titleString(self):
        raise NotImplementedError

    def xaxisName(self):
        raise NotImplementedError

    def yaxisName(self):
        raise NotImplementedError

    def y2axisName(self):
        return ''

    def xaxisScale(self):
        return None

    def yaxisScale(self):
        return None

    def y2axisScale(self):
        return None

    def isLegendEnabled(self):
        """Return true if the legend is currently enabled."""
        raise NotImplementedError

    def setLegend(self, on):
        """Switch legend on or off."""
        raise NotImplementedError

    def setVisibility(self, item, on):
        """Set visibility on a plot item."""
        raise NotImplementedError

    def isLogScaling(self, idx=0):
        """Return true if main Y axis is logscaled."""
        raise NotImplementedError

    def setLogScale(self, on):
        """Set logscale on main Y axis."""
        raise NotImplementedError

    def setSymbols(self, on):
        """Enable or disable symbols."""
        raise NotImplementedError

    def setLines(self, on):
        """Enable or disable lines."""
        raise NotImplementedError

    def addPlotCurve(self, plotcurve, replot=False):
        """Add a plot curve."""
        raise NotImplementedError

    def savePlot(self):
        """Save plot, asking user for a filename."""
        raise NotImplementedError

    def printPlot(self):
        """Print plot with print dialog."""
        raise NotImplementedError

    def saveQuietly(self):
        """Save plot quietly to a temporary file with default format.

        Return the created filename.
        """
        raise NotImplementedError
