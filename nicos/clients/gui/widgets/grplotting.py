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
#   Christian Felder <c.felder@fz-juelich.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************
"""NICOS GR plotting backend."""

import sys
import os
import time
import tempfile

sys.QT_BACKEND_ORDER = ["PyQt4", "PySide"]

import gr
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from qtgr import InteractiveGRWidget
from qtgr.events import GUIConnector, MouseEvent, LegendEvent
from gr.pygr import Plot, PlotAxes, PlotCurve, ErrorBar, Text
from gr.pygr.helper import ColorIndexGenerator

from nicos.clients.gui.widgets.plotting import NicosPlot, ViewPlotMixin, \
    DataSetPlotMixin, GaussFitter, prepareData
from nicos.guisupport.timeseries import buildTickDistAndSubTicks
from nicos.pycompat import string_types

DATEFMT = "%Y-%m-%d"
TIMEFMT = "%H:%M:%S"


class NicosTimePlotAxes(PlotAxes):

    def setWindow(self, xmin, xmax, ymin, ymax):
        res = PlotAxes.setWindow(self, xmin, xmax, ymin, ymax)
        if res:
            tickdist, self.majorx = buildTickDistAndSubTicks(xmin, xmax)
            self.xtick = tickdist / self.majorx
        return res


class NicosPlotCurve(PlotCurve):

    def __init__(self, x, y, errBar1=None, errBar2=None,
                 linetype=gr.LINETYPE_SOLID, markertype=gr.MARKERTYPE_DOT,
                 linecolor=None, markercolor=1, legend=None):
        PlotCurve.__init__(self, x, y, errBar1, errBar2,
                           linetype, markertype, linecolor, markercolor,
                           legend)
        self._dependent = []

    @property
    def dependent(self):
        """Return dependent objects which implement the GRMeta interface."""
        return self._dependent

    @dependent.setter
    def dependent(self, value):
        self._dependent = value

    # pylint: disable=W0221
    @PlotCurve.visible.setter
    def visible(self, flag):
        self._visible = flag
        for dep in self.dependent:
            dep.visible = flag

    def drawGR(self):
        PlotCurve.drawGR(self)
        for dep in self.dependent:
            if dep.visible:
                dep.drawGR()


class NicosGrPlot(InteractiveGRWidget, NicosPlot):

    GR_MARKER_SIZE = 1.
    HAS_AUTOSCALE = True
    SAVE_EXT = '.svg'

    def __init__(self, parent, window, timeaxis=False):
        InteractiveGRWidget.__init__(self, parent)
        NicosPlot.__init__(self, window, timeaxis=timeaxis)

        self.leftTurnedLegend = True
        self.statusMessage = None
        self.mouselocation = None
        self._cursor = self.cursor()
        self._mouseSelEnabled = self.getMouseSelectionEnabled()

        dictPrintType = dict(gr.PRINT_TYPE)
        map(dictPrintType.pop, [gr.PRINT_JPEG, gr.PRINT_TIF])
        self._saveTypes = (";;".join(dictPrintType.values()) + ";;" +
                           ";;".join(gr.GRAPHIC_TYPE.values()))
        gr.setmarkersize(NicosGrPlot.GR_MARKER_SIZE)
        self._saveName = None
        self._color = ColorIndexGenerator()
        self._plot = Plot(viewport=(.1, .85, .15, .88))
        self._axes = NicosTimePlotAxes(viewport=self._plot.viewport)
        self._axes.backgroundColor = 0
        self._plot.addAxes(self._axes)
        self._plot.title = self.titleString()
        self.addPlot(self._plot)

        self._guiConn = GUIConnector(self)
        self._guiConn.connect(LegendEvent.ROI_CLICKED,
                              self.on_legendItemClicked)
        self._guiConn.connect(MouseEvent.MOUSE_PRESS,
                              self.on_fitPicker_selected)
        self._guiConn.connect(MouseEvent.MOUSE_MOVE, self.on_mouseMove)
        self.logXinDomain.connect(self.on_logXinDomain)
        self.logYinDomain.connect(self.on_logYinDomain)
        self.setLegend(True)
        self.updateDisplay()

    def xtickCallBack(self, x, y, svalue):
        gr.setcharup(-1. if self.leftTurnedLegend else 1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_RIGHT if self.leftTurnedLegend else
                        gr.TEXT_HALIGN_LEFT, gr.TEXT_VALIGN_TOP)
        try:
            dx = .015
            timeVal = time.localtime(float(svalue))
            gr.text(x + (dx if self.leftTurnedLegend else -dx), y,
                    time.strftime(DATEFMT, timeVal))
            gr.text(x - (dx if self.leftTurnedLegend else -dx), y,
                    time.strftime(TIMEFMT, timeVal))
        except ValueError:
            gr.text(x, y, svalue)
        gr.setcharup(0., 1.)

    def setAutoScaleFlags(self, xflag, yflag):
        mask = 0x0
        if xflag:
            mask |= PlotAxes.SCALE_X
        if yflag:
            mask |= PlotAxes.SCALE_Y
        self.setAutoScale(mask)

    def setFonts(self, font, bold, larger):
        pass  # not implemented

    def updateDisplay(self):
        self._plot.title = self.titleString()
        if self.subTitleString():
            self._plot.subTitle = self.subTitleString()
        self._plot.xlabel = self.xaxisName()
        self._plot.ylabel = self.yaxisName()
        if self.normalized:
            self._plot.ylabel += " (norm: %s)" % self.normalized

        self.plotcurves = []
        self.addAllCurves()
        # SECOND AXIS NOT IMPLEMENTED
#        if self.has_secondary:
#            self.setAxisTitle(QwtPlot.yRight, y2axistext)

#            scale = self.y2axisScale()
#            if scale is None:
#                self.setAxisAutoScale(QwtPlot.yRight)
#            else:
#                self.setAxisScale(QwtPlot.yRight, scale[0], scale[1])
        if self.timeaxis:
            self._plot.viewport = (.1, .85, .18, .88)
            self._axes.setXtickCallback(self.xtickCallBack)
            self._plot.offsetXLabel = -.08

        scale = self.yaxisScale()
        if scale:
            axes = self._plot.getAxes(0)
            curwin = axes.getWindow()
            if not curwin:
                curwin = [0, 1, scale[0], scale[1]]
                curves = axes.getCurves()
                xmins = []
                xmaxs = []
                for c in curves:
                    if c.visible:
                        xmins.append(min(c.x))
                        xmaxs.append(max(c.x))
                if xmins and xmaxs:
                    curwin[0] = min(xmins)
                    curwin[1] = max(xmaxs)
            axes.setWindow(curwin[0], curwin[1], scale[0], scale[1])
        InteractiveGRWidget.update(self)

    def isLegendEnabled(self):
        return self._plot.isLegendEnabled()

    def setLegend(self, on):
        self._plot.setLegend(on)
        self.update()

    def isLogScaling(self, idx=0):
        axes = self._plot.getAxes(idx)
        return (axes.scale & gr.OPTION_Y_LOG if axes is not None else False)

    def setLogScale(self, on):
        self._plot.setLogY(on, rescale=True)
        self.update()

    def setSymbols(self, on):
        markertype = gr.MARKERTYPE_DOT
        if on:
            markertype = gr.MARKERTYPE_OMARK
        for axis in self._plot.getAxes():
            for curve in axis.getCurves():
                curve.markertype = markertype
        self.hasSymbols = on
        self.update()

    def setLines(self, on):
        linetype = None
        if on:
            linetype = gr.LINETYPE_SOLID
        for axis in self._plot.getAxes():
            for curve in axis.getCurves():
                curve.linetype = linetype
        self.hasLines = on
        self.update()

    def unzoom(self):
        self._plot.reset()
        self.update()

    def on_logXinDomain(self, flag):
        if not flag:
            self._plot.setLogX(flag)
            self.update()

    def on_logYinDomain(self, flag):
        if not flag:
            self.setLogScale(flag)

    def on_legendItemClicked(self, event):
        if event.getButtons() & MouseEvent.LEFT_BUTTON:
            event.curve.visible = not event.curve.visible
            self.update()

    def on_mouseMove(self, event):
        self.mouselocation = event
        wc = event.getWC(self._plot.viewport)
        if self.statusMessage:
            msg = "%s (X = %g, Y = %g)" % (self.statusMessage, wc.x, wc.y)
        else:
            msg = "X = %g, Y = %g" % (wc.x, wc.y)
        self.window.statusBar.showMessage(msg)

    def addPlotCurve(self, plotcurve, replot=False):
        curve = next((c for c in self._axes.getCurves()
                      if c.legend == plotcurve.legend), None)
        if curve:
            # update curve
            curve.x, curve.y = plotcurve.x, plotcurve.y
            if plotcurve.errorBar1 and curve.errorBar1:
                mcolor = curve.errorBar1.markercolor
                curve.errorBar1 = plotcurve.errorBar1
                curve.errorBar1.markercolor = mcolor
            else:
                curve.errorBar1 = plotcurve.errorBar1
            if plotcurve.errorBar2 and curve.errorBar2:
                mcolor = curve.errorBar2.markercolor
                curve.errorBar2 = plotcurve.errorBar2
                curve.errorBar2.markercolor = mcolor
            else:
                curve.errorBar2 = plotcurve.errorBar2
            if plotcurve not in self.plotcurves:
                self.plotcurves.append(plotcurve)
        else:
            color = self._color.getNextColorIndex()
            plotcurve.linecolor = color
            plotcurve.markercolor = color
            plotcurve.markertype = gr.MARKERTYPE_OMARK
            if plotcurve.errorBar1:
                plotcurve.errorBar1.markercolor = color
            if plotcurve.errorBar2:
                plotcurve.errorBar2.markercolor = color
            self._axes.addCurves(plotcurve)
            self.plotcurves.append(plotcurve)

    def savePlot(self):
        saveName = None
        dialog = QtGui.QFileDialog(self, "Select file name", "",
                                   self._saveTypes)
        dialog.selectNameFilter(gr.PRINT_TYPE[gr.PRINT_PDF])
        dialog.setNameFilterDetailsVisible(True)
        dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            qpath = dialog.selectedFiles()[0]
            if qpath:
                path = unicode(qpath)
                _p, suffix = os.path.splitext(path)
                if suffix:
                    suffix = suffix.lower()
                else:
                    # append selected name filter suffix (filename extension)
                    nameFilter = dialog.selectedNameFilter()
                    for k, v in gr.PRINT_TYPE.iteritems():
                        if v == nameFilter:
                            suffix = '.' + k
                            path += suffix
                            break
                if suffix and (suffix[1:] in gr.PRINT_TYPE.keys() or
                               suffix[1:] in gr.GRAPHIC_TYPE):
                    self.save(path)
                    saveName = os.path.basename(path)
                    self._saveName = saveName
                else:
                    raise Exception("Unsupported file format")
        return saveName

    def printPlot(self):
        self.printDialog("Nicos-" + self._saveName if self._saveName
                         else "untitled")
        return True

    @property
    def plot(self):
        """Get current gr.pygr.Plot object."""
        return self._plot

    def _save(self, extension=".pdf"):
        fd, pathname = tempfile.mkstemp(extension)
        self.save(pathname)
        os.close(fd)
        return pathname

    def saveQuietly(self):
        return self._save(".svg")

    def _getCurveData(self, curve):
        errBar1 = curve.errorBar1
        return [curve.x, curve.y, errBar1.dpos if errBar1 else None]

    def _getCurveLegend(self, curve):
        return curve.legend

    def _isCurveVisible(self, curve):
        return curve.visible

    def setVisibility(self, item, on):
        item.visible = on

    def _enterFitMode(self):
        self.window.statusBar.showMessage(self.statusMessage)
        self._cursor = self.cursor()
        self.setCursor(QtGui.QCursor(Qt.CrossCursor))
        self._mouseSelEnabled = self.getMouseSelectionEnabled()
        self.setMouseSelectionEnabled(False)

    def _fitRequestPick(self, paramname):
        self.statusMessage = 'Fitting: Click on %s' % paramname
        self.window.statusBar.showMessage(self.statusMessage)

    def _leaveFitMode(self):
        self.fitter = None
        self.statusMessage = None
        self.setCursor(self._cursor)
        self.setMouseSelectionEnabled(self._mouseSelEnabled)

    def _plotFit(self, fitter):
        color = self._color.getNextColorIndex()
        resultcurve = NicosPlotCurve(fitter.xfit, fitter.yfit,
                                     legend=fitter.title,
                                     linecolor=color, markercolor=color)
        self.addPlotCurve(resultcurve)
        resultcurve.markertype = gr.MARKERTYPE_DOT
        self.window.statusBar.showMessage("Fitting complete")

        text = '\n'.join(
            (n + ': ' if n else '') +
            (v if isinstance(v, string_types) else '%g' % v) +
            (dv if isinstance(dv, string_types) else ' +/- %g' % dv)
            for (n, v, dv) in fitter.interesting)
        resultcurve.dependent.append(
            Text(fitter.labelx, fitter.labely, text, self._axes, .012,
                 hideviewport=False))
        self.update()

    def on_fitPicker_selected(self, point):
        if self.fitter and point.getButtons() & MouseEvent.LEFT_BUTTON:
            p = point.getWC(self._plot.viewport)
            self.fitter.addPick((p.x, p.y))

    def _modifyCurve(self, curve, op):
        new_y = [eval(op, {'x': v1, 'y': v2})
                 for (v1, v2) in zip(curve.x, curve.y)]
        if curve.errorBar1:
            curve.errorBar1.y = new_y
        if curve.errorBar2:
            curve.errorBar2.y = new_y
        curve.y = new_y


class ViewPlot(ViewPlotMixin, NicosGrPlot):
    def __init__(self, parent, window, view):
        ViewPlotMixin.__init__(self, view)
        NicosGrPlot.__init__(self, parent, window, timeaxis=True)
        self.setSymbols(False)

    def titleString(self):
        return self.view.name

    def on_mouseMove(self, event):
        wc = event.getWC(self.plot.viewport)
        # overridden to show the correct timestamp
        ts = time.strftime(DATEFMT + ' ' + TIMEFMT, time.localtime(wc.x))
        if self.statusMessage:
            msg = "%s (X = %s, Y = %g)" % (self.statusMessage, ts, wc.y)
        else:
            msg = "X = %s, Y = %g" % (ts, wc.y)
        self.window.statusBar.showMessage(msg)

    def addCurve(self, i, series, replot=False):
        curvename = series.name
        if series.info:
            curvename += ' (' + series.info + ')'
        n = series.n
        if n > 0:
            color = self._color.getNextColorIndex()
            plotcurve = NicosPlotCurve(series.x[:n], series.y[:n],
                                       legend=curvename,
                                       linecolor=color, markercolor=color)
            self.series2curve[series] = plotcurve
            self.addPlotCurve(plotcurve, replot)

    def pointsAdded(self, series):
        plotcurve = self.series2curve[series]
        plotcurve.x = series.x[:series.n].copy()
        plotcurve.y = series.y[:series.n].copy()
        self._axes.addCurves(plotcurve)
        InteractiveGRWidget.update(self)


class DataSetPlot(DataSetPlotMixin, NicosGrPlot):

    def __init__(self, parent, window, dataset):
        DataSetPlotMixin.__init__(self, dataset)
        NicosGrPlot.__init__(self, parent, window)

    def titleString(self):
        return "Scan %s %s" % (self.dataset.name, self.dataset.scaninfo)

    def subTitleString(self):
        return "started %s" % time.strftime(DATEFMT + ' ' + TIMEFMT,
                                            self.dataset.started)

    def addCurve(self, i, curve, replot=False):
        if self.current_xname != 'Default' and \
           self.current_xname not in curve.datax:
            return
        if not curve.datay:
            return
        plotcurve = NicosPlotCurve([], [])
        self.setCurveData(curve, plotcurve)
        self.addPlotCurve(plotcurve, replot)
        if curve.function:
            plotcurve.markertype = gr.MARKERTYPE_DOT

    def setCurveData(self, curve, plotcurve):
        xname = curve.default_xname \
            if self.current_xname == 'Default' else self.current_xname
        norm = curve.datanorm[self.normalized] if self.normalized else None
        x, y, dy = prepareData(curve.datax[xname], curve.datay, curve.datady,
                               norm)
        if dy is not None:
            errbar = ErrorBar(x, y, dy, markercolor=plotcurve.markercolor)
            plotcurve.errorBar1 = errbar
        if curve.disabled or not len(x):
            plotcurve.visible = False
        plotcurve.x = x
        plotcurve.y = y
        plotcurve.legend = curve.full_description

    def pointsAdded(self):
        curve = None
        for curve, plotcurve in zip(self.dataset.curves, self.plotcurves):
            self.setCurveData(curve, plotcurve)
        self.updateDisplay()

    def fitQuick(self):
        if not self.mouselocation:
            return
        (coord, _axes, curve) = self._plot.pick(self.mouselocation.getNDC(),
                                                self.dwidth, self.dheight)
        if not curve:
            return
        wc = coord.getWC(self._plot.viewport)
        whichindex = None
        for idx, y in enumerate(curve.y):
            if wc.y == y:
                whichindex = idx
                break
        # try to find good starting parameters
        peakx, peaky = wc.x, wc.y
        # use either left or right end of curve as background
        leftx, lefty = curve.x[0], curve.y[0]
        rightx, righty = curve.x[-1], curve.y[-1]
        if abs(peakx - leftx) > abs(peakx - rightx):
            direction = -1
            backx, backy = leftx, lefty
        else:
            direction = 1
            backx, backy = rightx, righty
        i = whichindex
        n = len(curve.y)
        while 0 < i < n:
            if curve.y[i] < (peaky - backy) / 2.:
                break
            i += direction
        if i != whichindex:
            fwhmx = curve.x[i]
        else:
            fwhmx = (peakx + backx) / 2.
        self.fitter = GaussFitter(self, self.window, None, curve)
        self.fitter.values = [(backx, backy), (peakx, peaky),
                              (fwhmx, peaky / 2.)]
        self.fitter.begin()
        self.fitter.finish()
