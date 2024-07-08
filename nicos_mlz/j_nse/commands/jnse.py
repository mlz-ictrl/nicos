# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
#   Konstantin Kholostov <k.kholostov@fz-juelich.de>
#
# *****************************************************************************

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.core.scan import Scan


@usercommand
@helparglist('λ_values, Q_values, τ_values, '
             'number_of_phases, point_to_down, point_to_up, phase_step, '
             'counting_time, ')
def nsescan(ls, qs, ts, ph_n, p_down, p_up, ph_step, t):
    """J-NSE scan over all combinations of λ, Q and τ.

    For each (λ, Q, τ) combination the instrument moves the ``Lambda``,
    ``Q`` and ``t_nom`` devices to the requested table values (setting
    the velocity selector, mophi arm and all coil power supplies), then
    triggers ``nsedet`` which performs a phase subscan.

    The phase subscan steps ``pha1`` through ``ph_n`` positions:

    - steps 1 … ``p_down``: down-flipper coils (pi21, pi22) active;
      pha1 centred on the table value and incremented by ``ph_step``.
    - steps ``p_down+1`` … ``p_up``: only pi flipper active.
    - steps ``p_up+1`` … ``ph_n``: all flipper coils off.

    All λ, Q and τ values must be present in the instrument table.

    :param ls: wavelengths to scan (Å)
    :param qs: momentum-transfer values to scan (Å⁻¹)
    :param ts: Fourier times to scan (ns)
    :param ph_n: total number of phase steps per (λ, Q, τ) point
    :param p_down: number of steps with down-flipper coils active
    :param p_up: number of steps with pi flipper active (pi21/pi22 off)
    :param ph_step: phase increment per step (deg)
    :param t: counting time per phase step (s)

    Example — scan two τ points at fixed λ and Q::

    >>> nsescan([6], [0.08], [2, 2.7], 40, 32, 35, -45.0, 1)
    """
    _lambda = session.getDevice('Lambda')
    _q = session.getDevice('Q')
    _tau = session.getDevice('t_nom')
    _nsedet = session.getDevice('nsedet')
    positions = [[float(l), float(q), float(t)]
                 for l in ls for q in qs for t in ts]
    Scan(
        [_lambda, _q, _tau], positions,
        preset={'ph_n': ph_n, 'p_down': p_down, 'p_up': p_up,
                'ph_step': ph_step, 't': t},
        detlist=[_nsedet],
    ).run()
