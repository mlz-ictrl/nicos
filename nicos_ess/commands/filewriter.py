#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2022 by the NICOS contributors (see AUTHORS)
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
#
# *****************************************************************************
from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.core import ADMIN, requires

from nicos_ess.devices.datasinks.file_writer import FileWriterControlSink


def _find_filewriter_dev():
    for dev in session.datasinks:
        # Should only be one at most
        if isinstance(dev, FileWriterControlSink):
            return dev
    raise RuntimeError("Could not find FileWriterControlSink device")


@usercommand
@helparglist('experiment_title')
def start_job(experiment_title=None):
    """Start a file-writing job."""
    if experiment_title is not None:
        session.experiment.update(title=experiment_title)
    _find_filewriter_dev().start_job()


@usercommand
@helparglist('job_number')
def stop_job(job_number=None):
    """Stop a file-writing job.

    :param job_number: the job to stop, only required if more than one job.
    """
    _find_filewriter_dev().stop_job(job_number)


@usercommand
def list_jobs():
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
