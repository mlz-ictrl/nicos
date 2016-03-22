#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""Base file data sink class for NICOS."""

from nicos.core.data import DataSink
from nicos.core.params import Param, listof, subdir

TEMPLATE_DESC = '''Templates must contain percent-style placeholders
(e.g. ``%(proposal)s_%(pointcounter)08d``) with the following keys:

* counters:

  - ``(type)counter`` for globally unique counters
  - ``(type)propcounter`` for unique counters within a proposal
  - ``(type)samplecounter`` for unique counters within a sample directory \
    (for many instruments, there is no separate sample directory, so this \
    counter is the same as the propcounter)
  - ``(type)number`` for the dataset's number within its parent

  ``type`` is the dataset type, e.g. ``point`` or ``scan``.

* proposal info from the experiment (e.g. ``proposal`` for the prop. number)

* all devices and parameters (e.g. ``dev1`` for the value of dev1 and
  ``dev1.param`` for a parameter)
'''


class FileSink(DataSink):
    """Base class for sinks that save data into files."""

    parameters = {
        'subdir':           Param('Filetype specific subdirectory name',
                                  type=subdir, mandatory=False, default=''),
        'filenametemplate': Param('List of templates for data file names '
                                  '(will be hardlinked)',
                                  ext_desc=TEMPLATE_DESC, type=listof(str),
                                  default=['%(pointcounter)08d.dat'],
                                  settable=False, prefercache=False),
    }
