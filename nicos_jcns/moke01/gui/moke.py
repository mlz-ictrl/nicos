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

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.livewidget import LiveWidget1D
from nicos.guisupport.plots import GRMARKS, MaskedPlotCurve
from nicos.guisupport.qt import QDate, QMessageBox, QTimer, QStandardItem, \
    QStandardItemModel, Qt
from nicos.utils import findResource
from nicos_jcns.moke01.utils import calculate, fix_filename, generate_output

from gr.pygr import ErrorBar
import numpy
# pylint: disable=import-error
from uncertainties.core import AffineScalarFunc, Variable


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
        if isinstance(x[0], (AffineScalarFunc, Variable)):
            dx = [i.s for i in x]
            x = [i.n for i in x]
        if isinstance(y[0], (AffineScalarFunc, Variable)):
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
        self.plot1 = MokePlot('MagB, T', 'Intensity, V', self)
        self.plot2 = MokePlot('MagB, T', 'Ellipticity, a.u.', self)
        self.m = {}
        client.connected.connect(self.on_connected)
        client.disconnected.connect(self.on_disconnected)

    def button_calc_clicked(self):
        if not self.ln_angle.text() or not self.ln_ext.text():
            QMessageBox.information(None, '', 'Please input Canting angle/Extinction values')
            return
        if not self.m:
            QMessageBox.information(None, '', 'Not measured yet or last measurement is n/a')
            return
        angle = float(self.ln_angle.text()) # urad
        ext = float(self.ln_ext.text()) # V
        try:
            fit_min, fit_max, IntvB, EvB, kerr = calculate(self.m, angle, ext)
        except Exception as e:
            QMessageBox.information(None, '', f'Calculation has failed:\n{e}')
            return
        # upd IntvB plot with mean curve and fits
        x = numpy.array([float(self.m['Bmin']), float(self.m['Bmax'])])
        self.plot1.add_curve([], x=x, y=fit_min[0] * x + fit_min[1],
                             legend='Fit min')
        self.plot1.add_curve([], x=x, y=fit_max[0] * x + fit_max[1],
                             legend='Fit max')
        self.plot1.add_curve(IntvB, legend='Mean')
        # show EvB plot and kerr angle
        sample_name = f'{self.m["time"]} {self.m["name"]}'
        self.plot2.reset()
        self.plot2.add_curve(EvB, legend=sample_name)
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
        self.plot0 = MokePlot('PS_current, A', 'MagB, T', self)
        self.lyt_mag_plot.addWidget(self.plot0)
        self.lyt_int_plot.addWidget(self.plot1)
        self.lyt_elli_plot.addWidget(self.plot2)
        self._update_plot0 = QTimer()
        self._update_plot0.timeout.connect(self._update_calibration)
        self._update_plot1 = QTimer()
        self._update_plot1.timeout.connect(self._update_intensity)

    def on_connected(self):
        self._read_last_measurement()
        self._read_calibration()
        self.cmb_mag_mode.currentIndexChanged.connect(self._read_calibration)
        self.chck_unlock.stateChanged.connect(self._on_unlock_changed)
        self.btn_calibrate.clicked.connect(self.button_calibrate_clicked)
        self.btn_run.clicked.connect(self.button_run_clicked)
        self.btn_calc.clicked.connect(self.button_calc_clicked)
        self._update_plot0.start(500) # _update_calibration
        self._update_plot1.start(500) # _update_intensity

    def on_disconnected(self):
        self._update_plot0.stop() # _update_calibration
        self._update_plot1.stop() # _update_intensity
        self.cmb_mag_mode.currentIndexChanged.disconnect(self._read_calibration)
        self.btn_run.clicked.disconnect(self.button_run_clicked)
        self.btn_calc.clicked.disconnect(self.button_calc_clicked)

    def _read_last_measurement(self):
        self.m = self.client.eval('session.getDevice("MagB").measurement')
        if self.m:
            self.cmb_mag_mode.setCurrentIndex(self.cmb_mag_mode.findText(str(self.m['mode'])))
            self.ln_sample.setText(self.m['name'])
            self.rad_rotation.setChecked(self.m['exp_type'] == 'rotation')
            self.ln_Bmin.setText(str(self.m['Bmin']))
            self.ln_Bmax.setText(str(self.m['Bmax']))
            self.ln_int_step.setText(str(self.m['step']))
            self.cmb_int_ramp.setCurrentIndex(self.cmb_int_ramp.findText(str(self.m['ramp'])))
            self.ln_int_cycles.setText(str(self.m['cycles']))
            sample_name = f'{self.m["time"]} {self.m["name"]}'
            if self.m['IntvB']:
                self.plot1.reset()
                self.plot1.add_curve(self.m['IntvB'], legend=sample_name)
                self.display_rawdata(generate_output(self.m))

    def _read_calibration(self):
        self.plot0.reset()
        mode = self.cmb_mag_mode.currentText()
        calibration = self.client.eval('session.getDevice("MagB").calibration')
        if mode == 'stepwise':
            self.ln_int_step.setEnabled(True)
            self.ln_int_steptime.setEnabled(True)
            self.cmb_int_ramp.setEnabled(False)
        elif mode == 'continuous':
            self.ln_int_step.setEnabled(False)
            self.ln_int_steptime.setEnabled(False)
            self.cmb_int_ramp.setEnabled(True)
        if mode in calibration.keys():
            for ramp, curves in calibration[mode].items():
                for i, curve in enumerate(curves):
                    self.plot0.add_curve(curve,
                                         legend=f'{mode} {"increasing B" if i else "decreasing B"}'
                                                f' @ {ramp} A/min')

        if calibration.keys:
            self.cmb_int_ramp.clear()
            self.cmb_int_ramp.addItems(calibration[mode].keys())
        if 'ramp' in self.m.keys():
            ramp = str(self.m['ramp'])
        else:
            ramp = self.cmb_int_ramp.currentText() or \
                   str(self.client.eval('session.getDevice("MagB").ramp'))
        self.cmb_int_ramp.setCurrentIndex(self.cmb_int_ramp.findText(ramp))

    def button_calibrate_clicked(self):
        self.client.run(f'MagB.calibrate("{self.cmb_mag_mode.currentText()}", '
                        f'{self.ln_mag_ramp.text()}, {self.ln_mag_cycles.text()})')

    def _update_calibration(self):
        if self.client.eval('session.getDevice("MagB")._calibration_updated'):
            self.client.run('MagB._calibration_updated = False', noqueue=True)
            self._read_calibration()

    def _on_unlock_changed(self, state):
        self.ln_mag_ramp.setEnabled(bool(state))
        self.ln_mag_cycles.setEnabled(bool(state))
        self.btn_calibrate.setEnabled(bool(state))

    def button_run_clicked(self):
        mode = self.cmb_mag_mode.currentText()
        Bmin = self.ln_Bmin.text()
        Bmax = self.ln_Bmax.text()
        ramp = self.cmb_int_ramp.currentText()
        cycles = self.ln_int_cycles.text()
        step = self.ln_int_step.text()
        steptime = self.ln_int_steptime.text()
        name = self.ln_sample.text()
        if not all([name, mode, Bmin, Bmax, ramp, cycles, step, steptime]):
            QMessageBox.information(None, '', 'Please input measurement settings')
            return
        if float(steptime) <= 0.1:
            QMessageBox.information(None, '', 'Step time must be > 0.1 s')
            return
        exp_type = 'rotation' if self.rad_rotation.isChecked() else 'ellipticity'
        self.client.run(f'MagB.measure_intensity("{mode}", {Bmin}, {Bmax}, '
                        f'{ramp}, {cycles}, {step}, {steptime}, "{name}", '
                        f'"{exp_type}")')
        self._update_plot1.start(500) # _update_intensity

    def _update_intensity(self):
        self.m = self.client.eval('session.getDevice("MagB").measurement')
        self.display_rawdata(generate_output(self.m))
        if not self.m:
            self._update_plot1.stop() # _update_intensity
            return
        # live-update graph of intensity vs field
        sample_name = f'{self.m["time"]} {self.m["name"]}'
        # before measurement is finished and stored to `MagB.measurement`
        # IntvB can be fetched from MagB._IntvB
        IntvB = self.client.eval('session.getDevice("MagB")._IntvB')
        if IntvB:
            self.plot1.reset()
            self.plot1.add_curve(IntvB, legend=sample_name)
        # live-update progress bar
        maxprogress = self.client.eval('session.getDevice("MagB")._maxprogress')
        self.bar_cycles.setMaximum(maxprogress)
        progress = self.client.eval('session.getDevice("MagB")._progress')
        self.bar_cycles.setValue(progress)
        # live-update remaining time
        if self.m['mode'] == 'stepwise':
            steptime = float(self.ln_int_steptime.text())
            timeleft = f'{int(steptime * (maxprogress - progress) / 60):02}:' \
                       f'{int(steptime * (maxprogress - progress) % 60):02}'
            self.lcd_timeleft.display(timeleft)
        # stop QTimer when MagB finishes cycling
        if not self.client.eval('session.getDevice("MagB")._cycling') \
                and self.m['IntvB']:
            self._update_plot1.stop() # _update_intensity


class MokeHistory(MokeBase):

    def __init__(self, parent, client, options):
        MokeBase.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_jcns/moke01/gui/mokehistory.ui'))
        self.lyt_int_plot.addWidget(self.plot1)
        self.lyt_elli_plot.addWidget(self.plot2)
        self._model = QStandardItemModel()
        self.lst_history.setModel(self._model)
        self.lst_history.selectionModel().selectionChanged.\
            connect(self.onSelectionChanged)
        self.measurements = {}
        date1 = datetime.datetime.now().date()
        date0 = date1 - datetime.timedelta(days=30)
        date0 = date0.strftime('%Y-%m-%d')
        date1 = date1.strftime('%Y-%m-%d')
        self.dt_from.setDate(QDate(*[int(i) for i in date0.split('-')]))
        self.dt_to.setDate(QDate(*[int(i) for i in date1.split('-')]))

    def on_connected(self):
        self.read_measurements()
        self.dt_from.dateChanged.connect(self.read_measurements)
        self.dt_to.dateChanged.connect(self.read_measurements)
        self.btn_calc.clicked.connect(self.button_calc_clicked)

    def on_disconnected(self):
        self.dt_from.dateChanged.disconnect(self.read_measurements)
        self.dt_to.dateChanged.disconnect(self.read_measurements)
        self.btn_calc.clicked.disconnect(self.button_calc_clicked)

    def read_measurements(self):
        self.measurements = {}
        self._model.clear()
        fr_time = self.dt_from.date().toString(Qt.DateFormat.ISODateWithMs)
        to_time = self.dt_to.date().toString(Qt.DateFormat.ISODateWithMs)
        measurements = \
            self.client.eval(f'MagB.history("measurement", "{fr_time}", "{to_time}")')
        for _, m in measurements:
            keys = ['name', 'time', 'IntvB']
            if all(key in m.keys() for key in keys) and m['IntvB']:
                if 'name' in m.keys() and 'time' in m.keys():
                    name = f'{m["time"]} {m["name"]}'
                    self.measurements[name] = m
                    self._model.insertRow(0, QStandardItem(name))

    def onSelectionChanged(self, selected, _):
        if selected.indexes():
            item = self._model.itemFromIndex(selected.indexes()[0])
            self.m = self.measurements[item.text()]
            self.display_rawdata(generate_output(self.m))
        if self.m['IntvB']:
            sample_name = f'{self.m["time"]} {self.m["name"]}'
            self.plot1.reset()
            self.plot2.reset()
            self.plot1.add_curve(self.m['IntvB'], legend=sample_name)
