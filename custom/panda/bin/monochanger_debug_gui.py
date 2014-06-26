#!/usr/bin/env python
#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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
    def __init__(self, model, name, index, has_status=False, target=None):
        super(BaseDev, self).__init__()
        self.index = index
        self.name = name
        self.model = model

        has_target = target is not None

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

        if has_target:
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
            self._bus = ModbusTcpClient('wechsler.panda.frm2')
            self._bus.connect()
            self._sync()
        except Exception:
            print "Modbus failed, using demo mode!"
            self._bus=None

        self._sync()

        widgets = []
        widgets.append(BaseDev(self, 'last_liftpos', 0,
                               target='%d' % self.ReadWord(17)))
        widgets.append(BaseDev(self, 'analog1', 8, has_status=True))
        widgets.append(BaseDev(self, 'analog2', 9, has_status=True))
        widgets.append(BaseDev(self, 'liftpos_analog', 18 ))
        widgets.append(BaseDev(self, 'lift_sw', 2, has_status=True))
        widgets.append(BaseDev(self, 'lift', 11, has_status=True,
                               target='%d' % self.ReadWord(51) ))

        widgets.append(BaseDev(self, 'last_magpos', 1,
                               target='%d' % self.ReadWord(18)))
        widgets.append(BaseDev(self, 'magazin_sw', 3, has_status=True))
        widgets.append(BaseDev(self, 'magazin', 12, has_status=True,
                               target='%d' % self.ReadWord(54) ))

        widgets.append(BaseDev(self, 'magazin_occ_sw', 6, has_status=True))
        widgets.append(BaseDev(self, 'magazin_occ', 7, has_status=True))

        widgets.append(BaseDev(self, 'liftclamp_sw', 4, has_status=True))
        widgets.append(BaseDev(self, 'liftclamp', 13, has_status=True,
                               target='%d' % self.ReadWord(57) ))

        widgets.append(BaseDev(self, 'magazinclamp_sw', 5, has_status=True))
        widgets.append(BaseDev(self, 'magazinclamp', 14, has_status=True,
                               target='%d' % self.ReadWord(60) ))

        widgets.append(BaseDev(self, 'tableclamp', 15, has_status=True,
                               target='%d' % self.ReadWord(63) ))

        widgets.append(BaseDev(self, 'inhibit_relay', 16, has_status=True,
                               target='%d' % self.ReadWord(66) ))

        widgets.append(BaseDev(self, 'enable_word', 19,
                               target='0x%04x' % self.ReadWord(73) ))

        widgets.append(BaseDev(self, 'spare inputs', 10, has_status=True))
        widgets.append(BaseDev(self, 'spare outputs', 17, has_status=True,
                               target='0x%04x' % self.ReadWord(69) ))

        widgets.append(BaseDev(self, 'cycle_counter', 20 ))

        for w in widgets:
            self.addWidget(w)

        widgets.sort(key=lambda w:w.index)
        self.widgets=widgets


        self.startTimer(225) # in ms !

    def resetter(self, index):
        if 2 <= index <= 10:
            self.reset(33 + (index-2) * 2)
        elif 11 <= index <= 17:
            self.reset(52 + (index-11) * 3)
        else:
            print "resetter: bad index %d" % index

    def stopper(self, index):
        if 2 <= index <= 10:
            self.stop(33 + (index-2) * 2)
        elif 11 <= index <= 17:
            self.stop(52 + (index-11) * 3)
        elif index == 19:
            self.WriteWord(73,0)
        else:
            print "stopper: bad index %d" % index

    def targeter(self, index, valuestr):
        v=str(valuestr).strip()
        if not v:
            return #ignore empty values (no value entered into the box?)
        if v.startswith('0x') or v.startswith('0X'):
            v = int(v[2:],16)
        elif v.startswith(('x', 'X',  '$')):
            v = int(v[1:],16)
        else:
            v = int(v)
        if 0 <= index <= 1:
            self.WriteWord(17 + index, v)
        elif 11 <= index <= 17:
            self.WriteWord(51 + (index-11) * 3, v)
        elif index ==19:
            self.WriteWord(73, v)
        else:
            print "targeter: got value for bad Index %d:%r" % (index, valuestr)

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

        # 0: %MB34 : last_liftpos
        w[0].valueWidget.setText('0x%04x' % self.ReadWord(17))
        w[0].targetWidget.setPlaceholderText('0x%04x' % self.ReadWord(17))

        # 1: %MB36: last_magpos
        w[1].valueWidget.setText('0x%04x' % self.ReadWord(18))
        w[1].targetWidget.setPlaceholderText('0x%04x' % self.ReadWord(18))

        # 2: %MB64: lift_switches
        w[2].valueWidget.setText('%d' % self.ReadWord(32))
        stat = self.ReadWord(33)
        stati = Stati(stat)
        for i in range(4):
            if stat & (1<<(i+8)):
                stati.append('Switch for Position %d is in Error'%(i+1))
        for i in range(4):
            _ = stat>>(2*i)
            if (_ & 3) == 2:
                stati.append('Switch for Position %d is active'%(i+1))
        w[2].statvalueWidget.setText('0x%04x' % stat)
        w[2].statusWidget.setText(', '.join(stati))

        # 3: %MB68: magazin_switches
        w[3].valueWidget.setText('%d' % self.ReadWord(34))
        stat = self.ReadWord(35)
        stati = Stati(stat)
        sw = 'ID1 ID2 ID3 Refpos'.split()
        for i in range(4):
            if stat & (1 << (i + 8)):
                stati.append('%s-Switch in Error' % sw[i])
        for i in range(4):
            _ = stat >> (2 * i)
            if (_ & 3) == 2:
                stati.append('%s active' % sw[i])
        w[3].statvalueWidget.setText('0x%04x' % stat)
        w[3].statusWidget.setText(', '.join(stati))

        # 4: %MB72: liftclamp_switches
        val = self.ReadWord(36)
        stat = self.ReadWord(37)
        stati = Stati(stat)
        sw = 'r_closed l_closed r_open l_open'.split()
        for i in range(4):
            if stat & (1<<(i+8)):
                stati.append('%s-Switch in Error' % sw[i])
        for i in range(4):
            _ = stat>>(2*i)
            if (_ & 3)== 2:
                stati.append('%s active' % sw[i])
        w[4].valueWidget.setText('%d' % val)
        w[4].statvalueWidget.setText('0x%04x' % stat)
        w[4].statusWidget.setText(', '.join(stati))

        # 5: %MB76: magazinclamp_switches
        val = self.ReadWord(38)
        stat = self.ReadWord(39)
        stati = Stati(stat)
        sw = 'mag_clamp_closed mag_clamp_open'.split()
        for i in range(2):
            if stat & (1<<(i+8)):
                stati.append('%s-Switch in Error'%sw[i])
        for i in range(2):
            _ = stat>>(2*i)
            if (_ & 3)== 2:
                stati.append('%s active'%sw[i])
        w[5].valueWidget.setText('%d' % val)
        w[5].statvalueWidget.setText('0x%04x' % stat)
        w[5].statusWidget.setText(', '.join(stati))

        # 6: %MB80: magazin_occ_switches
        val = self.ReadWord(40)
        stat = self.ReadWord(41)
        stati = Stati(stat)
        sw = '101_r 101_l 110_r 110_l 011_r 011_l 111_r 111_l'.split()
        for i in range(8):
            if stat & (1<<i):
                stati.append('%s-Switch in Error'%sw[i])
        for i in range(8):
            if val & (1<<i):
                stati.append('%s active'%sw[i])
        w[6].valueWidget.setText('0b'+bin(65536|val)[11:])
        w[6].statvalueWidget.setText('0x%04x' % stat)
        w[6].statusWidget.setText(', '.join(stati))

        # 7: %MB84: magazin_occ
        val = self.ReadWord(42)
        stat = self.ReadWord(43)
        stati = Stati(stat)
        sw = '101_occ 110_occ 011_occ 111_occ 101_free 110_free 011_free 111_free'
        sw = sw.split()
        for i in range(8):
            if val & (1<<i):
                stati.append('%s'%sw[i])
        w[7].valueWidget.setText('0b'+bin(65536|val)[11:])
        w[7].statvalueWidget.setText('0x%04x' % stat)
        w[7].statusWidget.setText(', '.join(stati))

        # 8: %MB88: analog1
        val = self.ReadWord(44)
        stat = self.ReadWord(45)
        w[8].valueWidget.setText('%d' % val)
        w[8].statvalueWidget.setText('0x%04x' % stat)
        w[8].statusWidget.setText('sensing')

        # 9: %MB92: analog2
        val = self.ReadWord(46)
        stat = self.ReadWord(47)
        w[9].valueWidget.setText('%d' % val)
        w[9].statvalueWidget.setText('0x%04x' % stat)
        w[9].statusWidget.setText('reference')

        # 10: %MB96: spare inputs
        val = self.ReadWord(48)
        stat = self.ReadWord(49)
        w[10].valueWidget.setText(bin(65536|val)[3:])
        w[10].statvalueWidget.setText('0x%04x' % stat)
        w[10].statusWidget.setText('spare inputs')

        # 11: %MB100: lift
        val = self.ReadWord(50)
        target = self.ReadWord(51)
        stat = self.ReadWord(52)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0800:
            stati.append('ERR:Lift switches in Error')
        w[11].valueWidget.setText('%d' % val)
        w[11].statvalueWidget.setText('0x%04x' % stat)
        w[11].statusWidget.setText(', '.join(stati))
        w[11].targetWidget.setPlaceholderText('%d' % target)

        # 12: %MB106: magazin
        val = self.ReadWord(53)
        target = self.ReadWord(54)
        stat = self.ReadWord(55)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0800:
            stati.append('ERR:magazin switches in Error')
        w[12].valueWidget.setText('%d' % val)
        w[12].statvalueWidget.setText('0x%04x' % stat)
        w[12].statusWidget.setText(', '.join(stati))
        w[12].targetWidget.setPlaceholderText('%d' % target)

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
        w[13].valueWidget.setText('%d' % val)
        w[13].statvalueWidget.setText('0x%04x' % stat)
        w[13].statusWidget.setText(', '.join(stati))
        w[13].targetWidget.setPlaceholderText('%d' % target)

        # 14: %MB118: magazinclamp
        val = self.ReadWord(59)
        target = self.ReadWord(60)
        stat = self.ReadWord(61)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0800:
            stati.append('ERR:magazineclamp switches in Error')
        if stat & 0x0004:
            stati.append('No Air pressure')
        if stat & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if stat & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        w[14].valueWidget.setText('%d' % val)
        w[14].statvalueWidget.setText('0x%04x' % stat)
        w[14].statusWidget.setText(', '.join(stati))
        w[14].targetWidget.setPlaceholderText('%d' % target)

        # 15: %MB124: tableclamp
        val = self.ReadWord(62)
        target = self.ReadWord(63)
        stat = self.ReadWord(64)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0800:
            stati.append('ERR:tableclamp switches in Error')
        if stat & 0x0004:
            stati.append('No Air pressure')
        if stat & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if stat & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        w[15].valueWidget.setText('%d' % val)
        w[15].statvalueWidget.setText('0x%04x' % stat)
        w[15].statusWidget.setText(', '.join(stati))
        w[15].targetWidget.setPlaceholderText('%d' % target)

        # 16: %MB130: inhibit_relay
        val = self.ReadWord(65)
        target = self.ReadWord(66)
        stat = self.ReadWord(67)
        stati = Stati(stat)
        if (stat & 0x9000) == 0x9000:
            stati.append('ERR:Movement timed out')
        if stat & 0x0002:
            stati.append('ERR:Actuator Wire shorted!')
        if stat & 0x0001:
            stati.append('ERR:Actuator Wire open!')
        w[16].valueWidget.setText('%d' % val)
        w[16].statvalueWidget.setText('0x%04x' % stat)
        w[16].statusWidget.setText(', '.join(stati))
        w[16].targetWidget.setPlaceholderText('%d' % target)

        # 17: %MB136: spare outputs
        val = self.ReadWord(68)
        target = self.ReadWord(69)
        stat = self.ReadWord(70)
        stati = Stati(stat)
        w[17].valueWidget.setText('%d' % val)
        w[17].statvalueWidget.setText('0x%04x' % stat)
        w[17].statusWidget.setText(', '.join(stati))
        w[17].targetWidget.setPlaceholderText('%d' % target)

        # 18: %MB142: Analog liftposition
        val = self.ReadFloat(71)
        w[18].valueWidget.setText('%.2f' % val)

        # 19: %MB146: enable code word
        val = self.ReadWord(73)
        w[19].valueWidget.setText('0x%04x' % val)
        w[19].targetWidget.setPlaceholderText('0x%04x' % val)

        # 20: %MB148: cycle counter
        val = self.ReadWord(74)
        w[20].valueWidget.setText('0x%04x' % val)


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

