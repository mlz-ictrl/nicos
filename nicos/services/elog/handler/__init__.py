#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""The NICOS electronic logbook."""

from os import path


class Handler:
    def __init__(self, log, plotformat):
        self.log = log
        self.plotformat = plotformat
        self.dir = self.logdir = None

    def handle(self, key, timestamp, data):
        fun = getattr(self, f'handle_{key}', None)
        if fun:
            fun(timestamp, data)

    def close(self):
        pass

    def handle_directory(self, time, data):
        """Handle the 'directory' event.

           data = [directory, instrument, proposal]
        """
        self.dir, self.instr, self.proposal = data
        self.logdir = path.join(self.dir, 'logbook')

    def handle_newexperiment(self, time, data):
        """Handle the 'newexperiment' event.

            data = [proposal, title]
        """

    def handle_setup(self, time, setupnames):
        """Handle the 'setup' event."""

    def handle_entry(self, time, data):
        """Handle the 'entry' event."""

    def handle_remark(self, time, remark):
        """Handle the 'remark' event."""

    def handle_scriptbegin(self, time, script):
        """Handle the 'scriptbegin' event."""

    def handle_scriptend(self, time, script):
        """Handle the 'scriptend' event."""

    def handle_sample(self, time, sample):
        """Handle the 'sample' event."""

    def handle_detectors(self, time, dlist):
        """Handle the 'detectors' event."""

    def handle_environment(self, time, elist):
        """Handle the 'environment' event."""

    def handle_offset(self, time, data):
        """Handle the 'offset' event.

           data = [devices, oldoffset, newoffset]
        """

    def handle_attachment(self, time, data):
        """Handle the 'attachment' event.

           data = [description, fpaths, names]
        """

    def handle_message(self, time, message):
        """Handle the 'message' event."""

    def handle_scanbegin(self, time, dataset):
        """Handle the 'scanbegin' event."""

    def handle_scanend(self, time, dataset):
        """Handle the 'scanend' event."""


# more ideas:
# - internal links -> reference scan numbers or attachments
