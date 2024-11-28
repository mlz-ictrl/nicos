# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Stanislav Nikitin <stanislav.nikitin@psi.ch>
#
# *****************************************************************************

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.analyze import gauss
from nicos.commands.tas import qcscan

__all__ = ['adjust_lattice_parameter']


@usercommand
@helparglist('peak [, step=0.01, np=21, mn=1000]')
def adjust_lattice_parameter(peak, step=0.01, np=21, mn=1000):
    """Adjust the lattice parameter using a given peak
    """

    # Check direction of the scan
    if peak[0] != 0 and peak[1] == 0 and peak[2] == 0:
        scanstep = [1, 0, 0, 0] * step
        # var = 'H'
        ind = 0
    if peak[0] == 0 and peak[1] != 0 and peak[2] == 0:
        scanstep = [0, 1, 0, 0] * step
        # var = 'K'
        ind = 1
    if peak[0] == 0 and peak[1] == 0 and peak[2] != 0:
        scanstep = [0, 0, 1, 0] * step
        # var = 'L'
        ind = 2
    else:
        session.log.error('The peak should be parallel to one of the axes')
        return

    # do the scan and fit with a Gaussian
    qcscan(peak, scanstep, np, m=mn)
    # fit_res = gauss(var, 'CNTS')
    fit_res = gauss()

    # read and remember the old lattice parameter
    smp = session.experiment.sample
    abc = smp.lattice  # TODO there might not always be a lattice param
    old_par = abc[ind]

    # calculate and return the new parameter
    new_par = old_par*peak[ind]/fit_res[0][0]

    # calculate relative change in the lattice parameter
    rl_ch = abs(new_par-old_par)/old_par*100
    # check if the change is above treshold of 5 percent
    if rl_ch > 5:
        session.log.info('The change in lattice parameter is' +
                         ' %.3f percent', rl_ch)
        session.log.info('Please update the lattice parameters manually')
    else:
        session.log.info('The new lattice parameter is %.4f A', new_par)
        smp.lattice[ind] = new_par
