#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Michael Hart <michael.hart@stfc.ac.uk>
#
# *****************************************************************************

"""Mantid Instrument View Panel."""

try:
    import mantid.simpleapi as simpleapi  # pylint: disable=import-error
    import mantidqtpython as mpy  # pylint: disable=import-error
except ImportError:
    simpleapi = None
    mpy = None


import os

from PyQt4.QtGui import QHBoxLayout, QWidget

from nicos.clients.gui.panels import Panel
from nicos.guisupport.widget import NicosWidget


class MantidDeviceWatcher(NicosWidget, QWidget):
    """
    Updates the instrument view when device values change.

    Observes devices that derive from MantidDevice and makes attached
    InstrumentViewPanel update its view accordingly.
    """

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)
        self._algorithm_map = {}

    def registerKeys(self):
        # All currently loaded devices that inherit from MantidDevice
        mantid_devs = self.parent().client.getDeviceList(
            'nicos_demo.mantid.devices.devices.MantidDevice',
            only_explicit=False
        )

        # Clear map when setup changes
        self._algorithm_map = {}
        for dev in mantid_devs:
            # Algorithm names won't change, so we can cache them
            self._algorithm_map[dev] = self.parent().client.getDeviceParam(
                dev, 'algorithm')
            self.registerDevice(dev)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        alg_name = self._algorithm_map[dev]
        self.parent().invoke_algorithm(alg_name, value)


class InstrumentViewPanel(Panel):
    """
    Mantid InstrumentView widget as a NICOS Panel.

    Displays 3D view of instrument using the Mantid InstrumentView widget,
    based on Instrument Definition File and MantidDevices configured in setup.
    """

    panelName = 'Instrument View'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)

        if not simpleapi or not mpy:
            raise RuntimeError('Mantid modules could not be imported. '
                               'Ensure Mantid is installed and PYTHONPATH is '
                               'set to contain the Mantid /bin directory.')

        hbox = QHBoxLayout(self)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        self._watcher = MantidDeviceWatcher(self)
        self._widget = None
        self._workspace = None
        self._current_idf = None

    def invoke_algorithm(self, alg, params):
        """
        Execute algorithm against workspace to update view according to
        updated device values.

        :type  alg: str
        :param alg: Name of Mantid algorithm to invoke
        :type  params: dict
        :param params: Parameters to pass to algorithm
        """
        getattr(simpleapi, alg)(Workspace=self._workspace, **params)

    def _get_setup_idf(self):
        """
        Return the absolute path name of the IDF defined by the current setup.

        :return: Full path and file name of IDF
        """
        idf_name = self.client.eval('session.instrument.idf', None)

        # TODO: Support for IDFs outside of Mantid Instrument Directory?
        if idf_name is not None:
            idf_path = simpleapi.ConfigService.getInstrumentDirectory()
            return os.path.join(idf_path, idf_name)

        return None

    def updateStatus(self, status, exception=False):
        if status == 'idle':
            new_idf = self._get_setup_idf()
            if new_idf != self._current_idf:
                self._load_idf(new_idf)

    def _load_idf(self, new_idf):
        # The widget self-destructs when you delete the workspace below, for
        # some reason, so let's remove it cleanly first.
        if self._widget is not None:
            self.layout().removeWidget(self._widget)
            self._widget = None

        # If you don't do this there is an Unhandled Exception, which crashes
        # NICOS completely, when you try to switch setups, with a message of:
        # > Instrument view: workspace doesn't exist
        if self._workspace is not None:
            simpleapi.DeleteWorkspace("ws")
            self._workspace = None

        if new_idf is not None:
            self._workspace = simpleapi.LoadEmptyInstrument(
                new_idf, OutputWorkspace="ws")
            self._widget = mpy.MantidQt.MantidWidgets.InstrumentWidget(
                "ws", self)
            self.layout().addWidget(self._widget)
            self._watcher.setClient(self.client)

        self._current_idf = new_idf
