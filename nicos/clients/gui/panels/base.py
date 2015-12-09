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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""Support for "auxiliary" windows containing panels."""

from time import time as currenttime

from PyQt4.QtGui import QWidget, \
    QHBoxLayout, QDialog, QPalette
from PyQt4.QtCore import QObject, pyqtSignal

from nicos.utils.loggers import NicosLogger
from nicos.clients.gui.utils import DlgUtils, SettingGroup
from nicos.guisupport.utils import checkSetupSpec
from nicos.clients.gui.config import panel


class SetupDepWindowMixin(QObject):
    def __init__(self, client):
        if client._reg_keys:
            values = client.ask('getcachekeys', ','.join(client._reg_keys))
            if values is not None:
                currtime = currenttime()
                for key, value in values:
                    if key == 'session/mastersetup':
                        for widget in client._reg_keys[key]:
                            if widget():
                                widget().on_keyChange(key, value, currtime,
                                                      False)


class PanelDialog(SetupDepWindowMixin, QDialog):
    def __init__(self, parent, client, panelcfg, title):
        from nicos.clients.gui.panels.utils import createWindowItem
        self.panels = []
        QDialog.__init__(self, parent)
        self.mainwindow = parent.mainwindow
        self.log = NicosLogger('PanelDialog')
        self.log.parent = self.mainwindow.log
        self.client = client
        self.user_color = self.palette().color(QPalette.Base)
        self.user_font = self.font()
        if isinstance(panelcfg, type) and issubclass(panelcfg, Panel):
            panelcfg = panel('%s.%s' % (panelcfg.__module__,
                                        panelcfg.__name__))
        elif isinstance(panelcfg, str):
            panelcfg = panel(panelcfg)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        pnl = createWindowItem(panelcfg, self, self, self.mainwindow, self.log)
        if pnl:
            hbox.addWidget(pnl)
        self.setLayout(hbox)
        self.setWindowTitle(title)
        SetupDepWindowMixin.__init__(self, self.client)


class SetupDepPanelMixin(QObject):
    ''' Mixin to handle setup-dependent visibility

    Note: You must explicity add the following class attribute in all
    classes using this mixin (A PyQt resctriction, see
    https://riverbankcomputing.com/pipermail/pyqt/2013-September/033199.html):

    `setWidgetVisible = SetupDepPanelMixin.setWidgetVisible`

    '''
    setupSpec = ()
    setWidgetVisible = pyqtSignal(QWidget, bool, name='setWidgetVisible')

    def __init__(self, client):
        client.register(self, 'session/mastersetup')

    def setOptions(self, options):
        setups = options.get('setups', '')
        if not isinstance(setups, str):
            setups = list(setups)
        self.setSetups(setups)

    def setSetups(self, setupSpec):
        self.setupSpec = setupSpec
        self.log.debug('Setups are : %r' % self.setupSpec)

    def on_keyChange(self, key, value, time, expired):
        if key == 'session/mastersetup' and self.setupSpec:
            if hasattr(self, 'setWidgetVisible'):
                enabled = checkSetupSpec(self.setupSpec, value, log=self.log)
                self.setWidgetVisible.emit(self, enabled)


class Panel(QWidget, SetupDepPanelMixin, DlgUtils):
    panelName = ''

    setWidgetVisible = SetupDepPanelMixin.setWidgetVisible

    def __init__(self, parent, client):
        QWidget.__init__(self, parent)
        self.log = NicosLogger(self.panelName)
        SetupDepPanelMixin.__init__(self, client)
        DlgUtils.__init__(self, self.panelName)
        self.parentwindow = parent
        self.client = client
        self.mainwindow = parent.mainwindow
        self.actions = set()
        self.log.parent = self.mainwindow.log
        self.sgroup = SettingGroup(self.panelName)
        with self.sgroup as settings:
            self.loadSettings(settings)

    def postInit(self):
        """This method can be implemented to perform actions after all panels
        has been instantiated. It will be automatically called after all panels
        has been created. This can be useful e.g. for accessing other panels
        using their unique ``panelName``.

        """

    def setExpertMode(self, expert):
        pass

    def setViewOnly(self, viewonly):
        pass

    def loadSettings(self, settings):
        pass

    def saveSettings(self, settings):
        pass

    def setCustomStyle(self, font, back):
        pass

    def getToolbars(self):
        return []

    def getMenus(self):
        return []

    def hideTitle(self):
        """Called when the panel is shown in a dock or tab widget, which
        provides its own place for the panel title.

        If the panel has a title widget, it should hide it in this method.
        """
        pass

    def requestClose(self):
        return True

    def updateStatus(self, status, exception=False):
        pass
