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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI config helpers."""

from nicos.clients.gui.utils import SettingGroup
from nicos.pycompat import exec_


class hsplit(tuple):
    def __new__(cls, *children, **options):
        return tuple.__new__(cls, (children, options))

    def __init__(self, *args, **kw):  # pylint: disable=super-init-not-called
        self.children = self[0]
        self.options = self[1]


class vsplit(tuple):
    def __new__(cls, *children, **options):
        return tuple.__new__(cls, (children, options))

    def __init__(self, *args, **kw):  # pylint: disable=super-init-not-called
        self.children = self[0]
        self.options = self[1]


class tabbed(tuple):
    def __new__(cls, *children):
        return tuple.__new__(cls, children)


class docked(tuple):
    def __new__(cls, mainitem, *dockitems):
        return tuple.__new__(cls, (mainitem, dockitems))


class window(tuple):
    def __new__(cls, *args):
        assert len(args) == 3
        return tuple.__new__(cls, args)

    def __init__(self, *args):  # pylint: disable=super-init-not-called
        self.name = self[0]
        self.icon = self[1]
        self.contents = self[2]


class panel(tuple):
    def __new__(cls, clsname, **options):
        return tuple.__new__(cls, (clsname, options))

    def __init__(self, *args, **kw):  # pylint: disable=super-init-not-called
        self.clsname = self[0]
        self.options = self[1]


class tool(tuple):
    def __new__(cls, name, clsname, **options):
        return tuple.__new__(cls, (name, clsname, options))

    def __init__(self, *args, **kw):  # pylint: disable=super-init-not-called
        self.name = self[0]
        self.clsname = self[1]
        self.options = self[2]


class cmdtool(tuple):
    def __new__(cls, name, cmdline):
        return tuple.__new__(cls, (name, cmdline))

    def __init__(self, *args):  # pylint: disable=super-init-not-called
        self.name = self[0]
        self.cmdline = self[1]


class menu(tuple):
    def __new__(cls, name, *items):
        return tuple.__new__(cls, (name, items))

    def __init__(self, *args):  # pylint: disable=super-init-not-called
        self.name = self[0]
        self.items = self[1]


class gui_config(object):
    def __init__(self, main_window, windows, tools, name, options):
        self.main_window = main_window
        self.windows = windows
        self.tools = tools
        self.name = name
        self.options = options

    def _has_panel(self, config, panel_classes):
        """Return True if the config contains a panel with the given class."""
        if isinstance(config, window):
            return self._has_panel(config.contents, panel_classes)
        elif isinstance(config, (hsplit, vsplit)):
            for child in config:
                if self._has_panel(child, panel_classes):
                    return True
        elif isinstance(config, panel):
            return config.clsname in panel_classes
        elif isinstance(config, tabbed):
            return any(self._has_panel(child[1], panel_classes)
                       for child in config)
        elif isinstance(config, docked):
            if self._has_panel(config[0], panel_classes):
                return True
            return any(self._has_panel(child[1], panel_classes)
                       for child in config[1])

    def find_panel(self, panel_classes):
        if self._has_panel(self.main_window, panel_classes):
            return -1
        for i, winconfig in enumerate(self.windows):
            if self._has_panel(winconfig, panel_classes):
                return i


def prepareGuiNamespace():
    ns = {}
    ns['vsplit'] = vsplit
    ns['hsplit'] = hsplit
    ns['window'] = window
    ns['panel'] = panel
    ns['tool'] = tool
    ns['cmdtool'] = cmdtool
    ns['menu'] = menu
    ns['docked'] = docked
    ns['tabbed'] = tabbed
    ns['options'] = {}
    return ns


def processGuiConfig(configcode):
    ns = prepareGuiNamespace()
    exec_(configcode, ns)
    gui_conf = gui_config(ns['main_window'], ns.get('windows', []),
                          ns.get('tools', []), ns.get('name', 'NICOS'),
                          ns.get('options', {}))
    if gui_conf.name != 'NICOS':
        SettingGroup.global_group = gui_conf.name
    return gui_conf
