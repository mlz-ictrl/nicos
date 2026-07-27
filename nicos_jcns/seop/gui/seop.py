# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Alexander Zaft <a.zaft@fz-juelich.de>
#
# *****************************************************************************

""" Gui elements to control 3He/Seop with NICOS


"""
import time
from datetime import datetime

import gr
from gr.pygr import Plot, PlotCurve
from numpy import array

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.core import status
from nicos.guisupport.livewidget import Axes, LiveWidget1D
from nicos.guisupport.plots import DATEFMT, GRMARKS, TIMEFMT
from nicos.guisupport.qt import QLayout, QMainWindow, QSizePolicy, \
    QStatusBar, pyqtSlot
from nicos.guisupport.qtgr import InteractiveGRWidget, MouseEvent
from nicos.guisupport.timeseries import buildTickDistAndSubTicks
from nicos.guisupport.utils import DoubleValidator
from nicos.guisupport.widget import NicosWidget
from nicos.utils import findResource


class SeopPlot(LiveWidget1D):
    def __init__(self, xlabel, ylabel, timeaxis, marker=False, parent=None, **kwds):
        super().__init__(parent, **kwds)
        # Replace GRWidget with InteractiveGRWidget
        self.layout().removeWidget(self.gr)
        self.gr.deleteLater()
        self.gr = InteractiveGRWidget(self)
        self.plot = Plot(viewport=(0.1, 0.95, 0.20, 0.95))
        self.axes = Axes(self, viewport=self.plot.viewport, xdual=False, ydual=False)
        self.plot.addAxes(self.axes)
        self.gr.addPlot(self.plot)
        self.layout().addWidget(self.gr)
        #
        self.leftTurnedLegend = True
        self.axes.resetCurves()
        self.plot.offsetXLabel = -.1
        if timeaxis:
            self.axes.setXtickCallback(self.xtickCallBack)
            self.plot.viewport = [0.12, 0.98, 0.2, 0.98]
        self.setTitles({'x': xlabel, 'y': ylabel})
        self._curves = [PlotCurve([0], [1], linewidth=2, legend='')]
        if marker:
            self._curves[0].markertype = GRMARKS['diagonalcross']
            self.changeMarkerSize(1.5)

        self.axes.addCurves(self._curves[0])
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding,
                           QSizePolicy.Policy.MinimumExpanding)

    def setPlotData(self, x, y):
        self._curves[0].x = array(x)
        self._curves[0].y = array(y)

        self.make_xticks()
        self.update()
        self.reset()

    def reset(self):
        self.plot.reset()

    def make_xticks(self):
        first, last = self._curves[0].x[0], self._curves[0].x[-1]
        tickdist, _nticks = buildTickDistAndSubTicks(first, last, 5)
        self.axes.xtick = tickdist

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


class SeopPlotPanel(Panel):
    panelName = 'Seop Plot'
    dformat = '%Y-%m-%d %H:%M:%S.%f'
    numPts = 20  # only relevant for Amplitude and Phase

    def __init__(self, parent, client, options):
        super().__init__(parent, client, options)
        loadUi(self, findResource('nicos_jcns/seop/gui/seopplot.ui'))
        opts = options.get('plotconf', {})
        self.command = options.get('command')
        self.statusBar = QStatusBar(self)
        self.layout().addWidget(self.statusBar)
        self.xtime = options.get('xtime', False)
        opts['marker'] = self.xtime
        self.plot = SeopPlot(parent=self.widget, timeaxis=self.xtime, **opts)
        self.widget.layout().addWidget(self.plot)
        self.plot.setSizePolicy(QSizePolicy.Policy.Expanding,
                                QSizePolicy.Policy.Expanding)
        self.plot.gr.cbm.addHandler(MouseEvent.MOUSE_MOVE, self.on_mouseMove)
        if not self.xtime:
            self.numPtsWidgets.hide()

        cache = self.client.getCacheKey('nmr/value')
        if cache:
            _, last_time = cache
            self.last_timestamp = datetime.strptime(last_time, self.dformat)
        else:
            self.last_timestamp = None
        self.client.cache.connect(self.on_client_cache)
        if self.last_timestamp:
            self.update_plot()

    def on_client_cache(self, data):
        (_time, key, _op, value) = data
        if key != 'nmr/value':
            return
        ts = datetime.strptime(value.strip("'"), self.dformat)
        if not self.last_timestamp or self.last_timestamp < ts:
            self.last_timestamp = ts
            self.update_plot()

    def update_plot(self):
        if self.xtime:
            x, y = self.client.eval(f'nmr.{self.command}({self.numPts})')
        else:
            x, y = self.client.eval(f'nmr.{self.command}()')
        if not x or not y:
            return
        if x and isinstance(x[0], str):
            x = [datetime.strptime(d, self.dformat).timestamp() for d in x]
        self.plot.setPlotData(x, y)

    def on_resetViewButton_pressed(self):
        self.plot.reset()
        self.plot.update()

    def on_mouseMove(self, event):
        if event.getWindow():  # inside plot
            self.mouselocation = event
            wc = event.getWC(self.plot.plot.viewport)
            self.statusBar.showMessage('X = %g, Y = %g' % (wc.x, wc.y))
        else:
            self.statusBar.clearMessage()

    def on_setNumPtsButton_pressed(self):
        try:
            self.numPts = int(self.numPtsEdit.text())
        except ValueError:
            self.log.warning('Invalid value for log points!')
        else:
            self.update_plot()


class SeopSettingsPanel(Panel):
    """All settings available for the seop system."""
    panelName = 'NMR Settings'

    def __init__(self, parent, client, options):
        super().__init__(parent, client, options)
        loadUi(self, findResource('nicos_jcns/seop/gui/seopsettings.ui'))
        self.keytowidget = {
            # AFP section
            'tasks/afp/signal/amplitude': self.AFPAmplitudeEdit,
            'tasks/afp/signal/duration': self.AFPDurationEdit,
            'tasks/afp/signal/freq_center': self.AFPFreqCenterEdit,
            'tasks/afp/signal/freq_delta': self.AFPFreqDeltaEdit,
            'tasks/afp/switch_sleep': self.AFPMuteTimeEdit,
            'tasks/afp/signal/envelope_width': self.AFPEnvWidthEdit,
            # AFP devices
            'tasks/afp/devices/analog/port': self.AFPAnalogPortEdit,
            'tasks/afp/devices/analog/sample_rate': self.AFPSampleRateEdit,
            'tasks/afp/devices/analog/voltage_min': self.AFPVminEdit,
            'tasks/afp/devices/analog/voltage_max': self.AFPVmaxEdit,
            'tasks/afp/devices/state/port': self.AFPStatePortEdit,
            'tasks/afp/devices/switch/port': self.AFPMutePortEdit,
            # NMR
            'tasks/nmr/signal/amplitude': self.NMRAmplitudeEdit,
            'tasks/nmr/signal/duration': self.NMRSignalDurationEdit,
            'tasks/nmr/signal/freq_center': self.NMRFreqCenterEdit,
            'tasks/nmr/measurement/duration': self.NMRMeasureDurationEdit,
            'tasks/nmr/measurement/ringdown': self.NMRRingdownEdit,
            'tasks/nmr/dsp/downsampling_factor': self.NMRDownsampleEdit,
            'tasks/nmr/dsp/freq_lowpass': self.NMRLowpassEdit,
            'tasks/nmr/dsp/freq_mixdown': self.NMRMixdownEdit,
            'tasks/nmr/dsp/freq_mixdown_offset': self.NMRMixdownOffsetEdit,
            'tasks/nmr/background/interval': self.NMRBackgroundIntervalEdit,
            # NMR devices
            'tasks/nmr/devices/input/port': self.NMRInputPortEdit,
            'tasks/nmr/devices/input/sample_rate': self.NMRInputSampleRateEdit,
            'tasks/nmr/devices/output/port': self.NMROutputPortEdit,
            'tasks/nmr/devices/output/sample_rate': self.NMROutputSampleRateEdit,
            'tasks/nmr/devices/output/voltage_min': self.NMROutputVminEdit,
            'tasks/nmr/devices/output/voltage_max': self.NMROutputVmaxEdit,
            'tasks/nmr/devices/switch/port': self.NMRSwitchPortEdit,
            'tasks/nmr/devices/trigger/port': self.NMRTriggerPortEdit,
        }
        self.widgettokey = {v: k for k, v in self.keytowidget.items()}
        client.connected.connect(self.on_client_connected)
        client.device.connect(self.on_client_device)
        self.destroyed.connect(self.on_destroyed)
        dvalidator = DoubleValidator()
        for key, widget in self.keytowidget.items():
            if 'port' in key:
                continue
            widget.setValidator(dvalidator)
        self.setEnabled('cell' in client.getDeviceList())

    def on_client_connected(self):
        self._load_config()
        for widget in self.keytowidget.values():
            widget.returnPressed.connect(self.setConfigData)

    def on_client_device(self, data):
        (action, devlist) = data
        if 'cell' not in devlist:
            return
        if action == 'create':
            self.setEnabled(True)
        elif action == 'destroy':
            self.setEnabled(False)

    def on_destroyed(self):
        self.client.connected.disconnect(self.on_client_connected)
        self.client.device.disconnect(self.on_client_device)

    def _load_config(self):
        for key, widget in self.keytowidget.items():
            value = self.client.eval(f"cell.cfg_get('{key}')", '')
            widget.setText(value)

    def setEnabled(self, enabled):
        self.scrollArea.setEnabled(enabled)

    def setConfigData(self):
        widget = self.sender()
        key = self.widgettokey.get(widget, None)
        if not key:
            return
        value = widget.text()
        # Special case: tasks/nmr/signal/duration and
        # tasks/nmr/signal_switch/duration should be the same.
        # The switch triggers the measurement when the signal is complete, should not diverge.
        # Cutting off the ringdown is done with "ringdown".
        if key == 'tasks/nmr/signal/duration':
            self.client.run(f"cell.cfg_set('tasks/nmr/signal_switch/duration', '{value}')")
        self.client.run(f"cell.cfg_set('{key}', '{value}')")

    @pyqtSlot()
    def on_reloadBtn_clicked(self):
        self._load_config()


class SeopControl:
    """Common handlers for SeopControlPanel and SeopControlButtons"""

    @pyqtSlot()
    def on_doAFPFlipBtn_clicked(self):
        self.client.run('AFP()')

    @pyqtSlot()
    def on_doNMRBtn_clicked(self):
        self.client.run('NMR()')

    @pyqtSlot()
    def on_backgroundStartBtn_clicked(self):
        self.client.run('startBackgroundNMR()')

    @pyqtSlot()
    def on_backgroundStopBtn_clicked(self):
        self.client.run('stopBackgroundNMR()')


class SeopControlPanel(Panel, SeopControl):
    """Small gui panel for control. Maps to script commands."""
    panelName = 'NMR Control'

    def __init__(self, parent, client, options):
        super().__init__(parent, client, options)
        loadUi(self, findResource('nicos_jcns/seop/gui/seopcontrol.ui'))
        parent.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        # self.client.connected.connect(self.on_client_connected)
        # self.client.disconnected.connect(self.on_client_disconnected)

    # def on_client_connected(self):
    #      self.doAFPFlipBtn.setEnabled(True)
    #      self.doNMRBtn.setEnabled(True)
    #      self.backgroundNMRBtn.setEnabled(True)

    # def on_client_disconnected(self):
    #      self.doAFPFlipBtn.setEnabled(False)
    #      self.doNMRBtn.setEnabled(False)
    #      self.backgroundNMRBtn.setEnabled(False)


class SeopControlButtons(QMainWindow, SeopControl):
    """SeopControlPanel as a tool window."""
    panelName = 'NMR Control'

    def __init__(self, parent, client, **options):
        super().__init__(parent)
        loadUi(self,
               findResource('nicos_jcns/seop/gui/seopcontrol_mainwindow.ui'))
        self.client = client
        self.log = parent.log.getChild('seop')


class SpectrumPlot(SeopPlot):

    def __init__(self, xlabel, ylabel, timeaxis, marker=False, parent=None, **kwds):
        self.autoresize = True
        SeopPlot.__init__(self, xlabel, ylabel, timeaxis, marker, parent, **kwds)
        self.clear()

    def clear(self):
        self._curves[0].visible = False
        self.update()

    def setPlotData(self, x, y):
        self._curves[0].visible = True
        super().setPlotData(x, y)

    def reset(self):
        if self.autoresize:
            SeopPlot.reset(self)


class SpectrometerPanel(NicosWidget, Panel):
    panelName = 'Spectrometers'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_jcns/seop/gui/spectrometers.ui'))

        # Cache wavelength ticks and spectrum values by spectrometer.
        self._x = {}
        self._y = {}
        self._enabled = False

        # init plot area
        self.plot = SpectrumPlot('Wavelength, nm', 'Intensity, cts', None, False, self)
        self.plot.autoresize = self.chkAutoresize.isChecked()
        self.lytPlot.addWidget(self.plot)

        # init NicosWidget to listen on cache
        NicosWidget.__init__(self)
        self.setClient(client)

        client.connected.connect(self.on_connected)
        client.disconnected.connect(self.on_disconnected)
        self.destroyed.connect(self.on_destroyed)
        if client.isconnected:
            self.on_connected()

    def on_destroyed(self):
        self.client.connected.disconnect(self.on_connected)
        self.client.disconnected.disconnect(self.on_disconnected)

    def on_connected(self):
        self._enabled = False
        devices = set(self.client.getDeviceList())
        first_available = None
        for i in range(self.cmbSpecs.count()):
            spec = self.cmbSpecs.itemText(i)
            if spec not in devices:
                continue
            if first_available is None:
                first_available = i
            spec_state = self.client.eval(f'{spec}.status()[0]',
                                          default=status.UNKNOWN)
            # Start and Stop enable and disable acquisition on read. An
            # enabled spectrometer can report OK while idle between reads.
            if spec_state > status.BUSY:
                continue
            if self._enabled:
                self.client.run(f'{spec}.disable()')
            else:
                # Keep _enabled false while the selection handler clears the plot.
                self.cmbSpecs.setCurrentIndex(i)
                self._enabled = True
        if not self._enabled and first_available is not None:
            self.cmbSpecs.setCurrentIndex(first_available)
        self.btnStartStop.setText('Stop' if self._enabled else 'Start')

    def on_disconnected(self):
        self._enabled = False
        self._x.clear()
        self._y.clear()
        self.btnStartStop.setText('Start')
        self.plot.clear()

    def registerKeys(self):
        for i in range(self.cmbSpecs.count()):
            spec = self.cmbSpecs.itemText(i)
            for k in (f'{spec}/value', f'{spec}/xticks'):
                self.registerKey(k)

    def on_keyChange(self, key, value, time, expired):
        if value is None or not key.endswith(('/value', '/xticks')) \
                or len(value) == 0 or expired:
            return
        spec, field = key.rsplit('/', 1)
        if field == 'xticks':
            self._x[spec] = value
        else:
            self._y[spec] = value
        if spec == self.cmbSpecs.currentText():
            self._plot_spectrum(spec)

    def _plot_spectrum(self, spec):
        x = self._x.get(spec, ())
        y = self._y.get(spec, ())
        if 0 < len(x) == len(y):
            self.plot.setPlotData(x, y)

    @pyqtSlot()
    def on_btnStartStop_clicked(self):
        if not self.client.isconnected:
            return
        spec = self.cmbSpecs.currentText()
        if spec in self.client.getDeviceList():
            self._enabled = not self._enabled
            self.client.run(f'{spec}.{"en" if self._enabled else "dis"}able()')
            self.btnStartStop.setText('Stop' if self._enabled else 'Start')

    @pyqtSlot(int)
    def on_cmbSpecs_currentIndexChanged(self, index):
        self.plot.clear()
        selected = self.cmbSpecs.currentText()
        self._plot_spectrum(selected)
        if not self.client.isconnected or not self._enabled:
            return
        enabled = False
        devices = set(self.client.getDeviceList())
        for i in range(self.cmbSpecs.count()):
            spec = self.cmbSpecs.itemText(i)
            if spec not in devices:
                continue
            spec_state = self.client.eval(f'{spec}.status()[0]',
                                          default=status.UNKNOWN)
            if spec_state == status.UNKNOWN:
                continue
            if spec == selected:
                enabled = (spec_state <= status.BUSY
                           or spec_state == status.DISABLED)
                if spec_state == status.DISABLED:
                    self.client.run(f'{spec}.enable()')
            elif spec_state <= status.BUSY:
                self.client.run(f'{spec}.disable()')
        self._enabled = enabled and self.client.isconnected
        self.btnStartStop.setText('Stop' if self._enabled else 'Start')

    @pyqtSlot(bool)
    def on_chkAutoresize_toggled(self, checked):
        self.plot.autoresize = checked
