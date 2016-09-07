#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI log viewer panel with simple filter options."""

import os.path
from cgi import escape

import PyQt4.QtGui  # pylint: disable=W0611
from PyQt4.QtCore import QDateTime, pyqtSlot

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, DlgUtils


class LogViewerPanel(Panel, DlgUtils):
    panelName = 'Log viewer'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        DlgUtils.__init__(self, 'Logviewer')

        self._logPath = 'log'

        loadUi(self, 'logviewer.ui', 'panels')

        # initialize date/time range to display logs from yesterday
        # (same time) to now
        self.dateTimeEditFrom.setDateTime(
            QDateTime.currentDateTime().addDays(-1))
        self.dateTimeEditTo.setDateTime(QDateTime.currentDateTime())

        if self.client.connected:
            self.on_client_connected()


    def on_client_connected(self):
        # determine log path via daemon
        controlPath = self.client.eval('config.nicos_root', '')
        loggingPath = self.client.eval('config.logging_path', '')

        self._logPath = os.path.join(controlPath, loggingPath)

        # display filtered logs
        self.updateView()

    @pyqtSlot()
    def updateView(self):
        # clear displayed log content
        self.logContent.clear()

        # determine filter for logs (via gui)
        filters = self._getFilters()

        # read log files and filter content
        content = self._getFilteredLogs(filters)

        # display filtered logs
        self.logContent.setHtml(content)

    @pyqtSlot()
    def findStr(self):
        self.logContent.find(self.findLineEdit.text())

    def _getFilters(self):
        result = {
            'levels': []
        }

        # determine desired levels
        if self.levelDebugCheckBox.isChecked():
            result['levels'].append('DEBUG')
        if self.levelInfoCheckBox.isChecked():
            result['levels'].append('INFO')
        if self.levelWarningCheckBox.isChecked():
            result['levels'].append('WARNING')
        if self.levelErrorCheckBox.isChecked():
            result['levels'].append('ERROR')
        if self.levelInputCheckBox.isChecked():
            result['levels'].append('INPUT')

        # determine desired nicos service
        result['service'] = self.serviceComboBox.currentText().lower()

        # determine desired date/time range
        result['fromDateTime'] = self.dateTimeEditFrom.dateTime()
        result['toDateTime'] = self.dateTimeEditTo.dateTime()

        return result

    def _getFilteredLogs(self, filters):
        # local vars for readability
        service = filters['service']
        fromDateTime = filters['fromDateTime']
        toDateTime = filters['toDateTime']

        path = os.path.join(self._logPath, service)

        result = '<pre style="font-family: monospace">'

        while True:
            # determine logfile name
            dateStr = fromDateTime.toString('yyyy-MM-dd')
            logFile = '%s-%s.log' % (service, dateStr)

            # determine logfile path
            logFile = os.path.join(path, logFile)

            # if logfile for given date exists, read and filter content
            if os.path.exists(logFile):
                result += self._getFilteredFileContent(logFile, fromDateTime,
                                                       filters)

            if fromDateTime.daysTo(toDateTime) <= 0:
                break

            fromDateTime = fromDateTime.addDays(1)

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

        return ''.join(result)

    STYLES = {
        'DEBUG':   'color: darkgray',
        'WARNING': 'color: fuchsia',
        'ERROR':   'color: red; font-weight: bold',
    }

    def _colorizeLevel(self, line, level):
        style = self.STYLES.get(level, '')
        if style:
            return '<span style="%s">%s</span>' % (style, escape(line))
        return escape(line)
