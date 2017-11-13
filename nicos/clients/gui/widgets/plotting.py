#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

import os
import time
import tempfile
from os import path

import numpy as np
import numpy.ma
import gr
from gr.pygr import Plot, PlotAxes, ErrorBar, Text, RegionOfInterest, \
    CoordConverter
from gr.pygr.helper import ColorIndexGenerator

from nicos.guisupport.qt import Qt, QPoint, QApplication, QMenu, QAction, \
    QDialog, QFileDialog, QCursor, QFont, QListWidgetItem, QMessageBox

from qtgr import InteractiveGRWidget
from qtgr.events import GUIConnector, MouseEvent, LegendEvent, ROIEvent

from nicos.guisupport.plots import NicosPlotAxes, NicosTimePlotAxes, \
    MaskedPlotCurve, DATEFMT, TIMEFMT
from nicos.clients.gui.dialogs.data import DataExportDialog
from nicos.clients.gui.utils import DlgUtils, DlgPresets, dialogFromUi
from nicos.utils import safeFilename
from nicos.utils.fitting import Fit, FitResult, LinearFit, GaussFit, \
    PseudoVoigtFit, PearsonVIIFit, TcFit, CosineFit, SigmoidFit, FitError, \
    ExponentialFit
from nicos.pycompat import string_types, exec_, xrange as range  # pylint: disable=W0622


def prepareData(x, y, dy, norm):
    """Prepare and sanitize data for plotting.

    x, y and dy are lists or arrays. norm can also be None.

    Returns x, y and dy arrays, where dy can also be None.
    """
    # make arrays
    x = np.asarray(x)
    # replace complex data types (strings...) by numbers
    if not x.dtype.isbuiltin:
        x = np.zeros(x.shape)
    y = np.asarray(y, float)
    dy = np.asarray(dy, float)
    # normalize
    if norm is not None:
        norm = np.asarray(norm, float)
        y /= norm
        dy /= norm
    # remove infinity/NaN
    indices = np.isfinite(y)
    x = x[indices]
    y = y[indices]
    if dy.size:
        dy = dy[indices]
        # remove error bars that aren't finite
        dy[~np.isfinite(dy)] = 0
    # if there are no errors left, don't bother drawing them
    if dy.sum() == 0:
        return x, y, None
    return x, y, dy


class Fitter(object):
    title = 'unknown fit'
    picks = []

    def __init__(self, plot, window, action, curve):
        self.plot = plot
        self.window = window
        self.action = action
        self.curve = curve
        self.data = plot._getCurveData(curve)

        self.values = []
        self.stage = 0

    def begin(self):
        self.plot._enterFitMode()
        if self.action:
            self.action.setChecked(True)
        self.plot._fitRequestPick(self.picks[0])

    def addPick(self, point):
        self.stage += 1
        self.values.append(point)
        if self.stage < len(self.picks):
            paramname = self.picks[self.stage]
            self.plot._fitRequestPick(paramname)
        else:
            self.finish()

    def cancel(self):
        self.plot._leaveFitMode()
        if self.action:
            self.action.setChecked(False)

    def finish(self):
        self.cancel()
        try:
            res = self.do_fit()
        except FitError as e:
            self.plot.showInfo('Fitting failed: %s.' % e)
            return
        self.plot._plotFit(res)

    def do_fit(self):
        raise NotImplementedError


class LinearFitter(Fitter):
    title = 'linear fit'
    picks = ['First point', 'Second point']

    def do_fit(self):
        (x1, y1), (x2, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        m0 = (y2-y1) / (x2-x1)
        f = LinearFit([m0, y1 - m0*x1], xmin=x1, xmax=x2, timeseries=True)
        return f.run_or_raise(*self.data)


class ExponentialFitter(Fitter):
    title = 'exp. fit'
    picks = ['First point', 'Second point']

    def do_fit(self):
        (x1, y1), (x2, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        b0 = np.log(y1 / y2) / (x1 - x2)
        x0 = x1 - np.log(y1) / b0
        f = ExponentialFit([b0, x0], xmin=x1, xmax=x2, timeseries=True)
        return f.run_or_raise(*self.data)


class CosineFitter(Fitter):
    title = 'cosine fit'
    picks = ['Maximum', 'Next minimum']

    def do_fit(self):
        (x1, y1), (x2, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        a = abs(y1 - y2) / 2.
        b = (y1 + y2) / 2.
        width = abs(x1 - x2)
        freq = 1/(width * 2.)
        f = CosineFit([a, freq, x1, b])
        return f.run_or_raise(*self.data)


class GaussFitter(Fitter):
    title = 'peak fit'
    picks = ['Background', 'Peak', 'Half Maximum']

    def do_fit(self):
        (xb, yb), (x0, y0), (xw, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        parstart = [x0, abs(y0-yb), abs(x0-xw), yb]
        totalwidth = abs(x0 - xb)
        f = GaussFit(parstart, xmin=x0 - totalwidth, xmax=x0 + totalwidth)
        return f.run_or_raise(*self.data)


class SigmoidFitter(Fitter):
    """."""

    title = 'sigmoid fit'
    picks = ['Left point', 'Right point']

    def do_fit(self):
        (x1, y1), (x2, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        pastart = [y2 - y1, 1, (x2 - x1) / 2. + x1, y1]
        f = SigmoidFit(pastart, xmin=x1, xmax=x2)
        return f.run_or_raise(*self.data)


class PseudoVoigtFitter(Fitter):
    title = 'peak fit (PV)'
    picks = ['Background', 'Peak', 'Half Maximum']

    def do_fit(self):
        (xb, yb), (x0, y0), (xw, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        parstart = [yb, abs(y0-yb), x0, abs(x0-xw), 0.5]
        totalwidth = abs(x0 - xb)
        f = PseudoVoigtFit(parstart, xmin=x0 - totalwidth, xmax=x0 + totalwidth)
        return f.run_or_raise(*self.data)


class PearsonVIIFitter(Fitter):
    title = 'peak fit (PVII)'
    picks = ['Background', 'Peak', 'Half Maximum']

    def do_fit(self):
        (xb, yb), (x0, y0), (xw, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        parstart = [yb, abs(y0-yb), x0, abs(x0-xw), 5.0]
        totalwidth = abs(x0 - xb)
        f = PearsonVIIFit(parstart, xmin=x0 - totalwidth, xmax=x0 + totalwidth)
        return f.run_or_raise(*self.data)


class TcFitter(Fitter):
    title = 'Tc fit'
    picks = ['Background', 'Tc']

    def do_fit(self):
        (_, Ib), (Tc, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        alpha0 = 0.5
        # guess A from maximum data point
        Tmin = min(self.data[0])
        A0 = max(self.data[1]) / ((Tc-Tmin)/Tc)**alpha0
        parstart = [Ib, A0, Tc, alpha0]
        f = TcFit(parstart)
        return f.run_or_raise(*self.data)


class ArbitraryFitter(Fitter):
    title = 'fit'

    arby_functions = {
        'Gaussian x2': ('a + b*exp(-(x-x1)**2/s1**2) + c*exp(-(x-x2)**2/s2**2)',
                        'a b c x1 x2 s1 s2'),
        'Gaussian x3 symm.':
            ('a + b*exp(-(x-x0-x1)**2/s1**2) + b*exp(-(x-x0+x1)**2/s1**2) + '
             'c*exp(-(x-x0)**2/s0**2)', 'a b c x0 x1 s0 s1'),
        'Parabola': ('a*x**2 + b*x + c', 'a b c'),
    }

    def begin(self):
        dlg = dialogFromUi(self.plot, 'fit_arby.ui', 'panels')
        pr = DlgPresets('fit_arby',
                        [(dlg.function, ''), (dlg.fitparams, ''),
                         (dlg.xfrom, ''), (dlg.xto, '')])
        pr.load()
        for name in sorted(self.arby_functions):
            QListWidgetItem(name, dlg.oftenUsed)

        def click_cb(item):
            func, params = self.arby_functions[item.text()]
            dlg.function.setText(func)
            dlg.fitparams.setPlainText('\n'.join(
                p + ' = ' for p in params.split()))
        dlg.oftenUsed.itemClicked.connect(click_cb)
        ret = dlg.exec_()
        if ret != QDialog.Accepted:
            return
        pr.save()
        fcnstr = dlg.function.text()
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

        ns = {}
        exec_('from numpy import *', ns)
        try:
            model = eval('lambda x, %s: %s' % (', '.join(params), fcnstr), ns)
        except SyntaxError as e:
            self.plot.showInfo('Syntax error in function: %s' % e)
            return

        f = Fit('fit', model, params, values, xmin, xmax)
        res = f.run(*self.data)
        if res._failed:
            self.plot.showInfo('Fitting failed: %s.' % res._message)
            return
        res.label_x = res.curve_x[0]
        res.label_y = max(res.curve_y)
        res.label_contents = list(zip(*res._pars))

        self.plot._plotFit(res)


class NicosPlotCurve(MaskedPlotCurve):

    GR_MARKER_SIZE = 1.0

    _parent = ''

    def __init__(self, x, y, errBar1=None, errBar2=None,
                 linetype=gr.LINETYPE_SOLID, markertype=gr.MARKERTYPE_DOT,
                 linecolor=None, markercolor=1, legend=None, fillx=0, filly=0):
        MaskedPlotCurve.__init__(self, x, y, errBar1, errBar2,
                                 linetype, markertype, linecolor, markercolor,
                                 legend, fillx=fillx, filly=filly)
        self._dependent = []

    @property
    def dependent(self):
        """Return dependent objects which implement the GRMeta interface."""
        return self._dependent

    @dependent.setter
    def dependent(self, value):
        self._dependent = value

    @property
    def visible(self):
        return MaskedPlotCurve.visible.__get__(self)

    @visible.setter
    def visible(self, flag):
        MaskedPlotCurve.visible.__set__(self, flag)
        for dep in self.dependent:
            dep.visible = flag

    def drawGR(self):
        gr.setmarkersize(self.GR_MARKER_SIZE)
        MaskedPlotCurve.drawGR(self)
        for dep in self.dependent:
            if dep.visible:
                dep.drawGR()


class NicosPlot(DlgUtils):

    HAS_AUTOSCALE = False
    SAVE_EXT = '.png'

    def __init__(self, window, timeaxis=False):
        DlgUtils.__init__(self, 'Plot')
        self.window = window
        self.plotcurves = []
        self.show_all = False
        self.timeaxis = timeaxis
        self.hasSymbols = False
        self.hasLines = True

        # currently selected normalization column
        self.normalized = None

        self.fitter = None

        font = self.window.user_font
        bold = QFont(font)
        bold.setBold(True)
        larger = QFont(font)
        larger.setPointSize(font.pointSize() * 1.6)
        self.setFonts(font, bold, larger)

    def setBackgroundColor(self, color):
        raise NotImplementedError

    def setFonts(self, font, bold, larger):
        raise NotImplementedError

    def titleString(self):
        raise NotImplementedError

    def subTitleString(self):
        return ''

    def xaxisName(self):
        raise NotImplementedError

    def yaxisName(self):
        raise NotImplementedError

    def xaxisScale(self):
        return None

    def yaxisScale(self):
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

    def unzoom(self):
        """Unzoom the plot."""
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

    def visibleCurves(self):
        """Return a list of tuples (index, description) of visible curves."""
        raise NotImplementedError

    def visibleDataCurves(self):
        """Return a list of tuples (index, description) of visible curves
        that are not fits.
        """
        raise NotImplementedError

    def selectCurve(self):
        """Let the user select a visible plot curve.

        If there is only one curve, return it directly.
        """
        visible_curves = self.visibleDataCurves()
        if not visible_curves:
            return
        if len(visible_curves) > 1:
            dlg = dialogFromUi(self, 'selector.ui', 'panels')
            dlg.setWindowTitle('Select curve to fit')
            dlg.label.setText('Select a curve:')
            for _, descr in visible_curves:
                QListWidgetItem(descr, dlg.list)
            dlg.list.setCurrentRow(0)
            if dlg.exec_() != QDialog.Accepted:
                return
            fitcurve = visible_curves[dlg.list.currentRow()][0]
        else:
            fitcurve = visible_curves[0][0]
        return self.plotcurves[fitcurve]

    def beginFit(self, fitterclass, fitteraction):
        """Begin a fitting operation with given Fitter subclass and QAction."""
        if fitteraction and not fitteraction.isChecked():
            # "unchecking" the action -> cancel fit
            if self.fitter is not None:
                self.fitter.cancel()
            return
        # other fitter: cancel first
        if self.fitter is not None:
            self.fitter.cancel()
        fitcurve = self.selectCurve()
        if not fitcurve:
            return self.showError('Plot must have a visible curve '
                                  'to be fitted.')
        self.fitter = fitterclass(self, self.window, fitteraction, fitcurve)
        self.fitter.begin()

    def _getCurveData(self, curve):
        """Return [x, y, dy] or [x, y, None] arrays for given curve."""
        raise NotImplementedError

    def _getCurveLegend(self, curve):
        """Return legend string of the curve."""
        raise NotImplementedError

    def _isCurveVisible(self, curve):
        """Return true if curve is currently visible."""
        raise NotImplementedError

    def _enterFitMode(self):
        raise NotImplementedError

    def _leaveFitMode(self):
        raise NotImplementedError

    def _fitRequestPick(self, paramname):
        raise NotImplementedError

    def _plotFit(self, fitter):
        raise NotImplementedError

    def modifyData(self):
        visible_curves = self.visibleCurves()
        # get input from the user: which curves should be modified how
        dlg = dialogFromUi(self, 'modify.ui', 'panels')

        def checkAll():
            for i in range(dlg.list.count()):
                dlg.list.item(i).setCheckState(Qt.Checked)
        dlg.selectall.clicked.connect(checkAll)
        for i, descr in visible_curves:
            li = QListWidgetItem(descr, dlg.list)
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
            curve = self.plotcurves[visible_curves[i][0]]
            self._modifyCurve(curve, op)
        self.update()

    def _modifyCurve(self, curve, op):
        raise NotImplementedError


class NicosGrPlot(NicosPlot, InteractiveGRWidget):

    axescls = NicosPlotAxes
    HAS_AUTOSCALE = True
    SAVE_EXT = '.svg'

    def __init__(self, parent, window, timeaxis=False):
        InteractiveGRWidget.__init__(self, parent)
        NicosPlot.__init__(self, window, timeaxis=timeaxis)

        self.timeaxis = timeaxis or (self.axescls == NicosTimePlotAxes)
        self.leftTurnedLegend = True
        self.statusMessage = None
        self.mouselocation = None
        self._cursor = self.cursor()
        self._mouseSelEnabled = self.getMouseSelectionEnabled()

        dictPrintType = dict(gr.PRINT_TYPE)
        for prtype in [gr.PRINT_JPEG, gr.PRINT_TIF]:
            dictPrintType.pop(prtype)
        self._saveTypes = (";;".join(dictPrintType.values()) + ";;" +
                           ";;".join(gr.GRAPHIC_TYPE.values()))
        self._saveName = None
        self._color = ColorIndexGenerator()
        self._plot = Plot(viewport=(.1, .85, .15, .88))
        self._plot.setLegendWidth(0.05)
        self._axes = self.axescls(viewport=self._plot.viewport)
        self._axes.backgroundColor = 0
        self._plot.addAxes(self._axes)
        self._plot.title = self.titleString()
        self.addPlot(self._plot)

        guiConn = GUIConnector(self)
        guiConn.connect(LegendEvent.ROI_CLICKED, self.on_legendItemClicked,
                        LegendEvent)
        guiConn.connect(ROIEvent.ROI_CLICKED, self.on_roiItemClicked, ROIEvent)
        guiConn.connect(MouseEvent.MOUSE_PRESS, self.on_fitPicker_selected)
        guiConn.connect(MouseEvent.MOUSE_MOVE, self.on_mouseMove)
        self.logXinDomain.connect(self.on_logXinDomain)
        self.logYinDomain.connect(self.on_logYinDomain)
        self.setLegend(True)
        self.updateDisplay()

    def xtickCallBack(self, x, y, _svalue, value):
        gr.setcharup(-1. if self.leftTurnedLegend else 1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_RIGHT if self.leftTurnedLegend else
                        gr.TEXT_HALIGN_LEFT, gr.TEXT_VALIGN_TOP)
        dx = .015
        timeVal = time.localtime(value)
        gr.text(x + (dx if self.leftTurnedLegend else -dx), y,
                time.strftime(DATEFMT, timeVal))
        gr.text(x - (dx if self.leftTurnedLegend else -dx), y,
                time.strftime(TIMEFMT, timeVal))
        gr.setcharup(0., 1.)

    def setAutoScaleFlags(self, xflag, yflag):
        mask = 0x0
        if xflag:
            mask |= PlotAxes.SCALE_X
        if yflag:
            mask |= PlotAxes.SCALE_Y
        self.setAutoScale(mask)

    def setBackgroundColor(self, color):
        pass  # not implemented

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
        markertype = gr.MARKERTYPE_OMARK if on else gr.MARKERTYPE_DOT
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
            if event.curve._parent:
                event.curve._parent.disabled = not event.curve._parent.disabled
            self.update()

    def on_roiItemClicked(self, event):
        if event.getButtons() & MouseEvent.RIGHT_BUTTON:
            if isinstance(event.roi.reference, FitResult):
                menu = QMenu(self)
                actionClipboard = QAction("Copy fit values to clipboard", menu)
                menu.addAction(actionClipboard)
                p0dc = event.getDC()
                selectedItem = menu.exec_(self.mapToGlobal(QPoint(p0dc.x,
                                                                  p0dc.y)))
                if selectedItem == actionClipboard:
                    res = event.roi.reference
                    text = '\n'.join(
                        (n + '\t' if n else '\t') +
                        (v + '\t' if isinstance(v, string_types)
                         else '%g\t' % v) +
                        (dv if isinstance(dv, string_types)
                         else '%g' % dv)
                        for (n, v, dv) in res.label_contents)
                    QApplication.clipboard().setText(text)

    def on_mouseMove(self, event):
        if event.getWindow():  # inside plot
            self.mouselocation = event
            wc = event.getWC(self._plot.viewport)
            if self.statusMessage:
                msg = "%s (X = %g, Y = %g)" % (self.statusMessage, wc.x, wc.y)
            else:
                msg = "X = %g, Y = %g" % (wc.x, wc.y)
            self.window.statusBar.showMessage(msg)
        else:
            self.window.statusBar.clearMessage()

    def addPlotCurve(self, plotcurve, replot=False):
        existing_curve = next((c for c in self._axes.getCurves()
                               if c._parent is plotcurve._parent), None)
        if existing_curve and not replot:
            existing_curve.visible = plotcurve.visible
            existing_curve.legend = plotcurve.legend
            # update curve
            existing_curve.x, existing_curve.y = plotcurve.x, plotcurve.y
            if plotcurve.errorBar1 and existing_curve.errorBar1:
                mcolor = existing_curve.errorBar1.markercolor
                existing_curve.errorBar1 = plotcurve.errorBar1
                existing_curve.errorBar1.markercolor = mcolor
            else:
                existing_curve.errorBar1 = plotcurve.errorBar1
            if plotcurve.errorBar2 and existing_curve.errorBar2:
                mcolor = existing_curve.errorBar2.markercolor
                existing_curve.errorBar2 = plotcurve.errorBar2
                existing_curve.errorBar2.markercolor = mcolor
            else:
                existing_curve.errorBar2 = plotcurve.errorBar2
            if existing_curve not in self.plotcurves:
                self.plotcurves.append(existing_curve)
        else:
            color = self._color.getNextColorIndex()
            plotcurve.linecolor = color
            plotcurve.markercolor = color
            plotcurve.markertype = gr.MARKERTYPE_OMARK if self.hasSymbols \
                else gr.MARKERTYPE_DOT
            if plotcurve.errorBar1:
                plotcurve.errorBar1.markercolor = color
            if plotcurve.errorBar2:
                plotcurve.errorBar2.markercolor = color
            self._axes.addCurves(plotcurve)
            self.plotcurves.append(plotcurve)

    def savePlot(self):
        saveName = None
        dialog = QFileDialog(self, "Select file name", "", self._saveTypes)
        dialog.selectNameFilter(gr.PRINT_TYPE[gr.PRINT_PDF])
        dialog.setNameFilterDetailsVisible(True)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        if dialog.exec_() == QDialog.Accepted:
            path = dialog.selectedFiles()[0]
            if path:
                _p, suffix = os.path.splitext(path)
                if suffix:
                    suffix = suffix.lower()
                else:
                    # append selected name filter suffix (filename extension)
                    nameFilter = dialog.selectedNameFilter()
                    for k, v in gr.PRINT_TYPE.items():
                        if v == nameFilter:
                            suffix = '.' + k
                            path += suffix
                            break
                if suffix and (suffix[1:] in gr.PRINT_TYPE or
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
        self.setCursor(QCursor(Qt.CrossCursor))
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

    def _plotFit(self, res):
        color = self._color.getNextColorIndex()
        resultcurve = NicosPlotCurve(res.curve_x, res.curve_y,
                                     legend=res._title,
                                     linecolor=color, markercolor=color)
        self.addPlotCurve(resultcurve, True)
        resultcurve.markertype = gr.MARKERTYPE_DOT
        self.window.statusBar.showMessage("Fitting complete")

        text = '\n'.join(
            (n + ': ' if n else '') +
            (v if isinstance(v, string_types) else '%g' % v) +
            (dv if isinstance(dv, string_types) else ' +/- %g' % dv)
            for (n, v, dv) in res.label_contents)
        grtext = Text(res.label_x, res.label_y, text, self._axes, .012,
                      hideviewport=False)
        resultcurve.dependent.append(grtext)
        coord = CoordConverter(self._axes.sizex, self._axes.sizey,
                               self._axes.getWindow())
        roi = RegionOfInterest(reference=res, regionType=RegionOfInterest.TEXT,
                               axes=self._axes)
        for nxi, nyi in zip(*grtext.getBoundingBox()):
            coord.setNDC(nxi, nyi)
            roi.append(coord.getWC(self._axes.viewport))
        self._plot.addROI(roi)
        self.update()

    def on_fitPicker_selected(self, point):
        if self.fitter and point.getButtons() & MouseEvent.LEFT_BUTTON and \
                point.getWindow():
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


class ViewPlot(NicosGrPlot):

    axescls = NicosTimePlotAxes

    def __init__(self, parent, window, view):
        self.view = view
        self.series2curve = {}
        NicosGrPlot.__init__(self, parent, window, timeaxis=True)
        self.setSymbols(False)

    def cleanup(self):
        self.view = None
        self._axes.setXtickCallback(None)

    def titleString(self):
        return self.view.name

    def xaxisName(self):
        return 'time'

    def yaxisName(self):
        return 'value'

    def yaxisScale(self):
        if self.view.yfrom is not None:
            return (self.view.yfrom, self.view.yto)

    def on_mouseMove(self, event):
        wc = event.getWC(self._plot.viewport)
        # overridden to show the correct timestamp
        ts = time.strftime(DATEFMT + ' ' + TIMEFMT, time.localtime(wc.x))
        if self.statusMessage:
            msg = "%s (X = %s, Y = %g)" % (self.statusMessage, ts, wc.y)
        else:
            msg = "X = %s, Y = %g" % (ts, wc.y)
        self.window.statusBar.showMessage(msg)

    def addAllCurves(self):
        for i, series in enumerate(self.view.series.values()):
            self.addCurve(i, series)

    def addCurve(self, i, series, replot=False):
        n = series.n
        if n > 0:
            color = self._color.getNextColorIndex()
            plotcurve = NicosPlotCurve(series.x[:n], series.y[:n],
                                       legend=series.title,
                                       linecolor=color, markercolor=color)
            plotcurve._parent = series
            self.series2curve[series] = plotcurve
            self.addPlotCurve(plotcurve, replot)

    def visibleCurves(self):
        return [(i, self._getCurveLegend(plotcurve))
                for (i, plotcurve) in enumerate(self.plotcurves)
                if self._isCurveVisible(plotcurve)]

    def visibleDataCurves(self):
        return [(i, self._getCurveLegend(plotcurve))
                for (i, plotcurve) in enumerate(self.plotcurves)
                if self._isCurveVisible(plotcurve)
                and 'fit' not in self._getCurveLegend(plotcurve)]

    def pointsAdded(self, series):
        plotcurve = self.series2curve[series]
        plotcurve.x = series.x[:series.n].copy()
        plotcurve.y = series.y[:series.n].copy()
        plotcurve.legend = series.title
        self._axes.addCurves(plotcurve)
        InteractiveGRWidget.update(self)

    def setSlidingWindow(self, window):
        self._axes.slidingwindow = window

    def saveData(self):
        curvenames = [self._getCurveLegend(plotcurve)
                      for plotcurve in self.plotcurves]
        dlg = DataExportDialog(self, curvenames,
                               'Select curve(s), file name and format',
                               '', 'ASCII data files (*.dat)')
        res = dlg.exec_()
        if res != QDialog.Accepted:
            return
        if not dlg.selectedFiles():
            return
        fmtno = dlg.formatCombo.currentIndex()
        sel_filename = dlg.selectedFiles()[0]
        if '.' not in sel_filename:
            sel_filename += '.dat'
        base, ext = path.splitext(sel_filename)

        curve_index = dlg.curveCombo.currentIndex()
        if curve_index == 0:
            curves = self.plotcurves
            filenames = [base + '_' +
                         safeFilename(self._getCurveLegend(curve)) + ext
                         for curve in curves]
        else:
            curves = [self.plotcurves[curve_index - 1]]
            filenames = [sel_filename]

        for curve, filename in zip(curves, filenames):
            x, y, _ = self._getCurveData(curve)
            n = len(x)

            if n < 1:
                QMessageBox.information(
                    self, 'Error',
                    'No data in curve %r' % self._getCurveLegend(curve))
                continue

            with open(filename, 'wb') as fp:
                for i in range(n):
                    if fmtno == 0:
                        fp.write('%s\t%s\n' % (x[i] - x[0], y[i]))
                    elif fmtno == 1:
                        fp.write('%s\t%s\n' % (x[i], y[i]))
                    else:
                        fp.write('%s\t%s\n' % (
                            time.strftime('%Y-%m-%d.%H:%M:%S',
                                          time.localtime(x[i])),
                            y[i]))


class DataSetPlot(NicosGrPlot):

    axescls = NicosPlotAxes

    def __init__(self, parent, window, dataset):
        self.dataset = dataset
        self.current_xname = dataset.default_xname
        NicosGrPlot.__init__(self, parent, window)
        self.setSymbols(True)

    def titleString(self):
        return "Scan %s %s" % (self.dataset.name, self.dataset.scaninfo)

    def subTitleString(self):
        return "started %s" % time.strftime(DATEFMT + ' ' + TIMEFMT,
                                            self.dataset.started)

    def xaxisName(self):
        return self.current_xname

    def yaxisName(self):
        return ''

    def addAllCurves(self):
        for i, curve in enumerate(self.dataset.curves):
            self.addCurve(i, curve)

    def addCurve(self, i, curve, replot=False):
        if self.current_xname != 'Default' and \
           self.current_xname not in curve.datax:
            return
        if not curve.datay:
            return
        plotcurve = NicosPlotCurve([], [], filly=0.1)
        plotcurve._parent = curve
        self.setCurveData(curve, plotcurve)
        self.addPlotCurve(plotcurve, replot)
        if curve.function:
            plotcurve.markertype = gr.MARKERTYPE_DOT

    def setCurveData(self, curve, plotcurve):
        xname = curve.default_xname \
            if self.current_xname == 'Default' else self.current_xname
        if self.normalized == 'Maximum':
            norm = [max(curve.datay)] * len(curve.datay)
        else:
            norm = curve.datanorm[self.normalized] if self.normalized else None
        x, y, dy = prepareData(curve.datax[xname], curve.datay, curve.datady,
                               norm)
        y = numpy.ma.masked_equal(y, 0)
        if dy is not None:
            errbar = ErrorBar(x, y, dy, markercolor=plotcurve.markercolor)
            plotcurve.errorBar1 = errbar
        plotcurve.x = x
        plotcurve.y = y
        plotcurve.filly = 0.1 if self.isLogScaling() else 0
        plotcurve.visible = not (curve.disabled or curve.hidden or not x.size)
        plotcurve.legend = curve.full_description if not curve.hidden else ''

    def enableCurvesFrom(self, otherplot):
        visible = {}
        for curve in otherplot.plotcurves:
            visible[self._getCurveLegend(curve)] = self._isCurveVisible(curve)
        changed = False
        remaining = len(self.plotcurves)
        for plotcurve in self.plotcurves:
            namestr = self._getCurveLegend(plotcurve)
            if namestr in visible:
                self.setVisibility(plotcurve, visible[namestr])
                changed = True
                if not visible[namestr]:
                    remaining -= 1
        # no visible curve left?  enable all of them again
        if not remaining:
            for plotcurve in self.plotcurves:
                # XXX only if it has a legend item (excludes monitor/time columns)
                self.setVisibility(plotcurve, True)
        if changed:
            self.update()

    def visibleCurves(self):
        return [(i, curve.full_description)
                for (i, curve) in enumerate(self.dataset.curves)
                if self._isCurveVisible(self.plotcurves[i])]

    def visibleDataCurves(self):
        # visibleCurves only includes data curves anyway
        return self.visibleCurves()

    def setLogScale(self, on):
        NicosGrPlot.setLogScale(self, on)
        filly = .1 if self.isLogScaling() else 0
        for axis in self._plot.getAxes():
            for curve in axis.getCurves():
                curve.filly = filly
        self.update()

    def pointsAdded(self):
        curve = None
        for curve, plotcurve in zip(self.dataset.curves, self.plotcurves):
            self.setCurveData(curve, plotcurve)
        if self.plotcurves and len(self.plotcurves[0].x) == 2:
            # When there is only one point, GR autoselects a range related to
            # the magnitude of the point. Now that we have two points, we can
            # scale to actual X interval of the scan.
            self._axes.reset()
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
