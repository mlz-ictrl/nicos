#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""NICOS GUI electronic logbook window."""

__version__ = "$Revision$"

from os import path

from PyQt4.QtCore import SIGNAL, Qt, QTimer, QUrl, pyqtSignature as qtsig

from nicos.gui.panels import Panel
from nicos.gui.utils import loadUi, DlgUtils, setBackgroundColor


class ELogPanel(Panel, DlgUtils):
    panelName = 'Electronic logbook'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        DlgUtils.__init__(self, 'Logbook')
        loadUi(self, 'elog.ui', 'panels')
        self.stacker.setCurrentIndex(0)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.connect(self.timer, SIGNAL('timeout()'), self.on_timer_timeout)

        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)

    def on_timer_timeout(self):
        sig = SIGNAL('loadFinished(bool)')
        frame = self.preview.page().mainFrame().childFrames()[1]
        scrollval = frame.scrollBarValue(Qt.Vertical)
        was_at_bottom = scrollval == frame.scrollBarMaximum(Qt.Vertical)
        # restore current scrolling position in document on reload
        def callback(new_size):
            nframe = self.preview.page().mainFrame().childFrames()[1]
            if was_at_bottom:
                nframe.setScrollBarValue(Qt.Vertical,
                                         nframe.scrollBarMaximum(Qt.Vertical))
            else:
                nframe.setScrollBarValue(Qt.Vertical, scrollval)
            self.disconnect(self.preview, sig, callback)
        self.connect(self.preview, sig, callback)
        self.preview.reload()

    def on_client_connected(self):
        datapath = self.client.eval('_GetDatapath()')
        logfile = path.join(datapath[0], 'logbook', 'logbook.html')
        self.preview.load(QUrl(logfile))  # XXX reload periodically

    def on_refreshLabel_linkActivated(self, link):
        if link == 'refresh':
            self.on_timer_timeout()
        elif link == 'back':
            self.preview.back()
        elif link == 'forward':
            self.preview.forward()

    def setCustomStyle(self, font, back):
        self.freeFormText.setFont(font)
        setBackgroundColor(self.freeFormText, back)

    @qtsig('')
    def on_newProposal_clicked(self):
        try:
            num = int(str(self.proposalNum.text()))
        except ValueError:
            return self.showError('Proposal should be numeric.')
        self.client.ask('eval', 'NewExperiment(%r)' % num)
        self.timer.start(750)

    @qtsig('')
    def on_newSample_clicked(self):
        name = str(self.sampleName.text())
        if not name:
            return
        self.client.ask('eval', 'NewSample(%r)' % name)
        self.timer.start(750)

    @qtsig('')
    def on_addRemark_clicked(self):
        remark = str(self.remarkText.text())
        if not remark:
            return
        self.client.ask('eval', 'Remark(%r)' % remark)
        self.remarkText.setText('')
        self.remarkText.setFocus()
        self.timer.start(750)

    @qtsig('')
    def on_addFreeForm_clicked(self):
        freeform = str(self.freeFormText.toPlainText())
        if not freeform:
            return
        self.client.ask('eval', 'LogEntry(%r)' % freeform)
        self.freeFormText.clear()
        self.freeFormText.setFocus()
        self.timer.start(750)

    @qtsig('')
    def on_fileSelect_clicked(self):
        self.selectInputFile(self.fileName, 'Choose a file to attach')
        self.fileRename.setFocus()

    @qtsig('')
    def on_addFile_clicked(self):
        fname = str(self.fileName.text())
        if not path.isfile(fname):
            return self.showError('The given file name is not a valid file.')
        newname = str(self.fileRename.text())
        if not newname:
            newname = path.basename(fname)
        desc = str(self.fileDesc.text())
        # XXX put the file somewhere the daemon can find it
        self.client.ask('eval', 'LogAttach(%r, [%r], [%r])' %
                        (desc, fname, newname))
        self.fileName.setFocus()
        self.timer.start(750)

    def on_creoleLabel_linkActivated(self, link):
        self.stacker.setCurrentIndex(1)

    @qtsig('')
    def on_creoleDone_clicked(self):
        self.stacker.setCurrentIndex(0)

    def on_remarkText_returnPressed(self):
        self.addRemark.click()

    def on_fileName_returnPressed(self):
        self.addFile.click()

    def on_fileRename_returnPressed(self):
        self.addFile.click()
