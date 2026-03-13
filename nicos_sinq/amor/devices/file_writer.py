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
#   Stefan Mathis <stefan.mathis@psi.ch>
#   Jochen Stahn <jochen.stahn@psi.ch>
#
# *****************************************************************************

from datetime import datetime
from os import path

from nicos import session
from nicos.core.params import Override
from nicos_sinq.devices.datasinks.file_writer import FileWriterControlSink, \
    FileWriterSinkHandler


class AmorFileWriterSinkHandler(FileWriterSinkHandler):
    """
    An AMOR-specific filewriter sink handler which removes the proposal path
    handling from the ESS-originated FileWriterSinkHandler.
    """

    def begin(self):
        if self.sink._manual_start:
            return

        if self._scan_set and self.dataset.number > 1:
            return

        _, filepaths = self.manager.getFilenames(
            self.dataset, self.sink.filenametemplate, self.sink.subdir
        )
        filename = filepaths[0]
        if hasattr(self.dataset, 'replay_info'):
            # Replaying previous job
            self.sink._start_job(filename,
                                 self.dataset.counter,
                                 self.dataset.replay_info['structure'],
                                 self.dataset.replay_info['start_time'],
                                 self.dataset.replay_info['stop_time'],
                                 self.dataset.replay_info['replay_of'])
            return

        datetime_now = datetime.now()
        structure = self.sink._attached_nexus.get_structure(self.dataset,
                                                            datetime_now)
        self.sink._start_job(filename, self.dataset.counter,
                             structure, datetime_now)


class AmorFileWriterControlSink(FileWriterControlSink):
    """
    A FileWriterControlSink using the AmorFileWriterSinkHandler.
    """

    parameter_overrides = {
        'one_file_per_scan': Override(prefercache=False),
    }

    handlerclass = AmorFileWriterSinkHandler


class AmorDrFileWriterSinkHandler(FileWriterSinkHandler):
    """
    An AMOR-specific filewriter sink handler for the console PC amor-dr.psi.ch
    which puts the file into the folder structure on amor-dr.psi.ch (as opposed
    to AmorFileWriterSinkHandler, which uses the default SINQ storage
    locations.)

    The full_filename is forwarded to the filewriter instances running on
    amor-dr.psi.ch which generate the actual file and store it accordingly.
    """

    def begin(self):
        if self.sink._manual_start:
            return

        if self._scan_set and self.dataset.number > 1:
            return

        filename, _ = self.manager.getFilenames(
            self.dataset, self.sink.filenametemplate, self.sink.subdir
        )

        full_filename = path.join(session.experiment.datadir_amordr, filename)

        if hasattr(self.dataset, 'replay_info'):
            # Replaying previous job
            self.sink._start_job(full_filename,
                                 self.dataset.counter,
                                 self.dataset.replay_info['structure'],
                                 self.dataset.replay_info['start_time'],
                                 self.dataset.replay_info['stop_time'],
                                 self.dataset.replay_info['replay_of'])
            return

        datetime_now = datetime.now()
        structure = self.sink._attached_nexus.get_structure(self.dataset,
                                                            datetime_now)
        self.sink._start_job(full_filename, self.dataset.counter,
                             structure, datetime_now)

class AmorDrFileWriterControlSink(FileWriterControlSink):
    """
    A FileWriterControlSink using the AmorDrFileWriterSinkHandler.
    """

    parameter_overrides = {
        'one_file_per_scan': Override(prefercache=False),
    }

    handlerclass = AmorDrFileWriterSinkHandler
