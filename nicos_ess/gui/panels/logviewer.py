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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI log viewer panel with simple filter options."""

from __future__ import absolute_import, division, print_function

import os.path

from nicos.clients.gui.panels.logviewer import \
    LogViewerPanel as DefaultLogViewerPanel
from nicos.guisupport.qt import QDateTime


class LogViewerPanel(DefaultLogViewerPanel):
    """Provides a possibility to view various NICOS log files, but arranges
    logs in reverse order, i.e. latest on top """

    def _getFilteredLogs(self, filters):
        # local vars for readability
        service = filters['service']
        fromDateTime = filters['fromDateTime']
        toDateTime = filters['toDateTime']

        path = os.path.join(self._logPath, service)

        result = '<pre style="font-family: monospace">'

        while True:
            # determine logfile name
            dateStr = toDateTime.toString('yyyy-MM-dd')
            logFile = '%s-%s.log' % (service, dateStr)

            # determine logfile path
            logFile = os.path.join(path, logFile)

            # if logfile for given date exists, read and filter content
            if os.path.exists(logFile):
                result += self._getFilteredFileContent(logFile, toDateTime,
                                                       filters)

            if toDateTime.daysTo(fromDateTime) >= 0:
                break

            toDateTime = toDateTime.addDays(-1)

        result += '</pre>'
        return result

    def _getFilteredFileContent(self, path, fileDate, filters):
        # local vars for readability
        fromDateTime = filters['fromDateTime']
        toDateTime = filters['toDateTime']
        levels = filters['levels']

        result = []
        dateStr = fileDate.toString('yyyy-MM-dd ')

        with open(path, 'r') as f:
            # store if last line was added,
            # this is used to filter tracebacks etc properly
            lastLineAdded = False
            lastLevel = ''

            for line in f:
                # split line into:
                # time, level, service, msg
                parts = [part.strip() for part in line.split(' : ')]

                # append line continuations
                if len(parts) < 2:
                    if lastLineAdded:
                        result.append(self._colorizeLevel(line, lastLevel))
                    continue

                dateTime = QDateTime.fromString(parts[0], 'HH:mm:ss,zzz')
                dateTime.setDate(fileDate.date())
                level = parts[1]

                # check time
                if fromDateTime.secsTo(dateTime) < 0 or toDateTime.secsTo(dateTime) > 0:
                    lastLineAdded = False
                    continue

                # check level
                if level not in levels:
                    lastLineAdded = False
                    continue

                # add current day to the line
                line = dateStr + line

                result.append(self._colorizeLevel(line, level))
                lastLineAdded = True
                lastLevel = level

            result = reversed(result)

        return ''.join(result)
