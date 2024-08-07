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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

from os import path

from nicos.clients.gui.panels.devices import DEVICE_TYPE, DevicesPanel
from nicos.clients.gui.panels.generic import GenericPanel
from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, \
    WARN, statuses
from nicos.core.utils import ACCESS_LEVELS, GUEST
from nicos.guisupport.colors import colors
# pylint: disable=no-name-in-module
from nicos.guisupport.qt import QBrush, QColorConstants, QLinearGradient, \
    QPainter, QPen, QPixmap, QPointF, QRectF, Qt, QTextOption, \
    QTreeWidgetItem, QWidget
# pylint: enable=no-name-in-module
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.utils import AttrDict

SENSOR_ICON = dict(T='thermometer', P='gauge-meter', MF='gauge-meter')
MAX_WATER_LEVEL = 0.5


class Panel(GenericPanel):

    panelName = 'TMR Cooling System'

    def __init__(self, parent, client, options):
        options['uifile'] = 'nicos_jcns/tmr/gui/coolingsystem.ui'
        GenericPanel.__init__(self, parent, client, options)

    def paintEvent(self, event):
        GenericPanel.paintEvent(self, event)
        # background
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(QColorConstants.Svg.silver)
        qp.drawRect(0, 0, qp.window().width() - 1, qp.window().height() - 1)
        qp.end()


class Widget(NicosWidget, QWidget):

    designer_description = 'TMR cooling system'

    globe_valves = PropDef('globe_valves', 'QStringList',
                           [f'hv{i:02d}' for i in range(1, 6)])
    pumps = PropDef('pumps', 'QStringList',
                    [f'mp{i:02d}' for i in range(1, 3)])
    mf_sensors = PropDef('mf_sensors', 'QStringList',
                         [f'mf{i:02d}' for i in range(1, 3)])
    p_sensors = PropDef('p_sensors', 'QStringList',
                        [f'p{i:02d}' for i in range(1, 6)])
    t_sensors = PropDef('t_sensors', 'QStringList',
                        [f't{i:02d}' for i in range(1, 6)])
    conductance_sensor = PropDef('conductance_sensor', str, 'sc')
    level_sensor = PropDef('level_sensor', str, 'sf01')
    ph_sensor = PropDef('ph_sensor', str, 'sp')

    def __init__(self, parent, _designMode=False):
        QWidget.__init__(self, parent)
        DevicesPanel._createResources()
        self.statusBrush = {
            OK:         QBrush(Qt.GlobalColor.white),
            WARN:       QBrush(colors.dev_bg_warning),
            BUSY:       QBrush(colors.dev_bg_busy),
            NOTREACHED: QBrush(colors.dev_bg_error),
            DISABLED:   QBrush(colors.dev_bg_disabled),
            ERROR:      QBrush(colors.dev_bg_error),
            UNKNOWN:    QBrush(QColorConstants.Svg.olive),
        }
        self.valueBrush = {
            (False, False):  QBrush(),
            (False, True):   QBrush(colors.value_fixed),
            (True, False):   QBrush(colors.value_expired),
            (True, True):    QBrush(colors.value_expired),
        }
        NicosWidget.__init__(self)
        self._doubleclick = False
        # list of all widget devices
        self._devices = []
        for prop_name in ('globe_valves', 'pumps', 'mf_sensors', 'p_sensors',
                          't_sensors'):
            self._devices.extend(self.props[prop_name])
        for prop_name in ('conductance_sensor', 'level_sensor', 'ph_sensor'):
            self._devices.append(self.props[prop_name])

    def _newDevinfo(self, expr, unit, fmtstr, isdevice):
        devinfo = NicosWidget._newDevinfo(self, expr, unit, fmtstr, isdevice)
        devinfo.update(dict(description=(), required_level=GUEST,
                            selected=False, warnlimits=()))
        return devinfo

    def mouseDoubleClickEvent(self, event):
        # action will be triggered on release
        self._doubleclick = True

    def mouseMoveEvent(self, event):
        devs = self._get_devices_under_mouse(event.localPos())
        self.setCursor(Qt.PointingHandCursor if devs else Qt.ArrowCursor)
        self.setToolTip(''.join(f'<p><b>{d}</b>: {self.devinfo[d].description}'
                                f'</p>' for d in devs))

    def mousePressEvent(self, event):
        self._doubleclick = False

    def mouseReleaseEvent(self, event):
        devs = self._get_devices_under_mouse(event.localPos(), clicked=True)
        if self._doubleclick:
            for dev in devs:
                self._devpanel.on_tree_itemActivated(
                    QTreeWidgetItem([dev], DEVICE_TYPE), None)

    def _get_devices_under_mouse(self, local_pos, clicked=False):
        x = local_pos.x()
        y = self.height() - local_pos.y()
        devs = []
        for dev, devinfo in self.devinfo.items():
            if not devinfo.isdevice or not hasattr(devinfo, 'position'):
                continue
            pos = devinfo.position
            # unmark all devices to mark recently selected device afterwards
            if clicked:
                devinfo.selected = False
            if (pos.x <= x <= pos.x + pos.width
                    and pos.y <= y <= pos.y + pos.height):
                # remain selected until next click
                devinfo.selected = devinfo.selected or clicked
                self.update()
                devs.append(dev)
        return devs

    def resizeEvent(self, e):
        self.setMaximumHeight(round(self.width() / 1.35))

    def registerKeys(self):
        for dev in self._devices:
            self.registerDevice(f'{dev}')
            self.registerDevice(f'{dev}/description')
            self.registerDevice(f'{dev}/requires')
            self.registerDevice(f'{dev}/warnlimits')

    def setClient(self, client):
        super().setClient(client)
        # track mouse on hover to show tool tip
        self.setMouseTracking(True)
        # determine NICOS device panel
        self._devpanel = self.parent().mainwindow.findChild(DevicesPanel)
        # init description, required access level and warn limits
        for dev in self._devices:
            for p in ('description', 'warnlimits'):
                self.devinfo[dev][p] = self._client.getDeviceParam(dev, p)
            self.devinfo[dev].required_level = self._get_required_level(
                self._client.getDeviceParam(dev, 'requires'))

    def on_keyChange(self, key, value, time, expired):
        super().on_keyChange(key, value, time, expired)
        dev, param = key.rsplit('/', 1)
        if dev not in self._devmap:
            return
        devinfo = self.devinfo[self._devmap[dev]]
        if param == 'description':
            devinfo.description = value
        if param == 'requires':
            self.devinfo[dev].required_level = self._get_required_level(param)
        if param == 'warnlimits':
            devinfo.warnlimits = value

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self.update()

    def on_devStatusChange(self, dev, code, status, expired):
        self.update()

    def _get_required_level(self, requires):
        """Get access level code for moving a device from access level string.

        :param dict[str, str] requires: access requirements for moving a device
        :return int: minimum access level code to for moving ``dev``
        """
        default = ACCESS_LEVELS[GUEST]
        if requires is None:
            return default
        for level_code, level_string in ACCESS_LEVELS.items():
            if level_string == requires.get('level', default):
                return level_code

    def _get_value_colour(self, dev, default=Qt.black):
        """Determine value colour of ``dev` to visualise expired or fixed
        values.

        :param str dev: device name
        :param QColor or int default: Qt colour object or constant to use if
          ``dev`` value is neither ``fixed`` nor ``expired``
        :return QColor or int: Qt colour object or constant to use for ``dev``
          value visualisation
        """
        colour = self.valueBrush[self.devinfo[dev].expired,
                                 bool(self.devinfo[dev].fixed)].color()
        return colour if colour.value() else default

    def paintEvent(self, event):
        if self._client is None:
            return

        # configure painter
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setRenderHint(QPainter.HighQualityAntialiasing)
        qp.setRenderHint(QPainter.LosslessImageRendering)
        qp.setRenderHint(QPainter.SmoothPixmapTransform)
        qp.setRenderHint(QPainter.TextAntialiasing)

        # get window size and translate painter to bottom left
        width_window = qp.window().width() - 1
        height_window = qp.window().height() - 1
        qp.translate(0, height_window)
        qp.scale(1, -1)

        # set drawing limits
        x_min, x_max = .02 * width_window, .975 * width_window
        y_min, y_max = .05 * height_window, .95 * height_window
        width_max = x_max - x_min
        height_max = y_max - y_min

        # set default icon and line sizes
        size_icon = 0.045 * min(height_max, width_max)
        size_line = 0.15 * size_icon
        pen_basic = QPen(QColorConstants.Svg.lightskyblue, size_line,
                         cap=Qt.RoundCap)
        qp.setFont(self.props['valueFont'])
        qp.setPen(pen_basic)

        try:
            # height of lower cooling system section
            height_lower = 0.4 * height_max

            # target
            size_target = 2 * size_icon
            x_target = x_min
            y_target = y_min + 0.5 * height_lower - 0.5 * size_target
            x, y = self._draw_rect(qp, x_target, y_target, width=size_target,
                                   height=size_target, brush=Qt.cyan)
            for i in range(8):
                self._draw_line(qp, x + i / 7 * size_target, y, dy=size_target,
                                pen=QPen(Qt.black, 0.25 * size_line))

            # horizontal path below target
            x, y = self._draw_line(qp, x, y, dx=0.1 * x_max)
            # vertical path to bottom drawing limit
            dy = -(0.5 * height_lower - 0.5 * size_target)
            x, y = self._draw_line(qp, x, y, dy=dy)
            # TODO: remove HV04?
            # self._draw_valve(qp, x, y - 0.5 * dy, size=size_icon, dev='hv04')
            # horizontal path to right drawing limit
            width_max = x_max - x
            for pos, dev in ((0.2, 'mf01'), (0.5, 't01'), (0.8, 'p02')):
                self._draw_sensor(qp, x + pos * 0.3 * width_max, y,
                                  size=size_icon, dev=dev)
            self._draw_sensor(qp, x + 0.4 * width_max, y, size=size_icon,
                              dev='p01')
            x, y = self._draw_line(qp, x, y, dx=width_max)
            self._draw_valve(qp, x - 0.375 * width_max, y, size=size_icon)
            # TODO: remove MP02?
            # self._draw_pump(qp, x - 0.225 * width_max - size_icon, y,
            #                 size=2 * size_icon, dev='mp02')
            # vertical paths between lower and upper section
            x, _ = self._draw_line(qp, x - 0.7 * width_max, y, dy=height_lower)
            self._draw_valve(qp, x, y + 0.5 * height_lower, size=size_icon,
                             dev='hv03')
            x, y = self._draw_line(qp, x + 0.7 * width_max, y, dy=height_lower)

            # water level, electric conductance and pH sensors
            self._draw_water_sensors(qp, x - 0.1 * width_max, y,
                                     width=0.0625 * width_max,
                                     height=0.15 * height_max, x_max=x_max,
                                     y_max=y_max)

            # manual valve after water level sensors
            self._draw_valve(qp, x - 0.05 * width_max, y, size=size_icon)

            # additional branch below target
            x, y = self._draw_line(qp, x - 0.5 * width_max, y - height_lower,
                                   dy=0.35 * height_lower)
            x, y = self._draw_line(qp, x, y, dx=0.4 * width_max)
            self._draw_valve(qp, x - 0.275 * width_max, y, size=size_icon)
            self._draw_pump(qp, x - 0.125 * width_max - size_icon, y,
                            size=2 * size_icon, dev='mp01')
            dy = 0.5 * height_lower
            x, y = self._draw_line(qp, x, y, dy=dy)
            self._draw_valve(qp, x, y - 0.5 * dy - 0.1 * height_lower,
                             size=size_icon, dev='hv01')
            x, y = self._draw_line(qp, x, y, dx=0.1 * width_max)
            # TODO: remove HV05?
            # self._draw_valve(qp, x, y - 0.5 * dy, size=size_icon, dev='hv05')

            # horizontal path above target
            x, y = self._draw_line(qp, x_target, y_target + size_target,
                                   dx=0.1 * x_max)
            # vertical path to upper part
            dy = 0.5 * height_lower - 0.5 * size_target
            x, y = self._draw_line(qp, x, y, dy=dy)
            # TODO: remove HV02?
            # self._draw_valve(qp, x, y - 0.5 * dy, size=size_icon, dev='hv02')
            # horizontal path to heat exchanger
            self._draw_sensor(qp, x + 0.15 * width_max, y, size=size_icon,
                              dev='t02')
            x, y = self._draw_line(qp, x, y, dx=0.55 * width_max)

            # save heat exchanger coordinates
            x_heatex, y_heatex = x, y

            # filter with surrounding manual valves and pressure sensors
            x, y = self._draw_valve(qp, x - 0.24 * width_max + 0.5 * size_icon,
                                    y, size=size_icon)
            dy = 0.1 * height_max
            x, y = self._draw_line(qp, x + 0.015 * width_max + 0.5 * size_line,
                                   y, dy=dy)
            self._draw_sensor(qp, x, y, size=size_icon, dev='p03')
            qp.setBrush(QColorConstants.Svg.whitesmoke)
            qp.setPen(QPen(Qt.black, 0.5 * size_line))
            x += 0.025 * width_max - 0.5 * size_line
            y -= dy
            size_filter = 1.5 * size_icon
            qp.drawPolygon(QPointF(x, y),
                           QPointF(x + 0.5 * size_filter,
                                   y + 0.5 * size_filter),
                           QPointF(x + size_filter, y),
                           QPointF(x + 0.5 * size_filter,
                                   y - 0.5 * size_filter))
            pen = QPen(Qt.black, 0.5 * size_line, Qt.CustomDashLine,
                       Qt.FlatCap)
            pen.setDashPattern((0.5 * size_line, 0.25 * size_line))
            self._draw_line(qp, x + 0.5 * size_filter, y - 0.5 * size_filter,
                            dy=size_filter, pen=pen)
            qp.setPen(pen_basic)
            x, _ = self._draw_line(qp, x + size_filter + 0.025 * width_max, y,
                                   dy=dy)
            self._draw_sensor(qp, x, y + dy, size=size_icon, dev='p04')
            self._draw_valve(qp, x + 0.015 * width_max + 0.5 * size_icon, y,
                             size=size_icon)

            # vertical paths up to and down from heat exchanger
            height_heatex = 0.1 * height_max
            width_heatex = 0.075 * width_max
            x, y = self._draw_line(qp, x_heatex, y, dy=0.15 * height_heatex)
            x, y = self._draw_line(qp, x + 0.5 * width_heatex, y,
                                   dy=-0.15 * height_heatex)
            # horizontal path to water level sensor
            dx = 0.225 * width_max
            x, y = self._draw_line(qp, x, y, dx=dx)
            self._draw_valve(qp, x - dx + 0.16 * width_max - 3 * size_icon, y,
                             size=size_icon)
            # vertical path to water level, temperature and pressure sensors
            x, y = self._draw_line(qp, x, y, dy=0.15 * height_max)
            # horizontal path to temperature and pressure sensors
            # (right to left)
            dx = -0.15 * width_max
            dy = -0.05 * height_max
            self._draw_sensor(qp, x + dx, y + dy, size=size_icon, dev='t03')
            self._draw_sensor(qp, x + 0.25 * dx, y + dy, size=size_icon,
                              dev='p05')
            self._draw_line(qp, x, y + dy, dx=dx)

            x, y = self._draw_heat_exchanger(qp, x_heatex, y_heatex,
                                             width=width_heatex,
                                             height=height_heatex)

            # cooling system above heat exchanger
            dx = 0.075 * width_max
            dy = y_max - y - size_icon
            # vertical to upper end
            x, y = self._draw_line(qp, x, y, dy=dy)
            # horizontal path with pressure sensor T04 mass flow sensor MF02
            # TODO: remove t04 and mf02?
            # self._draw_sensor(qp, x - dx, y - 0.7 * dy, size=size_icon,
            #                   dev='t04')
            # self._draw_sensor(qp, x - dx, y - 0.3 * dy, size=size_icon,
            #                   dev='mf02')
            self._draw_line(qp, x, y - 0.7 * dy, dx=-dx)
            self._draw_line(qp, x, y - 0.3 * dy, dx=-dx)
            # path to manual valve, temperature sensor T05 and back to heatex
            dx = 0.45 * width_heatex
            x, y = self._draw_line(qp, x, y, dx=dx)
            self._draw_line(qp, x, y, dy=-dy)
            self._draw_valve(qp, x - 0.5 * (dx + 0.25 * qp.pen().widthF()), y,
                             size=size_icon)
            y -= 0.5 * dy
            dx = 0.075 * width_max
            # TODO: remove t05?
            # self._draw_sensor(qp, x + dx, y, size=size_icon, dev='t05')
            self._draw_line(qp, x, y, dx=dx)

            # mark currently selected device(s)
            for dev in self._devices:
                if not self.devinfo[dev].selected:
                    continue
                pos = self.devinfo[dev].position
                self._draw_rect(qp, pos.x, pos.y, width=pos.width,
                                height=pos.height,
                                pen=QPen(Qt.black, 1, Qt.DashLine))
        except Exception as err:
            # paint over all the drawings so far
            qp.setPen(Qt.NoPen)
            qp.setBrush(QColorConstants.Svg.silver)
            qp.drawRect(0, 0, qp.window().width() - 1,
                        qp.window().height() - 1)
            # paint error message
            size_error = 4 * size_icon
            self._draw_pixmap(qp, 'error', 0.5 * (x_max - size_error),
                              0.5 * y_max + size_error, size=size_error)
            font = qp.font()
            font.setPointSize(1.5 * font.pointSize())
            qp.setFont(font)
            pen_rect = QPen(Qt.darkRed, 0.5 * font.pointSize())
            self._draw_text(qp, 0.5 * x_max - 3 * size_error,
                            0.5 * y_max + 0.75 * size_error,
                            width=6 * size_error, height=2 * size_error,
                            rounded=size_line, text='Exception during '
                            f'drawing of TMR cooling system:\n{err!r}',
                            align=Qt.AlignCenter | Qt.AlignHCenter, bold=True,
                            wrap=QTextOption.WordWrap, brush=Qt.red,
                            pen_rect=pen_rect, pen_text=Qt.white)
        qp.end()

    # helper methods to draw qt elements
    def _draw_line(self, qp, x, y, dx=0, dy=0, pen=Qt.NoPen):
        """Draw line and return end coordinates. Per default the currently
        configured pen of ``qp`` will be used.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of line start
        :param float y: y coordinate of line start
        :param float dx: horizontal distance to line end
        :param float dy: vertical distance to line end
        :param QPen or QColor or int pen: Qt pen object or Qt colour (constant)
          to use
        :return tuple[float, float]: line end coordinates
        """
        qp.save()
        if pen:
            qp.setPen(pen)
        qp.drawLine(QPointF(x, y), QPointF(x + dx, y + dy))
        qp.restore()
        return x + dx, y + dy

    def _draw_marker(self, qp, x, y, width, height, dev, value_range,
                     check_limits=False):
        """Draw marker to visualise the current value of water sensors.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of the bottom left marker corner
        :param float y: y coordinate of the bottom left marker corner
        :param float width: water sensor width
        :param float height: water sensor height
        :param str dev: water sensor device name
        :param float value_range: possible value range to determine relative
          position of the marker
        :param bool check_limits: whether to check that the marker is not drawn
          outside the water sensor
        """
        size = 0.75 * qp.font().pointSizeF()
        y_min, y_max = y, y + height
        try:
            y += self.devinfo[dev].value / value_range * height
        except TypeError:
            return
        y_top, y_bottom = y + size, y - size
        if check_limits:
            if y - size < y_min:
                y_bottom = y_min
                y_top = y_min + 2 * size
            elif y + size > y_max:
                y_top = y_max
                y_bottom = y_max - 2 * size
        width -= size
        x, y = self._draw_line(qp, x, y, dx=size, pen=Qt.black)
        # triangle
        qp.save()
        qp.setBrush(Qt.black)
        qp.setPen(Qt.NoPen)
        qp.drawPolygon(QPointF(x, y),
                       QPointF(x + size, y_top),
                       QPointF(x + size, y_bottom))
        # rectangle with current value
        self._draw_text(qp, x + size, y_top,
                        width=width - size, height=2 * size,
                        text='{value:.1f} {unit}'.format(**self.devinfo[dev]),
                        align=Qt.AlignCenter, brush=Qt.black,
                        pen_text=self._get_value_colour(dev, default=Qt.white))
        qp.restore()

    def _draw_pixmap(self, qp, pixmap, x, y, size):
        """Draw a square-shaped pixel map with given parameters.

        :param QPainter qp: Qt painter object to use
        :param str pixmap: file basename of the pixel map to draw (e.g. 'pump')
        :param float x: x coordinate of the bottom left pixel map corner
        :param float y: y coordinate of the bottom left pixel map corner
        :param float size: pixel map size in x and y direction
        """
        qp.save()
        qp.scale(1, -1)
        qp.drawPixmap(QPointF(x, -(y + size)),
                      QPixmap(path.join(path.dirname(__file__), 'icons',
                                        f'{pixmap}.svg')).scaled(
                          round(size), round(size),
                          transformMode=Qt.SmoothTransformation))
        qp.restore()

    def _draw_rect(self, qp, x, y, width, height, rounded=False,
                   brush=Qt.NoBrush, pen=Qt.NoPen):
        """Draw a rectangle with given parameters.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of the bottom left rectangle corner
        :param float y: y coordinate of the bottom left rectangle corner
        :param float width: rectangle width
        :param float height: rectangle height
        :param bool or int rounded: whether to draw rounded rectangle with
          default (``rounded=True``) or given radius (``rounded=radius``)
        :param QBrush or QColor or int brush: Qt brush object or Qt colour
          (constant) to use for the background
        :param QPen or QColor or int pen: Qt pen object or Qt colour (constant)
          to use for the rectangle outline
        :return tuple[float, float]: x and y coordinates of bottom left
          rectangle corner
        """
        qp.save()
        qp.setBrush(brush)
        qp.setPen(pen)
        if rounded:
            radius = 2 * [
                (4 if rounded is True else rounded) * qp.pen().widthF()]
            qp.drawRoundedRect(QRectF(x, y, width, height), *radius)
        else:
            qp.drawRect(QRectF(x, y, width, height))
        qp.restore()
        return x, y

    def _draw_text(self, qp, x, y, width, height, text, rounded=False,
                   align=Qt.AlignLeft, bold=False, wrap=QTextOption.NoWrap,
                   brush=Qt.NoBrush, pen_rect=Qt.NoPen, pen_text=Qt.black):
        """Draw a rectangle with given text inside.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of the bottom left rectangle corner
        :param float y: y coordinate of the bottom left rectangle corner
        :param float width: rectangle width
        :param float height: rectangle height
        :param bool or int rounded: whether to draw rounded rectangle with
          default (``rounded=True``) or given radius (``rounded=radius``)
        :param int align: Qt text alignment
        :param str text: text to display in rectangle
        :param bool bold: whether the text shall be bold
        :param int wrap: Qt text wrap
        :param QBrush or QColor or int brush: Qt brush object or Qt colour
          (constant) to use for the rectangle background
        :param QPen or QColor or int pen_rect: Qt pen object or Qt colour
          (constant) to use for the rectangle outline
        :param QPen or QColor or int pen_text: Qt pen object or Qt colour
          (constant) to use for the text
        """
        qp.save()
        qp.scale(1, -1)
        if brush:
            self._draw_rect(qp, x, -y, width=width, height=height,
                            rounded=rounded, brush=brush, pen=pen_rect)
        qp.setPen(pen_text)
        font = qp.font()
        if bold:
            font.setBold(True)

        # adjust text size to fit into the rectangle if necessary
        rect = QRectF(x, -y, width, height)
        if not wrap:
            factor = rect.width() / qp.fontMetrics().width(text)
            if factor <= 1:
                font.setPointSizeF(font.pointSizeF() * 0.9 * factor)
            factor = rect.height() / qp.fontMetrics().height()
            if factor <= 1:
                font.setPointSizeF(font.pointSizeF() * 0.9 * factor)

        qp.setFont(font)
        option = QTextOption()
        option.setAlignment(align)
        option.setWrapMode(wrap)
        qp.drawText(rect, text, option)
        qp.restore()

    # helper methods to draw cooling system devices

    def _draw_heat_exchanger(self, qp, x, y, width, height):
        """Draw the heat exchanger of the cooling system.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of the bottom left cooling system tube
        :param float y: y coordinate of the bottom left cooling system tube
        :param float width: heat exchanger width
        :param float height: heat exchanger height (including wire)
        :return tuple[float, float]: x and y coordinates of the top left
          cooling system tube
        """
        qp.save()
        x -= 0.25 * width
        y += 0.15 * height
        brush = QLinearGradient(QPointF(x, y), QPointF(x, y + 0.5 * height))
        brush.setColorAt(0, Qt.red)
        brush.setColorAt(1, Qt.yellow)
        self._draw_rect(qp, x, y, width=width, height=0.5 * height,
                        pen=Qt.darkGray, brush=brush)

        margin_wire = 0.15
        x += margin_wire * width
        y += margin_wire * height
        dy_outerwire = (1 - margin_wire) * height
        # connecting tubes to upper part of cooling system
        y_connectors = y + dy_outerwire - 0.5 * qp.pen().widthF()
        dx_connectors = 0.125 * width
        ret = self._draw_line(qp, x, y_connectors, dx=dx_connectors)
        self._draw_line(qp, x + (1 - 2 * margin_wire) * width,
                        y_connectors, dx=-dx_connectors)
        # heat exchanger wire
        pen = QPen(Qt.darkGray, min(0.1 * width, 0.15 * height),
                   cap=Qt.FlatCap)
        self._draw_line(qp, x, y, dy=dy_outerwire, pen=pen)
        pen.setCapStyle(Qt.RoundCap)
        dx = 0.25 * width * (1 - 2 * margin_wire)
        dy = 0.25 * height * (1 - 2 * margin_wire)
        for i in range(4):
            x, y = self._draw_line(qp, x, y, dx=dx, dy=(-1)**i * dy, pen=pen)
        pen.setCapStyle(Qt.FlatCap)
        self._draw_line(qp, x, y, dy=dy_outerwire, pen=pen)
        qp.restore()
        return ret

    def _draw_pump(self, qp, x, y, size, dev):
        """Draw pump device ``dev`` visualising current value and status.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of the left cooling system tube
        :param float y: y coordinate of the left cooling system tube
        :param float size: pump icon size in x and y direction
        :param str dev: NICOS device name
        """
        qp.save()
        dev = self.props['pumps'][int(dev[-2:]) - 1]
        devinfo = self.devinfo[dev]
        devinfo.position = AttrDict(x=x - 0.05 * size, y=y - 0.6 * size,
                                    width=1.1 * size, height=1.5 * size)
        margin = 0.25
        size_pen = 0.025 * size
        qp.setPen(Qt.NoPen)
        qp.setBrush(self.statusBrush[devinfo.status[0]])
        # outer circle with status colour
        qp.drawEllipse(QRectF(x, y - 0.5 * size, size, size))
        # pump symbol
        self._draw_pixmap(qp, 'pump', x, y - 0.5 * size, size=size)
        qp.setPen(QPen(Qt.black, size_pen))
        qp.setBrush(Qt.lightGray)
        x += 0.5 * margin * size
        size -= margin * size
        # inner circle with coloured on/off switch
        qp.drawEllipse(QRectF(x, y - 0.5 * size, size, size))
        colour = Qt.green if devinfo.value.lower() == 'on' else Qt.red
        qp.setPen(QPen(colour, size_pen))
        size_icon = (1 - 2 * margin) * size
        x_icon = x + margin * size
        y_icon = y - 0.5 * size_icon + 0.025 * size
        qp.drawArc(QRectF(x_icon, y_icon, size_icon, size_icon), -50 * 16,
                   280 * 16)
        self._draw_line(qp, x_icon + 0.5 * size_icon,
                        y_icon + 0.65 * size_icon, dy=0.35 * size_icon)
        self._draw_text(qp, x, y_icon, width=size, height=0.5 * size_icon,
                        text=devinfo.value.lower(), align=Qt.AlignCenter,
                        pen_text=self._get_value_colour(dev, default=colour))
        self._draw_text(qp, x, y + (1 + 0.5 * margin) * size,
                        width=size, height=0.4 * size, text=dev.upper(),
                        align=Qt.AlignCenter, bold=True)
        # warning/error icon
        if devinfo.status[0] in (WARN, ERROR):
            qp.setOpacity(0.25)
            self._draw_pixmap(qp, statuses[devinfo.status[0]],
                              x + 0.125 * size, y - 0.35 * size,
                              size=0.75 * size)
            qp.setOpacity(1)
        qp.restore()

    def _draw_sensor(self, qp, x, y, size, dev):
        """Draw pump device ``dev`` visualising current value and status.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of the cooling system tube
        :param float y: y coordinate of the cooling system tube
        :param float size: sensor icon size in x and y direction
        :param str dev: NICOS device name
        """
        qp.save()
        # e.g. 'p03' corresponds to third device in self.props['p_sensors']
        stype, snum = dev[:-2], int(dev[-2:]) - 1
        dev = self.props[f'{stype.lower()}_sensors'][snum]
        x, y = self._draw_line(qp, x, y, dy=0.25 * size,
                               pen=QPen(Qt.black, 0.075 * size))
        devinfo = self.devinfo[dev]
        devinfo.position = AttrDict(x=x - 1.4 * size, y=y - 0.5 * size,
                                    width=2.8 * size, height=3 * size)
        # sensor icon
        icon = SENSOR_ICON[stype.upper()]
        try:
            value = f'%(value){devinfo.fmtstr.lstrip("%")} %(unit)s' % devinfo
            if devinfo.warnlimits:
                if devinfo.value < devinfo.warnlimits[0]:
                    icon += '-low'
                elif devinfo.value > devinfo.warnlimits[1]:
                    icon += '-high'
        except TypeError:
            value = devinfo.value
        self._draw_pixmap(qp, icon, x - 0.5 * size, y, size=size)
        # sensor type
        self._draw_text(qp, x + 0.5 * size, y + 0.35 * size,
                        width=size, height=0.5 * size,
                        text=stype.upper(),
                        bold=True, pen_rect=Qt.black)
        # sensor name
        self._draw_text(qp, x - 1.25 * size, y + 1.6 * size,
                        width=2.5 * size, height=0.5 * size, text=dev.upper(),
                        align=Qt.AlignCenter, bold=True, pen_rect=Qt.black)
        # sensor status and value in outlined/coloured rect
        self._draw_text(qp, x - 1.4 * size, y + 2.4 * size,
                        width=2.8 * size, height=0.75 * size,
                        text=value, align=Qt.AlignCenter,
                        brush=self.statusBrush[devinfo.status[0]],
                        pen_rect=Qt.black,
                        pen_text=self._get_value_colour(dev))
        qp.restore()

    def _draw_valve(self, qp, x, y, size, dev=None):
        """Draw manual valve or globe valve device ``dev`` visualising current
        value and status.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of the valve center
        :param float y: y coordinate of the valve center
        :param float size: valve icon size in x and y direction
        :param str or None dev: NICOS device name (globe valve) or ``None``
          (manual valve)
        """
        qp.save()
        size_connector = 0.25 * size
        size_icon = 0.75 * size
        size_line_border = 0.06 * size
        size_line_shutter = 0.1 * size_icon
        pen_connector = QPen(Qt.black, 0.5 * size_line_shutter)
        pen_shutter = QPen(Qt.black, size_line_shutter)
        width_valve_min, width_valve_max = 0.1 * size, 0.25 * size
        qp.setPen(QPen(Qt.darkGray, size_line_border))

        if dev is None:  # horizontal manual valve
            ret = x + 0.5 * size, y
            x_center = x + 0.5 * size_line_shutter
            qp.setBrush(QColorConstants.Svg.whitesmoke)
            qp.drawPolygon(QPointF(x - 0.5 * size, y - width_valve_max),
                           QPointF(x - 0.5 * size, y + width_valve_max),
                           QPointF(x, y + width_valve_min),
                           QPointF(x + 0.5 * size, y + width_valve_max),
                           QPointF(x + 0.5 * size, y - width_valve_max),
                           QPointF(x, y - width_valve_min),
                           QPointF(x - 0.5 * size, y - width_valve_max))
            self._draw_line(qp, x_center, y - width_valve_min,
                            dy=2 * width_valve_min, pen=pen_shutter)
            self._draw_line(qp, x_center, y + width_valve_min,
                            dy=size_connector, pen=pen_connector)
            self._draw_pixmap(qp, 'manual-valve', x_center - 0.5 * size_icon,
                              y + width_valve_min + size_connector,
                              size=size_icon)
        else:  # vertical globe valve
            # e.g. hv01 corresponds to first dev in self.props['globe_valves']
            dev = self.props['globe_valves'][int(dev[-2:]) - 1]
            devinfo = self.devinfo[dev]
            devinfo.position = AttrDict(x=x - 1.75 * size, y=y - 1.25 * size,
                                        width=2.25 * size, height=2.25 * size)
            y_start, y_end = y - 0.5 * size, y + 0.5 * size
            ret = x, y_end
            # visualise opening percentage with blue color
            brush_value = QColorConstants.Svg.steelblue
            try:
                # set negative values to 0
                value = max(0.0, float(devinfo.value))
            except ValueError:
                value = 0
            if value < 100:
                brush_value = QLinearGradient(QPointF(x, y_start),
                                              QPointF(x, y_end))
                brush_value.setColorAt(0, QColorConstants.Svg.steelblue)
                brush_value.setColorAt(value / 100,
                                       QColorConstants.Svg.steelblue)
                brush_value.setColorAt(value / 99.999,
                                       QColorConstants.Svg.whitesmoke)
                brush_value.setColorAt(1, QColorConstants.Svg.whitesmoke)
            qp.setBrush(brush_value)
            # valve in the shape of an "hourglass"
            qp.drawPolygon(QPointF(x - width_valve_max, y_start),
                           QPointF(x + width_valve_max, y_start),
                           QPointF(x + width_valve_min, y),
                           QPointF(x + width_valve_max, y_end),
                           QPointF(x - width_valve_max, y_end),
                           QPointF(x - width_valve_min, y),
                           QPointF(x - width_valve_max, y_start))
            qp.setPen(pen_shutter)
            if value < 100:
                # horizontal line if valve is not completely open
                self._draw_line(qp, x - width_valve_min, y,
                                dx=2 * width_valve_min)
            else:
                # vertical line to show that valve is open
                self._draw_line(qp, x, y - width_valve_min,
                                dy=2 * width_valve_min)

            # connecting line between valve and icon
            qp.setPen(pen_connector)
            x, y = self._draw_line(qp, x - width_valve_min, y,
                                   dx=-size_connector)
            # outer rect with status colour
            x, y = self._draw_rect(qp, x - size_icon, y - 0.5 * size_icon,
                                   width=size_icon, height=size_icon,
                                   rounded=True,
                                   brush=self.statusBrush[devinfo.status[0]],
                                   pen=Qt.black)
            # inner rect with warning/error icons if applicable
            size_inner = 0.75 * size_icon
            translation_inner = 0.125 * size_icon
            x_inner, y_inner = self._draw_rect(qp, x + translation_inner,
                                               y + translation_inner,
                                               width=size_inner,
                                               height=size_inner, rounded=True,
                                               brush=Qt.lightGray,
                                               pen=Qt.black)
            if devinfo.status[0] in (WARN, ERROR):
                self._draw_pixmap(qp, statuses[devinfo.status[0]],
                                  x_inner, y_inner, size=size_inner)
            if devinfo.required_level > self._client.user_level:
                # mark valve icon as disabled (grey overlay + dark X)
                qp.setOpacity(0.5)
                self._draw_rect(qp, x, y, width=size_icon, height=size_icon,
                                rounded=True, brush=Qt.darkGray)
                qp.setOpacity(1)
                pen = QPen(Qt.darkGray, size_line_shutter, cap=Qt.RoundCap)
                self._draw_line(qp, x_inner, y_inner, dx=size_inner,
                                dy=size_inner, pen=pen)
                self._draw_line(qp, x_inner + size_inner, y_inner,
                                dx=-size_inner, dy=size_inner, pen=pen)
            # valve name (above icon)
            self._draw_text(qp, x - 2 * size_icon, y + 1.75 * size_icon,
                            width=3 * size_icon, height=0.5 * size,
                            text=dev.upper(), align=Qt.AlignRight, bold=True)

            # valve value (below icon)
            self._draw_text(qp, x - 0.5 * size_icon, y - 0.25 * size_icon,
                            width=size + 0.5 * size_connector,
                            height=0.5 * size, text=f'{int(value)} %',
                            align=Qt.AlignCenter,
                            brush=self.statusBrush[devinfo.status[0]],
                            pen_rect=Qt.black,
                            pen_text=self._get_value_colour(dev))
        qp.restore()
        return ret

    def _draw_water_sensors(self, qp, x, y, width, height, x_max, y_max):
        """Draw water level, electric conductance and pH sensors visualising
        current values and status.

        :param QPainter qp: Qt painter object to use
        :param float x: x coordinate of the right cooling system tube
        :param float y: y coordinate of the right cooling system tube
        :param float width: horizontal distance between cooling system tubes
        :param float height: vertical distance between cooling system tubes
        :param float x_max: largest x coordinate of the drawing area
        :param float y_max: largest y coordinate of the drawing area
        """
        qp.save()
        dev = self.props['level_sensor']
        devinfo = self.devinfo[dev]
        margin = 0.1
        dx = x_max - x
        x_line, y_line = x, y
        # background of water level sensor
        x -= (1 + margin) * width
        y -= 2 * margin * height
        width_bg = (1 + 2 * margin) * width
        height_bg = (1 + 6 * margin) * height
        devinfo.position = AttrDict(x=x, y=y, width=width_bg,
                                    height=height_bg - margin * height)
        self._draw_rect(qp, x, y, width=width_bg, height=height_bg, rounded=8,
                        brush=QColorConstants.Svg.whitesmoke)
        self._draw_text(qp, x, y + (1 - 0.75 * margin) * height_bg,
                        width=width_bg, height=2 * margin * height,
                        text=dev.upper(), align=Qt.AlignCenter, bold=True)

        # save coordinates of conductance and pH sensors
        x_conduct_ph = x
        y_conduct_ph = y + (1 + 5.25 * margin) * height

        # connecting tubes of cooling system
        self._draw_line(qp, x_line, y_line, dx=dx)
        self._draw_line(qp, x_line - width, y_line + height, dx=-0.25 * dx)

        x += margin * width
        y += margin * height

        # set brush for 3D effect
        brush = QLinearGradient(x, y, x + width, y)
        brush.setColorAt(0, Qt.gray)
        brush.setColorAt(0.5, QColorConstants.Svg.whitesmoke)
        brush.setColorAt(1, Qt.gray)
        qp.setBrush(brush)
        qp.setPen(Qt.black)

        # arcs above and below water level sensor rectangle
        qp.drawChord(QRectF(x, y, width, 2 * margin * height), 0, 180 * 16)
        qp.drawChord(QRectF(x, y + height, width, 2 * margin * height), 0,
                     -180 * 16)

        # outer rectangle between arcs
        x, y = self._draw_rect(qp, x, y + margin * height, width=width,
                               height=height, brush=brush, pen=Qt.black)

        # inner rectangle consisting of two differently coloured triangles
        x += 0.5 * margin * width
        y += 0.5 * margin * height
        width -= margin * width
        height -= margin * height
        qp.setBrush(Qt.gray)
        qp.drawPolygon(QPointF(x, y), QPointF(x, y + height),
                       QPointF(x + width, y + height))
        qp.setBrush(Qt.lightGray)
        qp.drawPolygon(QPointF(x, y), QPointF(x + width, y),
                       QPointF(x + width, y + height))

        # display of current value
        x += 0.5 * margin * width
        y += 0.5 * margin * height
        width -= margin * width
        height -= margin * height
        try:
            value = float(self.devinfo[self.props['level_sensor']].value)
        except ValueError:
            value = 0
        if value == MAX_WATER_LEVEL:
            brush = QColorConstants.Svg.steelblue
        else:
            percentage = value / MAX_WATER_LEVEL
            brush = QLinearGradient(x, y, x, y + height)
            brush.setColorAt(0, QColorConstants.Svg.steelblue)
            brush.setColorAt(0.999 * percentage, QColorConstants.Svg.steelblue)
            brush.setColorAt(percentage, Qt.white)
        self._draw_rect(qp, x, y, width=width, height=height, brush=brush,
                        pen=Qt.black)
        # coloured status overlay
        if devinfo.status[0] != OK:
            qp.setOpacity(0.5)
            self._draw_rect(qp, x, y, width=width, height=height,
                            rounded=2, brush=self.statusBrush[devinfo.status[0]])
            if devinfo.status[0] in (WARN, ERROR):
                size = 0.2 * height
                self._draw_pixmap(qp, statuses[devinfo.status[0]],
                                  x + 0.5 * width - 0.5 * size,
                                  y + 0.5 * height - 0.5 * size, size=size)
            qp.setOpacity(1)
        # marker visualising current value
        self._draw_marker(qp, x, y, width=width, height=height, dev=dev,
                          value_range=MAX_WATER_LEVEL, check_limits=True)

        # background of electric conductance and pH sensors
        width, height = x_max - x_conduct_ph, y_max - y_conduct_ph
        x, y = self._draw_rect(qp, x_conduct_ph, y_conduct_ph, width=width,
                               height=height, rounded=8,
                               brush=QColorConstants.Svg.whitesmoke)
        x += 0.25 * margin * width
        y += 0.5 * margin * height
        height_text = 0.05 * height
        height -= margin * height + height_text
        width -= margin * width
        size_pen = 0.02 * width
        # display of current electric conductance and pH values
        for dev, width_dev, value_range, steps in (
                (self.props['conductance_sensor'], 0.6 * width, 500, 11),
                (self.props['ph_sensor'], 0.4 * width, 14, 5)):
            devinfo = self.devinfo[dev]
            devinfo.position = AttrDict(x=x - 0.25 * margin * width,
                                        y=y - 0.025 * height,
                                        width=width_dev + 0.5 * margin * width,
                                        height=1.125 * height)
            try:
                percentage = devinfo.value / value_range
            except TypeError:
                percentage = 0
            brush = QLinearGradient(x, y, x, y + height)
            brush.setColorAt(0, QColorConstants.Svg.paleturquoise)
            brush.setColorAt(1, Qt.white)
            # conductance/pH level
            self._draw_rect(qp, x, y, width=width_dev, height=height,
                            rounded=2, brush=brush,
                            pen=QPen(Qt.gray, size_pen))
            x_inner = x + 0.5 * size_pen
            height_marker = 1.5 * qp.font().pointSizeF()
            y_inner = y + 0.5 * height_marker + 2 * size_pen
            width_inner = width_dev - size_pen
            height_inner = height - height_marker - 4 * size_pen
            brush = QLinearGradient(x_inner, y_inner,
                                    x_inner, y_inner + height_inner)
            brush.setColorAt(0, QColorConstants.Svg.paleturquoise)
            brush.setColorAt(0.999 * percentage,
                             QColorConstants.Svg.paleturquoise)
            brush.setColorAt(percentage, Qt.white)
            brush.setColorAt(1, Qt.white)
            self._draw_rect(qp, x_inner, y_inner, width=width_inner,
                            height=height_inner, brush=brush)
            # coloured status overlay
            if devinfo.status[0] != OK:
                qp.setOpacity(0.5)
                self._draw_rect(qp, x, y, width=width_dev, height=height,
                                rounded=2,
                                brush=self.statusBrush[devinfo.status[0]])
                if devinfo.status[0] in (WARN, ERROR):
                    size = 0.1 * height
                    self._draw_pixmap(qp, statuses[devinfo.status[0]],
                                      x + 0.5 * width_dev - 0.5 * size,
                                      y + 0.5 * height - 0.5 * size,
                                      size=size)
                qp.setOpacity(1)
            # scale marking
            for i in range(steps):
                height_marker = height_inner / (steps - 1)
                y_marker = y_inner + i * height_marker + 0.5 * height_marker
                self._draw_text(qp, x_inner, y_marker,
                                width=0.5 * width_inner, height=height_marker,
                                text=f'{i * value_range / (steps - 1):.1f}',
                                align=Qt.AlignVCenter | Qt.AlignRight)
                self._draw_line(qp, x_inner + 0.65 * width_inner,
                                y_marker - 0.5 * height_marker,
                                dx=0.2 * width_inner, pen=Qt.black)
            # marker visualising current value
            self._draw_marker(qp, x_inner, y_inner, width=width_inner,
                              height=height_inner, dev=dev,
                              value_range=value_range)
            # device name above sensors
            self._draw_text(qp, x, y + (1 + 0.75 * margin) * height,
                            width=width_dev, height=height_text,
                            text=dev.upper(), align=Qt.AlignCenter, bold=True)
            x += width_dev + 0.5 * margin * width
        qp.restore()
