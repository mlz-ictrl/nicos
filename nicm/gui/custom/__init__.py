#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   Customization for the NICM GUI
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""Customization for the NICM GUI."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import sys

from PyQt4.QtCore import QSettings

customizations = [
    fn[:-3] for fn in os.listdir(os.path.dirname(__file__))
    if fn.lower().endswith('.py') and fn[:1] != '_'
]

customization_loaded = False

def has_customization(cname):
    return cname in customizations

def list_customizations():
    return customizations

def load_customization():
    global customization_loaded
    if customization_loaded:
        return
    settings = QSettings('frm2', 'nicmv2')
    settings.beginGroup('MainWindow')
    cname = str(settings.value('customname').toString()) or 'mira'
    if cname not in customizations:
        print 'Customization %r not available, using empty' % cname
        cname = 'empty'
    load_custom_module(cname)
    customization_loaded = True

def load_custom_module(name):
    __import__('nicm.gui.custom.' + name)
    me = sys.modules[__name__]
    it = sys.modules['nicm.gui.custom.' + name]
    me.__dict__.update(it.__dict__)
