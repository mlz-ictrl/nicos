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

"""Qt version of instrument monitor."""

import sys
import traceback

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4 import uic
from PyQt4.QtGui import QFrame, QLabel, QPalette, QMainWindow, QVBoxLayout, \
    QColor, QFont, QFontMetrics, QSizePolicy, QHBoxLayout, QApplication, \
    QCursor, QIcon
from PyQt4.QtCore import Qt, pyqtSignal

from nicos.core import Param
from nicos.utils import findResource, checkSetupSpec
from nicos.services.monitor import Monitor as BaseMonitor
from nicos.guisupport.widget import NicosWidget
from nicos.guisupport.display import ValueDisplay, PictureDisplay, \
    lightColorScheme
from nicos.clients.gui.utils import SettingGroup, loadBasicWindowSettings
from nicos.pycompat import iteritems, string_types

try:
    from nicos.guisupport.plots import TrendPlot
    plot_available = True
except (RuntimeError, ImportError):
    plot_available = False


class MonitorWindow(QMainWindow):
    _wantFullScreen = False

    keyChange = pyqtSignal(object, object)
    reconfigure = pyqtSignal(object)
    updateTitle = pyqtSignal(str)
    switchWarnPanel = pyqtSignal(bool)

    def __init__(self):
        self._reconfiguring = False
        QMainWindow.__init__(self)
        # set app icon in multiple sizes
        icon = QIcon()
        icon.addFile(':/appicon')
        icon.addFile(':/appicon-16')
        icon.addFile(':/appicon-48')
        self.setWindowIcon(icon)

        self.keyChange.connect(lambda obj, args: obj.on_keyChange(*args))
        self.reconfigure.connect(self.do_reconfigure)

        self.sgroup = SettingGroup('Monitor')
        with self.sgroup as settings:
            # geometry and window appearance
            loadBasicWindowSettings(self, settings)

    def keyPressEvent(self, event):
        if event.text() == 'q':
            self.close()
        elif event.text() == 'f':
            self._wantFullScreen = not self._wantFullScreen
            if self._wantFullScreen:
                self.showFullScreen()
            else:
                self.showNormal()
        elif event.text() == 'r':
            # resize/refresh/redraw
            self.resize(self.sizeHint())
        return QMainWindow.keyPressEvent(self, event)

    def closeEvent(self, event):
        with self.sgroup as settings:
            settings.setValue('geometry', self.saveGeometry())
        event.accept()

    def event(self, event):
        if self._reconfiguring and event.type() == 76:  # LayoutRequest
            self._reconfiguring = False
            # always resize first; works around layout bugs where the full
            # screen window is actually made larger than the full screen
            self.resize(self.sizeHint())
            if self._wantFullScreen:
                self.showFullScreen()
        return QMainWindow.event(self, event)

    def do_reconfigure(self, emitdict):
        self._reconfiguring = True
        for (layout, blockbox), enabled in iteritems(emitdict):
            blockbox.enableDisplay(layout, enabled)
        self.layout().activate()


class BlockBox(QFrame):
    """Provide the equivalent of a Tk LabelFrame: a group box that has a
    definite frame around it.
    """

    def __init__(self, parent, text, font, config=None):
        config = config or {}
        if config.get('frames', True):
            QFrame.__init__(self, parent, frameShape=QFrame.Panel,
                            frameShadow=QFrame.Raised, lineWidth=2)
        else:
            QFrame.__init__(self, parent, frameShape=QFrame.NoFrame)
        self._label = None
        if text:
            self._label = QLabel(' ' + text + ' ', parent,
                                 autoFillBackground=True, font=font)
            self._label.resize(self._label.sizeHint())
            self._label.show()

    def moveEvent(self, event):
        self._repos()
        return QFrame.moveEvent(self, event)

    def resizeEvent(self, event):
        self._repos()
        return QFrame.resizeEvent(self, event)

    def _repos(self):
        if self._label:
            mps = self.pos()
            msz = self.size()
            lsz = self._label.size()
            self._label.move(mps.x() + 0.5*(msz.width() - lsz.width()),
                             mps.y() - 0.5*lsz.height())

    def enableDisplay(self, layout, isvis):
        QFrame.setVisible(self, isvis)
        if self._label:
            self._label.setVisible(isvis)
        if not isvis:
            layout.removeWidget(self)
        else:
            layout.insertWidget(1, self)
        self.updateGeometry()


class Monitor(BaseMonitor):
    """Qt specific implementation of instrument monitor."""

    parameters = {
        'noexpired': Param('If true, show expired values as "n/a"', type=bool)
    }

    _master = None

    def mainLoop(self):
        self._qtapp.exec_()

    def closeGui(self):
        if self._master:
            self._master.close()

    def _class_import(self, clsname):
        modname, member = clsname.rsplit('.', 1)
        mod = __import__(modname, None, None, [member])
        return getattr(mod, member)

    def initGui(self):
        def log_unhandled(*exc_info):
            traceback.print_exception(*exc_info)  # pylint: disable=no-value-for-parameter
            self.log.exception('unhandled exception in QT callback',
                               exc_info=exc_info)
        sys.excepthook = log_unhandled

        self._qtapp = QApplication(['qtapp'],# '-style', 'windows'],
                                   organizationName='nicos',
                                   applicationName='gui',
                                  )
        self._master = master = MonitorWindow()
        master.show()

        if self._geometry == 'fullscreen':
            master.showFullScreen()
            master._wantFullScreen = True
            QCursor.setPos(master.geometry().bottomRight())
        elif isinstance(self._geometry, tuple):
            w, h, x, y = self._geometry  # pylint: disable=W0633
            master.setGeometry(x, y, w, h)

        # colors used for the display of watchdog warnings, not for the
        # individual value displays
        self._bgcolor = QColor('gray')
        self._black = QColor('black')
        self._red = QColor('red')
        self._gray = QColor('gray')

        master.setWindowTitle(self.title)
        self._bgcolor = master.palette().color(QPalette.Window)

        timefont  = QFont(self.font, self._timefontsize)
        blockfont = QFont(self.font, self._fontsizebig)
        warnfont  = QFont(self.font, self._fontsizebig)
        warnfont.setBold(True)
        labelfont = QFont(self.font, self._fontsize)
        stbarfont = QFont(self.font, int(self._fontsize * 0.8))
        valuefont = QFont(self.valuefont or self.font, self._fontsize)

        blheight = QFontMetrics(blockfont).height()
        tiheight = QFontMetrics(timefont).height()

        # split window into to panels/frames below each other:
        # one displays time, the other is divided further to display blocks.
        # first the timeframe:
        masterframe = QFrame(master)
        masterlayout = QVBoxLayout()
        self._titlelabel = QLabel('', master,
            font=timefont, autoFillBackground=True, alignment=Qt.AlignHCenter)
        pal = self._titlelabel.palette()
        pal.setColor(QPalette.WindowText, self._gray)
        self._titlelabel.setPalette(pal)
        self._titlelabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._master.updateTitle.connect(self._titlelabel.setText)

        masterlayout.addWidget(self._titlelabel)
        masterlayout.addSpacing(0.2 * tiheight)

        self._warnpanel = QFrame(master)
        self._warnpanel.setVisible(False)

        warningslayout = QVBoxLayout()
        lbl = QLabel('Warnings', self._warnpanel, font=warnfont)
        lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        warningslayout.addWidget(lbl)
        self._warnlabel = QLabel('', self._warnpanel, font=blockfont)
        warningslayout.addWidget(self._warnlabel)
        self._warnpanel.setLayout(warningslayout)
        masterlayout.addWidget(self._warnpanel)
        master.switchWarnPanel.connect(self._switch_warnpanel)

        displayframe = QFrame(master)
        self._plots = {}

        colorScheme = lightColorScheme if self.colors == 'light' else None

        def _create_field(groupframe, field):

            def _setup(widget):
                widget.valueFont = valuefont
                widget.setFont(labelfont)
                for key in field:
                    if key in widget.properties:
                        setattr(widget, key, field[key])
                widget.setSource(self)
                if hasattr(widget, 'widgetInfo'):
                    widget.widgetInfo.connect(self.newWidgetInfo)
                return widget

            if isinstance(field, string_types):
                field = {'dev': field}
            if 'min' in field:
                field['min'] = repr(field['min'])
            if 'max' in field:
                field['max'] = repr(field['max'])

            if 'gui' in field:
                resource = findResource(field.pop('gui'))
                try:
                    instance = uic.loadUi(resource)
                except Exception as err:
                    self.log.exception('could not load .ui file %r, ignoring',
                                       resource)
                    return QLabel('%r could not be loaded:\n%s' %
                                  (resource, err))
                for child in instance.findChildren(NicosWidget):
                    _setup(child)
                return instance
            elif 'widget' in field:
                widget_class = self._class_import(field.pop('widget'))
                widget = widget_class(groupframe)
                if isinstance(widget, NicosWidget):
                    _setup(widget)
                for child in widget.findChildren(NicosWidget):
                    _setup(child)
                return widget
            elif 'plot' in field and plot_available:
                # XXX make this more standard
                plotwidget = self._plots.get(field['plot'])
                if plotwidget:
                    plotwidget.devices += [field.get('dev', field.get('key', ''))]
                    plotwidget.names += [field.get('name', field.get('dev', field.get('key', '')))]
                    return None
                plotwidget = TrendPlot(groupframe)
                _setup(plotwidget)
                plotwidget.legend = field.get('legend', True)
                plotwidget.plotwindow = field.get('plotwindow', 3600)
                plotwidget.plotinterval = field.get('plotinterval', 2)
                self._plots[field['plot']] = plotwidget
                plotwidget.devices = [field.get('dev', field.get('key', ''))]
                plotwidget.names = [field.get('name', field.get('dev', field.get('key', '')))]
                return plotwidget
            elif 'picture' in field:
                picwidget = PictureDisplay(groupframe)
                picwidget.filepath = field['picture']
                return _setup(picwidget)
            else:
                display = ValueDisplay(groupframe, colorScheme=colorScheme,
                                       showExpiration=self.noexpired)
                return _setup(display)

        # now iterate through the layout and create the widgets to display it
        displaylayout = QVBoxLayout(spacing=20)
        for superrow in self.layout:
            boxlayout = QHBoxLayout(spacing=20)
            boxlayout.setContentsMargins(10, 10, 10, 10)
            for column in superrow:
                columnlayout = QVBoxLayout(spacing=0.8*blheight)
                for block in column:
                    blockconfig = block[1] if len(block) > 1 else None
                    block = block[0]
                    blocklayout_outer = QHBoxLayout()
                    blocklayout_outer.addStretch()
                    blocklayout = QVBoxLayout()
                    blocklayout.addSpacing(0.5 * blheight)
                    blockbox = BlockBox(displayframe, block[0], blockfont,
                                        blockconfig)
                    for row in block[1]:
                        if row in (None, '---'):
                            blocklayout.addSpacing(12)
                        else:
                            rowlayout = QHBoxLayout()
                            rowlayout.addStretch()
                            rowlayout.addSpacing(self._padding)
                            for field in row:
                                fieldwidget = _create_field(blockbox, field)
                                if fieldwidget:
                                    rowlayout.addWidget(fieldwidget)
                                    rowlayout.addSpacing(self._padding)
                            rowlayout.addStretch()
                            blocklayout.addLayout(rowlayout)
                    if blockconfig:
                        setups = blockconfig.get('setups', [])
                        blockbox.setHidden(True)  # start hidden
                        setupnames = [setups] if isinstance(setups, string_types) \
                                     else setups
                        for setupname in setupnames:
                            self._onlymap.setdefault(setupname, []).append(
                                (blocklayout_outer, blockbox))
                    blocklayout.addSpacing(0.3 * blheight)
                    blockbox.setLayout(blocklayout)
                    blocklayout_outer.addWidget(blockbox)
                    blocklayout_outer.addStretch()
                    columnlayout.addLayout(blocklayout_outer)
                columnlayout.addStretch()
                boxlayout.addLayout(columnlayout)
            displaylayout.addLayout(boxlayout)
        displayframe.setLayout(displaylayout)

        for plot in self._plots.values():
            plot.setSource(self)

        masterlayout.addWidget(displayframe)

        masterframe.setLayout(masterlayout)
        master.setCentralWidget(masterframe)

        # initialize status bar
        self._statuslabel = QLabel(font=stbarfont)
        master.statusBar().addWidget(self._statuslabel)
        self._statustimer = None

    def signalKeyChange(self, obj, *args):
        self._master.keyChange.emit(obj, args)

    def newWidgetInfo(self, info):
        self._statuslabel.setText(info)

    def updateTitle(self, title):
        self._master.updateTitle.emit(title)

    def switchWarnPanel(self, on):
        self._master.switchWarnPanel.emit(on)

    def _switch_warnpanel(self, on):
        if on:
            pal = self._titlelabel.palette()
            pal.setColor(QPalette.WindowText, self._black)
            pal.setColor(QPalette.Window, self._red)
            self._titlelabel.setPalette(pal)
            self._warnlabel.setText(self._currwarnings)
            self._warnpanel.setVisible(True)
            self._master.update()
        else:
            self._warnpanel.setVisible(False)
            pal = self._titlelabel.palette()
            pal.setColor(QPalette.WindowText, self._gray)
            pal.setColor(QPalette.Window, self._bgcolor)
            self._titlelabel.setPalette(pal)
            # resize to minimum
            self.reconfigureBoxes()
            # self._master.update()

    def reconfigureBoxes(self):
        emitdict = {}
        for setup, boxes in iteritems(self._onlymap):
            enabled = checkSetupSpec(setup, self._setups,
                                     compat='and', log=self.log)
            for k in boxes:
                emitdict[k] = emitdict.get(k, True) and enabled
        self._master.reconfigure.emit(emitdict)
