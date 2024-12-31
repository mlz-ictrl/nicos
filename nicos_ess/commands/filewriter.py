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
#   AÜC Hardal <umit.hardal@ess.eu>
#   Ebad Kamil <Ebad.Kamil@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#   Kenan Muric <kenan.muric@ess.eu>
#   Jonas Petersson <jonas.petersson@ess.eu>
#
# *****************************************************************************
from contextlib import contextmanager

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.core import ADMIN, SIMULATION, requires

from nicos_ess.devices.datasinks.file_writer import FileWriterControlSink


def _find_filewriter_dev():
    for dev in session.datasinks:
        # Should only be one at most
        if isinstance(dev, FileWriterControlSink):
            return dev
    raise RuntimeError('Could not find FileWriterControlSink device')


@usercommand
@helparglist('experiment_title')
@contextmanager
def nexusfile_open(experiment_title=None):
    """Command that creates a nexusfile and starts writing data to it
    for as long as your script is running within the indentation.

    Upon completing the code within the indented block the file writing
    will stop. This is the main command that should be used when you
    want to write nexusfiles.

    For example:

    >>> with nexusfile_open('motor_dataset'):
    >>>     maw(Motor, 35)     # write scan code in indented block

    , would create a nexusfile with the title 'motor_dataset' and then
    record data for as long as the Motor device is moving. Upon reaching
    the end of the indented code block the data recording will stop.

    It is possible to make a nested call of the command, but it is
    not adviced. It will still only create one file which
    is the one that was started with the first command call.
    """
    nested_call = False
    if experiment_title is None:
        experiment_title = session.experiment.title
    try:
        active_jobs = _find_filewriter_dev().get_active_jobs()
        if not active_jobs:
            session.log.info(
                'Setting experiment title to: %s',
                experiment_title)
            start_filewriting(experiment_title)
        else:
            #  Allow nested calls, but give a warning since it is not
            #  a preferred way of writing scripts
            session.log.warning(
                'Filewriter already running. '
                'Will not start a new file with title: %s',
                experiment_title
                )
            nested_call = True
        yield
    except Exception as e:
        session.log.error('Could not start filewriting: %s', e)
        session.log.warning('The rest of the batch file code will be ignored.')
    finally:
        if not nested_call:
            stop_filewriting()
        else:
            session.log.warning(
                'Since this context did not start the '
                'filewriter for file with title: %s, '
                'it will not attempt to stop the '
                'filewriter either', experiment_title
                )


@usercommand
@helparglist('experiment_title')
def start_filewriting(experiment_title=None):
    """Start a file-writing job."""
    if experiment_title is not None and session.mode != SIMULATION:
        session.experiment.update(title=experiment_title)
    _find_filewriter_dev().start_job()


@usercommand
@helparglist('job_number')
def stop_filewriting(job_number=None):
    """Stop a file-writing job.

    :param job_number: the job to stop, only required if more than one job.
    """
    _find_filewriter_dev().stop_job(job_number)


@usercommand
def list_filewriting_jobs():
    """List current and recent file-writing jobs."""
    _find_filewriter_dev().list_jobs()


@usercommand
@requires(level=ADMIN)
@helparglist('job_number')
def replay_job(job_number):
    """Replay a recent file-writing job.

    :param job_number: the number of the job to replay.
    """
    _find_filewriter_dev().replay_job(job_number)
