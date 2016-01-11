#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
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
    base_address = 0
    has_target = False
    has_status = False
    offset = 1

    def __init__(self, model, name, index, addr, has_status=False, target=None, value_offset=1):
        super(BaseDev, self).__init__()
        self.index = index
        self.name = name
        self.model = model


        self.offset = value_offset
        self.has_status = has_status
        self.has_target = target is not None
        self.base_address = addr

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
            self.targetWidget.setPlaceholderText(target)
            self.targetWidget.setMaximumWidth(120)
            self.targetWidget.returnPressed.connect(
                lambda *a: model.targeter(index,
                    (self.targetWidget.text(),
                     self.targetWidget.setText(''))[0]))
            self._inner_hbox1.addWidget(self.targetWidget)
            self.goButton = QPushButton('Go')
            self.goButton.clicked.connect(
                lambda *a: model.targeter(index,
                    (self.targetWidget.text(),
                     self.targetWidget.setText(''))[0]))
            self._inner_hbox1.addWidget(self.goButton)
            self.stopButton = QPushButton('Stop')
            self.stopButton.clicked.connect(lambda *a: model.stopper(index))
            self._inner_hbox1.addWidget(self.stopButton)


        # now (conditionally) the second hbox
        if has_status:
            self._inner_hbox2 = QHBoxLayout()
            self._inner_vbox.addLayout(self._inner_hbox2)

            self.statvalueWidget = QLineEdit('statval')
            self.statvalueWidget.setMaximumWidth(120)
            self._inner_hbox2.addWidget(self.statvalueWidget)
            self.statusWidget = QLineEdit('Statusstring if available')
            self.statusWidget.setMaximumWidth(10000)
            self._inner_hbox2.addWidget(self.statusWidget)
            self.resetButton = QPushButton('Reset')
            self.resetButton.clicked.connect(lambda *a: model.resetter(index))
            self._inner_hbox1.addWidget(self.resetButton)
            #~ self._inner_hbox2.addStretch(0.1)

        # allow space for resizing
        self._inner_hbox1.addStretch(1)

        self._inner_vbox.setSpacing(0)
        self._inner_vbox.setContentsMargins(0, 0, 0, 0)

        self._hlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._hlayout)
        self.show()


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
            self._bus = ModbusTcpClient('drum.panda.frm2')
            self._bus.connect()
            self._sync()
            print("Modbus synced!")
            print(self.ReadWord(0x20), self.ReadWord(0x21))
        except Exception as err:
            print("Modbus failed: %r, using demo mode!" % err)
            self._bus = None

        self._sync()

        widgets = []

        widgets.append(BaseDev(self, 'mtt motor inputs', 0, has_status=True, addr=34))

        widgets.append(BaseDev(self, 'spare inputs', 1, has_status=True, addr=44))
        widgets.append(BaseDev(self, 'spare outputs', 2, has_status=True,
                               target='0x%04x' % self.ReadWord(60), addr= 59))
        widgets.append(BaseDev(self, 'enable_word', 3,
                               target='0x%04x' % self.ReadWord(73), addr= 73))
        widgets.append(BaseDev(self, 'cycle_counter', 4, addr= 74))
        widgets.append(BaseDev(self, 'handle_cw', 5, has_status=True,
                               target='%d' % self.ReadWord(51), addr= 50))
        widgets.append(BaseDev(self, 'handle_ccw', 6, has_status=True,
                              target='%d' % self.ReadWord(54), addr= 53))
        widgets.append(BaseDev(self, 'enc1', 7, has_status=True, addr= 46))
        widgets.append(BaseDev(self, 'enc2', 8, has_status=True, addr= 48))
        widgets.append(BaseDev(self, 'arm_switch', 9, has_status=True,
                              target='%d' % self.ReadWord(63), addr= 62))
        widgets.append(BaseDev(self, 'encoder1', 10, has_status=False, addr= 65))
        widgets.append(BaseDev(self, 'arm', 11, has_status=True,
                              target='%f' % self.ReadFloat(70), value_offset=2, addr= 68))
        widgets.append(BaseDev(self, 'magnet', 12, has_status=True,
                              target='%d' % self.ReadWord(57), addr= 56))
        widgets.append(BaseDev(self, 'air', 13, has_status=True,
                              target='%d' % self.ReadWord(60), addr= 59))

        for w in widgets:
            self.addWidget(w)

        widgets.sort(key=lambda w:w.index)
        self.widgets=widgets


        self.startTimer(225) # in ms !

    def resetter(self, index):
        w=self.widgets[index]
        if w.has_status:
            addr = w.base_address + w.offset
            if w.has_target:
                addr += w.offset
            print(addr)
            self.reset(addr)
        else:
            print("resetter: device %d has no status" % index)

    def stopper(self, index):
        w=self.widgets[index]
        if w.has_target:
            addr = w.base_address
            if w.name == 'enable_word':
                print("stopper: DISABLING %d" % (addr))
                self.WriteWord(addr,0)
            else:
                addr += w.offset
                if w.has_target:
                    addr += w.offset
                print("stopper: stopping on addr %d" % (addr))
                self.stop(addr)

        else:
            print("stopper: cannot stop - no target %d" % index)

    def targeter(self, index, valuestr):
        w=self.widgets[index]
        if w.has_target:
            v=str(valuestr).strip()
            if not v:
                return #ignore empty values (no value entered into the box?)
            addr = w.base_address
            if w.offset == 2:
                v = float(v)
                addr += w.offset
                print("targeter: setting addr %d to %f" % (addr, v))
                self.WriteFloat(addr, v)
            else:
                if v.startswith('0x') or v.startswith('0X'):
                    v = int(v[2:],16)
                elif v.startswith(('x', 'X',  '$')):
                    v = int(v[1:],16)
                else:
                    v = int(v)
                if w.name != 'enable_word':
                    addr += w.offset
                print("targeter: setting addr %d to %r" % (addr, valuestr))
                self.WriteWord(addr, v)
        else:
            print("targeter: device fas no target %d:%r" % (index, valuestr))

    def ReadWord(self, addr):
        return self._registers[int(addr)]

    def WriteWord(self, addr, value):
        self._bus.write_register(int(addr|0x4000), int(value))
        self._sync()

    def ReadDWord(self, addr):
        return unpack('<I', pack('<HH', self._registers[int(addr)],
                                         self._registers[int(addr) + 1]))

    def WriteDWord(self, addr, value):
        low, high = unpack('<HH', pack('<I', int(value)))
        self._bus.write_registers(int(addr|0x4000), [low, high])
        self._sync()

    def ReadFloat(self, addr):
        return unpack('<f', pack('<HH', self._registers[int(addr) + 1],
                                         self._registers[int(addr)]))

    def WriteFloat(self, addr, value):
        low, high = unpack('<HH', pack('<f', float(value)))
        self._bus.write_registers(int(addr|0x4000), [high, low])
        self._sync()

    def _sync(self):
        if self._bus:
            self._registers = self._bus.read_holding_registers(0x4000,
                                                               75).registers[:]
            # print(self._registers)
        else:
            self._registers = [self.i]*75
            self.i += 1

    def reset(self, addr):
        self.WriteWord(addr, 0x0fff & self.ReadWord(addr))

    def stop(self, addr):
        self.WriteWord(addr, 0x1000 | (0x0fff & self.ReadWord(addr)))

    def timerEvent(self, event): # pylint: disable=R0915

        self._sync()
        w = self.widgets

        # 1: %MB68: cycle counter
        val = self.ReadWord(34)
        stat = self.ReadWord(35)
        w[0].valueWidget.setText(bin(65536|val)[3:])
        w[0].statvalueWidget.setText('0x%04x' % stat)
        w[0].statusWidget.setText('mtt motor inputs')

        # 10: %MB96: spare inputs
        val = self.ReadWord(44)
        stat = self.ReadWord(45)
        w[1].valueWidget.setText(bin(65536|val)[3:])
        w[1].statvalueWidget.setText('0x%04x' % stat)
        w[1].statusWidget.setText('spare inputs')


        # 17: %MB136: spare outputs
        val = self.ReadWord(59)
        target = self.ReadWord(60)
        stat = self.ReadWord(61)
        stati = Stati(stat)
        w[2].valueWidget.setText('%d' % val)
        w[2].statvalueWidget.setText('0x%04x' % stat)
        w[2].statusWidget.setText(', '.join(stati))
        w[2].targetWidget.setPlaceholderText('%d' % target)

        # 19: %MB146: enable code word
        val = self.ReadWord(73)
        w[3].valueWidget.setText('0x%04x' % val)
        w[3].targetWidget.setPlaceholderText('0x%04x' % val)

        # 20: %MB148: cycle counter
        val = self.ReadWord(74)
        w[4].valueWidget.setText('0x%04x' % val)

        # 13: %MB112: liftclamp
        val = self.ReadWord(50)
        target = self.ReadWord(51)
        stat = self.ReadWord(52)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0800:
            stati.append('ERR:liftclamp switches in Error')
        if stat & 0x0004:
            stati.append('No Air pressure')
        if stat & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if stat & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        w[5].valueWidget.setText('%d' % val)
        w[5].statvalueWidget.setText('0x%04x' % stat)
        w[5].statusWidget.setText(', '.join(stati))
        w[5].targetWidget.setPlaceholderText('%d' % target)

        # 13: %MB112: liftclamp
        val = self.ReadWord(53)
        target = self.ReadWord(54)
        stat = self.ReadWord(55)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0800:
            stati.append('ERR:liftclamp switches in Error')
        if stat & 0x0004:
            stati.append('No Air pressure')
        if stat & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if stat & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        w[6].valueWidget.setText('%d' % val)
        w[6].statvalueWidget.setText('0x%04x' % stat)
        w[6].statusWidget.setText(', '.join(stati))
        w[6].targetWidget.setPlaceholderText('%d' % target)

        # 7: %MB192: enc1
        val = self.ReadWord(46)
        stat = self.ReadWord(47)
        stati = Stati(stat)
        if stat & 0x0002:
            stati.append('ERR:Underflow!')
        if stat & 0x0001:
            stati.append('ERR:Overflow!')
        w[7].valueWidget.setText(str(val))
        w[7].statvalueWidget.setText('0x%04x' % stat)
        w[7].statusWidget.setText(', '.join(stati))

        # 7: %MB192: arm
        val = self.ReadWord(48)
        stat = self.ReadWord(49)
        stati = Stati(stat)
        if stat & 0x0002:
            stati.append('ERR:Underflow!')
        if stat & 0x0001:
            stati.append('ERR:Overflow!')
        w[8].valueWidget.setText(str(val))
        w[8].statvalueWidget.setText('0x%04x' % stat)
        w[8].statusWidget.setText(', '.join(stati))

        # 17: %MB136: spare outputs
        val = self.ReadWord(62)
        target = self.ReadWord(63)
        stat = self.ReadWord(64)
        stati = Stati(stat)
        w[9].valueWidget.setText('%d' % val)
        w[9].statvalueWidget.setText('0x%04x' % stat)
        w[9].statusWidget.setText(', '.join(stati))
        w[9].targetWidget.setPlaceholderText('%d' % target)

     # encoder
        val = self.ReadFloat(65)
        w[10].valueWidget.setText('%f' % val)

        # motro
        val = self.ReadFloat(68)
        target = self.ReadFloat(70)
        stat = self.ReadWord(72)
        stati = Stati(stat)
        w[11].valueWidget.setText('%f' % val)
        w[11].statvalueWidget.setText('0x%04x' % stat)
        w[11].statusWidget.setText(', '.join(stati))
        w[11].targetWidget.setPlaceholderText('%f' % target)

        # 13: %MB112: liftclamp
        val = self.ReadWord(56)
        target = self.ReadWord(57)
        stat = self.ReadWord(58)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0800:
            stati.append('ERR:liftclamp switches in Error')
        if stat & 0x0004:
            stati.append('No Air pressure')
        if stat & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if stat & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        w[12].valueWidget.setText('%d' % val)
        w[12].statvalueWidget.setText('0x%04x' % stat)
        w[12].statusWidget.setText(', '.join(stati))
        w[12].targetWidget.setPlaceholderText('%d' % target)

# 13: %MB112: air
        val = self.ReadWord(59)
        target = self.ReadWord(60)
        stat = self.ReadWord(61)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0800:
            stati.append('ERR:liftclamp switches in Error')
        if stat & 0x0004:
            stati.append('No Air pressure')
        if stat & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if stat & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        w[13].valueWidget.setText('%d' % val)
        w[13].statvalueWidget.setText('0x%04x' % stat)
        w[13].statusWidget.setText(', '.join(stati))
        w[13].targetWidget.setPlaceholderText('%d' % target)



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

