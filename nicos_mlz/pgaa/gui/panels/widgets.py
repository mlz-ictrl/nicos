#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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
#   Johannes Schwarz <johannes.schwarz@frm2.tum.de>
#
# *****************************************************************************
"""PGAA panel specific widgets."""

from __future__ import print_function

import time
from collections import OrderedDict
from os import path

from nicos.core import status
from nicos.guisupport.led import ClickableOutputLed
from nicos.guisupport.qt import QAbstractButton, QAbstractSpinBox, QCheckBox, \
    QComboBox, QCursor, QDateTime, QDateTimeEdit, QDoubleValidator, \
    QHBoxLayout, QIntValidator, QLCDNumber, QLabel, QLineEdit, QPainter, \
    QPixmap, QSlider, QSpinBox, QStackedWidget, QToolTip, QWidget, Qt, \
    pyqtSignal, pyqtSlot
from nicos.guisupport.widget import NicosListener, NicosWidget
from nicos.pycompat import iteritems

widgetpath = path.dirname(__file__)


class Led(ClickableOutputLed):

    def __init__(self, dev, active, inactive, client, parent=None,
                 designMode=False, colorActive='red', colorInactive='green'):
        ClickableOutputLed.__init__(self, parent, designMode=designMode)
        self.dev = dev

        self._colorActive = colorActive
        self._colorInactive = colorInactive

        self.stateActive = 1 if active is None else active
        self.stateInactive = 0 if inactive is None else inactive

        self.setClient(client)

    def on_keyChange(self, key, value, time, expired):
        self.ledStatus = not expired
        if self._goalval is not None:
            value = self._goalval
        if value == self._stateActive:
            self.ledColor = self._colorActive
        else:
            self.ledColor = self._colorInactive
        self.current = value

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.current == self._stateActive:
                self._client.tell('exec', '%s.move(%r)' %
                                  (self.dev, self._stateInactive))
            else:
                self._client.tell('exec', '%s.move(%r)' %
                                  (self.dev, self._stateActive))

            event.accept()
        else:
            event.ignore()


class CustomLED(ClickableOutputLed):
    """Just views to what state the Attenuator should/will be set."""

    valueChanged = pyqtSignal(int)

    def __init__(self, container, state_names=('in', 'out'),
                 state_colors=('blue', 'yellow'), initState=None):
        ClickableOutputLed.__init__(self, parent=container)
        self.stateActive = state_names[0]
        self.stateInactive = state_names[1]
        self._colorActive = state_colors[0]
        self._colorInactive = state_colors[1]
        self.current = initState
        self.set_ledcolor()

    def set_ledcolor(self):
        self.ledColor = self._colorActive \
            if self.current == self._stateActive else self._colorInactive

    def setValue(self, val):
        self.current = val
        self.set_ledcolor()

    def value(self):
        return self.current

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setValue(
                self._stateInactive if self.current == self._stateActive
                else self._stateActive)
            self.valueChanged[int].emit(self.current)
            event.accept()


class PicButton(QAbstractButton):

    def __init__(self, pixmap1, pixmap2, parent=None):
        QAbstractButton.__init__(self, parent)
        self.pixmap1 = pixmap1.scaledToWidth(50)
        self.pixmap2 = pixmap2.scaledToWidth(50)
        self.setFixedSize(30, 25)
        self.setCheckable(True)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(),
                           self.pixmap1 if self.isChecked() else self.pixmap2)
        event.accept()

    def sizeHint(self):
        return self.pixmap1.size()


class CustomCombo(QComboBox):

    valueChanged = pyqtSignal(int)

    def __init__(self, container=None, box_data=None, init_state=None):
        QComboBox.__init__(self, parent=container)
        self.current = init_state
        for item in box_data:
            self.addItem('%s' % item)
        self.setCurrentIndex(self.current)
        self.currentIndexChanged[int].connect(self.index_changed)

    @pyqtSlot(int)
    def index_changed(self, index):
        # self.setDisabled(True)
        self.valueChanged[int].emit(index)

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            if self.parent():
                self.parent().mousePressEvent(e)
        else:
            QComboBox.mousePressEvent(self, e)

    def setValue(self, val):
        self.current = val
        self.setCurrentIndex(self.findText('%s' % val))
        self.setEnabled(True)

    def value(self):
        return self.currentText()


class TimeEditWidget(QWidget):
    units = ('s', 'm', 'h', 'd')

    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0.1, 0.1, 0.1, 0.1)
        self.layout().setSpacing(1)
        self.val = QLineEdit()
        self.val.setValidator(QDoubleValidator(0, 1000000, 2))
        self.layout().addWidget(self.val)
        self.unit = QComboBox()
        self.unit.insertItems(0, self.units)
        self.layout().addWidget(self.unit)
        self.setValue(1)
        self.val.returnPressed.connect(self.on_returnPressed)
        self.val.editingFinished.connect(self.on_returnPressed)
        self.unit.currentIndexChanged.connect(self.recalcValue)

    def value(self):
        val = float(self.val.text())
        current_unit_index = self.unit.currentIndex()
        if current_unit_index == 1:  # minutes
            val *= 60.
        elif current_unit_index == 2:  # hours
            val *= 3600.
        elif current_unit_index == 3:  # days
            val *= 86400.
        return int(val)

    def setValue(self, val):
        fmt = '%%.%df' % self.val.validator().decimals()
        self.val.setText(fmt % float(val))
        self.unit.setCurrentIndex(0)
        self.currentUnit = 0

    def recalcValue(self, idx):
        # adjust widget value to unit
        unit_index_current = self.currentUnit
        unit_index_next = idx
        if unit_index_next > unit_index_current:
            start = unit_index_current
            end = unit_index_next
        elif unit_index_next < unit_index_current:
            start = unit_index_next
            end = unit_index_current
        val = float(self.val.text())
        factor = 1.
        for i in range(start, end):
            if self.units[i + 1] == 'd':
                factor *= 24.
            else:
                factor *= 60.
        if unit_index_next - unit_index_current > 0:
            factor = 1. / factor
        next_value = val * factor
        self.val.setText('%s' % next_value)
        self.currentUnit = idx

    def on_returnPressed(self):
        self.returnPressed.emit()


class ValueData(QStackedWidget):

    valueChanged = pyqtSignal([int], [float])

    def __init__(self, parent=None, init_widget_info=None, initState=None):
        QStackedWidget.__init__(self, parent)
        self.trueLive = TimeEditWidget(self)
        self.trueLive.setValue(1.0)

        self.clockTime = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.counts = QSpinBox(self)

        self.widget_types = {
            'LiveTime': self.trueLive,
            'TrueTime': self.trueLive,
            'ClockTime': self.clockTime,
            'counts': self.counts,
        }

        self.counts.setRange(0, 1000000000)
        self.counts.setSingleStep(50000)

        # config QDateTime:
        self.clockTime.setButtonSymbols(QAbstractSpinBox.NoButtons)

        # add widgets to Stack
        self.addWidget(self.trueLive)
        self.addWidget(self.clockTime)
        self.addWidget(self.counts)

        # Init given current widget with data (time.. etc)
        self.setCurrentWidget(self.widget_types[init_widget_info])

        self.setValue(initState)

        self.trueLive.returnPressed.connect(self.on_returnPressed)
        self.clockTime.editingFinished.connect(self.on_dt_changed)
        self.counts.valueChanged[str].connect(self.on_cts_changed)
        self.setMinimumWidth(90)

    def setWidget(self, widget_desc):
        new_widget = self.widget_types[widget_desc]
        if new_widget != self.currentWidget():
            self.setCurrentWidget(new_widget)
            cvalue = self.value()
            self.setValue(cvalue)
            # if widget_desc == 'counts':
            #     self.valueChanged[int].emit(self.value())
            # else:
            #     self.valueChanged[float].emit(self.value())

    def setValue(self, new_data):
        w = self.currentWidget()
        if isinstance(w, TimeEditWidget):
            w.setValue(new_data)
        elif isinstance(w, QDateTimeEdit):
            dt = QDateTime()
            dt.setMSecsSinceEpoch(float(new_data) * 1000)
            w.setDateTime(dt)
        elif isinstance(w, QSpinBox):
            w.setValue(int(new_data))
        self.current = new_data
        self.setEnabled(True)

    def value(self, key=None):
        w = self.widget_types.get(key)
        if w is None:
            w = self.currentWidget()
        if isinstance(w, TimeEditWidget):
            return float(w.value())
        elif isinstance(w, QDateTimeEdit):
            return float(w.dateTime().toMSecsSinceEpoch() / 1000.)
        elif isinstance(w, QSpinBox):
            return w.value()

    def on_returnPressed(self):
        value = self.trueLive.value()
        self.valueChanged[float].emit(value)

    def on_dt_changed(self):
        stamp = self.clockTime.dateTime().toMSecsSinceEpoch() / 1000.
        self.valueChanged[float].emit(stamp)

    def on_cts_changed(self):
        cts = self.counts.value()
        self.valueChanged[int].emit(cts)


class CellItem(QWidget):
    standard_value = ''

    cellChanged = pyqtSignal('QWidget')

    def __init__(self, controller, parent=None, state=None):
        QWidget.__init__(self, parent)

        # update Request for parameter gets sent to controller
        self.controller = controller

        # contains widgets that are currently displayed
        self.widgets = []
        self.state = state if state is not None else self.standard_value
        self.doubleclick = None

        # setting up layout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0.1, 0.1, 0.1, 0.1)
        layout.setSpacing(1)
        self.setLayout(layout)

    def set_enabled(self, enabled):
        for widget in self.widgets:
            widget.setEnabled(enabled)
        # some
        self.reloadstate()

    def reloadstate(self):
        pass

    def is_enabled(self):
        return max(w.isEnabled() for w in self.widgets)

    def set_layout(self):
        for w in self.widgets:
            self.layout().addWidget(w)

    def setValue(self, val):
        self.label.setText('%s' % val)

    def value(self):
        return self.label.text()

    def disable(self):
        for w in self.widgets:
            w.setDisabled(True)

    def mouseDoubleClickEvent(self, e):
        for w in self.widgets:
            w.setEnabled(True)
        if self.doubleclick is not None:
            self.doubleclick = True
        e.ignore()


class AttCell(CellItem):
    Attenuators = OrderedDict([
        (1.6, ('in', 'in', 'in')),
        (2.7, ('in', 'out', 'in')),
        (3.5, ('out', 'in', 'in')),
        (5.9, ('out', 'out', 'in')),
        (7.5, ('in', 'in', 'out')),
        (16., ('in', 'out', 'out')),
        (47., ('out', 'in', 'out')),
        (100., ('out', 'out', 'out')),
    ])

    standard_value = 100.

    def __init__(self, controller, parent=None, state=None):
        # AttCell can have two different view options:
        # viewing 3 Button for each Attenuator or a Combobox, displaying the
        # percentage of the Neutron Flux
        CellItem.__init__(self, controller, parent, state)

        self.state = float(self.state)
        self.cb = CustomCombo(
            None, box_data=list(AttCell.Attenuators.keys()),
            init_state=list(AttCell.Attenuators).index(self.state))
        self.widgets.append(self.cb)
        self.cled = []
        for i in range(3):
            self.cled.append(CustomLED(
                None, initState=AttCell.Attenuators[self.state][i]))
            self.widgets.append(self.cled[i])
            self.cled[i].hide()
            self.cled[i].valueChanged[int].connect(self.on_led_changed)
        self.cb.valueChanged[int].connect(self.on_cb_changed)
        self.set_layout()

    def setValue(self, value):
        if value in AttCell.Attenuators:
            self.state = float(value)
            if not self.cb.isVisible():
                for i, led in enumerate(self.cled):
                    led.setValue(AttCell.Attenuators[self.state][i])
            self.cb.setValue(self.state)

    def value(self):
        if not self.cb.isVisible():
            # Count back from 3 Attenuator Buttons to rel Flux
            att_vals = tuple(l.current for l in self.cled)
            for key, values in iteritems(AttCell.Attenuators):
                if values == att_vals:
                    return key
        else:
            return float(self.cb.currentText())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            cbvis = self.cb.isVisible()
            self.cb.setVisible(not cbvis)
            for w in self.cled:
                w.setVisible(cbvis)
            e.accept()

    @pyqtSlot(int)
    def on_cb_changed(self, index):
        self.cellChanged.emit(self)

    @pyqtSlot(int)
    def on_led_changed(self, val):
        self.cellChanged.emit(self)


class PosCell(CellItem):

    standard_value = 4

    def __init__(self, controller, parent=None, state=None):
        CellItem.__init__(self, controller, parent, state)
        self.cb = CustomCombo(self, box_data=range(1, 16 + 1),
                              init_state=int(state) - 1)
        self.widgets.append(self.cb)
        self.set_layout()
        self.setMaximumWidth(45)
        self.cb.valueChanged[int].connect(self.on_cb_changed)

    def setValue(self, newData):
        if newData in range(1, 16 + 1):
            self.cb.setValue(newData)

    def value(self):
        return int(self.cb.value())

    @pyqtSlot(int)
    def on_cb_changed(self, index):
        self.cellChanged.emit(self)


class BeamCell(CellItem):
    standard_value = 'open'

    def __init__(self, controller, parent=None, state=None):
        CellItem.__init__(self, controller, parent, state)

        self.led = CustomLED(self, state_names=('open', 'closed'),
                             state_colors=('red', 'green'),
                             initState=self.state)
        self.widgets.append(self.led)
        self.set_layout()
        self.led.valueChanged[int].connect(self.on_led_changed)

    def setValue(self, new_data):
        self.led.setValue(new_data)

    def value(self):
        return self.led.value()

    @pyqtSlot(int)
    def on_led_changed(self, val):
        self.cellChanged.emit(self)


class ValueCell(CellItem):
    standard_value = 1
    units = ('s', 'm', 'h', 'd')

    def __init__(self, controller, parent, state=None):
        CellItem.__init__(self, controller, parent, state)
        condition = CondCell.standard_value
        self.vd = ValueData(self, condition, self.state)
        self.widgets.append(self.vd)
        self.set_layout()
        self.setMinimumWidth(70)
        self.vd.valueChanged[int].connect(self.valueChanged)
        self.vd.valueChanged[float].connect(self.valueChanged)

    def setValue(self, new_data):
        next_val = float(new_data)
        self.vd.setValue(next_val)
        self.state = next_val

    def value(self, key=None):
        return self.vd.value(key)

    @pyqtSlot(int)
    @pyqtSlot(float)
    def valueChanged(self, val):
        self.cellChanged.emit(self)

    @pyqtSlot(str)
    def condCellChanged(self, val):
        self.vd.setWidget(val)


class CondCell(CellItem):
    standard_value = 'TrueTime'
    conds = ('LiveTime', 'TrueTime', 'ClockTime', 'counts')

    condChanged = pyqtSignal(str)

    def __init__(self, controller, parent=None, state=None):
        CellItem.__init__(self, controller, parent, state)
        index = int(self.conds.index(self.state))
        self.cc = CustomCombo(container=self, box_data=self.conds,
                              init_state=index)
        self.cc.valueChanged[int].connect(self.on_cb_changed)
        self.widgets.append(self.cc)
        self.set_layout()
        self.setMaximumWidth(100)

    def setValue(self, new_data):
        if new_data in CondCell.conds:
            self.cc.setValue(new_data)
            self.state = new_data
            self.condChanged.emit(new_data)

    def value(self):
        return self.cc.currentText()

    @pyqtSlot(int)
    def on_cb_changed(self, index):
        self.cellChanged.emit(self)
        self.condChanged.emit(self.value())


class StatusCell(CellItem):

    def __init__(self, controller, parent=None, state=None):
        CellItem.__init__(self, controller, parent, state)
        self.label = QLabel('%s' % self.state)
        self.label.setAlignment(Qt.AlignCenter)
        self.widgets.append(self.label)
        self.set_layout()
        self.setMinimumWidth(20)


class StartCell(CellItem):
    standard_value = [int(time.time()), 0]

    def __init__(self, controller, parent=None, state=None):
        CellItem.__init__(self, controller, parent, state)
        if not state:
            state = self.standard_value
        # widgets = QStackedWidget(self)

        self.date_widget = QDateTimeEdit(self)
        self.date_widget.setButtonSymbols(QAbstractSpinBox.NoButtons)

        # widgets.addWidget(self.date_widget)
        # self.delay_widget = QLabel('after %s seconds' %self.state[1])
        # widgets.addWidget(self.delay_widget)
        self.widgets.append(self.date_widget)
        # if self.state[0] > 0:
        #     self.widgets[0].setCurrentWidget(self.date_widget)
        # else:
        #     self.widgets[0].setCurrentWidget(self.delay_widget)

        self.date_widget.editingFinished.connect(self.on_dt_changed)
        self.set_layout()
        self.setValue(state)

    def setValue(self, new_data):
        self.state[0] = int(float(new_data[0]))
        self.state[1] = int(float(new_data[1]))
        dt = QDateTime()
        dt.setMSecsSinceEpoch(self.state[0] * 1000)
        self.date_widget.setDateTime(dt)

    def value(self):
        dt = int(self.date_widget.dateTime().toMSecsSinceEpoch() / 1000.)
        return '[%s,%s]' % (dt, self.state[1])

    # def mousePressEvent(self, e):
    #    if e.button() == Qt.RightButton:
    #        if self.widgets[0].currentIndex() == 0:
    #            self.widgets[0].setCurrentWidget(self.delay_widget)
    #        elif self.widgets[0].currentIndex() == 1:
    #            now = int(time.time())
    #            self.widgets[0].setCurrentWidget(self.date_widget)
    #            #self.date_widget.setDisabled(True)
    #            self.get_update(self.date_widget,now)
    #    else:
    #        CellItem.mousePressEvent(self, e)

    def on_dt_changed(self):
        self.cellChanged.emit(self)


class NameCommentCell(CellItem):

    def __init__(self, controller, parent=None, state=None):
        CellItem.__init__(self, controller, parent, state)
        self.le = QLineEdit(self.state)
        self.le.returnPressed.connect(self.on_return_pressed)
        self.le.editingFinished.connect(self.on_return_pressed)
        self.widgets.append(self.le)
        self.set_layout()
        self.setMaximumWidth(130)

    def reloadstate(self):
        text = str(self.le.text())
        if not text == self.state:
            self.cellChanged.emit(self)

    def on_return_pressed(self):
        self.cellChanged.emit(self)

    def value(self):
        return self.le.text()

    def setValue(self, val):
        self.le.setText(val)
        self.state = val

    def mouseDoubleClickEvent(self, e):
        CellItem.mouseDoubleClick(self, e)
        if e.button() == Qt.LeftButton:
            self.le.setFocus()
            e.accept()


class ElColCell(CellItem):
    standard_value = 'Col'

    def __init__(self, controller, parent=None, state=None):
        CellItem.__init__(self, controller, parent, state)
        pixmap1 = QPixmap(path.join(widgetpath, 'focus.png'))
        pixmap2 = QPixmap(path.join(widgetpath, 'collimator.png'))
        self.picbtn = PicButton(pixmap1, pixmap2, parent=self)
        self.widgets.append(self.picbtn)
        self.set_layout()
        self.picbtn.clicked.connect(self.on_clicked)
        self.setValue(state)

    def setValue(self, new_data):
        self.picbtn.setChecked(new_data == 'Ell')
        self.picbtn.update()

    def value(self):
        return 'Ell' if self.picbtn.isChecked() else 'Col'

    def on_clicked(self, val):
        self.cellChanged.emit(self)


class DetectorCell(CellItem):
    standard_value = ['_60p', 'LEGe']

    def __init__(self, controller, parent=None, state=None):
        CellItem.__init__(self, controller, parent, state)
        self.cb_60p = QCheckBox('60%', parent=self)
        self.widgets.append(self.cb_60p)
        self.cb_leg = QCheckBox('LEGe', parent=self)
        self.widgets.append(self.cb_leg)

        self.set_layout()
        self.setMaximumWidth(120)
        self.setValue(state)

        self.cb_leg.stateChanged.connect(self.on_statechanged)
        self.cb_60p.stateChanged.connect(self.on_statechanged)

    def setValue(self, data):
        self.cb_60p.setChecked('_60p' in data)
        self.cb_leg.setChecked('LEGe' in data)

    def value(self):
        s = []
        if self.cb_60p.isChecked():
            s.append('_60p')
        if self.cb_leg.isChecked():
            s.append('LEGe')
        return s

    def on_statechanged(self, state):
        self.cellChanged.emit(self)


class FileNum(NicosListener, QLineEdit):

    def __init__(self, client, parent=None):
        QLineEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.setValidator(QIntValidator(0, 99999, self))
        self._client = client
        self.setSource(self._client)

    def registerKeys(self):
        self.registerKey('csvsink/filecount')

    def on_keyChange(self, key, value, time, expired):
        self.setText('%s' % value)

    def mouseDoubleClickEvent(self, e):
        self.setReadOnly(False)

    def keyPressEvent(self, e):
        if e.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self._client.tell('exec', 'csvsink.filecount = %s' % int(self.text()))
            self.setReadOnly(True)
        else:
            QLineEdit.keyPressEvent(self, e)


class VacuumView(NicosListener, QLineEdit):

    def __init__(self, client, parent=None):
        QLineEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.setDisabled(True)
        self.setSource(client)

    def registerKeys(self):
        self.registerDevice('chamber_pressure')

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self.setText('%s' % unitvalue)


class MotorValue(NicosWidget, QLCDNumber):

    def __init__(self, client, parent=None):
        QLCDNumber.__init__(self, parent)
        NicosWidget.__init__(self)
        self.setSegmentStyle(QLCDNumber.Flat)
        self.setClient(client)

    def registerKeys(self):
        self.registerDevice('samplemotor')

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self.display(int(value))


class DevSlider(NicosWidget, QSlider):

    def __init__(self, client, dev, valmin, valmax, step=1, parent=None):
        QSlider.__init__(self, parent)
        self.setMinimum(valmin)
        self.setMaximum(valmax)
        self.setSingleStep(step)
        NicosWidget.__init__(self)
        self._dev = dev
        self.setClient(client)
        # self.connect(self, SIGNAL('sliderReleased()'),
        #              self. on_slider_release)
        # self.connect(self, SIGNAL('sliderMoved(int)'), self.on_slider_moved)
        self.sliderReleased.connect(self.on_slider_release)
        self.sliderMoved[int].connect(self.on_slider_moved)

    def on_slider_moved(self, pos=0):
        QToolTip.showText(QCursor.pos(), str(pos), self)

    def on_slider_release(self):
        pos = '%s' % self.sliderPosition()
        self._client.tell('exec', '%s.move(%s)' % (self._dev, pos))

    def registerKeys(self):
        self.registerDevice(self._dev)

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        val = int(value)
        self.setValue(val)

    def on_devStatusChange(self, dev, state, state_, expired):
        self.setDisabled(state==status.BUSY)


class PushSlider(DevSlider):

    strmap = {
        'up': 1,
        'down': 0,
    }

    def __init__(self, client, dev, parent=None):
        DevSlider.__init__(self, client, dev, 0, 1, 1, parent)
        self.sliderMoved[int].connect(self.on_slider_changed)

    def on_slider_changed(self, pos):
        if pos == 0:
            pos = 'down'
        elif pos == 1:
            pos = 'up'
        self._client.tell('exec', '%s.move(%r)' % (self._dev, pos))

    # device value == 1 means 'down' 0 means 'up'. needs to be inverted here
    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        if value in self.strmap:
            val = self.strmap[value]
            DevSlider.on_devValueChange(self, dev, val, strvalue, unitvalue,
                                        expired)

    def on_slider_release(self):
        self.on_slider_changed(self.sliderPosition())


class ElCol(NicosWidget, QAbstractButton):

    def __init__(self, client, parent=None):
        QAbstractButton.__init__(self, parent)
        self.flag = False
        self.pixmap = QPixmap(path.join(widgetpath, 'focus.png'))
        self.pixmap2 = QPixmap(path.join(widgetpath, 'collimator.png'))

        NicosWidget.__init__(self)
        self.setClient(client)
        self.current = self._client.getDeviceValue('ellcol')
        self.currmap = self.pixmap if self.current == 'Ell' else self.pixmap2
        self.repaint()
        self.clicked.connect(self.on_clicked)

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.flag is False:
            painter.drawPixmap(event.rect(), self.currmap)
            self.rect = event.rect()
        else:
            pixmap = self.pixmap if self.current == 'Ell' else self.pixmap2
            painter.drawPixmap(event.rect(), pixmap)
            self.rect = event.rect()
            self.currmap = pixmap
            self.flag = False

    def registerKeys(self):
        self.registerDevice('ellcol')

    def on_devValueChange(self, dev, value, strvalue, unitvalue, expired):
        self.current = value
        self.flag = True
        self.repaint()

    def sizeHint(self):
        return self.pixmap.size()

    def enterEvent(self, event):
        pass

    def leaveEvent(self, event):
        pass

    def on_clicked(self):
        data = 'Ell' if self.current == 'Col' else 'Col'
        self._client.tell('exec', "ellcol.move('%s')" % data)
