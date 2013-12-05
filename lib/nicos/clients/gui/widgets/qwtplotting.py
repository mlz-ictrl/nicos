#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

from time import localtime, strftime

from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve, QwtPlotItem, QwtText
from PyQt4.QtGui import QPen, QListWidgetItem, QDialog, QMessageBox
from PyQt4.QtCore import Qt, SIGNAL

import numpy as np

from nicos.clients.gui.utils import DlgPresets, dialogFromUi
from nicos.clients.gui.widgets.plotting import NicosPlot, ErrorBarPlotCurve
from nicos.clients.gui.dialogs.data import DataExportDialog
from nicos.clients.gui.fitutils import fit_gauss, fwhm_to_sigma, fit_tc, \
     fit_pseudo_voigt, fit_pearson_vii, fit_arby, fit_linear


TIMEFMT = '%Y-%m-%d %H:%M:%S'


class ViewPlot(NicosPlot):
    def __init__(self, parent, window, view):
        self.view = view
        self.hasSymbols = False
        self.hasLines = True
        NicosPlot.__init__(self, parent, window, timeaxis=True)

    def titleString(self):
        return '<h3>%s</h3>' % self.view.name

    def xaxisName(self):
        return 'time'

    def yaxisName(self):
        return 'value'

    def addAllCurves(self):
        for i, key in enumerate(self.view.keys):
            self.addCurve(i, key)

    def yaxisScale(self):
        if self.view.yfrom is not None:
            return (self.view.yfrom, self.view.yto)

    #pylint: disable=W0221
    def on_picker_moved(self, point, strf=strftime, local=localtime):
        # overridden to show the correct timestamp
        tstamp = local(int(self.invTransform(QwtPlot.xBottom, point.x())))
        info = "X = %s, Y = %g" % (
            strf('%y-%m-%d %H:%M:%S', tstamp),
            self.invTransform(QwtPlot.yLeft, point.y()))
        self.window.statusBar.showMessage(info)

    def addCurve(self, i, key, replot=False):
        pen = QPen(self.curvecolor[i % self.numcolors])
        curvename = key
        keyinfo = self.view.keyinfo.get(key)
        if keyinfo:
            curvename += ' (' + keyinfo + ')'
        plotcurve = QwtPlotCurve(curvename)
        plotcurve.setPen(pen)
        plotcurve.setSymbol(self.nosymbol)
        plotcurve.setStyle(QwtPlotCurve.Lines)
        x, y, n = self.view.keydata[key][:3]
        plotcurve.setData(x[:n], y[:n])
        self.addPlotCurve(plotcurve, replot)

    def pointsAdded(self, whichkey):
        for key, plotcurve in zip(self.view.keys, self.plotcurves):
            if key == whichkey:
                x, y, n = self.view.keydata[key][:3]
                plotcurve.setData(x[:n], y[:n])
                self.replot()
                return

    def setLines(self, on):
        for plotcurve in self.plotcurves:
            if on:
                plotcurve.setStyle(QwtPlotCurve.Lines)
            else:
                plotcurve.setStyle(QwtPlotCurve.NoCurve)
        self.hasLines = on
        self.replot()

    def setSymbols(self, on):
        for plotcurve in self.plotcurves:
            if on:
                plotcurve.setSymbol(self.symbol)
            else:
                plotcurve.setSymbol(self.nosymbol)
        self.hasSymbols = on
        self.replot()

    def selectCurve(self):
        if len(self.view.keys) > 1:
            dlg = dialogFromUi(self, 'selector.ui', 'panels')
            dlg.setWindowTitle('Select curve to fit')
            dlg.label.setText('Select a curve:')
            for key in self.view.keys:
                QListWidgetItem(key, dlg.list)
            dlg.list.setCurrentRow(0)
            if dlg.exec_() != QDialog.Accepted:
                return
            fitcurve = dlg.list.currentRow()
        else:
            fitcurve = 0
        return self.plotcurves[fitcurve]

    def fitLinear(self):
        self._beginFit('Linear', ['First point', 'Second point'],
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
        dlg = DataExportDialog(self, 'Select curve, file name and format',
                               '', 'ASCII data files (*.dat)')
        res = dlg.exec_()
        if res != QDialog.Accepted:
            return
        if not dlg.selectedFiles():
            return
        curve = self.plotcurves[dlg.curveCombo.currentIndex()]
        fmtno = dlg.formatCombo.currentIndex()
        filename = dlg.selectedFiles()[0]

        if curve.dataSize() < 1:
            QMessageBox.information(self, 'Error', 'No data in selected curve!')
            return

        with open(filename, 'wb') as fp:
            for i in range(curve.dataSize()):
                if fmtno == 0:
                    fp.write('%s\t%.10f\n' % (curve.x(i) - curve.x(0),
                                              curve.y(i)))
                elif fmtno == 1:
                    fp.write('%s\t%.10f\n' % (curve.x(i), curve.y(i)))
                else:
                    fp.write('%s\t%.10f\n' % (strftime(
                        '%Y-%m-%d.%H:%M:%S', localtime(curve.x(i))),
                        curve.y(i)))


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
        return '<h3>Scan %s</h3><font size="-2">%s, started %s</font>' % \
            (self.dataset.name, self.dataset.scaninfo,
             strftime(TIMEFMT, self.dataset.started))

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
            visible[str(plotcurve.title().text())] = plotcurve.isVisible()
        changed = False
        remaining = len(self.plotcurves)
        for plotcurve in self.plotcurves:
            namestr = str(plotcurve.title().text())
            if namestr in visible:
                self.setVisibility(plotcurve, visible[namestr])
                changed = True
                if not visible[namestr]:
                    remaining -= 1
        # no visible curve left?  enable all of them again
        if not remaining:
            for plotcurve in self.plotcurves:
                # only if it has a legend item (excludes monitor/time columns)
                if plotcurve.testItemAttribute(QwtPlotItem.Legend):
                    self.setVisibility(plotcurve, True)
        if changed:
            self.replot()

    def addCurve(self, i, curve, replot=False):
        pen = QPen(self.curvecolor[i % self.numcolors])
        plotcurve = ErrorBarPlotCurve(title=curve.full_description,
                                      curvePen=pen,
                                      errorPen=QPen(Qt.darkGray, 0),
                                      errorCap=8, errorOnTop=False)
        if not curve.function:
            plotcurve.setSymbol(self.symbol)
        if curve.yaxis == 2:
            plotcurve.setYAxis(QwtPlot.yRight)
            self.has_secondary = True
            self.enableAxis(QwtPlot.yRight)
        if curve.disabled:
            if not self.show_all:
                plotcurve.setVisible(False)
                plotcurve.setItemAttribute(QwtPlotItem.Legend, False)
        self.setCurveData(curve, plotcurve)
        self.addPlotCurve(plotcurve, replot)

    def setCurveData(self, curve, plotcurve):
        x = np.array(curve.datax)
        y = np.array(curve.datay, float)
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
        plotcurve.setData(x, y, None, dy)
        # setData creates a new legend item that must be styled
        if not plotcurve.isVisible() and self.legend():
            legenditem = self.legend().find(plotcurve)
            if legenditem:
                newtext = QwtText(legenditem.text())
                newtext.setColor(Qt.darkGray)
                legenditem.setText(newtext)

    def pointsAdded(self):
        curve = None
        for curve, plotcurve in zip(self.dataset.curves, self.plotcurves):
            self.setCurveData(curve, plotcurve)
        if curve and len(curve.datax) == 1:
            self.zoomer.setZoomBase(True)
        else:
            self.replot()

    def modifyData(self):
        visible_curves = [i for (i, _) in enumerate(self.dataset.curves)
                          if self.plotcurves[i].isVisible()]
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
        # make changes to Qwt curve objects only (so that "reset" will discard
        # them again)
        for i in curves:
            curve = self.plotcurves[visible_curves[i]]
            if isinstance(curve, ErrorBarPlotCurve):
                new_y = [eval(op, {'x': v1, 'y': v2})
                         for (v1, v2) in zip(curve._x, curve._y)]
                curve.setData(curve._x, new_y, curve._dx, curve._dy)
            else:
                curve.setData(curve.xData(),
                    [eval(op, {'x': v1, 'y': v2})
                     for (v1, v2) in zip(curve.xData(), curve.yData())])
        self.replot()

    def selectCurve(self):
        visible_curves = [i for (i, _) in enumerate(self.dataset.curves)
                          if self.plotcurves[i].isVisible()]
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
        self._beginFit('Gauss', ['Background', 'Peak', 'Half Maximum'],
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
        self._beginFit('Pseudo-Voigt', ['Background', 'Peak', 'Half Maximum'],
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
        self._beginFit('PearsonVII', ['Background', 'Peak', 'Half Maximum'],
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
        self._beginFit('Tc', ['Background', 'Tc'], self.tc_callback)

    def tc_callback(self, args):
        title = 'Tc fit'
        beta, x, y = fit_tc(*args)
        labelx = beta[2]  # at Tc
        labely = beta[0] + beta[1]  # at I_max
        interesting = [('Tc', beta[2]), (u'α', beta[3])]
        return x, y, title, labelx, labely, interesting, None

    def fitArby(self):
        self._beginFit('Arbitrary', [], self.arby_callback,
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
        visible_curves = [i for (i, _) in enumerate(self.dataset.curves)
                          if self.plotcurves[i].isVisible()]
        p = self.picker.trackerPosition()
        whichcurve = None
        whichindex = None
        mindist = None
        for i in visible_curves:
            index, dist = self.plotcurves[i].closestPoint(p)
            if mindist is None or dist < mindist:
                whichcurve = i
                whichindex = index
                mindist = dist
        self.fitcurve = self.plotcurves[whichcurve]
        data = self.fitcurve.data()
        # try to find good starting parameters
        peakx, peaky = data.x(whichindex), data.y(whichindex)
        # use either left or right end of curve as background
        leftx, lefty = data.x(0), data.y(0)
        rightx, righty = data.x(data.size() - 1), data.y(data.size() - 1)
        if abs(peakx - leftx) > abs(peakx - rightx):
            direction = -1
            backx, backy = leftx, lefty
        else:
            direction = 1
            backx, backy = rightx, righty
        i = whichindex
        while i > 0:
            if data.y(i) < (peaky - backy) / 2.:
                break
            i += direction
        if i != whichindex:
            fwhmx = data.x(i)
        else:
            fwhmx = (peakx + backx) / 2.
        self.fitvalues = [(backx, backy), (peakx, peaky), (fwhmx, peaky / 2.)]
        self.fitparams = ['Background', 'Peak', 'Half Maximum']
        self.fittype = 'Gauss'
        self.fitcallbacks = [self.gauss_callback, None]
        self._finishFit()
