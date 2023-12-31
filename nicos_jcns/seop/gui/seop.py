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
#   Alexander Zaft <a.zaft@fz-juelich.de>
#
# *****************************************************************************

""" Gui elements to control 3He/Seop with NICOS


"""
import time
from datetime import datetime

import gr
import yaml
from gr.pygr import Plot, PlotCurve
from numpy import array

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.livewidget import Axes, LiveWidget1D
from nicos.guisupport.plots import DATEFMT, GRMARKS, TIMEFMT
from nicos.guisupport.qt import QLayout, QMainWindow, QSizePolicy, \
    QStatusBar, Qt, QTreeWidgetItem, pyqtSlot
from nicos.guisupport.qtgr import InteractiveGRWidget, MouseEvent
from nicos.guisupport.timeseries import buildTickDistAndSubTicks
from nicos.utils import findResource


class SeopPlot(LiveWidget1D):
    def __init__(self, xlabel, ylabel, timeaxis, parent=None, **kwds):
        super().__init__(parent, **kwds)
        # Replace GRWidget with InteractiveGRWidget
        self.layout().removeWidget(self.gr)
        self.gr.deleteLater()
        self.gr = InteractiveGRWidget(self)
        self.plot = Plot(viewport=(0.1, 0.95, 0.1, 0.95))
        self.axes = Axes(self, viewport=self.plot.viewport,
                         xdual=kwds.get('xscale', 'binary') == 'binary',
                         ydual=kwds.get('yscale', 'binary') == 'binary')
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
        self._curves = [PlotCurve([0], [1], linewidth=2, legend='',
                                  markertype=GRMARKS['diagonalcross'])]
        self.axes.addCurves(self._curves[0])
        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)

    def setPlotData(self, x, y):
        self._curves[0].x = array(x)
        self._curves[0].y = array(y)

        self.make_xticks()
        self.update()
        self.reset()

    def resetView(self):
        self.axes.setWindow(self._curves[0].x[0], self._curves[0].x[-1],
                            self._curves[0].y[0], self._curves[0].y[-1])
        self.rescale()

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
    dformat = "%Y-%m-%d %H:%M:%S.%f"
    numPts = 20  # only relevant for Amplitude and Phase

    def __init__(self, parent, client, options):
        super().__init__(parent, client, options)
        loadUi(self, findResource('nicos_jcns/seop/gui/seopplot.ui'))
        opts = options.get('plotconf', {})
        self.command = options.get('command')
        self.statusBar = QStatusBar(self)
        self.layout().addWidget(self.statusBar)
        self.xtime = options.get('xtime', False)
        self.plot = SeopPlot(parent=self.widget, timeaxis=self.xtime, **opts)
        self.widget.layout().addWidget(self.plot)
        self.plot.setSizePolicy(QSizePolicy.Policy.Expanding,
                                QSizePolicy.Policy.Expanding)
        self.plot.gr.cbm.addHandler(MouseEvent.MOUSE_MOVE, self.on_mouseMove)
        if not self.xtime:
            self.numPtsEdit.setEnabled(False)
            self.setNumPtsButton.setEnabled(False)

        cache = self.client.getCacheKey("nmr/value")
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
        self.plot.resetView()

    def on_mouseMove(self, event):
        if event.getWindow():  # inside plot
            self.mouselocation = event
            wc = event.getWC(self.plot.plot.viewport)
            self.statusBar.showMessage("X = %g, Y = %g" % (wc.x, wc.y))
        else:
            self.statusBar.clearMessage()

    def on_setNumPtsButton_pressed(self):
        try:
            self.numPts = int(self.numPtsEdit.text())
        except ValueError:
            self.log.warning('Invalid value for log points!')
        else:
            self.update_plot()


class SeopSettingsTreeItem(QTreeWidgetItem):
    def __init__(self, cfgkey, strings):
        super().__init__(strings)
        self.cfgkey = cfgkey

    def setData(self, column, role, value):
        super().setData(column, role, value)


class SeopSettingsPanel(Panel):
    """Tree displaying all settings available to the seop system."""
    panelName = 'NMR Settings'

    def __init__(self, parent, client, options):
        super().__init__(parent, client, options)
        loadUi(self, findResource('nicos_jcns/seop/gui/seopsettings.ui'))
        self.configTree.itemDoubleClicked.connect(self.treeItemDoubleClicked)
        self.configTree.itemChanged.connect(self.setConfigData)
        client.connected.connect(self.on_client_connected)

    def on_client_connected(self):
        self._load_config()

    def _load_config(self):
        self.configTree.clear()
        cfg = self.client.eval('cell.raw_config_file()', None)
        if not cfg:
            return
        config = yaml.safe_load(cfg)
        for k, v in config.items():
            t = self._make_tree(k, k, v)
            self.configTree.addTopLevelItem(t)

        self.configTree.expandAll()
        for i in range(self.configTree.columnCount()):
            self.configTree.resizeColumnToContents(i)

    def _make_tree(self, path, key, config):
        if not isinstance(config, dict):
            cfgItem = SeopSettingsTreeItem(path, [key, str(config)])
            cfgItem.setFlags(cfgItem.flags() | Qt.ItemFlag.ItemIsEditable)
            # cfgItem.changed.connect(self.setConfigData)
            return cfgItem
        tree = SeopSettingsTreeItem(path, [key])
        for k, v in config.items():
            tree.addChild(self._make_tree('/'.join((path, k)), k, v))
        return tree

    def treeItemDoubleClicked(self, item, column):
        if column != 1:
            return
        self.configTree.editItem(item, column)

    def setConfigData(self, item, column):
        if column != 1:
            return
        data = item.data(1, Qt.ItemDataRole.DisplayRole)
        self.client.run(f"cell.cfg_set('{item.cfgkey}', '{data}')")

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
        parent.layout().setSizeConstraint(QLayout.SetFixedSize)
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
