# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
#   Pierre Boillat <pierre.boillat@psi.ch>
#
# *****************************************************************************
from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.scan import scan

__all__ = ['tomo_setup', 'tomo_run', 'tomo_resume', 'tomo_abort']

# pylint: disable=W0603
# pylint: disable=global-variable-not-assigned


def tomo_scanpos(nproj, nimg, ifirst=1):
    rlist = [(i // nimg) * 360.0 / nproj for i in range(nimg * (nproj + 1))]
    ilist = list(range(1, nimg * (nproj + 1) + 1))

    rlist = rlist[ifirst - 1:]
    ilist = ilist[ifirst - 1:]

    return ilist, rlist


@usercommand
@helparglist('device, nproj, nimg=1')
def tomo_setup(device, nproj, nimg=1):
    """Setup a new tomography run.

    This commands does not actually start the tomography
    (use "tomo_run()" for this), it only memorizes the
    chosen parameters. If a tomography was previoulsy started
    and did not finished, it needs either to be aborted with
    "tomo_abort()" or finished with "tomo_resume()" before another
    tomography can be set up. When several tomographies with the
    same parameters are performed, there is no need to use
    the "tomo_setup()" command several times, only set up once
    and then use "tomo_run()" for each of the tomographies.

    Examples:

    Setting up a 625 projections tomography at measurement position 2:

    >>> tomo_setup(sp2_ry, 625)

    Setting up a 375 projections tomography at measurement position 3,
    with 3 images per projection:

    >>> tomo_setup(sp3_ry, 375, 3)

    """
    if session.experiment.tomo_params['status'] == 'running':
        session.log.error(
            'The previously started tomography did not finish. Use '
            '"tomo_resume()" to continue it or "tomo_abort()" to abort it.')

    if device:
        session.experiment.tomo_params = {
            'device': device,
            'nproj': nproj,
            'nimg': nimg,
            'status': 'ready'
        }
    else:
        session.experiment.tomo_params = {
            'status': 'reset'
        }


@usercommand
@helparglist('')
def tomo_run():
    """Start a previously defined tomography.

    This command will start the tomography previously defined using the
    "tomo_setup()" command. If a tomography was previoulsy started and
    did not finished, it needs either to be aborted with "tomo_abort()"
    or finished with "tomo_resume()" before another tomography can be started.

    """
    status = session.experiment.tomo_params['status']

    if status == 'running':
        session.log.error(
            'The previously started tomography did not finish. '
            'Use "tomo_resume()" to continue it or '
            '"tomo_abort()" to abort it.')

    elif status == 'reset':
        session.log.error('Tomography not configured, use '
                          '"tomo_setup()" to choose the parameters.')

    else:

        rdev = session.getDevice(session.experiment.tomo_params['device'])
        idev = session.getDevice('img_index')

        ilist, rlist = tomo_scanpos(session.experiment.tomo_params['nproj'],
                                    session.experiment.tomo_params['nimg'])

        session.experiment.tomo_params['status'] = 'running'

        scan([idev, rdev], [ilist, rlist])

        session.experiment.tomo_params['status'] = 'ready'


@usercommand
@helparglist('')
def tomo_resume():
    """Resume a tomography.

    This command can only be used when a previously started tomography
    did not finish properly. The tomography will be restarted after
    the last good exposure. Note that the assumption of which is the
    last good exposure is done conservatively, which
    may lead to duplicate images of some projections.

    """
    status = session.experiment.tomo_params['status']

    if status != 'running':
        session.log.error('There is no started tomography to resume.')

    else:

        rdev = session.getDevice(session.experiment.tomo_params['device'])
        idev = session.getDevice('img_index')

        ifirst = int(idev.read(0))
        if ifirst > 1:
            ifirst -= 1

        ilist, rlist = tomo_scanpos(session.experiment.tomo_params['nproj'],
                                    session.experiment.tomo_params['nimg'],
                                    ifirst)

        session.experiment.tomo_params['status'] = 'running'

        scan([idev, rdev], [ilist, rlist])

        session.experiment.tomo_params['status'] = 'ready'


@usercommand
@helparglist('')
def tomo_abort():
    """Abort a tomography.

    This command can only be used when a previously started tomography
    did not finish properly.
    """
    status = session.experiment.tomo_params['status']

    if status != 'running':
        session.log.error('There is no started tomography to abort.')

    else:
        session.experiment.tomo_params['status'] = 'ready'
