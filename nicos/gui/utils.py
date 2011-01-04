#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
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
# *****************************************************************************

"""NICOS GUI utilities."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

import os
import re
import time
import random
import socket
from os import path
from math import sqrt, log
from itertools import islice, chain

from PyQt4 import QtCore, QtGui, uic

try:
    from scipy.odr import Model, RealData, ODR
    from scipy import exp, array, arange, piecewise
except ImportError:
    has_odr = False
else:
    has_odr = True


# -- Misc tools ----------------------------------------------------------------

def chunks(iterable, size):
    sourceiter = iter(iterable)
    while True:
        chunkiter = islice(sourceiter, size)
        yield chain([chunkiter.next()], chunkiter)

def get_display():
    try:
        lhost = socket.getfqdn(socket.gethostbyaddr(socket.gethostname())[0])
    except socket.gaierror:
        return ''
    else:
        return lhost + os.environ.get('DISPLAY', ':0')

def parse_conndata(s):
    res = re.match(r"(?:(\w+)@)?([\w.]+)(?::(\d+))?", s)
    if res is None:
        return None
    return res.group(1) or 'admin', res.group(2), int(res.group(3) or '1201')


def _s(n):
    return int(n), (n != 1 and 's' or '')

def format_alternate_duration(secs):
    if secs == 0:
        return 'less than 42 seconds'
    elif secs < 360:
        return '%s millimonth%s' % _s(secs / 2.592)
    elif secs < 3600:
        return '%s microyear%s' % _s(secs / 31.536)
    elif secs < 86400:
        return '%s centiweek%s, %s microyear%s' % (_s(secs / 6048) +
                                                   _s((secs % 6048) / 31.536))
    else:
        #return '%.2f nanolightyears per kiloknot' % (secs / 18391.8)
        return '%.2f calories per megawatt' % (secs / 4186800.0)

def format_duration(secs):
    if random.random() > 0.99:
        est = format_alternate_duration(secs)
    elif 0 <= secs < 60:
        est = '%s second%s' % _s(secs)
    elif secs < 3600:
        est = '%s minute%s' % _s(secs // 60 + 1)
    elif secs < 86400:
        est = '%s hour%s, %s minute%s' % (_s(secs // 3600) +
                                          _s((secs % 3600) // 60))
    else:
        est = '%s day%s, %s hour%s' % (_s(secs // 86400) +
                                       _s((secs % 86400) // 3600))
    return est

def format_endtime(secs):
    return time.strftime('%A, %H:%M', time.localtime(time.time() + secs))


# -- UI tools ------------------------------------------------------------------

def showToolText(toolbar, action):
    widget = toolbar.widgetForAction(action)
    if isinstance(widget, QtGui.QToolButton):
        widget.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

uipath = path.dirname(__file__)

def loadUi(widget, uiname):
    uic.loadUi(path.join(uipath, uiname), widget)

def dialogFromUi(parent, uiname):
    dlg = QtGui.QDialog(parent)
    loadUi(dlg, uiname)
    return dlg

def enumerateWithProgress(seq, text, every=1, parent=None, total=None):
    total = total or len(seq)
    pd = QtGui.QProgressDialog(parent)
    pd.setLabelText(text)
    pd.setRange(0, total)
    pd.setCancelButton(None)
    if total > every:
        pd.show()
    processEvents = QtGui.QApplication.processEvents
    try:
        for i, item in enumerate(seq):
            if i % every == 0:
                pd.setValue(i)
                processEvents()
            yield i, item
    finally:
        pd.close()


class SettingGroup(object):
    def __init__(self, name):
        self.name = name
        self.settings = QtCore.QSettings()
    def __enter__(self):
        self.settings.beginGroup(self.name)
        return self.settings
    def __exit__(self, *args):
        self.settings.endGroup()
        self.settings.sync()


class DlgUtils(object):
    def __init__(self, title):
        self._dlgutils_title = self.tr(title)

    def showError(self, text):
        QtGui.QMessageBox.warning(self, self._dlgutils_title, self.tr(text))
        return None

    def showInfo(self, text):
        QtGui.QMessageBox.information(self, self._dlgutils_title, self.tr(text))
        return None

    def askQuestion(self, text, select_no=False):
        defbutton = select_no and QtGui.QMessageBox.No or QtGui.QMessageBox.Yes
        buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
        return QtGui.QMessageBox.question(self, self._dlgutils_title,
            self.tr(text), buttons, defbutton) \
            == QtGui.QMessageBox.Yes


def setBackgroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QtGui.QPalette.Base, color)
    widget.setBackgroundRole(QtGui.QPalette.Base)
    widget.setPalette(palette)

def setForegroundColor(widget, color):
    palette = widget.palette()
    palette.setColor(QtGui.QPalette.WindowText, color)
    widget.setForegroundRole(QtGui.QPalette.WindowText)
    widget.setPalette(palette)


# -- Fitting tools -------------------------------------------------------------

class FitError(Exception):
    pass


def fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                    modelfunc, beta0):
    totalwidth = abs(x0 - xb)
    xmin = x0 - totalwidth
    xmax = x0 + totalwidth
    if not len(xdata):
        raise FitError('No data in plot')
    i, maxi = 0, len(xdata) - 1
    while xdata[i] < xmin and i < maxi:
        i += 1
    mini = i
    while xdata[i] < xmax and i < maxi:
        i += 1
    maxi = i
    if mini >= maxi:
        raise FitError('No data in selected region')
    fitx = xdata[mini:maxi]
    fity = ydata[mini:maxi]
    model = Model(modelfunc)
    if yerr is not None and yerr.shape == 1:
        fiterr = yerr[mini:maxi]
        data = RealData(fitx, fity, sy=fiterr)
    else:
        data = RealData(fitx, fity)
    odr = ODR(data, model, beta0, ifixx=array([0]*len(fitx)))
    out = odr.run()
    if out.info >= 5:
        raise FitError(', '.join(out.stopreason))
    xfine = arange(xmin, xmax, (xmax-xmin)/200)
    return out.beta, xfine, modelfunc(out.beta, xfine)


fwhm_to_sigma = 2*sqrt(2*log(2))

def gauss(beta, x):
    # beta: [background, height, center, sigma]
    return beta[0] + beta[1]*exp(-(x-beta[2])**2 / (2*beta[3]**2))

def fit_gauss(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw)):
    beta0 = [yb, abs(y0-yb), x0, abs(x0-xw)/fwhm_to_sigma]
    return fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                           gauss, beta0)

def pseudo_voigt(beta, x):
    # beta: [background, height, center, width, eta]
    eta = beta[4] % 1.0
    return beta[0] + beta[1] * (
        # Lorentzian
        eta / (1 + ((x-beta[2]) / beta[3])**2) +
        # Gaussian
        (1 - eta) * exp(-log(2) * ((x-beta[2]) / beta[3])**2))

def fit_pseudo_voigt(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw)):
    beta0 = [yb, abs(y0-yb), x0, abs(x0-xw), 0.5]
    return fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                           pseudo_voigt, beta0)

def pearson_vii(beta, x):
    # beta: [background, height, center, width, m]
    eta = beta[4] % 1.0
    return beta[0] + beta[1] / \
           (1 + (2**(1/beta[4]) - 1)*((x-beta[2]) / beta[3])**2) ** beta[4]

def fit_pearson_vii(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw)):
    beta0 = [yb, abs(y0-yb), x0, abs(x0-xw), 5.0]
    return fit_peak_common(xdata, ydata, yerr, (xb, yb), (x0, y0), (xw, yw),
                           pearson_vii, beta0)


def tc_curve(beta, T):
    # Model:
    #   I(T) = B + A * (1 - T/Tc)**alpha   for T < Tc
    #   I(T) = B                           for T > Tc
    B, A, Tc, alpha = beta
    def tc_curve_1(T):
        return A*(1 - T/Tc)**(alpha % 1.0) + abs(B)
    def tc_curve_2(T):
        return abs(B)
    return piecewise(T, [T < Tc], [tc_curve_1, tc_curve_2])

def fit_tc(xdata, ydata, yerr, (Tb, Ib), (Tc, Ic)):
    if not len(xdata):
        raise FitError('No data in plot')
    Tmin, Tmax = xdata.min(), xdata.max()
    model = Model(tc_curve)
    if yerr and yerr.shape == 1:
        data = RealData(xdata, ydata, sy=yerr)
    else:
        data = RealData(xdata, ydata)
    alpha0 = 0.5
    # guess A from maximum data point
    A0 = ydata.max() / ((Tc-Tmin)/Tc)**alpha0
    beta0 = [Ib, A0, Tc, alpha0]
    odr = ODR(data, model, beta0, ifixx=array([0]*len(xdata)))
    out = odr.run()
    Tfine = arange(Tmin, Tmax, (Tmax-Tmin)/100)
    if out.info >= 5:
        raise FitError(', '.join(out.stopreason))
    return out.beta, Tfine, tc_curve(out.beta, Tfine)
