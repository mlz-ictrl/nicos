#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
import os

import numpy
from gr.pygr import ErrorBar
# pylint: disable=import-error
from uncertainties.core import AffineScalarFunc

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.core import status
from nicos.guisupport.livewidget import LiveWidget1D
from nicos.guisupport.plots import GRMARKS, MaskedPlotCurve
from nicos.guisupport.qt import QDate, QMessageBox, QStandardItem, \
    QStandardItemModel, Qt, QTimer
from nicos.utils import findResource

from nicos_jcns.moke01.utils import calculate, fix_filename, generate_output


class MokePlot(LiveWidget1D):
    def __init__(self, xlabel, ylabel, parent=None, **kwds):
        LiveWidget1D.__init__(self, parent, **kwds)
        self.axes.resetCurves()
        self.axes.xdual, self.axes.ydual = False, False
        self.plot.setLegend(True)
        self.setTitles({'x': xlabel, 'y': ylabel})
        self._curves = []
        self._n = 0

    def add_curve(self, curve, x=None, y=None, dx=None, dy=None, legend=None):
        self._n += 1
        color = self._n % 7 if self._n % 7 else 7
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
            MaskedPlotCurve(x, y, errBar1=x_err, errBar2=y_err,
                            linewidth=1, legend=legend,
                            markertype=GRMARKS['solidsquare'],
                            markercolor=color, linecolor=color),
        )
        self._curves[-1].markersize = 0.5
        self.axes.addCurves(self._curves[-1])
        self._update()

    def reset(self):
        self.axes.resetCurves()
        self._curves = []
        self._n = 0
        self._update()

    def _update(self):
        self.plot.reset()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._update()
        super().mousePressEvent(event)


class MokeBase(Panel):
    panelName = 'MOKE'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        self.plot_IntvB = MokePlot('MagB, T', 'Intensity, V', self)
        self.plot_EvB = MokePlot('MagB, T', 'Ellipticity, a.u.', self)
        self.m = {}
        self.baseline = {}
        client.connected.connect(self.on_connected)
        client.disconnected.connect(self.on_disconnected)

    def on_button_calc_clicked(self):
        self.m = self.client.eval('session.getDevice("MagB").measurement')
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
        if self.chck_subtract_baseline.isChecked():
            IntvB = self.m['IntvB'] - self.m['baseline']
        angle = float(self.ln_canting_angle.text()) # urad
        ext = float(self.ln_extinction.text()) # V
        try:
            fit_min, fit_max, IntvB, EvB, kerr = calculate(IntvB, angle, ext)
        except Exception as e:
            QMessageBox.information(None, '', f'Calculation has failed:\n{e}')
            return
        # upd IntvB plot with mean curve and fits
        x = numpy.array([float(self.m['Bmin']), float(self.m['Bmax'])])
        self.plot_IntvB.add_curve([], x=x, y=fit_min[0] * x + fit_min[1],
                             legend='Fit min')
        self.plot_IntvB.add_curve([], x=x, y=fit_max[0] * x + fit_max[1],
                             legend='Fit max')
        self.plot_IntvB.add_curve(IntvB, legend='Mean')
        # show EvB plot and kerr angle
        sample_name = f'{self.m["time"]} {self.m["name"]}'
        self.plot_EvB.reset()
        self.plot_EvB.add_curve(EvB, legend=sample_name)
        self.ln_kerr.setText(str(kerr))

        output = generate_output(self.m, angle, ext)
        self.display_rawdata(output)
        folder = os.path.join(os.path.expanduser('~'), 'Measurements', 'moke')
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, fix_filename(sample_name) + '.txt'),
                  'w', encoding='utf-8') as f:
            f.write(output)

    def display_rawdata(self, output):
        self.txt_rawdata.clear()
        self.txt_rawdata.insertPlainText(output)


class MokePanel(MokeBase):

    def __init__(self, parent, client, options):
        MokeBase.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_jcns/moke01/gui/mokepanel.ui'))
        self.tabWidget.setCurrentIndex(0)
        self.plot_calibration = MokePlot('PS_current, A', 'MagB, T', self)
        self.lyt_plot_calibration.addWidget(self.plot_calibration)
        self.plot_baseline = MokePlot('MagB, T', 'Intensity, V', self)
        self.lyt_plot_baseline.addWidget(self.plot_baseline)
        self.lyt_plot_IntvB.addWidget(self.plot_IntvB)
        self.lyt_plot_EvB.addWidget(self.plot_EvB)
        self.update_plot_calibration = QTimer()
        self.update_plot_calibration.timeout.connect(self._update_calibration)
        self.update_plot_IntvB = QTimer()
        self.update_plot_IntvB.timeout.connect(self._update_measurement)
        self._mode_changed()
        self.cmb_mode.currentIndexChanged.connect(self._mode_changed)
        self.chck_calibration_unlock.stateChanged.connect(self._on_calibration_unlock_changed)
        self.chck_baseline_unlock.stateChanged.connect(self._on_baseline_unlock_changed)

    def on_connected(self):
        self._read_calibration()
        self.cmb_mode.currentIndexChanged.connect(self._read_calibration)
        self.btn_calibration.clicked.connect(self._on_button_calibrate_clicked)
        self.update_plot_calibration.start(500) # _update_calibration

        self._read_baseline()
        self.btn_baseline_import.clicked.connect(self._on_button_baseline_import_clicked)
        self.btn_baseline_save.clicked.connect(self._on_button_baseline_save_clicked)

        self.btn_run.clicked.connect(self._on_button_run_clicked)
        self.btn_calc.clicked.connect(self.on_button_calc_clicked)
        self.update_plot_IntvB.start(500) # _update_measurement
        self.chck_subtract_baseline.stateChanged.connect(self._on_subtract_baseline_changed)

    def on_disconnected(self):
        self.cmb_mode.currentIndexChanged.disconnect(self._read_calibration)
        self.btn_calibration.clicked.disconnect(self._on_button_calibrate_clicked)
        self.update_plot_calibration.stop() # _update_calibration

        self.btn_run.clicked.disconnect(self._on_button_run_clicked)
        self.btn_calc.clicked.disconnect(self.on_button_calc_clicked)
        self.update_plot_IntvB.stop() # _update_measurement

        self.btn_baseline_import.clicked.disconnect(self._on_button_baseline_import_clicked)
        self.btn_baseline_save.clicked.disconnect(self._on_button_baseline_save_clicked)

    def _mode_changed(self):
        mode = self.cmb_mode.currentText()
        if mode == 'stepwise':
            self.ln_step.setEnabled(True)
            self.ln_steptime.setEnabled(True)
            self.cmb_ramp.setEnabled(False)
        elif mode == 'continuous':
            self.ln_step.setEnabled(False)
            self.ln_steptime.setEnabled(False)
            self.cmb_ramp.setEnabled(True)

    def _read_calibration(self):
        self.plot_calibration.reset()
        calibration = self.client.eval('session.getDevice("MagB").calibration')
        mode = self.cmb_mode.currentText()
        if mode in calibration.keys():
            for ramp, curves in calibration[mode].items():
                self.plot_calibration.add_curve(curves.increasing()[0],
                                                legend=f'{mode} increasing B @ {ramp} A/min')
                self.plot_calibration.add_curve(curves.decreasing()[0],
                                                legend=f'{mode} decreasing B @ {ramp} A/min')

        if calibration.keys:
            self.cmb_ramp.clear()
            self.cmb_ramp.addItems(calibration[mode].keys())
        if 'ramp' in self.m.keys():
            ramp = str(self.m['ramp'])
        else:
            ramp = self.cmb_ramp.currentText() or \
                   str(self.client.eval('session.getDevice("MagB").ramp'))
        self.cmb_ramp.setCurrentIndex(self.cmb_ramp.findText(ramp))

    def _on_calibration_unlock_changed(self, state):
        self.ln_calibration_ramp.setEnabled(bool(state))
        self.ln_calibration_cycles.setEnabled(bool(state))
        self.btn_calibration.setEnabled(bool(state))

    def _on_button_calibrate_clicked(self):
        self.client.run(f'MagB.calibrate("{self.cmb_mode.currentText()}", '
                        f'{self.ln_calibration_ramp.text()}, {self.ln_calibration_cycles.text()})')

    def _update_calibration(self):
        if self.client.eval('session.getDevice("MagB")._calibration_updated'):
            self.client.run('MagB._calibration_updated = False', noqueue=True)
            self._read_calibration()

    def _read_baseline(self):
        self.baseline = self.client.eval(
            'session.getDevice("MagB").baseline.copy()')
        self._update_baseline_plot()

    def _update_baseline_plot(self):
        self.plot_baseline.reset()
        if self.baseline:
            for mode in self.baseline.keys():
                for field in self.baseline[mode].keys():
                    for ramp in self.baseline[mode][field].keys():
                        if self.baseline[mode][field][ramp]:
                            self.plot_baseline.add_curve(self.baseline[mode][field][ramp],
                                                         legend=f'{mode}, {field} @ {ramp} A/min')

    def _on_baseline_unlock_changed(self, state):
        self.btn_baseline_import.setEnabled(bool(state))
        self.btn_baseline_save.setEnabled(bool(state))
        self._read_baseline()

    def _on_button_baseline_import_clicked(self):
        self.m = self.client.eval('session.getDevice("MagB").measurement')
        if self.m and self.m['IntvB']:
            mode = self.m['mode']
            field = self.m['field_orientation']
            ramp = str(self.m['ramp'])
            if ramp not in self.baseline[mode][field].keys():
                self.baseline[mode][field][ramp] = {}
            self.baseline[mode][field][ramp] = \
                self.m['IntvB'].series_to_curves().mean()
            self._update_baseline_plot()

    def _on_button_baseline_save_clicked(self):
        self.m = self.client.eval('session.getDevice("MagB").measurement')
        if self.m and self.m['IntvB']:
            mode = self.m['mode']
            field = self.m['field_orientation']
            ramp = self.m['ramp']
            self.client.run('temp = MagB.baseline.copy()')
            self.client.run(f'temp["{mode}"]["{field}"]["{ramp}"] = '
                             'MagB.measurement["IntvB"].series_to_curves().mean()')
            self.client.run('MagB.baseline = temp')

    def _on_button_run_clicked(self):
        mode = self.cmb_mode.currentText()
        Bmin = self.ln_Bmin.text()
        Bmax = self.ln_Bmax.text()
        ramp = self.cmb_ramp.currentText()
        cycles = self.ln_cycles.text()
        step = self.ln_step.text()
        steptime = self.ln_steptime.text()
        name = self.ln_sample.text()
        if not all([name, mode, Bmin, Bmax, ramp, cycles, step, steptime]):
            QMessageBox.information(None, '', 'Please input measurement settings')
            return
        if float(steptime) < 0:
            QMessageBox.information(None, '', 'Step time must be non-negative value')
            return
        exp_type = 'rotation' if self.rad_rotation.isChecked() else 'ellipticity'
        field_orientation = 'polar' if self.rad_polar.isChecked() else 'longitudinal'
        self.client.run(f'MagB.measure_intensity("{mode}", "{field_orientation}", '
                        f'{Bmin}, {Bmax}, {ramp}, {cycles}, {step}, {steptime}, '
                        f'"{name}", "{exp_type}")')
        self.update_plot_IntvB.start(500) # _update_measurement

    def _update_measurement(self):
        self.m = self.client.eval('session.getDevice("MagB").measurement')
        if not self.m:
            self.update_plot_IntvB.stop() # _update_measurement
            return
        self.display_rawdata(generate_output(self.m))
        self.cmb_mode.setCurrentIndex(
            self.cmb_mode.findText(str(self.m['mode'])))
        self.ln_sample.setText(self.m['name'])
        self.rad_rotation.setChecked(self.m['exp_type'] == 'rotation')
        self.rad_polar.setChecked(self.m['field_orientation'] == 'polar')
        self.ln_Bmin.setText(str(self.m['Bmin']))
        self.ln_Bmax.setText(str(self.m['Bmax']))
        self.ln_step.setText(str(self.m['step']))
        self.ln_steptime.setText(str(self.m['steptime']))
        self.cmb_ramp.setCurrentIndex(self.cmb_ramp.findText(str(self.m['ramp'])))
        self.ln_cycles.setText(str(self.m['cycles']))
        # live-update graph of intensity vs field
        sample_name = f'{self.m["time"]} {self.m["name"]}'
        # before measurement is finished and stored to `MagB.measurement`
        # IntvB can be fetched from MagB._IntvB
        IntvB = self.client.eval('session.getDevice("MagB")._IntvB') or \
                self.m['IntvB']
        if IntvB:
            if self.chck_subtract_baseline.isChecked():
                IntvB = IntvB - self.m['baseline']
            self.plot_IntvB.reset()
            self.plot_IntvB.add_curve(IntvB, legend=sample_name)
        # live-update progress bar
        maxprogress = self.client.eval('session.getDevice("MagB")._maxprogress')
        self.bar_cycles.setMaximum(maxprogress)
        progress = self.client.eval('session.getDevice("MagB")._progress')
        self.bar_cycles.setValue(progress)
        # live-update remaining time
        if self.m['mode'] == 'stepwise':
            steptime = float(self.ln_steptime.text())
            timeleft = f'{int(steptime * (maxprogress - progress) / 60):02}:' \
                       f'{int(steptime * (maxprogress - progress) % 60):02}'
            self.lcd_timeleft.display(timeleft)
        # if MagB is disabled but the measurement did not exited properly
        if self.client.eval('session.getDevice("MagB")._cycling'):
            if self.client.eval(
                    'session.getDevice("MagB").status()[0]') == status.DISABLED:
                self.client.run('MagB._cycling = False')
                self.client.run('MagB._stop_requested = False')
        # stop QTimer when MagB finishes cycling
        else:
            self.update_plot_IntvB.stop() # _update_measurement

    def _on_subtract_baseline_changed(self, _):
        if not self.update_plot_IntvB.isActive():
            self._update_measurement()


class MokeHistory(MokeBase):

    def __init__(self, parent, client, options):
        MokeBase.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_jcns/moke01/gui/mokehistory.ui'))
        self.lyt_plot_IntvB.addWidget(self.plot_IntvB)
        self.lyt_plot_EvB.addWidget(self.plot_EvB)
        self._model = QStandardItemModel()
        self.lst_history.setModel(self._model)
        self.lst_history.selectionModel().currentChanged.\
            connect(self._on_current_changed)
        self.measurements = {}
        date1 = datetime.datetime.now().date()
        date0 = date1 - datetime.timedelta(days=30)
        date0 = date0.strftime('%Y-%m-%d')
        date1 = date1.strftime('%Y-%m-%d')
        self.dt_from.setDate(QDate(*[int(i) for i in date0.split('-')]))
        self.dt_to.setDate(QDate(*[int(i) for i in date1.split('-')]))

    def on_connected(self):
        self._read_measurements()
        self.dt_from.dateChanged.connect(self._read_measurements)
        self.dt_to.dateChanged.connect(self._read_measurements)
        self.btn_calc.clicked.connect(self.on_button_calc_clicked)
        self.chck_subtract_baseline.stateChanged.connect(self._on_subtract_baseline_changed)

    def on_disconnected(self):
        self.dt_from.dateChanged.disconnect(self._read_measurements)
        self.dt_to.dateChanged.disconnect(self._read_measurements)
        self.btn_calc.clicked.disconnect(self.on_button_calc_clicked)
        self.chck_subtract_baseline.stateChanged.disconnect(self._on_subtract_baseline_changed)

    def _read_measurements(self):
        self.measurements = {}
        self._model.clear()
        fr_time = self.dt_from.date().toString(Qt.DateFormat.ISODateWithMs)
        to_time = self.dt_to.date().toString(Qt.DateFormat.ISODateWithMs)
        measurements = \
            self.client.eval(f'MagB.history("measurement", "{fr_time}", "{to_time}")')
        for _, m in measurements:
            keys = ['name', 'time', 'IntvB']
            if all(key in m.keys() for key in keys) and m['IntvB']:
                name = f'{m["time"]} {m["name"]}'
                self.measurements[name] = m
                self._model.insertRow(0, QStandardItem(name))

    def _on_current_changed(self, current, _=None):
        if current:
            item = self._model.itemFromIndex(current)
            self.m = self.measurements[item.text()]
            self.display_rawdata(generate_output(self.m))
        IntvB = self.m['IntvB']
        if self.chck_subtract_baseline.isChecked():
            IntvB = self.m['IntvB'] - self.m['baseline']
        sample_name = f'{self.m["time"]} {self.m["name"]}'
        self.plot_IntvB.reset()
        self.plot_EvB.reset()
        self.plot_IntvB.add_curve(IntvB, legend=sample_name)

    def _on_subtract_baseline_changed(self, _):
        self._on_current_changed(self.lst_history.selectionModel().currentIndex())
