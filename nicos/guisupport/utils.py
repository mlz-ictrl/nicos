#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""GUI support utilities."""

import re
import fnmatch

from PyQt4.QtGui import QPalette, QValidator, QDoubleValidator


def setBackgroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    palette.setColor(QPalette.Base, color)
    widget.setBackgroundRole(QPalette.Window)
    widget.setPalette(palette)


def setForegroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.WindowText, color)
    palette.setColor(QPalette.Text, color)
    widget.setForegroundRole(QPalette.WindowText)
    widget.setPalette(palette)


def setBothColors(widget, colors):
    palette = widget.palette()
    palette.setColor(QPalette.WindowText, colors[0])
    palette.setColor(QPalette.Window, colors[1])
    palette.setColor(QPalette.Base, colors[1])
    widget.setBackgroundRole(QPalette.Window)
    widget.setForegroundRole(QPalette.WindowText)
    widget.setPalette(palette)


class DoubleValidator(QDoubleValidator):

    def validate(self, string, pos):
        if ',' in string:
            return QValidator.Invalid, string, pos
        return QDoubleValidator.validate(self, string, pos)


keyexpr_re = re.compile(r'(?P<dev_or_key>[a-zA-Z_0-9./]+)'
                        r'(?P<indices>(?:\[[0-9]+\])*)'
                        r'(?P<scale>\*[0-9.]+)?'
                        r'(?P<offset>[+-][0-9.]+)?$')


def extractKeyAndIndex(spec):
    """Extract a key and possibly subindex from a cache key specification
    given by the user.  This takes into account the following changes:

    * '/' can be replaced by '.'
    * If it is not in the form 'dev/key', '/value' is automatically appended.
    * Subitems can be specified: ``dev.keys[10], det.rates[0][1]``.
    * A scale factor can be added with ``*X``.
    * An offset can be added with ``+X`` or ``-X``.
    """
    match = keyexpr_re.match(spec.replace(' ', ''))
    if not match:
        return spec.lower().replace('.', '/'), (), 1.0, 0
    groups = match.groupdict()
    key = groups['dev_or_key'].lower().replace('.', '/')
    if '/' not in key:
        key += '/value'
    indices = groups['indices']
    try:
        if indices is not None:
            indices = tuple(map(int, indices[1:-1].split('][')))
        else:
            indices = ()
    except ValueError:
        indices = ()
    scale = groups['scale']
    try:
        scale = float(scale[1:]) if scale is not None else 1.0
    except ValueError:
        scale = 1.0
    offset = groups['offset']
    try:
        offset = float(offset) if offset is not None else 0.0
    except ValueError:
        offset = 0.0
    return key, indices, scale, offset


def checkSetupSpec(setupspec, setups, compat='or', log=None):
    """Check if the given setupspec should be displayed given the loaded setups.
    """
    def fixup_old(s):
        if s.startswith('!'):
            return 'not %s' % s[1:]
        return s

    def subst_setupexpr(match):
        if match.group() in ('has_setup', 'and', 'or', 'not'):
            return match.group()
        return 'has_setup(%r)' % match.group()

    def has_setup(spec):
        return bool(fnmatch.filter(setups, spec))

    if not setupspec:
        return True  # no spec -> always visible
    if not setups:
        return False  # no setups -> not visible (safety)
    if isinstance(setupspec, list):
        setupspec = (' %s ' % compat).join(fixup_old(v) for v in setupspec)
    if setupspec.startswith('!'):
        setupspec = fixup_old(setupspec)
    expr = re.sub(r'[\w\[\]*?]+', subst_setupexpr, setupspec)
    ns = {'has_setup': has_setup}
    try:
        return eval(expr, ns)
    except Exception:  # wrong spec -> visible
        if log:
            log.warning('invalid setup spec: %r' % setupspec)
        return True
