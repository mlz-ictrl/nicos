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

from time import strftime, localtime

from PyQt4.QtGui import QDialog, QFont, QListWidgetItem, QMessageBox
from PyQt4.QtCore import SIGNAL, Qt

import numpy as np

from nicos.utils.fitting import Fit, LinearFit, GaussFit, PseudoVoigtFit, \
    PearsonVIIFit, TcFit, FitError
from nicos.clients.gui.dialogs.data import DataExportDialog
from nicos.clients.gui.utils import DlgUtils, DlgPresets, dialogFromUi
from nicos.pycompat import exec_, xrange as range  # pylint: disable=W0622


TIMEFMT = '%Y-%m-%d %H:%M:%S'


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

    def model(self, x, a, b):
        return a*x + b

    def do_fit(self):
        (x1, y1), (x2, y2) = self.values  # pylint: disable=unbalanced-tuple-unpacking
        m0 = (y2-y1) / (x2-x1)
        f = LinearFit([m0, y1 - m0*x1], xmin=x1, xmax=x2, timeseries=True)
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
        dlg.connect(dlg.oftenUsed,
                    SIGNAL('itemClicked(QListWidgetItem *)'), click_cb)
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


def prepareData(x, y, dy, norm):
    """Prepare and sanitize data for plotting.

    x, y and dy are lists or arrays. norm can also be None.

    Returns x, y and dy arrays, where dy can also be None.
    """
    # make arrays
    x = np.array(x)
    y = np.array(y, float)
    dy = np.array(dy, float)
    # normalize
    if norm is not None:
        norm = np.asarray(norm, float)
        y /= norm
        dy /= norm
    # remove infinity/NaN
    indices = np.isfinite(y)
    x = x[indices]
    y = y[indices]
    if len(dy):
        dy = dy[indices]
        # remove error bars that aren't finite
        dy[~np.isfinite(dy)] = 0
    # if there are no errors left, don't bother drawing them
    if dy.sum() == 0:
        return x, y, None
    return x, y, dy


class NicosPlot(DlgUtils):

    HAS_AUTOSCALE = False
    SAVE_EXT = '.png'

    def __init__(self, window, timeaxis=False):
        DlgUtils.__init__(self, 'Plot')
        self.window = window
        self.plotcurves = []
        self.has_secondary = False
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

    def selectCurve(self):
        """Let the user select a visible plot curve.

        If there is only one curve, return it directly.
        """
        visible_curves = self.visibleCurves()
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
        dlg.connect(dlg.selectall, SIGNAL('clicked()'), checkAll)
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


class DataSetPlotMixin(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.current_xname = dataset.default_xname

    def titleString(self):
        return '<h3>Scan %s</h3><font size="-2">%s, started %s</font>' % \
            (self.dataset.name, self.dataset.scaninfo,
             strftime(TIMEFMT, self.dataset.started))

    def xaxisName(self):
        return self.current_xname

    def yaxisName(self):
        return ''

    def addAllCurves(self):
        for i, curve in enumerate(self.dataset.curves):
            self.addCurve(i, curve)

    def visibleCurves(self):
        return [(i, curve.full_description)
                for (i, curve) in enumerate(self.dataset.curves)
                if self._isCurveVisible(self.plotcurves[i])]

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


class ViewPlotMixin(object):
    def __init__(self, view):
        self.view = view
        self.series2curve = {}

    def titleString(self):
        return '<h3>%s</h3>' % self.view.name

    def xaxisName(self):
        return 'time'

    def yaxisName(self):
        return 'value'

    def yaxisScale(self):
        if self.view.yfrom is not None:
            return (self.view.yfrom, self.view.yto)

    def addAllCurves(self):
        for i, series in enumerate(self.view.series.values()):
            self.addCurve(i, series)

    def visibleCurves(self):
        return [(i, self._getCurveLegend(plotcurve))
                for (i, plotcurve) in enumerate(self.plotcurves)
                if self._isCurveVisible(plotcurve)]

    def saveData(self):
        curvenames = [self._getCurveLegend(plotcurve)
                      for plotcurve in self.plotcurves]
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
        if '.' not in filename:
            filename += '.dat'

        x, y, _ = self._getCurveData(curve)
        n = len(x)

        if n < 1:
            QMessageBox.information(self, 'Error',
                                    'No data in selected curve!')
            return

        with open(filename, 'wb') as fp:
            for i in range(n):
                if fmtno == 0:
                    fp.write('%s\t%.10f\n' % (x[i] - x[0], y[i]))
                elif fmtno == 1:
                    fp.write('%s\t%.10f\n' % (x[i], y[i]))
                else:
                    fp.write('%s\t%.10f\n' % (
                        strftime('%Y-%m-%d.%H:%M:%S', localtime(x[i])),
                        y[i]))

    def setSlidingWindow(self, window):
        pass


# pylint: disable=W0611
try:
    from nicos.clients.gui.widgets.grplotting import DataSetPlot, ViewPlot
except ImportError:
    from nicos.clients.gui.widgets.qwtplotting import DataSetPlot, ViewPlot
