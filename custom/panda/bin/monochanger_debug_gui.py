#!/usr/bin/env python
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
# Author:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Q'n'D, hacked together GUI for debugging PANDA's Monochanger"""

from __future__ import print_function

# This is supposed to be a custom instrument specific stand-alone tool!

import sys

from struct import pack, unpack
from pymodbus.client.sync import ModbusTcpClient # pylint: disable = F0401

from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QFrame, QLabel, QHBoxLayout, QVBoxLayout, \
     QPushButton, QLineEdit, QMainWindow


def Stati(status):
    l = []
    s = status >> 12
    if s & 8:
        l.append('-> ERROR%x <-' % s)
    elif s & 4:
        l.append('WARNING%x' % s)
    elif s & 2:
        l.append('BUSY')
    elif s & 1:
        l.append('IDLE')
    else:
        l.append('!!! INVALID STATUS !!!')
    return l


class BaseDev(QWidget):
    has_target = False
    has_status = False
    def __init__(self, model, name, addr):
        super(BaseDev, self).__init__()
        self.name = name
        self.model = model
        self.addr = addr

        self._namelabel = QLabel(name)
        self._namelabel.setMinimumWidth(120)
        self._namelabel.setMaximumWidth(120)
        #~ self._groupbox = QGroupBox(name)
        self._groupbox = QFrame()
        #~ self._groupbox.setFlat(False)
        #~ self._groupbox.setCheckable(False)
        self._hlayout = QHBoxLayout()
        self._hlayout.addWidget(self._namelabel)
        self._hlayout.addWidget(self._groupbox)
        self._hlayout.setSpacing(0)


        # inside of the groupbox there is a vbox with 1 or 2 hboxes
        self._inner_vbox = QVBoxLayout()
        self._groupbox.setLayout(self._inner_vbox)

        # upper inner hbox
        self._inner_hbox1 = QHBoxLayout()
        self._inner_vbox.addLayout(self._inner_hbox1)

        # fill upper hbox
        self.valueWidget = QLineEdit('0b123456789abcdef0')
        self.valueWidget.setMaximumWidth(120)
        self._inner_hbox1.addWidget(self.valueWidget)

        if self.has_target:
            self.targetWidget = QLineEdit()
            self.targetWidget.setPlaceholderText('')
            self.targetWidget.setMaximumWidth(120)
            self.targetWidget.returnPressed.connect(self._go_clicked)
            self._inner_hbox1.addWidget(self.targetWidget)
            self.goButton = QPushButton('Go')
            self.goButton.clicked.connect(self._go_clicked)
            self._inner_hbox1.addWidget(self.goButton)
            self.stopButton = QPushButton('Stop')
            self.stopButton.clicked.connect(self._stop_clicked)
            self._inner_hbox1.addWidget(self.stopButton)


        # now (conditionally) the second hbox
        if self.has_status:
            self._inner_hbox2 = QHBoxLayout()
            self._inner_vbox.addLayout(self._inner_hbox2)

            self.statvalueWidget = QLineEdit('statval')
            self.statvalueWidget.setMaximumWidth(120)
            self._inner_hbox2.addWidget(self.statvalueWidget)
            self.statusWidget = QLineEdit('Statusstring if available')
            self.statusWidget.setMaximumWidth(10000)
            self._inner_hbox2.addWidget(self.statusWidget)
            self.resetButton = QPushButton('Reset')
            self.resetButton.clicked.connect(self._reset_clicked)
            self._inner_hbox1.addWidget(self.resetButton)
            #~ self._inner_hbox2.addStretch(0.1)

        # allow space for resizing
        self._inner_hbox1.addStretch(1)

        self._inner_vbox.setSpacing(0)
        self._inner_vbox.setContentsMargins(0, 0, 0, 0)

        self._hlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._hlayout)
        self.show()

    def _go_clicked(self):
        self.model.targeter(self.index, self.targetWidget.text())
        self.targetWidget.setText('')

    def _stop_clicked(self):
        self.model.stopper(self.index)

    def _reset_clicked(self):
        self.resetter(self.index)

    def _update(self):
        pass

    def _str2bin(self, value):
        return int(value)

    def _bin2str(self, value):
        return str(value)

    def _status(self, value):
        return "no status decoder implemented"

class ReadWord(BaseDev):
    has_target = False
    has_status = False

    def _go_clicked(self):
        raise NotImplementedError()

    def _stop_clicked(self):
        raise NotImplementedError()

    def _reset_clicked(self):
        raise NotImplementedError()

    def _update(self):
        self.valueWidget.setText(self._bin2str(self.model.ReadWord(self.addr)))


class DiscreteInput(ReadWord):
    has_target = False
    has_status = True
    def _go_clicked(self):
        raise NotImplementedError()

    def _stop_clicked(self):
        self.model.WriteWord(self.addr +1, 0x1000)

    def _reset_clicked(self):
        self.model.WriteWord(self.addr +1, 0x0000)

    def _update(self):
        self.valueWidget.setText(self._bin2str(self.model.ReadWord(self.addr)))
        statval = self.model.ReadWord(self.addr + 1)
        self.statvalueWidget.setText('0x%04x' % statval)
        self.statusWidget.setText(self._status(statval))


class DiscreteOutput(DiscreteInput):
    has_target = True
    has_status = True
    def _go_clicked(self):
        value = self.targetWidget.text()
        if value:
            self.model.WriteWord(self.addr +1, self._str2bin(value))
            self.targetWidget.setText('')
            self.model.WriteWord(self.addr +2, 0x2000)

    def _stop_clicked(self):
        self.model.WriteWord(self.addr +2, 0x1000)

    def _reset_clicked(self):
        self.model.WriteWord(self.addr +2, 0x0000)

    def _str2bin(self, value):
        v = str(value).strip()
        if v.startswith(('x', 'X', '$')):
            v = int('0' + v[1:], 16)
        elif v.startswith(('0x', '0X')):
            v = int('0' + v[2:], 16)
        elif v.startswith('16#'):
            v = int('0' + v[3:], 16)
        elif v.startswith(('0b', '0B', '2#')):
            v = int('0' + v[2:], 2)
        elif v.startswith(('0', 'o', 'O')):
            v = int('0' + v[1:], 8)
        elif v.startswith('8#'):
            v = int('0' + v[2:], 8)
        elif v.startswith('10#'):
            v = int('0' + v[3:], 8)
        else:
            v = int(v)
        return v

    def _bin2str(self, value):
        if value <16:
            return '%d' % value
        return '0x%04x' % value

    def _update(self):
        self.valueWidget.setText(self._bin2str(self.model.ReadWord(self.addr)))
        statval = self.model.ReadWord(self.addr + 2)
        self.statvalueWidget.setText('0x%04x' % statval)
        self.statusWidget.setText(self._status(statval))


class WriteWord(ReadWord):
    has_target = True
    has_status = False
    def __init__(self, model, name, addr):
        ReadWord.__init__(self, model, name, addr)
        self.goButton.setText('Set')

    def _go_clicked(self):
        value = self.targetWidget.text()
        if value:
            self.model.WriteWord(self.addr, self._str2bin(value))
            self.targetWidget.setText('')

    def _stop_clicked(self):
        self.model.WriteWord(self.addr, 0)

    def _reset_clicked(self):
        self.model.WriteWord(self.addr, 0)

    def _str2bin(self, value):
        v = str(value).strip()
        if v.startswith('0x') or v.startswith('0X'):
            v = int(v[2:],16)
        elif v.startswith('0b') or v.startswith('0B'):
            v = int(v[2:],2)
        elif v.startswith('0') or v.startswith('o'):
            v = int(v[2:],8)
        elif v.startswith(('x', 'X',  '$')):
            v = int(v[1:],16)
        else:
            v = int(v)
        return v

    def _bin2str(self, value):
        return '0x%04x' % value


class AnalogInput(BaseDev):
    has_target = False
    has_status = True
    def _go_clicked(self):
        raise NotImplementedError()

    def _stop_clicked(self):
        self.model.WriteWord(self.addr +2, 0x1000)

    def _reset_clicked(self):
        self.model.WriteWord(self.addr +2, 0x0000)

    def _update(self):
        self.valueWidget.setText(self._bin2str(self.model.ReadFloat(self.addr)))

    def _str2bin(self, value):
        return float(value)

    def _bin2str(self, value):
        return '%g' % value



class LIFT(DiscreteOutput):
    def _status(self, value):
        stati=['Idle']
        if (value & 0x9000) == 0x9000:
            stati = ['ERR:Movement timed out']
        if value & 0x0800:
            stati.append('ERR:liftclamp switches in Error')
        if value & 0x0004:
            stati.append('No Air pressure')
        if value & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if value & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        return ', '.join(stati)

class MAGAZIN(DiscreteOutput):
    def _status(self, value):
        stati=['Idle']
        if (value & 0x9000) == 0x9000:
            stati = ['ERR:Movement timed out']
        if value & 0x0800:
            stati.append('ERR:liftclamp switches in Error')
        if value & 0x0004:
            stati.append('No Air pressure')
        if value & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if value & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        return ', '.join(stati)

class CLAMP(DiscreteOutput):
    def _status(self, value):
        stati=['Idle']
        if (value & 0x9000) == 0x9000:
            stati = ['ERR:Movement timed out']
        if value & 0x0800:
            stati.append('ERR:liftclamp switches in Error')
        if value & 0x0004:
            stati.append('No Air pressure')
        if value & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if value & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        return ', '.join(stati)

class MainWindow(QMainWindow):
    i=0
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)

        # scroll area Widget contents - layout
        self.scrollLayout = QtGui.QFormLayout()
        self.scrollLayout.setContentsMargins(0, 0, 0, 0)

        # scroll area Widget contents
        self.scrollWidget = QtGui.QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)

        # scroll area
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.scrollWidget)

        # main layout
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setSpacing(0)

        # add all main to the main vLayout
        self.mainLayout.addWidget(self.scrollArea)

        # central Widget
        self.centralWidget = QtGui.QWidget()
        self.centralWidget.setLayout(self.mainLayout)

        # set central Widget
        self.setCentralWidget(self.centralWidget)

        try:
            self._bus = ModbusTcpClient('wechsler.panda.frm2')
            self._bus.connect()
            self._sync()
            print("PLC conforms to spec %.4f" % self.ReadFloat(0))
        except Exception:
            print("Modbus failed, using demo mode!")
            self._bus = None

        self._sync()

        widgets = []
        widgets.append(WriteWord(self, 'last_liftpos', addr=58/2))
        widgets.append(ReadWord(self, 'analog1',addr=92/2))
        widgets.append(ReadWord(self, 'analog2',addr=96/2))
        widgets.append(AnalogInput(self, 'liftpos_analog', addr=146/2))
        widgets.append(DiscreteInput(self, 'lift_sw', addr=68/2))
        widgets.append(LIFT(self, 'lift', 104/2))

        widgets.append(WriteWord(self, 'last_magpos', addr=60/2))
        widgets.append(DiscreteInput(self, 'magazin_sw', addr=72/2))
        widgets.append(MAGAZIN(self, 'magazin', addr=110/2))

        widgets.append(DiscreteInput(self, 'magazin_occ_sw', addr=84/2))
        widgets.append(DiscreteInput(self, 'magazin_occ', addr=88/2))

        widgets.append(DiscreteInput(self, 'liftclamp_sw', addr=76/2))
        widgets.append(CLAMP(self, 'liftclamp', addr=116/2))

        widgets.append(DiscreteInput(self, 'magazinclamp_sw', addr=80/2))
        widgets.append(CLAMP(self, 'magazinclamp', addr=122/2))

        widgets.append(CLAMP(self, 'tableclamp', addr=128/2))

        widgets.append(CLAMP(self, 'inhibit_relay', addr=134/2))

        widgets.append(WriteWord(self, 'enable_word', addr=150/2))

        widgets.append(DiscreteInput(self, 'spare inputs', addr=100/2))
        widgets.append(DiscreteOutput(self, 'spare outputs', addr=140/2))

        widgets.append(ReadWord(self, 'cycle_counter', addr=152/2))

        for w in widgets:
            self.addWidget(w)

        self.widgets=widgets

        self.startTimer(225) # in ms !

    def ReadWord(self, addr):
        return self._registers[int(addr)]

    def WriteWord(self, addr, value):
        if self._bus:
            self._bus.write_register(int(addr|0x4000), int(value))
            self._sync()

    def ReadDWord(self, addr):
        return unpack('<I', pack('<HH', self._registers[int(addr)],
                                         self._registers[int(addr) + 1]))

    def WriteDWord(self, addr, value):
        if self._bus:
            low, high = unpack('<HH', pack('<I', int(value)))
            self._bus.write_registers(int(addr|0x4000), [low, high])
            self._sync()

    def ReadFloat(self, addr):
        return unpack('<f', pack('<HH', self._registers[int(addr) + 1],
                                         self._registers[int(addr)]))

    def WriteFloat(self, addr, value):
        if self._bus:
            low, high = unpack('<HH', pack('<f', float(value)))
            self._bus.write_registers(int(addr|0x4000), [high, low])
            self._sync()

    def _sync(self):
        if self._bus:
            self._registers = self._bus.read_holding_registers(0x4000,
                                                               77).registers[:]
        else:
            self._registers = [self.i + i for i in range(77)]
            self.i += 1

    def timerEvent(self, event): # pylint: disable=R0915
        self._sync()
        for w in self.widgets:
            w._update()
        return

    def addWidget(self, which):
        which.setContentsMargins(10,0,0,0)
        self.scrollLayout.addRow(which)
        l = QtGui.QFrame()
        l.setLineWidth(1)
        #~ l.setMidLineWidth(4)
        l.setFrameShape(QtGui.QFrame.HLine)
        l.setContentsMargins(10,0,10,0)
        self.scrollLayout.addRow(l)


def main():
    app = QtGui.QApplication(sys.argv)
    myWindow = MainWindow()
    myWindow.resize(800,600)
    myWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

