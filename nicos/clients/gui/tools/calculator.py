#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

import re
import math
from os import path

from nicos.guisupport.qt import QDialog, QPixmap, QTreeWidgetItem

from nicos.clients.gui.utils import loadUi, DlgPresets
from nicos.guisupport.utils import DoubleValidator
from nicos.pycompat import iteritems


M_N = 1.6749274e-27
H   = 6.6260696e-34
K_B = 1.3806488e-23
PI  = 3.1415926
MEV = 1.6021766e-22


def tofloat(ctl):
    try:
        return float(ctl.text())
    except ValueError:
        return 0.0


prefactor = M_N**2 / (PI * H**2)

bragg_fields = ['Lambda', '2Theta', 'N', 'D', 'Q', 'SampleDet']
bragg_convs  = [1e-10, PI/180, 1, 1e-10, 1e10, 1]

neutron_fields = ['L', 'K', 'E', 'Ny', 'T', 'V']


class CalculatorTool(QDialog):
    """Provides a dialog for several neutron-related calculations.

    The dialog offers several tabs for calculations (elastic scattering,
    conversion between wavelength and energy etc.)
    """

    def __init__(self, parent, client, **settings):
        QDialog.__init__(self, parent)
        loadUi(self, 'calculator.ui', 'tools')

        self.closeBtn.clicked.connect(self.doclose)

        self.braggfmlLabel.setPixmap(QPixmap(
            path.join(path.dirname(__file__), 'calculator_images',
                      'braggfml.png')))
        for fld in bragg_fields:
            getattr(self, 'chk' + fld).toggled.connect(self.gen_checked(fld))

        self._miezesettings = settings.get('mieze', [])
        if not self._miezesettings:
            self.tabWidget.removeTab(1)
        else:
            self.mzwavelengthInput.textChanged.connect(self.mzcalc)
            self.mzdistanceInput.textChanged.connect(self.mzcalc)
            self.mzformulaLabel.setPixmap(QPixmap(
                path.join(path.dirname(__file__), 'calculator_images',
                          'miezefml.png')))

            self.mztimeTable.setHeaderLabels(['Setting', u'MIEZE time τ'])
            for setting in self._miezesettings:
                self.mztimeTable.addTopLevelItem(QTreeWidgetItem([setting, '']))

        for fld in neutron_fields:
            getattr(self, 'prop' + fld).textEdited.connect(self.n_calc)

        self.presets = DlgPresets('nicoscalctool', [
            (self.tabWidget, 0),
            (self.mzwavelengthInput, '10'), (self.mzdistanceInput, '100'),
            (self.inputLambda, '4.5'), (self.input2Theta, '0'),
            (self.inputD, '10'), (self.inputN, '1'), (self.inputQ, '0'),
            (self.chkLambda, 1), (self.chk2Theta, 0), (self.chkN, 1),
            (self.chkD, 1), (self.chkQ, 0), (self.chkSampleDet, 1),
            (self.inputSampleDet, '0'),
            (self.propL, '1.8'), (self.propK, '3.4907'),
            (self.propE, '25.2482'), (self.propNy, '6.1050'),
            (self.propT, '292.9934'), (self.propV, '2197.80'),
        ])
        self.presets.load()
        self.braggcalc()
        self.n_calc('')

        dblval = DoubleValidator(self)
        for fld in bragg_fields:
            inputbox = getattr(self, 'input'+fld)
            inputbox.textChanged.connect(self.braggcalc)
            inputbox.setValidator(dblval)

    def closeEvent(self, event):
        self.deleteLater()
        self.accept()

    def doclose(self, *ignored):
        self.presets.save()
        self.close()

    def gen_checked(self, fld):
        def checked(state):
            getattr(self, 'input' + fld).setEnabled(state)
            self.braggcalc()
        return checked

    def braggcalc(self, *ignored):
        given = {}
        needed = {}
        for fld, conv in zip(bragg_fields, bragg_convs):
            if fld == 'SampleDet':
                continue
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
        except ZeroDivisionError as err:
            self.errorLabel.setText('Error: division by zero.')
        except ValueError as err:
            self.errorLabel.setText('Error: %s.' % err)
        else:
            self.errorLabel.setText('')
            # now, fill the disabled text fields
            for fld, conv in iteritems(needed):
                getattr(self, 'input'+fld).setText('%.3f' % (given[fld]/conv))
            if self.chkSampleDet.isChecked():
                sd = tofloat(self.inputSampleDet)
                dd = math.tan(given['2Theta']) * sd
                self.distance.setText('%.2f' % dd)
            else:
                self.distance.setText('')

    def n_calc(self, text):
        try:
            if self.sender() is self.propK:
                lam = 2*PI/float(text)
            elif self.sender() is self.propE:
                lam = H/math.sqrt(2*M_N*float(text)*MEV) * 1e10
            elif self.sender() is self.propNy:
                lam = math.sqrt(H/(2*M_N*float(text)*1e12)) * 1e10
            elif self.sender() is self.propT:
                lam = H/math.sqrt(2*M_N*K_B*float(text)) * 1e10
            elif self.sender() is self.propV:
                lam = H/M_N/float(text) * 1e10
            else:
                lam = float(self.propL.text())
            if self.sender() is not self.propL:
                self.propL.setText('%.4f' % lam)
            if self.sender() is not self.propK:
                self.propK.setText('%.4f' % (2*PI/lam))
            if self.sender() is not self.propE:
                self.propE.setText('%.4f' % (H**2/(2*M_N*lam**2*1e-20)/MEV))
            if self.sender() is not self.propNy:
                self.propNy.setText('%.4f' % (H/(2*M_N*lam**2*1e-20)/1e12))
            if self.sender() is not self.propT:
                self.propT.setText('%.4f' % (H**2/(2*M_N*K_B*lam**2*1e-20)))
            if self.sender() is not self.propV:
                self.propV.setText('%.2f' % (H/M_N/(lam*1e-10)))
        except Exception as err:
            self.propError.setText('Error: %s' % err)
        else:
            self.propError.setText('')

    def mzcalc(self, *ignored):
        L_s = tofloat(self.mzdistanceInput) * 1e-2  # in cm
        lam = tofloat(self.mzwavelengthInput) * 1e-10  # in Ang

        for i, setting in enumerate(self._miezesettings):
            f1, f2, bs = re.match(r'([\dp]+)_([\dp]+)(_BS)?', setting).groups()
            f1 = float(f1.replace('p', '.')) * 1000  # in kHz
            f2 = float(f2.replace('p', '.')) * 1000  # in kHz
            dOmega = (f2 - f1) * 2 * PI
            if bs:
                dOmega *= 2
            tau = (prefactor * lam**3 * dOmega * L_s) * 1e12  # in ps
            self.mztimeTable.topLevelItem(i).setText(1, '%.1f ps' % tau)
