# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""
NICOS value plot widget.
"""

import itertools
from time import localtime, strftime, time as currenttime

import gr
import numpy.ma
from gr import MARKERTYPE_ASTERISK, MARKERTYPE_BOWTIE, MARKERTYPE_CIRCLE, \
    MARKERTYPE_DIAGONAL_CROSS, MARKERTYPE_DIAMOND, MARKERTYPE_DOT, \
    MARKERTYPE_HEPTAGON, MARKERTYPE_HEXAGON, MARKERTYPE_HLINE, \
    MARKERTYPE_HOLLOW_PLUS, MARKERTYPE_HOURGLASS, MARKERTYPE_OCTAGON, \
    MARKERTYPE_OMARK, MARKERTYPE_PENTAGON, MARKERTYPE_PLUS, \
    MARKERTYPE_SOLID_BOWTIE, MARKERTYPE_SOLID_CIRCLE, \
    MARKERTYPE_SOLID_DIAMOND, MARKERTYPE_SOLID_HGLASS, MARKERTYPE_SOLID_PLUS, \
    MARKERTYPE_SOLID_SQUARE, MARKERTYPE_SOLID_STAR, \
    MARKERTYPE_SOLID_TRI_DOWN, MARKERTYPE_SOLID_TRI_LEFT, \
    MARKERTYPE_SOLID_TRI_RIGHT, MARKERTYPE_SOLID_TRI_UP, MARKERTYPE_SQUARE, \
    MARKERTYPE_STAR, MARKERTYPE_STAR_4, MARKERTYPE_STAR_5, MARKERTYPE_STAR_6, \
    MARKERTYPE_STAR_7, MARKERTYPE_STAR_8, MARKERTYPE_TRI_UP_DOWN, \
    MARKERTYPE_TRIANGLE_DOWN, MARKERTYPE_TRIANGLE_UP, MARKERTYPE_VLINE
from gr.pygr import Plot, PlotAxes, PlotCurve

from nicos.guisupport.qt import QHBoxLayout, QSize, QTimer, QWidget, pyqtSignal
from nicos.guisupport.qtgr import InteractiveGRWidget, LegendEvent, MouseEvent
from nicos.guisupport.timeseries import TimeSeries, buildTickDistAndSubTicks
from nicos.guisupport.widget import NicosWidget, PropDef
from nicos.utils import parseKeyExpression

DATEFMT = '%Y-%m-%d'
TIMEFMT = '%H:%M:%S'
SHORTTIMEFMT = '%H:%M'

GRMARKS = dict(
    dot=MARKERTYPE_DOT,
    plus=MARKERTYPE_PLUS,
    asterrisk=MARKERTYPE_ASTERISK,
    circle=MARKERTYPE_CIRCLE,
    diagonalcross=MARKERTYPE_DIAGONAL_CROSS,
    solidcircle=MARKERTYPE_SOLID_CIRCLE,
    triangleup=MARKERTYPE_TRIANGLE_UP,
    solidtriangleup=MARKERTYPE_SOLID_TRI_UP,
    triangledown=MARKERTYPE_TRIANGLE_DOWN,
    solidtriangledown=MARKERTYPE_SOLID_TRI_DOWN,
    square=MARKERTYPE_SQUARE,
    solidsquare=MARKERTYPE_SOLID_SQUARE,
    bowtie=MARKERTYPE_BOWTIE,
    solidbowtie=MARKERTYPE_SOLID_BOWTIE,
    hourglass=MARKERTYPE_HOURGLASS,
    solidhourglass=MARKERTYPE_SOLID_HGLASS,
    diamond=MARKERTYPE_DIAMOND,
    soliddiamond=MARKERTYPE_SOLID_DIAMOND,
    star=MARKERTYPE_STAR,
    solidstar=MARKERTYPE_SOLID_STAR,
    triupdown=MARKERTYPE_TRI_UP_DOWN,
    solidtriright=MARKERTYPE_SOLID_TRI_RIGHT,
    solidtrileft=MARKERTYPE_SOLID_TRI_LEFT,
    hollowplus=MARKERTYPE_HOLLOW_PLUS,
    solidplus=MARKERTYPE_SOLID_PLUS,
    pentagon=MARKERTYPE_PENTAGON,
    hexagon=MARKERTYPE_HEXAGON,
    heptagon=MARKERTYPE_HEPTAGON,
    octagon=MARKERTYPE_OCTAGON,
    star4=MARKERTYPE_STAR_4,
    star5=MARKERTYPE_STAR_5,
    star6=MARKERTYPE_STAR_6,
    star7=MARKERTYPE_STAR_7,
    star8=MARKERTYPE_STAR_8,
    vline=MARKERTYPE_VLINE,
    hline=MARKERTYPE_HLINE,
    omark=MARKERTYPE_OMARK,
)

GRCOLORS = dict(
    black=1,
    red=2,
    green=3,
    blue=4,
    lightblue=5,
    yellow=6,
    magenta=7,
    white=91,
)


# always set gr bordercolor according to linecolor
gr_setlinecolorind = gr.setlinecolorind

def setlinecolorind(color):
    gr_setlinecolorind(color)
    gr.setbordercolorind(color)

gr.setlinecolorind = setlinecolorind


class MaskedPlotCurve(PlotCurve):
    """Plot curve that handles masked arrays as X and Y data."""

    def __init__(self, *args, **kwargs):
        # fill values for masked x, y
        self.fillx = kwargs.pop('fillx', 0)
        self.filly = kwargs.pop('filly', 0)
        PlotCurve.__init__(self, *args, **kwargs)
        self._markersize = 1.0

    @property
    def x(self):
        x = PlotCurve.x.__get__(self)
        if numpy.ma.is_masked(x):
            return x.filled(self.fillx)
        return x

    @x.setter
    def x(self, x):
        PlotCurve.x.__set__(self, x)

    @property
    def y(self):
        y = PlotCurve.y.__get__(self)
        if numpy.ma.is_masked(y):
            return y.filled(self.filly)
        return y

    @y.setter
    def y(self, y):
        PlotCurve.y.__set__(self, y)

    @property
    def markersize(self):
        return self._markersize

    @markersize.setter
    def markersize(self, size):
        self._markersize = size

    def drawGR(self):
        gr.setmarkersize(self.markersize)
        PlotCurve.drawGR(self)


class NicosPlotAxes(PlotAxes):
    """Plot axes that enable automatic extension of the window by a tick
    distance in order to keep the curves from the edge of the grid.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setYtickCallback(self.ytickCallBack)
        self._ytick_labels = [0]

    def scaleWindow(self, xmin, xmax, xtick, ymin, ymax, ytick):
        dx, dy = 0, 0
        if self.autoscale & PlotAxes.SCALE_X:
            dx = xtick
        if self.autoscale & PlotAxes.SCALE_Y:
            dy = ytick
        return xmin - dx, xmax + dx, ymin - dy, ymax + dy

    def doAutoScale(self, curvechanged=None):
        vc = self.getVisibleCurves() or self.getCurves()
        original_win = self.getWindow()
        if original_win and curvechanged:
            xmin, xmax = original_win[:2]
            cmin, cmax = vc.xmin, vc.xmax
            new_x = curvechanged.x[-1]
            if cmax > xmax and new_x > xmax:
                return original_win
            elif cmin < xmin and new_x < xmin:
                return original_win
        return PlotAxes.doAutoScale(self, curvechanged)

    @property
    def yLabelLength(self):
        return max(self._ytick_labels)

    def ytickCallBack(self, x, y, svalue, _):
        self._ytick_labels.append(len(svalue))
        gr.text(x, y, svalue)

    def drawGR(self):
        self._ytick_labels = [0]
        lwidth = gr.inqlinewidth()
        gr.setlinewidth(0.1)
        PlotAxes.drawGR(self)
        gr.setlinewidth(lwidth)


class NicosTimePlotAxes(NicosPlotAxes):
    """Plot axes with automatic sensible formatting of time X-axis."""

    def __init__(self, viewport, xtick=None, ytick=None, majorx=None,
                 majory=None, drawX=True, drawY=True, slidingwindow=None):
        NicosPlotAxes.__init__(self, viewport, xtick, ytick, majorx, majory,
                               drawX, drawY)
        self.slidingwindow = slidingwindow

    def setWindow(self, xmin, xmax, ymin, ymax):
        res = NicosPlotAxes.setWindow(self, xmin, xmax, ymin, ymax)
        if res:
            tickdist, self.majorx = buildTickDistAndSubTicks(xmin, xmax)
            self.xtick = tickdist / self.majorx
        return res

    def doAutoScale(self, curvechanged=None):
        vc = self.getVisibleCurves() or self.getCurves()
        win = NicosPlotAxes.doAutoScale(self, curvechanged)
        xmin, xmax, ymin, ymax = win
        if self.slidingwindow and self.autoscale & PlotAxes.SCALE_X and \
           (vc.xmax - xmin) > self.slidingwindow:
            xmin = vc.xmax - self.slidingwindow
            self.setWindow(xmin, xmax, ymin, ymax)
        return self.getWindow()


class TrendPlot(NicosWidget, QWidget):

    designer_description = 'A trend plotter for one or more devices'
    designer_icon = ':/plotter'

    widgetInfo = pyqtSignal(str)
    timeSeriesUpdate = pyqtSignal(object)

    # colors = [Qt.red, Qt.darkGreen, Qt.blue, Qt.black, Qt.magenta, Qt.cyan,
    #           Qt.darkGray]

    devices = PropDef('devices', 'QStringList', [], """
List of devices or cache keys that the plot should display.

For devices use device name. For keys use cache key with "." or "/" separator,
e.g. T.heaterpower.

To access items of a sequence, use subscript notation, e.g. T.userlimits[0]
""")
    names = PropDef('names', 'QStringList', [], 'Names for the plot curves, '
                    'defaults to the device names/keys.')
    legend = PropDef('legend', bool, False, 'If a legend should be shown.')
    plotwindow = PropDef('plotwindow', int, 3600, 'The range of time in '
                         'seconds that should be represented by the plot.')
    plotinterval = PropDef('plotinterval', float, 2, 'The minimum time in '
                           'seconds between two points that should be '
                           'plotted.')
    height = PropDef('height', int, 10, 'Height of the plot widget in units '
                     'of app font character width.')
    width = PropDef('width', int, 30, 'Width of the plot widget in units '
                    'of app font character width.')

    def __init__(self, parent, designMode=False):
        self.ncurves = 0
        self.ctimers = {}
        self.keyexprs = {}
        self.plotcurves = {}
        self.series = {}
        self.legendobj = None

        # X label settings, default values for default window of 3600s
        self._showdate = False
        self._showsecs = False

        QWidget.__init__(self, parent)
        NicosWidget.__init__(self)

    def initUi(self):
        # axes setup
        self.widget = InteractiveGRWidget(self)
        self.plot = Plot(viewport=(.1, .95, .25, .95))
        self.axes = NicosTimePlotAxes(self.plot._viewport)
        self.axes.setWindow(0, 1, 0, 1)
        self.plot.addAxes(self.axes)
        self.plot.setLegend(True)
        self.plot.setLegendWidth(0.07)
        self.plot.offsetXLabel = -.2
        self.axes.setXtickCallback(self.xtickCallBack)
        self.widget.addPlot(self.plot)
        layout = QHBoxLayout(self)
        layout.addWidget(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.curves = []

        # event support
        self.widget.cbm.addHandler(LegendEvent.ROI_CLICKED,
                                   self.on_legendItemClicked, LegendEvent)
        self.widget.cbm.addHandler(MouseEvent.MOUSE_MOVE, self.on_mouseMove)

        self.timeSeriesUpdate.connect(self.on_timeSeriesUpdate)

    def xtickCallBack(self, x, y, _svalue, value):
        gr.setcharup(-1., 1.)
        gr.settextalign(gr.TEXT_HALIGN_RIGHT, gr.TEXT_VALIGN_TOP)
        dx = .02
        timeVal = localtime(value)
        if self._showdate:
            gr.text(x + dx, y - 0.01, strftime(DATEFMT, timeVal))
        if self._showsecs:
            gr.text(x - dx, y - 0.01, strftime(TIMEFMT, timeVal))
        else:
            gr.text(x - dx, y - 0.01, strftime(SHORTTIMEFMT, timeVal))
        gr.setcharup(0., 1.)

    def propertyUpdated(self, pname, value):
        if pname == 'plotwindow':
            self._showdate = value > 24*3600
            self._showsecs = value < 300
        elif pname in ('width', 'height'):
            self.setMinimumSize(
                QSize(round(self._scale * (self.props['width'] + .5)),
                      round(self._scale * (self.props['height'] + .5))))
        elif pname == 'legend':
            self.plot.setLegend(value)
        NicosWidget.propertyUpdated(self, pname, value)

    def setFont(self, font):
        pass  # TODO: can't set font for GR right now

    def on_mouseMove(self, event):
        wc = event.getWC(self.plot.viewport)
        ts = strftime(DATEFMT + ' ' + TIMEFMT, localtime(wc.x))
        msg = 't = %s, y = %g' % (ts, wc.y)
        self.widgetInfo.emit(msg)

    def on_legendItemClicked(self, event):
        if event.getButtons() & MouseEvent.LEFT_BUTTON:
            event.curve.visible = not event.curve.visible
            self.update()

    def on_timeSeriesUpdate(self, series):
        curve = self.plotcurves[series]
        curve.x = series.x
        curve.y = series.y
        c = self.axes.getCurves()
        dy = abs(c.ymin - c.ymax) * 0.05
        self.axes.setWindow(c.xmin, c.xmax, c.ymin - dy, c.ymax + dy)
        self.widget.update()
        self.ctimers[curve].start(5000)

    def on_keyChange(self, key, value, time, expired):
        if key not in self.keyexprs or value is None:
            return
        for expr in self.keyexprs[key]:
            series = self.series[key, expr]
            # restrict time of value to 1 minute past at
            # maximum, so that it doesn't get culled by the windowing
            time = max(time, currenttime() - 60)
            series.addValue(time, value)

    def addcurve(self, key, expr, title):
        series = TimeSeries(title, self.props['plotinterval'], expr,
                            self.props['plotwindow'], self)
        series.initEmpty()
        curve = PlotCurve([currenttime()], [0], legend=title)
        self.plotcurves[series] = curve
        self.ncurves += 1
        self.curves.append(curve)
        self.axes.addCurves(curve)
        self.series[key, expr] = series
        self.widget.update()

        # record the current value at least every 5 seconds, to avoid curves
        # not updating if the value doesn't change
        def update():
            series.synthesizeValue()
        self.ctimers[curve] = QTimer(singleShot=True)
        self.ctimers[curve].timeout.connect(update)

    def registerKeys(self):
        for keyexpr, title in itertools.zip_longest(self.props['devices'],
                                                    self.props['names']):
            if title is None:
                title = keyexpr
            key, expr, _ = parseKeyExpression(keyexpr)
            keyid = self._source.register(self, key)
            if (keyid, expr) not in self.series:
                self.keyexprs.setdefault(keyid, []).append(expr)
                self.addcurve(keyid, expr, title)
