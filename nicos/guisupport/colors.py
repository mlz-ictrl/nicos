# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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

from nicos.guisupport.qt import QColor, QPalette, Qt


def is_light_theme(palette):
    background = palette.window().color().lightness()
    foreground = palette.windowText().color().lightness()
    return background > foreground


class ColorStorage:
    """
    Central color definitions.

    With Qt 6.5, the enum QStyleHints::colorScheme and the signal
    QStyleHints::colorSchemeChanged will be introduced. When moving to that
    version, this class can be changed to use these instead of is_light_template.
    """
    def init_palette(self, palette):
        """Define standard colors."""
        self.palette = palette

        # shortcuts to commonly used palette colors
        self.base = self.palette.color(QPalette.ColorGroup.Active,
                                       QPalette.ColorRole.Base)
        self.text = self.palette.color(QPalette.ColorGroup.Active,
                                       QPalette.ColorRole.WindowText)

        # unchanging colors
        self.transparent = Qt.GlobalColor.transparent
        self.lowlevel = QColor('#666666')
        self.is_light = is_light_theme(palette)

        def sw(light, dark):
            return QColor(light if self.is_light else dark)

        # device tree
        self.dev_fg_ok = sw('#00aa00', '#00dd00')
        self.dev_fg_unknown = sw('#cccccc', '#777777')
        self.dev_bg_warning = sw('#ffa500', '#ffa500')
        self.dev_bg_busy = sw(Qt.GlobalColor.yellow, '#c2cc00')
        self.dev_bg_error = sw('#ff6655', '#c72514')
        self.dev_bg_disabled = sw('#bbbbbb', self.base.lighter(130))

        # value expired and  fixed
        self.value_fixed = sw(Qt.GlobalColor.blue, '#305eb3')
        self.value_expired = sw('#aaaaaa', '#444444')

        # Command Line
        self.cmd_running = sw('#ffdddd', '#d4af37')
        self.cmd_inactive = sw('#c9c9c9', '#444444')

        # Cmdlets
        self.invalid = sw('#ffcccc', '##e6320f')

        # CacheInspector
        self.ttl_color = sw('#fffa66', '#ff8f00')
        self.expired_color = sw('#ce9b9b', '#674e4e')

    def switch_color(self, light, dark):
        """switch for locally defined colors that do not make sense to be
        included here."""
        return light if self.is_light else dark


colors = ColorStorage()
