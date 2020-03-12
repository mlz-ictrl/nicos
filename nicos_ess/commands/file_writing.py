#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Nikhil Biyani <nikhil.biyani@psi.ch>
#
# *****************************************************************************

from __future__ import absolute_import, division, print_function

from time import time as currenttime

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.pycompat import number_types, string_types
from nicos.utils import parseDateString

from nicos_ess.devices.datasinks.nexussink import NexusFileWriterSink


@usercommand
@helparglist('template')
def SetNexusTemplate(template):
    """Selects the given template for the nexus files.

    The template should be one of the specified dictionaries in the
    nexus_templates module of the nexus data sink

    Example:

    >>> SetNexusTemplate('template1')
    """
    for sink in session.datasinks:
        if isinstance(sink, NexusFileWriterSink):
            sink.set_template(template)


@usercommand
@helparglist('fromtime[, totime]')
def RewriteHistory(fromtime, totime=None):
    """Rewrite the datasets to files in the given time period.

    *fromtime* and *totime* are either numbers giving **hours** in the past, or
    otherwise strings with a time specification (see below). If *totime* is not
    provided, the current time is used

    For example:

    Following commands rewrites the data from the time specified until now

    >>> RewriteHistory('1 day')             # allowed: d/day/days
    >>> RewriteHistory('1 week')            # allowed: w/week/weeks
    >>> RewriteHistory('30 minutes')        # allowed: m/min/minutes
    >>> RewriteHistory('2012-05-04 14:00')  # from that date/time on

    Following commands rewrites the data in the specified interval

    >>> RewriteHistory('14:00', '17:00')    # between 14h and 17h today
    >>> RewriteHistory('2012-05-04', '2012-05-08')  # between two days

    Following commands rewrites the data in the specified hours in past

    >>> RewriteHistory(3, 1)              # between last 3 to 1 hours from now
    >>> RewriteHistory(1)                 # in last 1 hour

    Following commands rewrites the data in the specified epoch times (sec)

    >>> RewriteHistory(1510827000, 1510828000)
    >>> RewriteHistory(1510827000)          # From specified time until now

    A combination can also be used

    >>> RewriteHistory(1510827000, 3)
    >>> RewriteHistory('2012-05-08', 1)
    """
    dataman = session.experiment.data
    for sink in session.datasinks:
        if isinstance(sink, NexusFileWriterSink):
            key = 'lastsinked'
            if isinstance(fromtime, string_types):
                try:
                    fromtime = parseDateString(fromtime)
                except ValueError:
                    pass
            # If the value is less than 10000, it represents hours
            if isinstance(fromtime, number_types) and 0 < fromtime < 10000:
                fromtime = currenttime() - fromtime * 3600
            if isinstance(totime, number_types) and 0 < totime < 10000:
                totime = currenttime() - totime * 3600
            sinks = sink.history(key, fromtime, totime)
            for _, (counter, started, finished, metainfo) in sinks:
                if counter == 0 or fromtime > finished:
                    continue
                session.log.info('Reissued dataset: %s collected during '
                                 '(%s, %s)', counter, started, finished)
                dataman.beginPoint(detectors=session.experiment.detectors,
                                   metainfo=metainfo,
                                   counter=counter,
                                   started=started,
                                   finished=finished)
                dataman.finishPoint()
