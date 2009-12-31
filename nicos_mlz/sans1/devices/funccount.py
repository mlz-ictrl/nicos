#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""Special device for Sans1 Func counter"""


from nicos.devices.tango import Sensor

CONFIG = '''
*RST;

:FUNC "FREQ";
:CALC:AVER 1;
:CALC:SMO:RESP FAST;
:CALC:SMO 1;
:INP:COUP AC;
:INP:FILT 0;
:INP:IMP +1.00000000E+006;
:INP:LEV +2.20000000E+000;
:INP:LEV:REL +50;
:INP:LEV:AUTO 0;
:INP:NREJ 1;
:INP:PROB +1;
:INP:RANG +5.00000000E+000;
:INP:SLOP POS;
:MMEM:CDIR "INT:\\";
:OUTP:POL NORM;
:OUTP 0;
:SAMP:COUN +1;
:FREQ:GATE:POL NEG;
:FREQ:GATE:SOUR TIME;
:FREQ:GATE:TIME +1.00000000000000E-001;
:TRIG:COUN +1;
:TRIG:DEL +0.00000000000000E+000;
:TRIG:SLOP NEG;
:TRIG:SOUR IMM;
'''

class FC53210A(Sensor):
    """Support for FC 53210A

    derived after endless hours of debuging.
    DON'T TRUST THE MANUAL!
    """
    def doReset(self):
        self._dev.Reset()
        self._dev.WriteLine(CONFIG)
        self._dev.Flush()
        self._dev.Communicate('SYST:ERR?')

    def doReadUnit(self):
        return 'Hz'

    def doRead(self, maxage=0):
        # XXX: todo: read frequency of a chopper disc and send it to the FC
        #            to avoid automeasurement (silly results)
        # note: chopper discs run in rpm, no Hz
        # return float(self._dev.Communicate('MEAS:FREQ? <expected_freq_in_HZ>'))
        return float(self._dev.Communicate('MEAS:FREQ? (@1)'))
