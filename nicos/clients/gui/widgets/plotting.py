#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

import os
import tempfile
import time
from os import path

import gr
import numpy as np
import numpy.ma
from gr.pygr import CoordConverter, ErrorBar, Plot, PlotAxes, \
    RegionOfInterest, Text
from gr.pygr.helper import ColorIndexGenerator

from nicos.clients.gui.dialogs.data import DataExportDialog
from nicos.clients.gui.utils import DlgPresets, DlgUtils, dialogFromUi, loadUi
from nicos.guisupport.plots import DATEFMT, TIMEFMT, MaskedPlotCurve, \
    NicosPlotAxes, NicosTimePlotAxes
from nicos.guisupport.qt import QAction, QApplication, QCursor, QDialog, \
    QFileDialog, QFont, QListWidgetItem, QMenu, QPoint, Qt
from nicos.guisupport.qtgr import GUIConnector, InteractiveGRWidget, \
    LegendEvent, MouseEvent, ROIEvent
from nicos.guisupport.utils import scaledFont
# pylint: disable=redefined-builtin
from nicos.pycompat import exec_, string_types, number_types
from nicos.utils import safeName
from nicos.utils.fitting import CosineFit, ExponentialFit, Fit, FitError, \
    FitResult, GaussFit, LinearFit, LorentzFit, PearsonVIIFit, \
    PseudoVoigtFit, SigmoidFit, TcFit


def cleanArray(arr):
    """Clean an array or list from unsupported objects for plotting.

    Objects are replaced by None, which is then converted to NaN.
    """
    try:
        return np.asarray(arr, float)
    except ValueError:
        return np.array([x if isinstance(x, number_types) else None
                         for x in arr], float)


def prepareData(x, y, dy, norm):
    """Prepare and sanitize data for plotting.

    x, y and dy are lists or arrays. norm can also be None.

    Returns x, y and dy arrays, where dy can also be None.
    """
    # make arrays
    x = cleanArray(x)
    y = cleanArray(y)
    dy = cleanArray(dy)
    # normalize
    if norm is not None:
        norm = np.asarray(norm, float)
        y /= norm
        dy /= norm
    # remove infinity/NaN
    indices = np.isfinite(y) & np.isfinite(x)
    x = x[indices]
    y = y[indices]
    if not y.size:
        raise ValueError('y does not contain any value')
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

    def __init__(self, plot, window, action, curve, pickmode):
        self.plot = plot
        self.window = window
        self.action = action
        self.curve = curve
        self.pickmode = pickmode
        self.data = plot._getCurveData(curve)

        self.values = []
        self.stage = 0

    def begin(self):
        self.plot._enterFitMode()
        if self.action:
            self.action.setChecked(True)
        if self.pickmode:
            self.plot._fitRequestPick(self.picks[0])
        else:
            self.finish()

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

    def limitsFromPlot(self):
        return self.plot.getViewport()[:2]


class LinearFitter(Fitter):
    title = 'linear fit'
    picks = ['First point', 'Second point']

    def do_fit(self):
        if self.pickmode:
            (xmin, y1), (xmax, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            m0 = (y2 - y1) / (xmax - xmin)
            pars = [m0, y1 - m0*xmin]
        else:
            pars = None
            xmin, xmax = self.limitsFromPlot()

        f = LinearFit(pars, xmin=xmin, xmax=xmax, timeseries=True)
        return f.run_or_raise(*self.data)


class ExponentialFitter(Fitter):
    title = 'exp. fit'
    picks = ['First point', 'Second point']

    def do_fit(self):
        if self.pickmode:
            (xmin, y1), (xmax, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            b0 = np.log(y1 / y2) / (xmin - xmax)
            x0 = xmin - np.log(y1) / b0
            pars = [b0, x0]
        else:
            pars = None
            xmin, xmax = self.limitsFromPlot()

        f = ExponentialFit(pars, xmin=xmin, xmax=xmax, timeseries=True)
        return f.run_or_raise(*self.data)


class CosineFitter(Fitter):
    title = 'cosine fit'
    picks = ['Maximum', 'Next minimum']

    def do_fit(self):
        pars = None
        if self.pickmode:
            (x1, y1), (x2, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            a = abs(y1 - y2) / 2.
            b = (y1 + y2) / 2.
            width = abs(x1 - x2)
            freq = 1 / (width * 2.)
            pars = [a, freq, x1, b]

        f = CosineFit(pars)
        return f.run_or_raise(*self.data)


class LorentzFitter(Fitter):
    title = 'peak fit'
    picks = ['Background', 'Peak', 'Half Maximum']

    def do_fit(self):
        if self.pickmode:
            (xb, yb), (x0, y0), (xw, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            pars = [x0, abs(y0-yb), abs(x0-xw), yb]
            totalwidth = abs(x0 - xb)
            xmin = x0 - totalwidth
            xmax = x0 + totalwidth
        else:
            pars = None
            xmin, xmax = self.limitsFromPlot()

        f = LorentzFit(pars, xmin=xmin, xmax=xmax)
        return f.run_or_raise(*self.data)


class GaussFitter(Fitter):
    title = 'peak fit'
    picks = ['Background', 'Peak', 'Half Maximum']

    def do_fit(self):
        if self.pickmode:
            (xb, yb), (x0, y0), (xw, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            pars = [x0, abs(y0-yb), abs(x0-xw), yb]
            totalwidth = abs(x0 - xb)
            xmin = x0 - totalwidth
            xmax = x0 + totalwidth
        else:
            pars = None
            xmin, xmax = self.limitsFromPlot()

        f = GaussFit(pars, xmin=xmin, xmax=xmax)
        return f.run_or_raise(*self.data)


class SigmoidFitter(Fitter):
    title = 'sigmoid fit'
    picks = ['Left point', 'Right point']

    def do_fit(self):
        if self.pickmode:
            (xmin, y1), (xmax, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            pars = [y2 - y1, 1, (xmax - xmin) / 2. + xmin, y1]
        else:
            pars = None
            xmin, xmax = self.limitsFromPlot()

        f = SigmoidFit(pars, xmin=xmin, xmax=xmax)
        return f.run_or_raise(*self.data)


class PseudoVoigtFitter(Fitter):
    title = 'peak fit (PV)'
    picks = ['Background', 'Peak', 'Half Maximum']

    def do_fit(self):
        if self.pickmode:
            (xb, yb), (x0, y0), (xw, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            pars = [yb, abs(y0 - yb), x0, abs(x0 - xw), 0.5]
            totalwidth = abs(x0 - xb)
            xmin = x0 - totalwidth
            xmax = x0 + totalwidth
        else:
            pars = None
            xmin, xmax = self.limitsFromPlot()

        f = PseudoVoigtFit(pars, xmin=xmin, xmax=xmax)
        return f.run_or_raise(*self.data)


class PearsonVIIFitter(Fitter):
    title = 'peak fit (PVII)'
    picks = ['Background', 'Peak', 'Half Maximum']

    def do_fit(self):
        if self.pickmode:
            (xb, yb), (x0, y0), (xw, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            pars = [yb, abs(y0-yb), x0, abs(x0-xw), 5.0]
            totalwidth = abs(x0 - xb)
            xmin = x0 - totalwidth
            xmax = x0 + totalwidth
        else:
            pars = None
            xmin, xmax = self.limitsFromPlot()

        f = PearsonVIIFit(pars, xmin=xmin, xmax=xmax)
        return f.run_or_raise(*self.data)


class TcFitter(Fitter):
    title = 'Tc fit'
    picks = ['Background', 'Tc']

    def do_fit(self):
        pars = None
        if self.pickmode:
            (_, Ib), (Tc, _) = self.values  # pylint: disable=unbalanced-tuple-unpacking
            alpha0 = 0.5
            # guess A from maximum data point
            Tmin = min(self.data[0])
            A0 = max(self.data[1]) / ((Tc-Tmin)/Tc)**alpha0
            pars = [Ib, A0, Tc, alpha0]

        f = TcFit(pars)
        return f.run_or_raise(*self.data)


class ArbyFitDialog(QDialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        loadUi(self, 'panels/fit_arby.ui')
        self.presets = DlgPresets('fit_arby',
                                  [(self.function, ''), (self.fitparams, ''),
                                   (self.xfrom, ''), (self.xto, '')])
        self.presets.load()
        for name in sorted(ArbitraryFitter.arby_functions):
            QListWidgetItem(name, self.oftenUsed)

    def on_oftenUsed_itemClicked(self, item):
        params, func = ArbitraryFitter.arby_functions[item.text()]
        self.function.setText(func)
        self.fitparams.setPlainText('\n'.join(params))

    def getFunction(self):
        self.presets.save()

        fcnstr = self.function.text()
        try:
            xmin = float(self.xfrom.text())
        except ValueError:
            xmin = None
        try:
            xmax = float(self.xto.text())
        except ValueError:
            xmax = None
        if xmin is not None and xmax is not None and xmin > xmax:
            xmax, xmin = xmin, xmax
        params, values = [], []
        for line in self.fitparams.toPlainText().splitlines():
            name_value = line.strip().split('=', 2)
            if len(name_value) < 2:
                continue
            params.append(name_value[0])
            try:
                values.append(float(name_value[1]))
            except ValueError:
                values.append(1.0)

        return fcnstr, params, values, xmin, xmax


class ArbitraryFitter(Fitter):
    title = 'fit'

    arby_functions = {
        'Gaussian x2': (
            ['a =', 'b =', 'c =', 'x1 =', 'x2 =', 's1 =', 's2 ='],
            'a + b*exp(-(x-x1)**2/s1**2) + c*exp(-(x-x2)**2/s2**2)',
        ),
        'Gaussian x3 symm.': (
            ['a =', 'b =', 'c =', 'x0 =', 'x1 =', 's0 =', 's1 ='],
            'a + b*exp(-(x-x0-x1)**2/s1**2) + b*exp(-(x-x0+x1)**2/s1**2) + '
            'c*exp(-(x-x0)**2/s0**2)',
        ),
        'Parabola': (
            ['a =', 'b =', 'c ='],
            'a*x**2 + b*x + c',
        ),
    }

    def begin(self):
        dlg = ArbyFitDialog(self.plot)
        ret = dlg.exec_()
        if ret != QDialog.Accepted:
            return

        fcnstr, params, values, xmin, xmax = dlg.getFunction()

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
        self._enableErrBars = True

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

    def isErrorBarEnabled(self, idx):
        return self._enableErrBars

    def setErrorBarEnabled(self, flag):
        """Dis/En-able error bars for this curve.

        Disabled error bars are not drawn and the corresponding
        property `errorBar{1,2}` returns None.

        Note: The internal reference to the `ErrorBar` is still kept and
        restored on enable.

        """
        self._enableErrBars = flag

    @property
    def errorBar1(self):
        if not self._enableErrBars:
            return None
        return MaskedPlotCurve.errorBar1.__get__(self)

    @errorBar1.setter
    def errorBar1(self, value):
        MaskedPlotCurve.errorBar1.__set__(self, value)

    @property
    def errorBar2(self):
        if not self._enableErrBars:
            return None
        return MaskedPlotCurve.errorBar2.__get__(self)

    @errorBar2.setter
    def errorBar2(self, value):
        MaskedPlotCurve.errorBar2.__set__(self, value)

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
        larger = scaledFont(font, 1.6)
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

    def isErrorBarEnabled(self):
        raise NotImplementedError

    def setErrorBarEnabled(self, on):
        """Switch error bars on or off."""
        raise NotImplementedError

    def setVisibility(self, item, on):
        """Set visibility on a plot item."""
        raise NotImplementedError

    def isLogScaling(self, idx=0):
        """Return true if main Y axis is logscaled."""
        raise NotImplementedError

    def isLogXScaling(self, idx=0):
        """Return true if X axis is logscaled."""
        raise NotImplementedError

    def setLogScale(self, on):
        """Set logscale on main Y axis."""
        raise NotImplementedError

    def setLogXScale(self, on):
        """Set logscale on X axis"""
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
            dlg = dialogFromUi(self, 'panels/selector.ui')
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

    def beginFit(self, fitterclass, fitteraction, pickmode):
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
        self.fitter = fitterclass(self, self.window, fitteraction, fitcurve,
                                  pickmode)
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

    def getViewport(self):
        raise NotImplementedError

    def modifyData(self):
        visible_curves = self.visibleCurves()
        # get input from the user: which curves should be modified how
        dlg = dialogFromUi(self, 'panels/modify.ui')

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
        self._markertype = gr.MARKERTYPE_OMARK

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

    def isLogXScaling(self, idx=0):
        axes = self._plot.getAxes(idx)
        return (axes.scale & gr.OPTION_X_LOG if axes is not None else False)

    def setLogScale(self, on):
        self._plot.setLogY(on, rescale=True)
        self.update()

    def setLogXScale(self, on):
        self._plot.setLogX(on, rescale=True)
        self.update()

    def isErrorBarEnabled(self):
        axes = self._plot.getAxes(0)
        if axes:
            curves = axes.getCurves()
            if curves:
                return curves[0].isErrorBarEnabled(1)
        return False

    def setErrorBarEnabled(self, flag):
        for axis in self._plot.getAxes():
            for curve in axis.getCurves():
                curve.setErrorBarEnabled(flag)
        self.update()

    def setSymbols(self, on):
        markertype = self._markertype if on else gr.MARKERTYPE_DOT
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
            existing_curve.setUpdateXCallback(None)
            existing_curve.setUpdateYCallback(None)
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
            plotcurve.markertype = self._markertype if self.hasSymbols \
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
        dialog.setOption(dialog.HideNameFilterDetails, False)
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
        if item._parent:
            item._parent.disabled = not on

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

    def setMarkerType(self, markertype):
        self._markertype = markertype


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
        visiblePlotCurves = self._axes.getVisibleCurves()
        if visiblePlotCurves:
            self._axes.curveDataChanged(visiblePlotCurves[-1])

    def addCurve(self, i, series, replot=False):
        plotcurve = None
        n = series.n
        if n > 0:
            color = self._color.getNextColorIndex()
            plotcurve = NicosPlotCurve(series.x, series.y,
                                       legend=series.title,
                                       linecolor=color, markercolor=color)
            plotcurve._parent = series
            self.series2curve[series] = plotcurve
            self.addPlotCurve(plotcurve, replot)
        return plotcurve

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
        plotcurve.x = series.x
        plotcurve.y = series.y
        plotcurve.legend = series.title
        self._axes.addCurves(plotcurve)
        InteractiveGRWidget.update(self)

    def setSlidingWindow(self, window):
        self._axes.slidingwindow = window

    def getViewport(self):
        return self._plot.getAxes(0).getWindow()

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
            curvedata = [convertXCol(fmtno, *self._getCurveData(c)[:2])
                         for c in self.plotcurves]
            if len(curvedata) > 1:
                filenames = [base + '_' +
                             safeName(self._getCurveLegend(c)) + ext
                             for c in self.plotcurves]
            else:
                filenames = [sel_filename]
        elif curve_index == 1:
            curvedata = [synthesizeSingleCurveData(
                [self._getCurveData(c)[:2] for c in self.plotcurves], fmtno)]
            filenames = [sel_filename]
        else:
            curve = self.plotcurves[curve_index - 2]
            curvedata = [convertXCol(fmtno, *self._getCurveData(curve)[:2])]
            filenames = [sel_filename]

        for curve, filename in zip(curvedata, filenames):
            np.savetxt(filename, curve, fmt='%s')


def convertXCol(fmtno, x, *ys):
    ystack = [np.asarray(y) for y in ys]
    if fmtno == 0:    # seconds since first datapoint
        x = np.asarray(x)
        return np.stack([x - x[0]] + ystack, 1)
    elif fmtno == 1:  # UNIX timestamp
        x = np.asarray(x)
        return np.stack([x] + ystack, 1)
    elif fmtno == 2:  # formatted time
        return np.stack([np.array([time.strftime('%Y-%m-%d.%H:%M:%S',
                                                 time.localtime(v))
                                   for v in x])] + ystack, 1)
    raise NotImplementedError('invalid time format')


def synthesizeSingleCurveData(curvedata, fmtno, window=0.1):
    """Generate a single matrix with value Y1...Yn for a single time column
    from a list of separate (X, Y) curves

    Y values of curves that don't have data for inbetween points is not
    interpolated, but the last value is repeated.
    """
    ncurves = len(curvedata)
    lastvalues = [None] * ncurves
    indices = [0] * ncurves
    times = []
    points = [[] for _ in range(ncurves)]
    timestamps = [c[0] for c in curvedata]
    yvalues = [c[1] for c in curvedata]

    while True:
        # find the curve with the least unused timestamp
        ileast = min(range(ncurves),
                     key=lambda i: timestamps[i][indices[i]])
        lastvalues[ileast] = yvalues[ileast][indices[ileast]]
        ts = timestamps[ileast][indices[ileast]]
        indices[ileast] += 1
        # find any curves where the next unused timestamp is close to the
        # found least timestamp
        for i in range(ncurves):
            if i != ileast and timestamps[i][indices[i]] - ts <= window:
                lastvalues[i] = yvalues[i][indices[i]]
                indices[i] += 1
        # once all curves have seen a value, synthesize a point with the
        # current "lastvalues"
        if None not in lastvalues:
            times.append(ts)
            for pts, value in zip(points, lastvalues):
                pts.append(value)
        # if any of the curves have been exhausted, stop
        if any(indices[i] >= len(timestamps[i]) for i in range(ncurves)):
            break

    return convertXCol(fmtno, times, *points)


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
        visiblePlotCurves = self._axes.getVisibleCurves()
        if visiblePlotCurves:
            self._axes.curveDataChanged(visiblePlotCurves[-1])

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
        return plotcurve

    def setCurveData(self, curve, plotcurve):
        xname = curve.default_xname \
            if self.current_xname == 'Default' else self.current_xname
        if self.normalized == 'Maximum':
            norm = [max(curve.datay)] * len(curve.datay)
        else:
            norm = curve.datanorm[self.normalized] if self.normalized else None
        try:
            x, y, dy = prepareData(curve.datax[xname], curve.datay,
                                   curve.datady, norm)
        except ValueError:
            # empty column, should be ignored
            x, y, dy = np.array([0]), np.array([0]), None
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
        (_coord, _axes, curve) = self._plot.pick(self.mouselocation.getNDC(),
                                                 self.dwidth, self.dheight)
        if not curve:
            return
        self.fitter = GaussFitter(self, self.window, None, curve, False)
        self.fitter.begin()

    def getViewport(self):
        return self._plot.getAxes(0).getWindow()
