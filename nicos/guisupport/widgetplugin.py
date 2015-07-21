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
#
# *****************************************************************************

"""
Qt designer plugin for NICOS UI widgets.
"""
from __future__ import print_function

# need to repeat that here, since the Designer runs this file without importing
# nicos.guisupport first.
import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

import os

from PyQt4.QtGui import QIcon
from PyQt4.QtDesigner import QPyDesignerCustomWidgetPlugin


class NicosPluginBase(QPyDesignerCustomWidgetPlugin):

    widget_class = None
    widget_icon = None
    widget_description = None

    def __init__(self, parent=None):
        QPyDesignerCustomWidgetPlugin.__init__(self)
        self._initialized = False

    # methods from QDesignerCustomWidgetInterface

    def initialize(self, formEditor):
        if self.isInitialized():
            return
        self._initialized = True

    def isInitialized(self):
        return self._initialized

    def createWidget(self, parent):
        try:
            # pylint: disable=E1102
            return self.widget_class(parent, designMode=True)
        except Exception as e:
            name = self.widget_class.__name__
            print("Designer plugin error creating %s: %s" % (name, e))
            return None

    def name(self):
        return self.widget_class.__name__

    def group(self):
        return 'NICOS'

    def icon(self):
        if self.widget_class.designer_icon is None:
            return QIcon()
        return QIcon(self.widget_class.designer_icon)

    def domXml(self):
        name = self.name()
        lowerName = name[0].lower() + name[1:]
        return '<widget class="%s" name="%s" />\n' % (name, lowerName)

    def includeFile(self):
        return self.widget_class.__module__

    def toolTip(self):
        return self.widget_class.designer_description or self.name()

    def whatsThis(self):
        return self.widget_class.designer_description or self.name()

    def isContainer(self):
        return False


from nicos.guisupport.widget import NicosWidget

# imported for side effects
from nicos.guisupport import display, led, button, typedvalue, containers  # pylint: disable=W0611
try:
    from nicos.guisupport import plots  # pylint: disable=W0611
except (ImportError, RuntimeError):
    # Qwt may be missing
    pass

# import other modules to make their widgets known to __subclasses__()
for addmod in os.environ.get('NICOSDESIGNER_MODULES', '').split(':'):
    if addmod:
        __import__(addmod)


def _register(cls):
    if cls.designer_description:
        class Plugin(NicosPluginBase):
            widget_class = cls
        Plugin.__name__ = cls.__name__ + 'Plugin'
        globals()[Plugin.__name__] = Plugin
        # print 'Registered', Plugin.__name__
    for subcls in cls.__subclasses__():
        _register(subcls)

_register(NicosWidget)

del NicosPluginBase
