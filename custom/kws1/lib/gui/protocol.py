#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Generate a measurement protocol from saved runs."""

import os
from os import path

from PyQt4.QtGui import QPrintDialog, QPrinter, QFileDialog
from PyQt4.QtCore import pyqtSignature as qtsig

from nicos.utils import findResource, printTable
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, DlgUtils
from nicos.pycompat import to_utf8


class ProtocolPanel(Panel, DlgUtils):
    """Generate a measurement protocol from saved runs."""

    panelName = 'KWS protocol'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        DlgUtils.__init__(self, 'Protocol')
        loadUi(self, findResource('custom/kws1/lib/gui/protocol.ui'))

        self.firstEdit.setShadowText('default: all')
        self.lastEdit.setShadowText('default: all')
        self.fontBox.setValue(self.outText.font().pointSize())

    @qtsig('')
    def on_genBtn_clicked(self):
        datadir = self.client.eval('session.experiment.proposalpath', '')
        if not datadir:
            self.showError('Cannot determine data directory! Are you '
                           'connected?')
            return
        if not path.isdir(path.join(datadir, 'data')):
            self.showError('Cannot read data! This tool works only when '
                           'the data is accessible at %s.' % datadir)
            return

        first = self.firstEdit.text() or None
        if first:
            try:
                first = int(first)
            except ValueError:
                self.showError('First run is not a number!')
                return
        last = self.lastEdit.text() or None
        if last:
            try:
                last = int(last)
            except ValueError:
                self.showError('Last run is not a number!')
                return

        with_ts = self.stampBox.isChecked()

        data = []
        senv = set()

        for fname in os.listdir(path.join(datadir, 'data')):
            if not fname.endswith('.DAT'):
                continue
            parts = fname.split('_')
            if not (len(parts) > 1 and parts[1].isdigit()):
                continue
            runno = int(parts[1])
            if first is not None and runno < first:
                continue
            if last is not None and runno > last:
                continue
            try:
                data.append(self._read(runno, senv,
                                       path.join(datadir, 'data', fname)))
            except Exception as err:
                self.log.warning('could not read %s: %s', fname, err)
                continue
        data.sort(key=lambda x: x['#'])

        headers = ['Run', 'Sel', 'Coll', 'Det', 'Sample',
                   'TOF', 'Pol', 'Lens', 'Time', 'Rate']
        if with_ts:
            headers.insert(1, 'Started')
        for sename in sorted(senv):
            if sename not in ('T', 'Ts'):
                headers.append(sename)
        items = []
        day = ''
        for info in data:
            if 'Sample' not in info:
                continue
            if with_ts and info['Day'] != day:
                day = info['Day']
                items.append([''] * len(headers))
                items.append(['', day] + [''] * (len(headers) - 2))
            items.append([info.get(key, '') for key in headers])

        lines = []
        printTable(headers, items, lines.append)
        self.outText.setPlainText('\n'.join(lines) + '\n')

    @qtsig('')
    def on_saveBtn_clicked(self):
        initialdir = self.client.eval('session.experiment.scriptpath', '')
        fn = QFileDialog.getSaveFileName(self, 'Save protocol', initialdir,
                                         'Text files (*.txt)')
        if not fn:
            return
        try:
            text = self.outText.toPlainText()
            with open(fn, 'wb') as fp:
                fp.write(to_utf8(text))
        except Exception as err:
            self.showError('Could not save: %s' % err)

    @qtsig('')
    def on_printBtn_clicked(self):
        # Let the user select the desired printer via the system printer list
        printer = QPrinter()
        dialog = QPrintDialog(printer)
        if not dialog.exec_():
            return
        doc = self.outText.document().clone()
        font = self.outText.font()
        font.setPointSize(self.fontBox.value())
        doc.setDefaultFont(font)
        printer.setPageMargins(10, 15, 10, 20, QPrinter.Millimeter)
        doc.print_(printer)

    def _read(self, runno, senv, fname):
        data = {'#': runno, 'Run': str(runno), 'TOF': 'no'}
        it = iter(open(fname))
        for line in it:
            if line.startswith('Standard_Sample '):
                parts = line.split()
                data['Day'] = parts[-2]
                data['Started'] = parts[-1][:-3]
            elif line.startswith('(* Comment'):
                next(it)
                data['Sel'] = next(it).split('|')[-1].strip()[7:]
                data['Sample'] = next(it).split('|')[0].strip()
            elif line.startswith('(* Collimation'):
                next(it)
                next(it)
                info = next(it).split()
                data['Coll'] = info[0] + 'm'
                data['Pol'] = info[4]
                data['Lens'] = info[5]
                if data['Lens'] == 'out-out-out':
                    data['Lens'] = 'no'
            elif line.startswith('(* Detector Discription'):
                for _ in range(3):
                    next(it)
                info = next(it).split()
                data['Det'] = '%.3gm' % float(info[1])
            elif line.startswith('(* Temperature'):
                for _ in range(4):
                    info = next(it)
                    if 'dummy' in info:
                        continue
                    parts = info.split()
                    data[parts[0]] = parts[3]
                    senv.add(parts[0])
            elif line.startswith('(* Real'):
                data['Time'] = next(it).split()[0] + 's'
                data['t'] = int(data['Time'][:-1])
            elif line.startswith('(* Detector Data Sum'):
                next(it)
                data['Rate'] = '%.1f' % (float(next(it).split()[0]) / data['t'])
            elif line.startswith('(* Chopper'):
                data['TOF'] = 'TOF'
            elif line.startswith('(* Detector Time Slices'):
                if data['TOF'] != 'TOF':
                    data['TOF'] = 'RT'
            elif line.startswith('(* Detector Data'):
                break
        return data
