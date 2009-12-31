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
#   Henrik Thoma <henrik.thoma@frm2.tum.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""Cryopad specific commands for POLI."""

import numpy as np

from nicos import session
from nicos.commands import usercommand
from nicos.commands.analyze import fit
from nicos.commands.device import maw
from nicos.commands.scan import scan
from nicos.utils.fitting import PredefinedFit

__all__ = [
    'NutatorPerpendicularity',
    'NutatorsZeros_In',
    'NutatorsZeros_Out',
    'PC1Current',
    'PC2Current',
]


class PerpFit(PredefinedFit):
    fit_title = 'nutator_perp'
    fit_params = ['pmax', 'theta0']
    fit_p_descr = ['Pmax', 'theta_0']

    def fit_model(self, x, pmax, theta0):
        return pmax * np.cos(np.radians(x - theta0))

    def guesspar(self, _x, _y):
        return [1, 0]


class ZerosFit(PredefinedFit):
    fit_title = 'nutator_zeros'
    fit_params = ['pmax', 'theta0']
    fit_p_descr = ['Pmax', 'theta_0']

    def fit_model(self, x, pmax, theta0):
        gamma = np.radians(session.getDevice('gamma')())
        return -pmax * np.cos(np.radians(x - theta0)) * \
            np.sin(np.radians(x - theta0)) * (1 + np.cos(gamma))

    def guesspar(self, _x, _y):
        return [1, 0]


class PCurrentFit(PredefinedFit):
    fit_title = 'prec_current'
    fit_params = ['p0', 'pmax', 'theta0', 'period']
    fit_p_descr = ['P0', 'Pmax', 'theta_0', 'period']

    def fit_model(self, x, p0, pmax, theta0, period):
        ExpDecrease = 10000.0
        lam = session.getDevice('wavelength')()
        return p0 + pmax*np.cos(np.radians(x - theta0) * period * lam) * \
            np.exp(-(x / ExpDecrease)**2)

    def guesspar(self, _x, _y):
        return [0, 1, 0, 100]


@usercommand
def NutatorPerpendicularity(start=45, stop=135, step=5, t=2):
    adet = session.getDevice('adet')
    maw('nutator2', 0, 'nutator1', start, 'Fout', 'off', 'pc1', 0, 'pc2', 0)
    nsteps = int((stop - start) / step)
    scan('nutator1', start, step, nsteps, adet, t=t)
    fit(PerpFit, 'Asym')


@usercommand
def NutatorsZeros_In(start=45, stop=135, step=5, t=2):
    adet = session.getDevice('adet')
    lam = session.getDevice('wavelength')()
    Cryopad = session.getDevice('Cryopad')
    maw('pc2', 0, 'pc1', 180.0/(Cryopad.coefficients[0] * lam), 'Fout', 'off')
    nsteps = int((stop - start) / step)
    scan(['nutator1', 'nutator2'], [start, start-90], [step, step], nsteps,
         adet, t=t)
    fit(ZerosFit, 'Asym')


@usercommand
def NutatorsZeros_Out(start=45, stop=135, step=5, t=2):
    adet = session.getDevice('adet')
    lam = session.getDevice('wavelength')()
    Cryopad = session.getDevice('Cryopad')
    maw('pc2', 180.0/(Cryopad.coefficients[3] * lam), 'pc1', 0, 'Fout', 'off')
    nsteps = int((stop - start) / step)
    scan(['nutator1', 'nutator2'], [start, start-90], [step, step], nsteps,
         adet, t=t)
    fit(ZerosFit, 'Asym')


@usercommand
def PC1Current(start=-4, stop=4, step=0.25, t=2):
    adet = session.getDevice('adet')
    maw('nutator2', 0, 'nutator1', 0, 'Fout', 'off', 'pc2', 0)
    nsteps = int((stop - start) / step)
    scan('pc1', start, step, nsteps, adet, t=t)
    fit(PCurrentFit, 'Asym')


@usercommand
def PC2Current(start=-4, stop=4, step=0.25, t=2):
    adet = session.getDevice('adet')
    maw('nutator2', 0, 'nutator1', 0, 'Fout', 'off', 'pc1', 0)
    nsteps = int((stop - start) / step)
    scan('pc2', start, step, nsteps, adet, t=t)
    fit(PCurrentFit, 'Asym')
