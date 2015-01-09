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

"""NICOS GUI plotting helpers."""

import sys
import os
import time
import tempfile

sys.QT_BACKEND_ORDER = ["PyQt4", "PySide"]

import gr
import numpy as np
from PyQt4 import QtGui
from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import QListWidgetItem, QDialog, QMessageBox
from qtgr import InteractiveGRWidget
from qtgr.events import GUIConnector, MouseEvent, LegendEvent
from gr.pygr import Plot, PlotAxes, PlotCurve, ErrorBar, Text
from gr.pygr.helper import ColorIndexGenerator

from nicos.clients.gui.utils import DlgUtils, DlgPresets, dialogFromUi
from nicos.clients.gui.dialogs.data import DataExportDialog
from nicos.clients.gui.fitutils import has_odr, FitError
from nicos.clients.gui.fitutils import fit_gauss, fwhm_to_sigma, fit_tc, \
     fit_pseudo_voigt, fit_pearson_vii, fit_arby, fit_linear
from nicos.pycompat import string_types

DATEFMT = "%Y-%m-%d"
TIMEFMT = "%H:%M:%S"


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


    #  pylint: disable=W0221
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


class NicosPlot(InteractiveGRWidget, DlgUtils):

    GR_MARKER_SIZE = 1.

    def __init__(self, parent, window, timeaxis=False):
        InteractiveGRWidget.__init__(self, parent)
        DlgUtils.__init__(self, 'Plot')
        self.window = window
        self.plotcurves = []
        self.normalized = False
        self.has_secondary = False
        self.show_all = False
        self.timeaxis = timeaxis
        self._statusMessage = None

        self.fits = 0
        self.fittype = None
        self.fitparams = None
        self.fitcurve = None
        self.fitstage = 0
        self.fitPicker = None
        self.fitcallbacks = [None, None]
        self.mouselocation = None
        self._cursor = self.cursor()
        self._mouseSelEnabled = self.getMouseSelectionEnabled()

        dictPrintType = dict(gr.PRINT_TYPE)
        map(dictPrintType.pop, [gr.PRINT_JPEG, gr.PRINT_TIF])
        self._saveTypes = (";;".join(dictPrintType.values()) + ";;" +
                           ";;".join(gr.GRAPHIC_TYPE.values()))
        gr.setmarkersize(NicosPlot.GR_MARKER_SIZE)
        self._saveName = None
        self._color = ColorIndexGenerator()
        self._plot = Plot(viewport=(.1, .85, .15, .88))
        self._axes = PlotAxes(viewport=self._plot.viewport)
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

    @property
    def statusMessage(self):
        """Get current status Message."""
        return self._statusMessage

    @statusMessage.setter
    def statusMessage(self, svalue):
        self._statusMessage = svalue

    def xtickCallBack(self, x, y, svalue):
        gr.setcharup(1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_LEFT, gr.TEXT_VALIGN_TOP)
        try:
            dx = .015
            gr.text(x - dx, y,
                    time.strftime(DATEFMT, time.localtime(float(svalue))))
            gr.text(x + dx, y,
                    time.strftime(TIMEFMT, time.localtime(float(svalue))))
        except ValueError:
            gr.text(x, y, svalue)
        gr.setcharup(0., 1.)

    def on_zoomer_zoomed(self, rect):
        pass

    def setFonts(self, font, bold, larger):
        raise NotImplementedError

    def titleString(self):
        raise NotImplementedError
    def subTitleString(self):
        return None
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

    def updateDisplay(self):
        self._plot.title = self.titleString()
        if self.subTitleString():
            self._plot.subTitle = self.subTitleString()
        self._plot.xlabel = self.xaxisName()
        self._plot.ylabel = self.yaxisName()
        if self.normalized:
            self._plot.ylabel += " (norm)"

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
        InteractiveGRWidget.update(self)

    def showCurves(self, legend, on=True):
        curves = [c for c in self._axes.getCurves() if c.legend in legend]
        for c in curves:
            c.visible = on
        self.update()

    def isLegendEnabled(self):
        return self._plot.isLegendEnabled()

    def setLegend(self, on):
        self._plot.setLegend(on)
        self.update()

    def setVisibility(self, item, on):
        item.visible = on

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
        curve = None
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

    @property
    def plot(self):
        """Get current gr.pygr.Plot object."""
        return self._plot

    def printPlot(self):
        if self._saveName:
            title = "GR_Demo-" + self._saveName
        else:
            title = "GR_Demo-untitled"
        self.printDialog(title)
        return True

    def _save(self, extension=".pdf"):
        fd, pathname = tempfile.mkstemp(extension)
        self.save(pathname)
        os.close(fd)
        return pathname

    def savePdf(self):
        return self._save(".pdf")

    def saveSvg(self):
        return self._save(".svg")

    def _beginFit(self, fittype, fitparams, fitcallback, pickcallback=None):
        if self.fittype is not None:
            return
        if not has_odr:
            return self.showError('scipy.odr is not available.')
        if not self.plotcurves:
            return self.showError('Plot must have a curve to be fitted.')
        fitcurve = self.selectCurve()
        if not fitcurve:
            return
        self.fitcurve = fitcurve
        self.fitvalues = []
        self.fitparams = fitparams
        self.fittype = fittype
        self.fitstage = 0
        self.fitcallbacks = [fitcallback, pickcallback]
        if self.fitparams:
            self.statusMessage = "Fitting: Click on %s" % fitparams[0]
            self.window.statusBar.showMessage(self.statusMessage)
            self._cursor = self.cursor()
            self.setCursor(QtGui.QCursor(Qt.CrossCursor))
            self._mouseSelEnabled = self.getMouseSelectionEnabled()
            self.setMouseSelectionEnabled(False)
        else:
            self._finishFit()

    def _finishFit(self):
        try:
            if self.fitcallbacks[1]:
                if not self.fitcallbacks[1]():  # pylint: disable=E1102
                    raise FitError('Aborted.')
            curve = self.fitcurve
            if not curve:
                return
            errBar1 = curve.errorBar1
            if errBar1:
                args = ([curve.x, curve.y, errBar1._dpos]
                        + self.fitvalues)
            else:
                args = [curve.x, curve.y, None] + self.fitvalues
            x, y, title, labelx, labely, interesting, _lineinfo = (
                self.fitcallbacks[0](args))  # pylint: disable=E1102

            color = self._color.getNextColorIndex()
            resultcurve = NicosPlotCurve(x, y, legend=title, linecolor=color,
                                         markercolor=color)
            self.addPlotCurve(resultcurve)
            resultcurve.markertype = gr.MARKERTYPE_DOT
            self.statusMessage = None
            self.window.statusBar.showMessage("Fitting complete")
            self.fittype = None
            self.fits += 1
            self.fitcurve = None

            text = '\n'.join((n + ': ' if n else '') +
                             (v if isinstance(v, string_types) else '%g' % v)
                             for (n, v) in interesting)
            resultcurve.dependent.append(Text(labelx, labely, text, self._axes,
                                              .012))
            self.update()
        except FitError, err:
            self.showInfo('Fitting failed: %s.' % err)
            self.fittype = None
            self.fitcurve = None
        finally:
            self.setCursor(self._cursor)
            self.setMouseSelectionEnabled(self._mouseSelEnabled)

    def on_fitPicker_selected(self, point):
        if (self.fittype is not None
            and point.getButtons() & MouseEvent.LEFT_BUTTON):
            p = point.getWC(self._plot.viewport)
            self.fitvalues.append((p.x , p.y))
            self.fitstage += 1
            if self.fitstage < len(self.fitparams):
                paramname = self.fitparams[self.fitstage]
                self.statusMessage = "Fitting: Click on %s" % paramname
                self.window.statusBar.showMessage(self.statusMessage)
            else:
                self._finishFit()


class ViewPlot(NicosPlot):
    def __init__(self, parent, window, view):
        self.series2curve = {}
        self.view = view
        self.hasSymbols = False
        self.hasLines = True
        NicosPlot.__init__(self, parent, window, timeaxis=True)
        self.setSymbols(False)

    def titleString(self):
        return self.view.name

    def xaxisName(self):
        return 'time'

    def yaxisName(self):
        return 'value'

    def addAllCurves(self):
        for i, series in enumerate(self.view.series.values()):
            self.addCurve(i, series)

    def yaxisScale(self):
        if self.view.yfrom is not None:
            return (self.view.yfrom, self.view.yto)

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
            plotcurve = NicosPlotCurve(series.x[:n], series.y[:n], legend=curvename,
                                       linecolor=color, markercolor=color)
            self.series2curve[series] = plotcurve
            self.addPlotCurve(plotcurve, replot)

    def pointsAdded(self, series):
        plotcurve = self.series2curve[series]
        plotcurve.x = series.x[:series.n].copy()
        plotcurve.y = series.y[:series.n].copy()
        self._axes.addCurves(plotcurve)
        InteractiveGRWidget.update(self)

    def setLines(self, on):
        linetype = None
        if on:
            linetype = gr.LINETYPE_SOLID
        for axis in self._plot.getAxes():
            for curve in axis.getCurves():
                curve.linetype = linetype
        self.update()

    def selectCurve(self):
        if len(self.plotcurves) > 1:
            dlg = dialogFromUi(self, 'selector.ui', 'panels')
            dlg.setWindowTitle('Select curve to fit')
            dlg.label.setText('Select a curve:')
            for plotcurve in self.plotcurves:
                QListWidgetItem(plotcurve.legend, dlg.list)
            dlg.list.setCurrentRow(0)
            if dlg.exec_() != QDialog.Accepted:
                return
            fitcurve = dlg.list.currentRow()
        else:
            fitcurve = 0
        return self.plotcurves[fitcurve]

    def fitLinear(self):
        return self._beginFit('Linear', ['First point', 'Second point'],
                              self.linear_fit_callback)

    def linear_fit_callback(self, args):
        title = 'linear fit'
        beta, x, y = fit_linear(*args)
        _x1, x2 = min(x), max(x)
        labelx = x2
        labely = beta[0] * x2 + beta[1]
        interesting = [('Slope', '%.3f /s' % beta[0]),
                       ('', '%.3f /min' % (beta[0] * 60)),
                       ('', '%.3f /h' % (beta[0] * 3600))]
        return x, y, title, labelx, labely, interesting, None

    def saveData(self):
        curvenames = [plotcurve.legend for plotcurve in self.plotcurves]
        dlg = DataExportDialog(self, curvenames,
                               'Select curve, file name and format',
                               '', 'ASCII data files (*.dat)')
        res = dlg.exec_()
        if res != QDialog.Accepted:
            return
        if not dlg.selectedFiles():
            return
        curve = self.plotcurves[dlg.curveCombo.currentIndex()]
        fmtno = dlg.formatCombo.currentIndex()
        filename = dlg.selectedFiles()[0]
        n = len(curve.x)

        if n < 1:
            QMessageBox.information(self, 'Error', 'No data in selected curve!')
            return

        with open(filename, 'wb') as fp:
            for i in range(n):
                if fmtno == 0:
                    fp.write('%s\t%.10f\n' % (curve.x[i] - curve.x[0],
                                              curve.y[i]))
                elif fmtno == 1:
                    fp.write('%s\t%.10f\n' % (curve.x[i], curve.y[i]))
                else:
                    fp.write('%s\t%.10f\n' % (time.strftime(
                        '%Y-%m-%d.%H:%M:%S', time.localtime(curve.x[i])),
                        curve.y[i]))


arby_functions = {
    'Gaussian x2': ('a + b*exp(-(x-x1)**2/s1**2) + c*exp(-(x-x2)**2/s2**2)',
                    'a b c x1 x2 s1 s2'),
    'Gaussian x3 symm.':
        ('a + b*exp(-(x-x0-x1)**2/s1**2) + b*exp(-(x-x0+x1)**2/s1**2) + '
         'c*exp(-(x-x0)**2/s0**2)', 'a b c x0 x1 s0 s1'),
    'Parabola': ('a*x**2 + b*x + c', 'a b c'),
}

class DataSetPlot(NicosPlot):

    def __init__(self, parent, window, dataset):
        self.dataset = dataset
        NicosPlot.__init__(self, parent, window)

    def titleString(self):
        return "Scan %s %s" % (self.dataset.name,
                                            self.dataset.scaninfo)

    def subTitleString(self):
        return "started %s" % time.strftime(TIMEFMT, self.dataset.started)

    def xaxisName(self):
        try:
            return '%s (%s)' % (self.dataset.xnames[self.dataset.xindex],
                                self.dataset.xunits[self.dataset.xindex])
        except IndexError:
            return ''

    def yaxisName(self):
        return ''

    def xaxisScale(self):
        if self.dataset.xrange:
            return self.dataset.xrange
        try:
            return (float(self.dataset.positions[0][self.dataset.xindex]),
                    float(self.dataset.positions[-1][self.dataset.xindex]))
        except (IndexError, TypeError, ValueError):
            return None

    def yaxisScale(self):
        if self.dataset.yrange:
            return self.dataset.yrange

    def addAllCurves(self):
        for i, curve in enumerate(self.dataset.curves):
            self.addCurve(i, curve)

    def enableCurvesFrom(self, otherplot):
        visible = {}
        for plotcurve in otherplot.plotcurves:
            visible[plotcurve.legend] = plotcurve.visible
        changed = False
        remaining = len(self.plotcurves)
        for plotcurve in self.plotcurves:
            namestr = plotcurve.legend
            if namestr in visible:
                self.setVisibility(plotcurve, visible[namestr])
                changed = True
                if not visible[namestr]:
                    remaining -= 1
        # no visible curve left?  enable all of them again
        if not remaining:
            for plotcurve in self.plotcurves:
                # only if it has a legend item (excludes monitor/time columns)
                if plotcurve.legend:
                    plotcurve.visible = True
        if changed:
            self.update()

    def addCurve(self, i, curve, replot=False):
        dy, errbar = None, None
        x, y = np.array(curve.datax), np.array(curve.datay, float)
        n = len(curve.datax)
        if n > 0:
            if curve.dyindex == -2:
                dy = np.sqrt(abs(y))
            elif curve.dyindex > -1:
                dy = np.array(curve.datady)
            if self.normalized:
                norm = None
                if curve.monindices:
                    norm = np.array(curve.datamon)
                elif curve.timeindex > -1:
                    norm = np.array(curve.datatime)
                if norm is not None:
                    y /= norm
                    if dy is not None: dy /= norm
            if dy is not None:
                dneg = y - dy
                dpos = y + dy
                errbar = ErrorBar(x[:n], y[:n], dneg, dpos)

            plotcurve = NicosPlotCurve(x[:n], y[:n], errbar,
                                       legend=curve.full_description)
            if curve.disabled and not self.show_all:
                plotcurve.visible = False
            self.addPlotCurve(plotcurve, replot)

    def setCurveData(self, curve, plotcurve):
        x = np.array(curve.datax)
        y = np.array(curve.datay, float)
        n = len(curve.datax)
        dy = None
        if curve.dyindex == -2:
            dy = np.sqrt(abs(y))
        elif curve.dyindex > -1:
            dy = np.array(curve.datady)
        if self.normalized:
            norm = None
            if curve.monindices:
                norm = np.array(curve.datamon)
            elif curve.timeindex > -1:
                norm = np.array(curve.datatime)
            if norm is not None:
                y /= norm
                if dy is not None: dy /= norm

        if dy is not None:
            dneg = y - dy
            dpos = y + dy
            errbar = ErrorBar(x[:n], y[:n], dneg, dpos,
                              markercolor=plotcurve.markercolor)
            plotcurve.errorBar1 = errbar
        plotcurve.x = x[:n]
        plotcurve.y = y[:n]
        plotcurve.legend = curve.full_description

    def pointsAdded(self):
        curve = None
        for curve, plotcurve in zip(self.dataset.curves, self.plotcurves):
            self.setCurveData(curve, plotcurve)
        self.updateDisplay()

    def modifyData(self):
        visible_curves = [i for (i, _) in enumerate(self.dataset.curves)
                          if self.plotcurves[i].visible]
        # get input from the user: which curves should be modified how
        dlg = dialogFromUi(self, 'modify.ui', 'panels')
        def checkAll():
            for i in range(dlg.list.count()):
                dlg.list.item(i).setCheckState(Qt.Checked)
        dlg.connect(dlg.selectall, SIGNAL('clicked()'), checkAll)
        for i in visible_curves:
            li = QListWidgetItem(self.dataset.curves[i].full_description,
                                 dlg.list)
            if len(visible_curves) == 1:
                li.setCheckState(Qt.Checked)
                dlg.operation.setFocus()
            else:
                li.setCheckState(Qt.Unchecked)
        if dlg.exec_() != QDialog.Accepted:
            return
        # evaluate selection
        op = dlg.operation.text()
        curves = []
        for i in range(dlg.list.count()):
            li = dlg.list.item(i)
            if li.checkState() == Qt.Checked:
                curves.append(i)

        # modify curve data
        for i in curves:
            curve = self.plotcurves[visible_curves[i]]
            new_y = [eval(op, {'x': v1, 'y': v2})
                     for (v1, v2) in zip(curve.x, curve.y)]
            if curve.errorBar1:
                curve.errorBar1.y = new_y
            if curve.errorBar2:
                curve.errorBar2.y = new_y
            curve.y = new_y
        self.update()

    def selectCurve(self):
        visible_curves = [i for (i, _) in enumerate(self.dataset.curves)
                          if self.plotcurves[i].visible]
        if not visible_curves:
            return
        if len(visible_curves) > 1:
            dlg = dialogFromUi(self, 'selector.ui', 'panels')
            dlg.setWindowTitle('Select curve to fit')
            dlg.label.setText('Select a curve:')
            for i in visible_curves:
                QListWidgetItem(self.dataset.curves[i].full_description,
                                dlg.list)
            dlg.list.setCurrentRow(0)
            if dlg.exec_() != QDialog.Accepted:
                return
            fitcurve = visible_curves[dlg.list.currentRow()]
        else:
            fitcurve = visible_curves[0]
        return self.plotcurves[fitcurve]

    def fitGaussPeak(self):
        return self._beginFit('Gauss', ['Background', 'Peak', 'Half Maximum'],
                              self.gauss_callback)

    def gauss_callback(self, args):
        title = 'peak fit'
        beta, x, y = fit_gauss(*args)
        labelx = beta[2] + beta[3] / 2
        labely = beta[0] + beta[1]
        interesting = [('Center', beta[2]),
                       ('FWHM', beta[3] * fwhm_to_sigma),
                       ('Ampl', beta[1]),
                       ('Integr', beta[1] * beta[3] * np.sqrt(2 * np.pi))]
        linefrom = beta[2] - beta[3] * fwhm_to_sigma / 2
        lineto = beta[2] + beta[3] * fwhm_to_sigma / 2
        liney = beta[0] + beta[1] / 2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitPseudoVoigtPeak(self):
        return self._beginFit('Pseudo-Voigt', ['Background', 'Peak', 'Half Maximum'],
                              self.pv_callback)

    def pv_callback(self, args):
        title = 'peak fit (PV)'
        beta, x, y = fit_pseudo_voigt(*args)
        labelx = beta[2] + beta[3] / 2
        labely = beta[0] + beta[1]
        eta = beta[4] % 1.0
        integr = beta[1] * beta[3] * (
            eta * np.pi + (1 - eta) * np.sqrt(np.pi / np.log(2)))
        interesting = [('Center', beta[2]), ('FWHM', beta[3] * 2),
                       ('Eta', eta), ('Integr', integr)]
        linefrom = beta[2] - beta[3]
        lineto = beta[2] + beta[3]
        liney = beta[0] + beta[1] / 2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitPearsonVIIPeak(self):
        return self._beginFit('PearsonVII', ['Background', 'Peak', 'Half Maximum'],
                              self.pvii_callback)

    def pvii_callback(self, args):
        title = 'peak fit (PVII)'
        beta, x, y = fit_pearson_vii(*args)
        labelx = beta[2] + beta[3] / 2
        labely = beta[0] + beta[1]
        interesting = [('Center', beta[2]), ('FWHM', beta[3] * 2),
                       ('m', beta[4])]
        linefrom = beta[2] - beta[3]
        lineto = beta[2] + beta[3]
        liney = beta[0] + beta[1] / 2
        return x, y, title, labelx, labely, interesting, \
            (linefrom, lineto, liney)

    def fitTc(self):
        return self._beginFit('Tc', ['Background', 'Tc'], self.tc_callback)

    def tc_callback(self, args):
        title = 'Tc fit'
        beta, x, y = fit_tc(*args)
        labelx = beta[2]  # at Tc
        labely = beta[0] + beta[1]  # at I_max
        interesting = [('Tc', beta[2]), (u'α', beta[3])]
        return x, y, title, labelx, labely, interesting, None

    def fitArby(self):
        return self._beginFit('Arbitrary', [], self.arby_callback,
                              self.arby_pick_callback)

    def arby_callback(self, args):
        title = 'fit'
        beta, x, y = fit_arby(*args)
        labelx = x[0]
        labely = y.max()
        interesting = list(zip(self.fitvalues[1], beta))
        return x, y, title, labelx, labely, interesting, None

    def arby_pick_callback(self):
        dlg = dialogFromUi(self, 'fit_arby.ui', 'panels')
        pr = DlgPresets('fit_arby',
            [(dlg.function, ''), (dlg.fitparams, ''),
             (dlg.xfrom, ''), (dlg.xto, '')])
        pr.load()
        for name in sorted(arby_functions):
            QListWidgetItem(name, dlg.oftenUsed)
        def click_cb(item):
            func, params = arby_functions[item.text()]
            dlg.function.setText(func)
            dlg.fitparams.setPlainText('\n'.join(
                p + ' = ' for p in params.split()))
        dlg.connect(dlg.oftenUsed,
                    SIGNAL('itemClicked(QListWidgetItem *)'), click_cb)
        ret = dlg.exec_()
        if ret != QDialog.Accepted:
            return False
        pr.save()
        fcn = dlg.function.text()
        try:
            xmin = float(dlg.xfrom.text())
        except ValueError:
            xmin = None
        try:
            xmax = float(dlg.xto.text())
        except ValueError:
            xmax = None
        if xmin is not None and xmax is not None and xmin > xmax:
            xmax, xmin = xmin, xmax
        params, values = [], []
        for line in dlg.fitparams.toPlainText().splitlines():
            name_value = line.strip().split('=', 2)
            if len(name_value) < 2:
                continue
            params.append(name_value[0])
            try:
                values.append(float(name_value[1]))
            except ValueError:
                values.append(0)
        self.fitvalues = [fcn, params, values, (xmin, xmax)]
        return True

    def fitQuick(self):
        if self.mouselocation:
            (coord, _axes, curve) = self._plot.pick(self.mouselocation.getNDC(),
                                                    self.dwidth, self.dheight)
            if curve:
                self.fitcurve = curve
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
                while i > 0:
                    if curve.y[i] < (peaky - backy) / 2.:
                        break
                    i += direction
                if i != whichindex:
                    fwhmx = curve.x[i]
                else:
                    fwhmx = (peakx + backx) / 2.
                self.fitvalues = [(backx, backy), (peakx, peaky),
                                  (fwhmx, peaky / 2.)]
                self.fitparams = ['Background', 'Peak', 'Half Maximum']
                self.fittype = 'Gauss'
                self.fitcallbacks = [self.gauss_callback, None]
                self._finishFit()
