#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

__version__ = "$Revision$"

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
            #pylint: disable=E1102
            return self.widget_class(parent, designMode=True)
        except Exception, e:
            name = self.widget_class.__name__
            print "Designer plugin error creating %s: %s" % (name, str(e))
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
        name = str(self.name())
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


from nicos.guisupport.display import ValueDisplay
from nicos.guisupport.led import StatusLed, ValueLed
from nicos.guisupport.plots import TrendPlot


for cls in [ValueDisplay, StatusLed, ValueLed, TrendPlot]:
    class Plugin(NicosPluginBase):  #pylint: disable=R0923
        widget_class = cls
    Plugin.__name__ = cls.__name__ + 'Plugin'
    globals()[Plugin.__name__] = Plugin


del NicosPluginBase
