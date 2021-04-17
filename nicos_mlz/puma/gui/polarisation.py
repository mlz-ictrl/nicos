# -*- coding: utf-8 -*-
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
#   Goetz Eckold <geckold@gwdg.de>
#
# *****************************************************************************

from math import asin, atan, cos, degrees, pi, radians, sin, sqrt, tan

from numpy import arange, array, sign

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, waitCursor
from nicos.clients.gui.widgets.plotting import NicosPlotCurve
from nicos.core.errors import NicosError
from nicos.guisupport.livewidget import LiveWidget1D
from nicos.guisupport.plots import GRCOLORS, GRMARKS
from nicos.guisupport.qt import QDoubleValidator, QLabel, QMessageBox, QSize, \
    QSizePolicy, Qt, QVBoxLayout, QWidget, pyqtSlot
from nicos.guisupport.widget import NicosWidget
from nicos.utils import findResource

from nicos_mlz.puma.lib.pa import PA

COLOR_BLACK = GRCOLORS['black']
COLOR_RED = GRCOLORS['red']
COLOR_GREEN = GRCOLORS['green']
COLOR_BLUE = GRCOLORS['blue']

SOLID_CIRCLE_MARKER = GRMARKS['solidcircle']


class MiniPlot(LiveWidget1D):

    client = None

    def __init__(self, xlabel, ylabel, parent=None, **kwds):
        LiveWidget1D.__init__(self, parent)
        self.plot.xlabel = xlabel
        self.plot.ylabel = ylabel

        self.curve.linecolor = kwds.get('color2', COLOR_RED)
        self.curve.linewidth = 2
        self.curve.GR_MARKERSIZE = 20
        self.curve.markertype = SOLID_CIRCLE_MARKER
        self.curve.markercolor = kwds.get('color2', COLOR_RED)

        self.downcurve = NicosPlotCurve(
            [0], [.1], linecolor=kwds.get('color1', COLOR_BLACK))
        self.downcurve.linewidth = 2
        self.downcurve.markertype = SOLID_CIRCLE_MARKER
        self.downcurve.GR_MARKERSIZE = 20
        self.downcurve.markertype = SOLID_CIRCLE_MARKER
        self.downcurve.markercolor = kwds.get('color1', COLOR_BLACK)
        self.axes.addCurves(self.downcurve)

        # Disable creating a mouse selection to zoom
        self.gr.setMouseSelectionEnabled(False)
        self.plot.setLegend(True)

    def sizeHint(self):
        return QSize(120, 120)

    def reset(self):
        self.plot.reset()


class PlotWidget(QWidget):

    def __init__(self, title, xlabel, ylabel, name='unknown', parent=None,
                 **kwds):
        QWidget.__init__(self, parent)
        self.name = name
        parent.setLayout(QVBoxLayout())
        self.plot = MiniPlot(xlabel, ylabel, self, color1=COLOR_BLACK,
                             color2=COLOR_RED)
        titleLabel = QLabel(title)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet('QLabel {font-weight: 600}')
        parent.layout().insertWidget(0, titleLabel)
        self.plot.setSizePolicy(QSizePolicy.MinimumExpanding,
                                QSizePolicy.MinimumExpanding)
        parent.layout().insertWidget(1, self.plot)

    def setData(self, x, y1, y2):
        self.plot.curve.x = array(x)
        self.plot.curve.y = array(y1)
        self.plot.downcurve.x = array(x)
        self.plot.downcurve.y = array(y2)

        self.plot.reset()
        self.plot.update()


class IntensityPlot(PlotWidget):

    def __init__(self, direction, parent=None):
        PlotWidget.__init__(self, 'Calculated intensity at PSD for spin-%s '
                            'neutrons' % direction,
                            'PSD channel position (cm)', 'intensity',
                            parent=parent)
        self.plot.curve.legend = 'without analyzer'
        self.plot.downcurve.legend = 'with analyzer'


class TransmissionPlot(PlotWidget):

    def __init__(self, direction, parent=None):
        PlotWidget.__init__(self, 'Calculated refl/trans coeff of deflectors '
                            'for spin-%s neutrons' % direction,
                            'Deflector angle (deg)', 'Refl/trans coefficient',
                            parent=parent)
        self.plot.curve.linecolor = COLOR_BLUE
        self.plot.curve.legend = 'Reflectivity'
        self.plot.curve.markercolor = COLOR_BLUE
        self.plot.downcurve.linecolor = COLOR_GREEN
        self.plot.downcurve.legend = 'Transmissivity'
        self.plot.downcurve.markercolor = COLOR_GREEN


class PolarisationPanel(NicosWidget, Panel):

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        self.setClient(client)
        NicosWidget.__init__(self)
        client.connected.connect(self.on_client_connected)
        self.destroyed.connect(self.on_destroyed)

    def on_destroyed(self):
        pass

    def initUi(self):
        with waitCursor():
            loadUi(self, findResource('nicos_mlz/puma/gui/polarisation.ui'))

        valid = QDoubleValidator()

        for f in (self.kf, self.alpha0, self.eta, self.gamma1, self.gamma2,
                  self.bA, self.dA, self.LSA, self.LSD1, self.LSD2, self.LPSD,
                  self.LAD, self.R, self.L, self.d, self.bS, self.psdwidth,
                  self.bD, self.theta05, self.theta06, self.theta07, self.x05,
                  self.x06, self.x07, self.y05, self.y06, self.y07, self.ta5,
                  self.ta6, self.ta7, self.rd5, self.rd6, self.rd7, self.rg5,
                  self.rg6, self.rg7, self.PSDintUp, self.PSDintDown,
                  self.IgesUp, self.IgesDown, self.fractionUp,
                  self.fractionDown, self.I5Up, self.I5Down, self.I6Up,
                  self.I6Down, self.I7Up, self.I7Down, self.ratioUp,
                  self.ratioDown, self.Dplus, self.Dminus,
                  self.x05_cur, self.x06_cur, self.x07_cur, self.ta5_cur,
                  self.ta6_cur, self.ta7_cur, self.rd5_cur, self.rd6_cur,
                  self.rd7_cur, self.rg5_cur, self.rg6_cur, self.rg7_cur,
                  self.theta05_cur, self.theta06_cur, self.theta07_cur):
            f.setValidator(valid)
            f.setReadOnly(True)

        for b in (self.buttonRecall, self.buttonOK, self.buttonCancel,
                  self.buttonOptimize, self.label_187, self.label_18,
                  self.label_20, self.label_21, self.x05, self.x06, self.x07,
                  self.x05_cur, self.x06_cur, self.x07_cur, self.progress):
            b.hide()

        self.plot1 = IntensityPlot('up', self.plotWidget1)
        self.plot2 = IntensityPlot('down', self.plotWidget2)
        self.plot3 = TransmissionPlot('up', self.plotWidget3)
        self.plot4 = TransmissionPlot('down', self.plotWidget4)

    def registerKeys(self):
        for d in ('ta5', 'ta6', 'ta7',
                  'ra5', 'ra6', 'ra7',
                  'rd5', 'rd6', 'rd7',
                  'rd5_cad', 'rd6_cad', 'rd7_cad',
                  'rg5', 'rg6', 'rg7'
                  'kf', 'lsa', 'lsd1', 'lsd2', 'lad', 'lpsd', 'slit2.width'):
            self.registerDevice(d)
        for k in ('def1/reflectivity', 'polcol/divergency', 'def1/length',
                  'def1/thickness', 'man/mosaicity', 'man/planedistance',
                  'man/raildistance', 'med/tubediameter',
                  'med/psdchannelwidth', 'man/parkpos'):
            self.registerKey(k)

    def on_client_connected(self):
        with waitCursor():
            missed_devices = []
            for d in ('def1', 'polcol', 'man', 'med'):
                self.client.eval('%s.pollParam()', None)
                params = self.client.getDeviceParams(d)
                for p, v in params.items():
                    self._update_key('%s/%s' % (d, p), v)
            for d in ('ra5', 'ra6', 'ra7', 'ta5', 'ta6', 'ta7',
                      'rd5', 'rd6', 'rd7', 'rg5', 'rg6', 'rg7',
                      'rd5_cad', 'rd6_cad', 'rd7_cad',
                      'lsa', 'lsd1', 'lsd2', 'lad', 'lpsd',
                      'kf', 'def1', 'def2', 'slit2.width'):
                try:
                    self.log.debug('poll: %s', d)
                    self.client.eval("session.getDevice('%s').poll()" % d)
                    val = self.client.getDeviceValue('%s' % d)
                    self._update_key('%s/value' % d, val)
                    self.log.debug('%s/%s', d, val)
                except (NicosError, NameError):
                    missed_devices += [d]
        if not missed_devices:
            self.recalculate()
            for w in (self.kf, self.LSA, self.LSD1, self.LSD1, self.gamma1,
                      self.gamma2, self.LAD, self.bA, self.bD, self.bS):
                w.textChanged.connect(self.recalculate)
        else:
            QMessageBox.warning(self.parent().parent(), 'Error',
                                'The following devices are not available:<br>'
                                "'%s'" % ', '.join(missed_devices))
            self.setDisabled(True)

    def on_client_cache(self, data):
        (_time, key, _op, value) = data
        if '/' not in key:
            return
        self._update_key(key, value)

    def _update_key(self, key, value):
        if key == 'polcol/divergency':
            self.alpha0.setText('%.1f' % float(value))
        elif key == 'def1/reflectivity':
            self.R.setText('%.1f' % float(value))
        elif key == 'def1/length':
            self.L.setText('%.1f' % float(value))
        elif key == 'def1/thickness':
            self.d.setText('%.2f' % float(value))
        elif key == 'man/mosaicity':
            self.eta.setText('%.1f' % float(value))
        elif key == 'man/planedistance':
            self.dA.setText('%.3f' % float(value))
        elif key == 'man/raildistance':
            self.x05.setText('%.2f' % float(value))
            self.x07.setText('%.2f' % -float(value))
        elif key == 'man/bladewidth':
            self.bA.setText('%.2f' % float(value))
        elif key == 'med/tubediameter':
            self.bD.setText('%.1f' % float(value))
        elif key == 'med/psdchannelwidth':
            self.psdwidth.setText('%.2f' % float(value))
        else:
            ldevname, subkey = key.rsplit('/', 1)
            if subkey == 'value':
                s = None
                if ldevname in ('ra5', 'ra6', 'ra7'):
                    s = 'theta0%s_cur' % ldevname[2]
                elif ldevname in ('rd5_cad', 'rd6_cad', 'rd7_cad'):
                    s = '%s_cur' % ldevname[:3]
                elif ldevname in ('ta5', 'ta6', 'ta7',
                                  # 'rd5', 'rd6', 'rd7',
                                  'rg5', 'rg6', 'rg7'):
                    s = '%s_cur' % ldevname
                elif ldevname in ('lsa', 'lsd1', 'lsd2', 'lad', 'lpsd'):
                    s = '%s' % ldevname.upper()
                elif ldevname in ('kf',):
                    s = '%s' % ldevname
                elif ldevname in ('def1', 'def2'):
                    s = ldevname.replace('def', 'gamma')
                elif ldevname in ('slit2.width',):
                    s = 'bS'
                if s:
                    getattr(self, s).setText('%.3f' % float(value))

    @pyqtSlot()
    def recalculate(self):
        self._optimize()
        try:
            self._simulate()
        except (ZeroDivisionError, IndexError):
            QMessageBox.warning(self.parent().parent(), 'Error',
                                'The current instrument setup is not well '
                                'defined for polarisation analysis')

    def _optimize(self):
        kf = float(self.kf.text())
        dA = float(self.dA.text())
        theta0 = -asin(pi / (kf * dA))
        theta0deg = degrees(theta0)

        x5 = float(self.x05.text())
        x7 = float(self.x07.text())

        LSA = float(self.LSA.text())
        LSD1 = float(self.LSD1.text())
        LSD2 = float(self.LSD2.text())
        gamma1 = float(self.gamma1.text())
        tg1 = tan(radians(2 * gamma1))
        gamma2 = float(self.gamma2.text())
        tg2 = tan(radians(2 * gamma2))

        # calculate longitudinal translation of analyzers in mm
        try:
            y5 = (LSA - LSD2) - x5 / tg2
            y7 = (LSA - LSD1) - x7 / tg1
        except ZeroDivisionError:
            return
        self.y05.setText('%.2f' % y5)
        self.y07.setText('%.2f' % y7)

        # calculate rotation of analyzers in deg
        self.theta05.setText('%.2f' % (theta0deg + 2 * gamma2))
        self.theta06.setText('%.2f' % theta0deg)
        self.theta07.setText('%.2f' % (theta0deg + 2 * gamma1))

        LAD = float(self.LAD.text())
        BA = float(self.bA.text())
        BD = float(self.bD.text())

        # calculate setting for ta in mm
        ta6 = 120 - 115  # the rotation axis is at 5 mm off from center of man
        self.ta5.setText('%.1f' % (ta6 + y5))
        self.ta6.setText('%.1f' % ta6)
        self.ta7.setText('%.1f' % (ta6 + y7))

        # calculate detector settings
        rd6 = 2 * theta0deg
        e1 = (-BA * sin(theta0) - BD) / (-BA * sin(theta0) - LAD)
        rg6 = degrees(atan(e1))

        beta5 = radians(2 * (theta0deg + gamma2))
        beta7 = radians(2 * (theta0deg + gamma1))

        if abs(y5) < 0.1:
            kappa5 = sign(x5) * pi
        else:
            kappa5 = atan(-x5 / y5)
        if abs(y7) < 0.1:
            kappa7 = sign(x7) * pi
        else:
            kappa7 = atan(-x7 / y7)

        e1 = sqrt(x5 * x5 + y5 * y5) / LAD * sin(beta5 - kappa5)
        try:
            eps5 = asin(e1)
        except ValueError:
            return
        delta5 = beta5 - eps5

        e1 = sqrt(x7 * x7 + y7 * y7) / LAD * sin(-beta7 + kappa7)
        try:
            eps7 = asin(e1)
        except ValueError:
            return
        delta7 = beta7 - eps7

        # calculate the correction angle allowing for the effective width of
        # the crystal blade

        L = LAD * sin(-delta5 + kappa5) / sin(-beta5 + kappa5) - \
            0.5 * BA * cos(theta0)
        deps = 0.5 * (-BD - BA * sin(theta0)) / L
        deps = atan(deps)
        eps5 += abs(deps)

        L = LAD * sin(-delta7 + kappa7) / sin(-beta7 + kappa7) - \
            0.5 * BA * cos(theta0)
        deps = 0.5 * (-BD - BA * sin(theta0)) / L
        deps = atan(deps)
        eps7 += abs(deps)

        # convert angles to degrees
        self.rd5.setText('%.2f' % degrees(delta5))
        self.rd6.setText('%.2f' % rd6)
        self.rd7.setText('%.2f' % degrees(delta7))
        self.rg5.setText('%.2f' % degrees(eps5))
        self.rg6.setText('%.2f' % rg6)
        self.rg7.setText('%.2f' % degrees(eps7))

    @pyqtSlot(bool)
    def on_buttonApply_clicked(self, checked):
        # values are readonlylists which can't modified
        med = list(self.client.getDeviceValue('med'))
        cad = self.client.getDeviceValue('cad')

        man = [125] * 11 + [0] * 11
        for i, w in enumerate((self.ta5, self.ta6, self.ta7)):
            man[4 + i] = float(w.text())
        for i, w in enumerate((self.theta05, self.theta06, self.theta07)):
            man[15 + i] = float(w.text())

        refgap = self.client.getDeviceParam('med', 'refgap')
        absmax = self.client.getDeviceParam('rd1', 'userlimits')[1] - 0.2
        absmin = self.client.getDeviceParam('rd11', 'userlimits')[0] + 0.2

        med = [absmax - i * refgap for i in range(4)]  # pos of rd1..4]
        med += [0] * 3  # place holder for rd5..6
        med += [absmin + i * refgap for i in reversed(range(4))]  # pos rd8..11
        med += [0] * 11  # rg1..11

        for i, w in enumerate((self.rd5, self.rd6, self.rd7)):
            med[4 + i] = float(w.text()) - cad
        for i, w in enumerate((self.rg5, self.rg6, self.rg7)):
            med[15 + i] = float(w.text())

        script = 'maw(man, %r, med, %r)' % (man, med)
        # print(script)
        self.client.run(script, noqueue=False)

    def _simulate(self):
        """Calculate the proper longitudinal displacements.

        Version without tilting the whole multianalyzer.
        """
        valuedict = {}
        for o in [self.kf, self.dA, self.alpha0, self.eta, self.LSA,
                  self.LSD1, self.LSD2, self.LPSD, self.gamma1,
                  self.gamma2, self.theta06, self.theta05, self.theta07,
                  self.y05, self.y06, self.y07, self.x05, self.x06,
                  self.x07, self.bS, self.bA, self.L, self.d, self.R,
                  self.psdwidth]:
            valuedict[o.objectName()] = float(o.text())

        pa = PA(**valuedict)
        pa.run()

        self.PSDintUp.setText('%.2f' % pa.psdintup)
        self.fractionUp.setText('%.2f' % pa.fractionup)
        self.I5Up.setText('%.2f' % pa.i5up)
        self.I6Up.setText('%.2f' % pa.i6up)
        self.I7Up.setText('%.2f' % pa.i7up)
        self.IgesUp.setText('%.2f' % pa.igesup)
        self.ratioUp.setText('%.2f' % pa.ratioup)

        self.PSDintDown.setText('%.2f' % pa.psdintdown)
        self.fractionDown.setText('%.2f' % pa.fractiondown)
        self.I5Down.setText('%.2f' % pa.i5down)
        self.I6Down.setText('%.2f' % pa.i6down)
        self.I7Down.setText('%.2f' % pa.i7down)
        self.IgesDown.setText('%.2f' % pa.igesdown)
        self.ratioDown.setText('%.2f' % pa.ratiodown)

        AA = pa.i5down + pa.i7down
        self.Dplus.setText('%.2f' % ((pa.i6down + pa.i6up) / AA))
        self.Dminus.setText('%.2f' % ((pa.i6down - pa.i6up) / AA))

        px = arange(-7, 7.01, pa.psdwidth / 10.)
        self.plot1.setData(px, pa.psdup[1:], pa.psdupa[1:])
        self.plot2.setData(px, pa.psddown[1:], pa.psddowna[1:])

        ang = arange(-2, 2.01, 0.1)
        self.plot3.setData(ang, pa.reflup, (1. - array(pa.reflup)).tolist())
        self.plot4.setData(ang, pa.refldown,
                           (1. - array(pa.refldown)).tolist())
