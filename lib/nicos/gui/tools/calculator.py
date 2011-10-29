#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""Calculation GUI tool."""

__version__ = "$Revision$"

import re
import math
from os import path

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QDialog, QPixmap, QTreeWidgetItem, QDoubleValidator
from PyQt4.uic import loadUi

from nicos.gui.utils import DlgPresets


M_N = 1.6749e-27
H   = 6.6261e-34
PI  = 3.1415926

def tofloat(ctl):
    try:
        return float(str(ctl.text()))
    except:
        return 0.0

prefactor = M_N**2 / (PI * H**2)

bragg_fields = ['Lambda', '2Theta', 'N', 'D', 'Q', 'SampleDet']
bragg_convs  = [1e-10, PI/180, 1, 1e-10, 1e10, 1]


class CalculatorTool(QDialog):
    def __init__(self, parent=None, **settings):
        QDialog.__init__(self, parent)
        loadUi(path.join(path.dirname(__file__), 'calc.ui'), self)

        self.connect(self.closeBtn, SIGNAL('clicked()'),
                     self.doclose)

        self.braggfmlLabel.setPixmap(QPixmap(
            path.join(path.dirname(__file__), 'calculator_images',
                      'braggfml.png')))
        for fld in bragg_fields:
            self.connect(getattr(self, 'chk' + fld), SIGNAL('toggled(bool)'),
                         self.gen_checked(fld))

        self._miezesettings = settings.get('mieze', [])
        if not self._miezesettings:
            self.tabWidget.removeTab(2)
        else:
            self.connect(self.mzwavelengthInput,
                         SIGNAL('textChanged(const QString &)'), self.mzcalc)
            self.connect(self.mzdistanceInput,
                         SIGNAL('textChanged(const QString &)'), self.mzcalc)
            self.mzformulaLabel.setPixmap(QPixmap(
                    path.join(path.dirname(__file__), 'calculator_images',
                              'miezefml.png')))

            self.mztimeTable.setHeaderLabels(['Setting', u'MIEZE time τ'])
            for setting in self._miezesettings:
                self.mztimeTable.addTopLevelItem(QTreeWidgetItem([setting, '']))

        self.presets = DlgPresets('nicoscalctool', [
            (self.tabWidget, 0),
            (self.mzwavelengthInput, '10'), (self.mzdistanceInput, '100'),
            (self.inputLambda, '10'), (self.input2Theta, '0'),
            (self.inputD, '0'), (self.inputN, '1'), (self.inputQ, '0'),
            (self.chkLambda, 1), (self.chk2Theta, 0), (self.chkN, 1),
            (self.chkD, 1), (self.chkQ, 0), (self.chkSampleDet, 1),
            (self.inputSampleDet, '0'),
            ])
        self.presets.load()
        self.braggcalc()

        dblval = QDoubleValidator(self)
        for fld in bragg_fields:
            input = getattr(self, 'input'+fld)
            self.connect(input, SIGNAL('textChanged(const QString &)'),
                         self.braggcalc)
            input.setValidator(dblval)

    def doclose(self, *ignored):
        self.presets.save()
        self.close()

    def gen_checked(self, fld):
        def checked(state):
            getattr(self, 'input'+fld).setEnabled(state)
            self.braggcalc()
        return checked

    def braggcalc(self, *ignored):
        given = {}
        needed = {}
        for fld, conv in zip(bragg_fields, bragg_convs):
            if fld == 'SampleDet': continue
            if getattr(self, 'chk'+fld).isChecked():
                given[fld] = tofloat(getattr(self, 'input'+fld)) * conv
            else:
                needed[fld] = conv
        if len(given) < 3:
            self.errorLabel.setText('Error: Not enough variables given.')
            return
        elif len(given) > 3:
            self.errorLabel.setText('Error: Too many variables given.')
            return
        elif 'Q' in given and 'D' in given and 'N' in given:
            self.errorLabel.setText('Error: All of n, d, q given.')
            return
        elif 'Q' in given and 'Lambda' in given and '2Theta' in given:
            self.errorLabel.setText('Error: All of q, lambda, 2theta given.')
            return
        try:
            # let's see what to calculate first:
            if '2Theta' in given and 'Lambda' in given:
                # three of four variables in Bragg's equation known
                if 'N' in given:
                    given['D'] = given['N']*given['Lambda']/2/math.sin(given['2Theta']/2)
                else:
                    given['N'] = 2*given['D']*math.sin(given['2Theta']/2)/given['Lambda']
                given['Q'] = given['N']*2*PI/given['D']
            else:
                # two of three variables in q = 2pi(n/d) known
                if 'N' in given and 'D' in given:
                    given['Q'] = given['N']*2*PI/given['D']
                elif 'Q' in given and 'D' in given:
                    given['N'] = given['D']*given['Q']/2/PI
                else:
                    given['D'] = given['N']*2*PI/given['Q']
                # then, only lambda or 2theta is missing
                if 'Lambda' in given:
                    arg = given['N']*given['Lambda']/2/given['D']
                    if not 0 <= arg <= 1:
                        raise ValueError('impossible scattering angle')
                    given['2Theta'] = 2*math.asin(arg)
                else:
                    given['Lambda'] = 2*given['D']*math.sin(given['2Theta']/2)/given['N']
        except ZeroDivisionError, err:
            self.errorLabel.setText('Error: division by zero.')
        except ValueError, err:
            self.errorLabel.setText('Error: %s.' % err)
        else:
            self.errorLabel.setText('')
            # now, fill the disabled text fields
            for fld, conv in needed.iteritems():
                getattr(self, 'input'+fld).setText('%.3f' % (given[fld]/conv))
            if self.chkSampleDet.isChecked():
                sd = tofloat(self.inputSampleDet)
                dd = math.tan(given['2Theta']) * sd
                self.distance.setText('%.2f' % dd)
            else:
                self.distance.setText('')

    def mzcalc(self, *ignored):
        L_s = tofloat(self.mzdistanceInput) * 1e-2  # in cm
        lam = tofloat(self.mzwavelengthInput) * 1e-10  # in Ang

        for i, setting in self._miezesettings:
            f1, f2, bs = re.match(r'([\dp]+)_([\dp]+)(_BS)?', setting).groups()
            f1 = float(f1.replace('p', '.')) * 1000  # in kHz
            f2 = float(f2.replace('p', '.')) * 1000  # in kHz
            dOmega = (f2 - f1) * 2 * PI
            if bs: dOmega *= 2
            tau = (prefactor * lam**3 * dOmega * L_s) * 1e12  # in ps
            self.mztimeTable.topLevelItem(i).setText(1, '%.1f ps' % tau)
