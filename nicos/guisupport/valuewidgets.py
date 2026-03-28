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
#   Artur Glavic <artur.glavic@psi.ch>
#
# *****************************************************************************

"""
Widget for Qt Monitor that display values graphically.
"""

from math import cos, log10, pi, sin
from time import time as currenttime

from nicos.guisupport.qt import QBrush, QColor, QFontMetrics, \
    QGraphicsDropShadowEffect, QGraphicsScene, QGraphicsView, QLabel, \
    QPainter, QPen, QPointF, QProgressBar, QRadialGradient, QSize, \
    QSizePolicy, Qt, QVBoxLayout, QWidget
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.guisupport.display import defaultColorScheme


class AlternativeValueBase(NicosWidget):
    """
    Base class for other widgets that display a value in a graphical way.
    """
    dev = PropDef('dev', str, '', 'NICOS device name, if set, display '
                  'value of this device')
    key = PropDef('key', str, '', 'Cache key to display (without "nicos/"'
                  ' prefix), set either "dev" or this')
    statuskey = PropDef('statuskey', str, '', 'Cache key to extract status '
                        'information  for coloring value, if "dev" is '
                        'given this is set automatically')
    name = PropDef('name', str, '', 'Name of the value to display')
    unit = PropDef('unit', str, '', 'Unit of the value to display')
    fmtstr = PropDef('format', str, '', 'Python format string to use for the '
                     'value; if "dev" is given this defaults to the '
                     '"fmtstr" set in NICOS')
    width = PropDef('width', int, 8, 'Width of the widget in units of the '
                    'width of one character')
    height = PropDef('height', int, 8, 'Height of the widget in units of the '
                     'width of one character')
    start_value = PropDef('start_value', float, 0., 'Lowest value for display')
    end_value = PropDef('end_value', float, 100., 'Highest value for display')

    def __init__(self, colorScheme=None):
        NicosWidget.__init__(self)
        self._colorscheme = colorScheme or defaultColorScheme

    def registerKeys(self):
        if self.props['dev']:
            self.registerDevice(self.props['dev'],
                                self.props['unit'], self.props['fmtstr'])
        else:
            self.registerKey(self.props['key'], self.props['statuskey'],
                             self.props['unit'], self.props['fmtstr'])

    def propertyUpdated(self, pname, value):
        if pname == 'dev':
            if value:
                self.key = value + '.value'
                self.statuskey = value + '.status'
        elif pname == 'width':
            if value > 0:
                curheight = self.minimumSize().height()
                onechar = QFontMetrics(self.valueFont).horizontalAdvance('0')
                self.setMinimumSize(QSize(round(onechar * (value + .5)), curheight))
        elif pname == 'height':
            if value > 0:
                curwidth = self.minimumSize().width()
                onechar = QFontMetrics(self.valueFont).horizontalAdvance('0')
                self.setMinimumSize(QSize(curwidth, round(onechar * (value + .5))))
        NicosWidget.propertyUpdated(self, pname, value)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        # check expired values
        self._expired = expired
        self._lastvalue = value
        self._lastchange = currenttime()

        self.doUpdateValue()

    def doUpdateValue(self):
        raise NotImplementedError(
            'Must subclass AlternativeValueBase with this method implemented.')


class ValueProgressBar(AlternativeValueBase, QWidget):
    """A Progressbar to display a value."""

    def __init__(self, parent, designMode=False, colorScheme=None, **kwds):
        AlternativeValueBase.__init__(self, colorScheme)
        QWidget.__init__(self, parent, **kwds)

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.label = QLabel(self)
        vbox.addWidget(self.label)
        self.pbar = QProgressBar(self)
        vbox.addWidget(self.pbar)
        self.pbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.pbar.setMinimumSize(2, 2)

        self.setNameLabel(self.name)
        self.pbar.setValue(50)
        self.pbar.setTextVisible(True)

    def propertyUpdated(self, pname, value):
        AlternativeValueBase.propertyUpdated(self, pname, value)
        if pname == 'name':
            self.setNameLabel(value)

    def setNameLabel(self, value):
        if value:
            self.label.setText(value)
            self.label.show()
        else:
            self.label.hide()

    def doUpdateValue(self):
        value = self._lastvalue
        perc = int(100.*(value - self.props['start_value']) / (
            self.props['end_value'] - self.props['start_value']))
        self.pbar.setValue(max(0, min(100, perc)))
        self.pbar.setToolTip(self.props['dev']+' = '+f'{value:.3f}')

        self.setDisabled(self._expired)


class ValueGauge(AlternativeValueBase, QGraphicsView):
    """An analogue Gauge type display for the value."""

    start_angle = PropDef('start_angle', float, -120,
                          'Location of first tick, 0 is top')
    end_angle = PropDef('end_angle', float, 120.,
                        'Location of last tick, 0 is top')
    ticks = PropDef('ticks', int, 5,
                    'Number of tick-lines with values to draw')
    log_values = PropDef('log_values', bool, 0,
                         'Show values logarithmically')
    status_led = PropDef('status_led', bool, 0,
                         'Show LED status indicator')
    background_color = PropDef('background_color', str, '#ffffff')
    inlay_color = PropDef('inlay_color', str, '#ee0000')
    boundary_color = PropDef('boundary_color', str, '#000000')

    def __init__(self, parent, designMode=False, colorScheme=None, **kwds):
        AlternativeValueBase.__init__(self, colorScheme)
        QGraphicsView.__init__(self, parent, **kwds)

        for pname in ['start_angle', 'end_angle', 'ticks']:
            setattr(self, '_'+pname, self.props[pname])

        self.setStyleSheet('background: transparent; border: transparent;')
        self.setGeometry(-100, -100, 200, 200)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(-100, -100, 200, 200)
        self.setRenderHint(QPainter.Antialiasing)

        self._draw_background()
        self._draw_arrow()
        self._draw_LED()
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def getShadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(QPointF(2, 5))
        shadow.setBlurRadius(5)
        return shadow

    def propertyUpdated(self, pname, value):
        AlternativeValueBase.propertyUpdated(self, pname, value)
        if pname in ['start_angle', 'end_angle', 'ticks', 'start_value',
                     'end_value', 'name', 'background_color', 'inlay_color',
                     'boundary_color', 'log_values']:
            setattr(self, '_'+pname, value)
            self.scene.clear()
            self._draw_background()
            self._draw_arrow()
            self._draw_LED()

    def sizeHint(self):
        return self.minimumSize()

    def _draw_background(self):
        s = self.scene
        bg = QColor(self.background_color)

        frame = s.addEllipse(-90, -90, 180, 180,
                             pen=QPen(QColor(self.boundary_color), 5))
        frame.setGraphicsEffect(self.getShadow())
        frame.setZValue(10)
        s.addEllipse(-89, -89, 178, 178, brush=QBrush(bg))
        # Add a glass-like reflection effect to make it look more 3D
        glass_effect = QRadialGradient(-35, -45, 40)
        glass_effect.setColorAt(0, QColor(255, 255, 255, 255))
        glass_effect.setColorAt(1, QColor(0, 0, 0, 25))
        s.addEllipse(-87, -87, 174, 174, brush=QBrush(glass_effect)).setZValue(20)

        ticks = self._ticks
        start = self._start_angle
        end = self._end_angle
        rin = 60
        rout = 80
        ravg = (rout+rin)//2

        # draw a colored line below the ticks
        bar = s.addEllipse(-ravg, -ravg, 2*ravg, 2*ravg,
                           pen=QPen(QColor(self.inlay_color), 5))
        bar.setStartAngle(16*int(-end+90))
        bar.setSpanAngle(16*int(end-start))
        bar.setZValue(2)
        angle = start*pi/180
        x2 = rout*sin(angle)
        y2 = -rout*cos(angle)
        s.addLine(0, 0, x2, y2, pen=QPen(bg, 6)).setZValue(3)
        angle = end*pi/180
        x2 = rout*sin(angle)
        y2 = -rout*cos(angle)
        s.addLine(0, 0, x2, y2, pen=QPen(bg, 6)).setZValue(3)

        rtxt = 45
        val_start = self.start_value
        val_end = self.end_value
        val_range = val_end - val_start
        if self.log_values:
            lstart = log10(val_start or 1.)
            lend = log10(val_end)
            lrange = lend-lstart
        for ti in range(ticks):
            angle = (start + ti/(ticks-1) * (end-start))*pi/180.
            x1 = rin*sin(angle)
            x2 = rout*sin(angle)
            y1 = -rin*cos(angle)
            y2 = -rout*cos(angle)
            s.addLine(x1, y1, x2, y2, pen=QPen(QColor(0, 0, 0, 255), 2)).setZValue(4)

            if self.log_values:
                val = 10**(lstart+lrange*ti/(ticks-1))
                txt = s.addText('%g' % (val))
            else:
                txt = s.addText('%g' % (val_start + val_range*ti/(ticks-1)))
            txt.setZValue(4)
            txt.setPos(rtxt*sin(angle)-txt.boundingRect().width()//2,
                       -rtxt*cos(angle)-txt.boundingRect().height()//2)

        if self.unit and self.name:
            txt = s.addText(f'{self.name} / {self.unit}')
        elif self.name:
            txt = s.addText(f'{self.name}')
        elif self.unit:
            txt = s.addText(f'{self.unit}')

        txt.setZValue(5)
        txt.setScale(1.5)
        ho = int(txt.boundingRect().width()*1.5/2)
        vo = int(txt.boundingRect().height()*1.5/2)
        if start < -150 or end > 150:
            txt.setPos(-ho, -25-vo)
        else:
            txt.setPos(-ho, 60-vo)

    def _draw_arrow(self):
        s = self.scene
        self.arrow = s.addLine(0, 20, 0, -82, pen=QPen(QColor(0, 0, 0, 255), 4))
        self.arrow.setRotation(self._start_angle)
        self.arrow.setZValue(10)
        self.arrow.setGraphicsEffect(self.getShadow())

        s.addEllipse(-10, -10, 20, 20,
                     pen=QPen(QColor(0, 0, 0, 255), 2), brush=QBrush(QColor(0, 0, 0, 255))
                     ).setZValue(15)

    def _draw_LED(self):
        if not self.status_led:
            return
        # Indicator for device status
        self.led = self.scene.addEllipse(
            -25, 30, 16, 16, pen=QPen(QColor(self.boundary_color), 2),
            brush=QBrush(QColor(30, 20, 20)))
        self.led.setZValue(4)

    def doUpdateValue(self):
        if self.log_values:
            lstart = log10(self.start_value or 1.)
            lend = log10(self.end_value)
            lvalue = log10(self._lastvalue or self.start_value or 1.)
            fraction = min(1., max(0., (lvalue - lstart) / (lend - lstart)))
        else:
            fraction = min(1., max(0., (self._lastvalue - self.start_value) /
                                   (self.end_value - self.start_value)))
        if self._expired:
            angle = 180.
        else:
            angle = self.start_angle+(self.end_angle-self._start_angle)*fraction

        self.arrow.setRotation(angle)
        self.setToolTip(self.dev+' = '+f'{self._lastvalue:.3f}')
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def on_devStatusChange(self, dev, code, status, expired):
        if not self.status_led:
            return
        self.led.setBrush(QBrush(self._colorscheme['fore'][code]))
