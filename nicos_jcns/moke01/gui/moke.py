# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

import datetime
import math
import os

import numpy
from gr.pygr import ErrorBar
from qtgr.events import LegendEvent, MouseEvent
# pylint: disable=import-error
from uncertainties.core import AffineScalarFunc

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.livewidget import LiveWidget1D
from nicos.guisupport.plots import GRMARKS, MaskedPlotCurve
from nicos.guisupport.qt import QDate, QFont, QMessageBox, QStandardItem, \
    QStandardItemModel, Qt, QToolBar, pyqtSlot
from nicos.guisupport.widget import NicosWidget
from nicos.protocols.daemon import BREAK_AFTER_STEP, BREAK_NOW
from nicos.utils import findResource
from nicos.utils.functioncurves import Curve2D, Curves

from nicos_jcns.moke01.utils import calculate, fix_filename, generate_output


class MokePlotCurve(MaskedPlotCurve):

    ShowAll = 0
    HideErrorBars = 1
    HideAll = 2

    def __init__(self, *args, **kwargs):
        MaskedPlotCurve.__init__(self, *args, **kwargs)
        self._show_error_bars = False
        self._status = MokePlotCurve.HideErrorBars

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        if self.status == MokePlotCurve.ShowAll:
            self.visible = True
            self._show_error_bars = True
        elif self.status == MokePlotCurve.HideErrorBars:
            self.visible = True
            self._show_error_bars = False
        else:
            self.visible = False
            self._show_error_bars = False

    @property
    def errorBar1(self):
        return self._e1 if self._show_error_bars else None

    @property
    def errorBar2(self):
        return self._e2 if self._show_error_bars else None


class MokePlot(LiveWidget1D):
    def __init__(self, xlabel, ylabel, parent=None, **kwds):
        LiveWidget1D.__init__(self, parent, **kwds)
        self.axes.resetCurves()
        self.axes.xdual = self.axes.ydual = False
        self.plot.setLegend(True)
        self.setTitles({'x': xlabel, 'y': ylabel})
        self._curves = []
        self.gr.cbm.addHandler(LegendEvent.ROI_CLICKED,
                               self.on_legendItemClicked, LegendEvent)

    def add_curve(self, curve, color=None, legend=None):
        self.plot.title = legend
        if not curve:
            return
        if color is None:
            color = len(self._curves) % 7 + 1
        x = y = dx = dy = None
        if curve:
            x = [i for i, _ in curve]
            y = [i for _, i in curve]
        if x and isinstance(x[0], AffineScalarFunc):
            dx = [i.s for i in x]
            x = [i.n for i in x]
        if y and isinstance(y[0], AffineScalarFunc):
            dy = [i.s for i in y]
            y = [i.n for i in y]
        x_err = ErrorBar(x, y, dx, direction=ErrorBar.HORIZONTAL,
                         markercolor=color, linecolor=color) if dx else None
        y_err = ErrorBar(x, y, dy, direction=ErrorBar.VERTICAL,
                         markercolor=color, linecolor=color) if dy else None
        self._curves.append(
            MokePlotCurve(x, y, errBar1=x_err, errBar2=y_err, linewidth=1,
                          legend=legend, markertype=GRMARKS['solidsquare'],
                          markercolor=color, linecolor=color),
        )
        self._curves[-1].markersize = 0.5
        self.axes.addCurves(self._curves[-1])
        self._update()

    def add_mokecurves(self, curves, legend=None):
        if isinstance(curves, Curves):
            for i, curve in enumerate(curves):
                if i % 2 == 0:
                    to_plot = Curve2D(curve)
                else:
                    to_plot.append(curve)
                    self.add_curve(to_plot, color=7, legend=str(i // 2 + 1))
                    # on default make only the last curve visible
                    if i < len(curves) - 1:
                        self._curves[-1].visible = False
            mean = curves.increasing(by_y=False).mean()
            mean.extend(curves.decreasing(by_y=False).mean())
            self.add_curve(mean, color=1, legend='mean')
        self.plot.title = legend

    def reset(self):
        self.axes.resetCurves()
        self._curves = []
        self._update()

    def _update(self):
        self.plot.reset()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._update()

    def on_legendItemClicked(self, event):
        if event.getButtons() & MouseEvent.LEFT_BUTTON:
            event.curve.status = (event.curve.status + 1) % 3
            self._update()
        if event.getButtons() & MouseEvent.RIGHT_BUTTON:
            event.curve.status = (event.curve.status - 1) % 3
            self._update()


class MokeBase(Panel):
    panelName = 'MOKE'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        self.plot_IntvB = MokePlot('MagB, mT', 'Intensity, mV', self)
        # viewport of IntvB plot is set to accomodate plot title
        self.plot_IntvB.plot.viewport = (.1, .9, .1, .9)
        self.plot_EvB = MokePlot('MagB, mT', 'Ellipticity, µrad.', self)
        self.m = {}

    @pyqtSlot()
    def on_btn_calc_clicked(self):
        if not self.ln_canting_angle.text() or not self.ln_extinction.text():
            QMessageBox.information(None, '', 'Please input Canting angle/Extinction values')
            return
        if not self.m:
            QMessageBox.information(None, '', 'Not measured yet or last measurement is n/a')
            return
        if not self.m['IntvB']:
            QMessageBox.information(None, '', 'The measurement is not yet finished')
            return

        IntvB = self.m['IntvB']
        int_mean = IntvB.series_to_curves().mean().yvx(0) # [mV]
        if self.chk_subtract_baseline.isChecked():
            if 'baseline' in self.m and self.m['baseline']:
                IntvB -= self.m['baseline'] # ([mT, mV])
            if int_mean:
                IntvB -= int_mean.y # ([mT, mV])
        angle = float(self.ln_canting_angle.text()) # [SKT]
        # recalculate angle in SKT to µrad
        angle *= 1.5 / 25 / 180 * math.pi * 1e6 # [µrad]
        ext = float(self.ln_extinction.text()) # mV
        try:
            fit_min, fit_max, IntvB, EvB, kerr = calculate(IntvB, int_mean.y, angle, ext)
        except Exception as e:
            QMessageBox.information(None, '', f'Calculation has failed:\n{e}')
            return
        # upd IntvB plot with mean curve and fits
        x = numpy.array([float(self.m['Bmin']), float(self.m['Bmax'])])
        self.plot_IntvB.add_curve(list(zip(x, fit_min[0] * x + fit_min[1])),
                                  legend='Fit min')
        self.plot_IntvB.add_curve(list(zip(x, fit_max[0] * x + fit_max[1])),
                                  legend='Fit max')
        self.plot_IntvB.add_curve(IntvB, legend='Mean')
        # show EvB plot and kerr angle
        self.plot_EvB.reset()
        self.plot_EvB.add_curve(EvB, legend=self.m['name'])
        self.ln_kerr.setText(str(kerr))

        output = generate_output(self.m, angle, ext)
        self.display_rawdata(output)
        folder = os.path.join(os.path.expanduser('~'), 'Measurements', 'moke')
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f'{fix_filename(self.m["name"])}.txt'),
                  'w', encoding='utf-8') as f:
            f.write(output)

    def display_rawdata(self, output):
        self.txt_rawdata.clear()
        self.txt_rawdata.insertPlainText(output)


class MokePanel(NicosWidget, MokeBase):

    def __init__(self, parent, client, options):
        MokeBase.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_jcns/moke01/gui/mokepanel.ui'))
        self.tabWidget.setCurrentIndex(0)
        self.calibration = {}
        self.plot_calibration = MokePlot('PS_current, A', 'MagB, mT', self)
        self.lyt_plot_calibration.addWidget(self.plot_calibration)
        self.baseline = {}
        self.plot_baseline = MokePlot('MagB, mT', 'Intensity, mV', self)
        self.lyt_plot_baseline.addWidget(self.plot_baseline)
        self.lyt_plot_IntvB.addWidget(self.plot_IntvB)
        self.lyt_plot_EvB.addWidget(self.plot_EvB)
        self.txt_rawdata.setFont(QFont('Courier New'))
        NicosWidget.__init__(self)
        self.setClient(self.client)
        self.bar = QToolBar('Script control')
        self.bar.addAction(self.actionStopNow)
        self.bar.addAction(self.actionStopLater)
        self.bar.addAction(self.actionEmergencyStop)
        self.bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def getToolbars(self):
        return [self.bar]

    def updateStatus(self, status, exception=False):
        self._status = status
        isconnected = status != 'disconnected'
        self.actionStopNow.setEnabled(isconnected and status != 'idle')
        self.actionStopLater.setEnabled(isconnected and status != 'idle')
        self.actionEmergencyStop.setEnabled(isconnected)

    @pyqtSlot()
    def on_actionStopNow_triggered(self):
        self.client.tell_action('stop', BREAK_NOW)

    @pyqtSlot()
    def on_actionStopLater_triggered(self):
        self.client.tell_action('stop', BREAK_AFTER_STEP)

    @pyqtSlot()
    def on_actionEmergencyStop_triggered(self):
        self.client.tell_action('emergency')

    def registerKeys(self):
        for k in ('magb/baseline', 'magb/calibration', 'magb/measurement',
                  'magb/cycle', 'magb/maxprogress', 'magb/progress'):
            self.registerKey(k)

    def on_keyChange(self, key, value, time, expired):
        if key == 'magb/calibration':
            self.calibration = value.copy()
            mode = self.cmb_mode.currentText()
            if self.calibration:
                self.cmb_ramp.clear()
                self.cmb_ramp.addItems(self.calibration[mode].keys())
            self.plot_calibration.reset()
            for mode in self.calibration:
                for ramp, curves in self.calibration[mode].items():
                    self.plot_calibration.add_curve(
                        curves.increasing()[0],
                        legend=f'{mode} increasing B @ {ramp} A/min'
                    )
                    self.plot_calibration.add_curve(
                        curves.decreasing()[0],
                        legend=f'{mode} decreasing B @ {ramp} A/min'
                    )
        elif key == 'magb/baseline':
            self.plot_baseline.reset()
            if value:
                for mode in value:
                    for field in value[mode]:
                        for ramp in value[mode][field]:
                            if value[mode][field][ramp]:
                                self.plot_baseline.add_curve(
                                    value[mode][field][ramp],
                                    legend=f'{mode}, {field} @ {ramp} A/min'
                                )
        elif key == 'magb/cycle':
            self.lcd_cycle.display(value + 1)
        elif key == 'magb/maxprogress':
            self.bar_cycles.setMaximum(value) # progress bar
        elif key == 'magb/progress':
            if value:
                self.bar_cycles.setValue(value) # progress bar
                timeleft = self._timeleft(value)
                self.lcd_timeleft.display(f'{int(timeleft / 60):02}:{int(timeleft % 60):02}')
            # live-update graph of intensity vs field
            # before measurement is finished and stored to `MagB.measurement`
            # IntvB can be fetched from MagB._IntvB
            if self.m:
                IntvB = self.client.eval('session.getDevice("MagB")._IntvB')
                int_mean = IntvB.series_to_curves().mean().yvx(0)
                if self.chk_subtract_baseline.isChecked() and IntvB:
                    if 'baseline' in self.m and self.m['baseline']:
                        IntvB -= self.m['baseline']
                    if int_mean:
                        IntvB -= int_mean.y
                self.plot_IntvB.reset()
                self.plot_IntvB.add_curve(IntvB, legend=self.m['name'])
                m = self.m
                m['IntvB'] = IntvB
                m['BvI'] = self.client.eval('session.getDevice("MagB")._BvI')
                self.display_rawdata(generate_output(m))
        elif key == 'magb/measurement':
            self.m = value.copy()
            keys = ['id', 'mode', 'exp_type', 'field_orientation', 'steptime',
                    'description', 'name', 'Bmin', 'Bmax', 'ramp', 'cycles',
                    'step', 'IntvB',]
            if self.m and all(k in self.m for k in keys):
                self.display_rawdata(generate_output(self.m))
                self.cmb_mode.setCurrentIndex(
                    self.cmb_mode.findText(str(self.m['mode'])))
                self.ln_id.setText(self.m['id'])
                self.ln_description.setText(self.m['description'])
                self.rad_rotation.setChecked(self.m['exp_type'] == 'rotation')
                self.rad_ellipticity.setChecked(self.m['exp_type'] == 'ellipticity')
                self.rad_polar.setChecked(self.m['field_orientation'] == 'polar')
                self.rad_longitudinal.setChecked(self.m['field_orientation'] == 'longitudinal')
                self.ln_Bmin.setText(str(self.m['Bmin']))
                self.ln_Bmax.setText(str(self.m['Bmax']))
                self.ln_step.setText(str(self.m['step']))
                self.ln_steptime.setText(str(self.m['steptime']))
                self.cmb_ramp.setCurrentIndex(self.cmb_ramp.findText(format(self.m['ramp'], '.1f')))
                self.ln_cycles.setText(str(self.m['cycles']))
                self.plot_IntvB.reset()
                if self.m['IntvB']:
                    IntvB = self.m['IntvB']
                    int_mean = IntvB.series_to_curves().mean().yvx(0)
                    if self.chk_subtract_baseline.isChecked():
                        if 'baseline' in self.m and self.m['baseline']:
                            IntvB -= self.m['baseline']
                        if int_mean:
                            IntvB -= int_mean.y
                    self.plot_IntvB.reset()
                    self.plot_IntvB.add_mokecurves(IntvB.series_to_curves(),
                                                   legend=self.m['name'])

    def on_cmb_mode_currentTextChanged(self, mode):
        if mode == 'stepwise':
            self.ln_step.setEnabled(True)
            self.ln_steptime.setEnabled(True)
            self.cmb_ramp.setEnabled(False)
        elif mode == 'continuous':
            self.ln_step.setEnabled(False)
            self.ln_steptime.setEnabled(False)
            self.cmb_ramp.setEnabled(True)

    def on_chk_calibration_unlock_stateChanged(self, state):
        self.ln_calibration_ramp.setEnabled(bool(state))
        self.ln_calibration_cycles.setEnabled(bool(state))
        self.btn_calibration.setEnabled(bool(state))

    @pyqtSlot()
    def on_btn_calibration_clicked(self):
        self.client.run(f'MagB.calibrate("{self.cmb_mode.currentText()}", '
                        f'{self.ln_calibration_ramp.text()}, '
                        f'{self.ln_calibration_cycles.text()})')

    def on_chk_baseline_unlock_stateChanged(self, state):
        self.btn_baseline_import.setEnabled(bool(state))
        self.btn_baseline_save.setEnabled(bool(state))

    @pyqtSlot()
    def on_btn_baseline_import_clicked(self):
        if self.m and self.m['IntvB']:
            mode = self.m['mode']
            field = self.m['field_orientation']
            ramp = format(self.m['ramp'], '.1f')
            self.plot_baseline.add_curve(
                self.m['IntvB'].series_to_curves().mean() -
                self.m['IntvB'].series_to_curves().mean().yvx(0).y,
                legend=f'{mode}, {field} @ {ramp} A/min'
            )

    @pyqtSlot()
    def on_btn_baseline_save_clicked(self):
        if self.m and self.m['IntvB']:
            mode = self.m['mode']
            field = self.m['field_orientation']
            ramp = self.m['ramp']
            self.client.run('temp = MagB.baseline.copy()')
            self.client.run(f'temp["{mode}"]["{field}"]["{ramp:.1f}"] = '
                             'MagB.measurement["IntvB"].series_to_curves().mean()'
                             ' - MagB.measurement["IntvB"].series_to_curves().mean().yvx(0).y')
            self.client.run('MagB.baseline = temp')

    @pyqtSlot()
    def on_btn_run_clicked(self):
        measurement = {
            'mode': self.cmb_mode.currentText(),
            'Bmin': float(self.ln_Bmin.text()),
            'Bmax': float(self.ln_Bmax.text()),
            'ramp': float(self.cmb_ramp.currentText()),
            'cycles': int(self.ln_cycles.text()),
            'step': float(self.ln_step.text()),
            'steptime': float(self.ln_steptime.text()),
            'id': self.ln_id.text(),
            'description': self.ln_description.text(),
            'exp_type': 'rotation' if self.rad_rotation.isChecked() \
                else 'ellipticity',
            'field_orientation': 'polar' if self.rad_polar.isChecked() \
                else 'longitudinal'
        }
        for key, item in measurement.items():
            if item is None or item == '':
                QMessageBox.information(None, '', f'Please input {key} value')
                return
        if measurement['steptime'] < 0:
            QMessageBox.information(None, '', 'Step time must be non-negative value')
            return
        self.client.run(f'MagB.measure_intensity({measurement})')

    def on_chk_subtract_baseline_stateChanged(self, _):
        if self.client.eval('session.getDevice("MagB")._measuring'):
            self.on_keyChange('magb/progress', None, None, None)
        else:
            self.on_keyChange('magb/measurement', self.m, None, None)

    def _timeleft(self, progress):
        """Calculates approximate remaining time of a measurement."""
        t = 0
        keys = ['mode', 'steptime', 'Bmin', 'Bmax', 'ramp', 'cycles', 'step',]
        if self.m and all(k in self.m for k in keys):
            Bmin = self.m['Bmin']
            Bmax = self.m['Bmax']
            cycles = self.m['cycles']
            step = self.m['step']
            steptime = self.m['steptime']
            ramp = self.m['ramp']
            mode = self.m['mode']
            if mode == 'stepwise':
                n = int(abs(Bmax - Bmin) / step)
                ranges = [(Bmin, Bmax, n, False), (Bmax, Bmin, n, False)] * cycles
                values = [i for r in ranges for i in numpy.linspace(*r)]
                if progress < len(values) and self.calibration:
                    B0 = values[progress - 1] if progress else 0
                    I0 = self._field2current(B0, values[progress] > B0).n
                    for B1 in values[progress:]:
                        I1 = self._field2current(B1, B1 > B0).n
                        t += abs(I1 - I0) / ramp * 60 + 1 # ~1 s overhead
                        t += steptime
                        t += 0.5 # avg measurement delay
                        B0, I0 = B1, I1
            else:
                if self.calibration:
                    Imin = self._field2current(Bmin, Bmin > 0).n
                    Imax = self._field2current(Bmax, Bmax > Bmin).n
                    n = 100
                    dt = abs(Imax - Imin) / n / ramp * 60
                    if dt < 0.5:
                        dt = 0.5
                        n = int(abs(Imax - Imin) / (dt * ramp / 60))
                    ranges = [(Imin, Imax, n, False), (Imax, Imin, n, False)] * cycles
                    values = [i for r in ranges for i in numpy.linspace(*r)]
                    if progress < len(values):
                        I0 = values[progress - 1] if progress else 0
                        for I1 in values[progress:]:
                            t += abs(I1 - I0) / ramp * 60
                            I0 = I1
        return t

    def _field2current(self, field, increasing):
        mode = self.m['mode']
        ramp = self.m['ramp']
        curves = self.calibration[mode][format(ramp, '.1f')]
        return curves.increasing()[0].xvy(field).x \
            if increasing else curves.decreasing()[0].xvy(field).x


class MokeHistory(MokeBase):

    def __init__(self, parent, client, options):
        MokeBase.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_jcns/moke01/gui/mokehistory.ui'))
        self.lyt_plot_IntvB.addWidget(self.plot_IntvB)
        self.lyt_plot_EvB.addWidget(self.plot_EvB)
        self._model = QStandardItemModel()
        self.lst_history.setModel(self._model)
        self.lst_history.selectionModel().currentChanged.\
            connect(self.on_lst_history_index_changed)
        self.txt_rawdata.setFont(QFont('Courier New'))
        self.measurements = {}
        date1 = datetime.datetime.now().date()
        date0 = date1 - datetime.timedelta(days=30)
        date0 = date0.strftime('%Y-%m-%d')
        date1 = date1.strftime('%Y-%m-%d')
        self.dt_from.setDate(QDate(*[int(i) for i in date0.split('-')]))
        self.dt_to.setDate(QDate(*[int(i) for i in date1.split('-')]))
        client.connected.connect(self.on_connected)
        client.disconnected.connect(self.on_disconnected)

    def on_connected(self):
        self._read_measurements()
        self.dt_from.dateChanged.connect(self._read_measurements)
        self.dt_to.dateChanged.connect(self._read_measurements)

    def on_disconnected(self):
        self.dt_from.dateChanged.disconnect(self._read_measurements)
        self.dt_to.dateChanged.disconnect(self._read_measurements)

    def _read_measurements(self):
        self.measurements = {}
        self._model.clear()
        fr_time = self.dt_from.date().toString(Qt.DateFormat.ISODateWithMs)
        to_time = self.dt_to.date().toString(Qt.DateFormat.ISODateWithMs)
        measurements = \
            self.client.eval(f'MagB.history("measurement", "{fr_time}", "{to_time}")')
        for _, m in measurements:
            if 'name' in m.keys() and 'IntvB' in m.keys() and m['IntvB']:
                if m['name'] not in self.measurements.keys():
                    self._model.insertRow(0, QStandardItem(m['name']))
                self.measurements[m['name']] = m

    def on_lst_history_index_changed(self, current, _=None):
        if current:
            item = self._model.itemFromIndex(current)
            self.m = self.measurements[item.text()]
            self.display_rawdata(generate_output(self.m))
        IntvB = self.m['IntvB']
        int_mean = IntvB.series_to_curves().mean().yvx(0)
        if self.chk_subtract_baseline.isChecked():
            if 'baseline' in self.m and self.m['baseline']:
                IntvB -= self.m['baseline']
            if int_mean:
                IntvB -= int_mean.y
        self.plot_IntvB.reset()
        self.plot_EvB.reset()
        self.plot_IntvB.add_mokecurves(IntvB.series_to_curves(),
                                       legend=self.m['name'])

    def on_chk_subtract_baseline_stateChanged(self, _):
        self.on_lst_history_index_changed(self.lst_history.selectionModel().currentIndex())
