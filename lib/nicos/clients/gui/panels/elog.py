#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

from os import path
from cgi import escape

from PyQt4.QtGui import QMainWindow, QTextEdit, QDialog, QInputDialog, QMenu, \
     QToolBar
from PyQt4.QtCore import SIGNAL, Qt, QTimer, QUrl, pyqtSignature as qtsig

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, dialogFromUi, DlgUtils


class ELogPanel(Panel, DlgUtils):
    panelName = 'Electronic logbook'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        DlgUtils.__init__(self, 'Logbook')
        loadUi(self, 'elog.ui', 'panels')

        self.timer = QTimer(self, singleShot=True, timeout=self.on_timer_timeout)

        if self.client.connected:
            self.on_client_connected()
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)

        self.preview.page().setForwardUnsupportedContent(True)
        self.connect(self.preview.page(),
                     SIGNAL('unsupportedContent(QNetworkReply *)'),
                     self.on_page_unsupportedContent)

    def getMenus(self):
        menu1 = QMenu('&Browser', self)
        menu1.addAction(self.actionBack)
        menu1.addAction(self.actionForward)
        menu1.addSeparator()
        menu1.addAction(self.actionRefresh)
        menu2 = QMenu('&Logbook', self)
        menu2.addAction(self.actionAddComment)
        menu2.addAction(self.actionAddRemark)
        menu2.addSeparator()
        menu2.addAction(self.actionAttachFile)
        menu2.addSeparator()
        menu2.addAction(self.actionNewSample)
        return [menu1, menu2]

    def getToolbars(self):
        bar = QToolBar('Logbook')
        bar.addAction(self.actionBack)
        bar.addAction(self.actionForward)
        bar.addSeparator()
        bar.addAction(self.actionRefresh)
        bar.addSeparator()
        bar.addAction(self.actionAddComment)
        bar.addAction(self.actionAddRemark)
        bar.addSeparator()
        bar.addAction(self.actionNewSample)
        bar.addAction(self.actionAttachFile)
        return [bar]

    def on_timer_timeout(self):
        sig = SIGNAL('loadFinished(bool)')
        try:
            frame = self.preview.page().mainFrame().childFrames()[1]
        except IndexError:
            print 'No logbook seems to be loaded.'
            self.on_client_connected()
            return
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
        proposaldir = self.client.eval('session.experiment.proposaldir', None)
        if not proposaldir:
            return
        logfile = path.join(proposaldir, 'logbook', 'logbook.html')
        if path.isfile(logfile):
            self.preview.load(QUrl(logfile))
        else:
            self.preview.setHtml(
                '<style>body { font-family: sans-serif; }</style>'
                '<p><b>The logbook HTML file does not seem to exist.</b></p>'
                '<p>Please check that the file is created and accessible on '
                '<b>your local computer</b> at %s.  Then click '
                '"refresh" above.' % escape(path.normpath(logfile)))

    def on_page_unsupportedContent(self, reply):
        if reply.url().scheme() != 'file':
            return
        filename = str(reply.url().path())
        if filename.endswith('.dat'):
            content = open(filename).read()
            window = QMainWindow(self)
            window.resize(600, 800)
            window.setWindowTitle(filename)
            widget = QTextEdit(window)
            widget.setFontFamily('monospace')
            window.setCentralWidget(widget)
            widget.setText(content)
            window.show()

    def on_refreshLabel_linkActivated(self, link):
        if link == 'refresh':
            self.on_timer_timeout()
        elif link == 'back':
            self.preview.back()
        elif link == 'forward':
            self.preview.forward()

    @qtsig('')
    def on_actionRefresh_triggered(self):
        self.on_timer_timeout()

    @qtsig('')
    def on_actionBack_triggered(self):
        self.preview.back()

    @qtsig('')
    def on_actionForward_triggered(self):
        self.preview.forward()

    @qtsig('')
    def on_actionNewSample_triggered(self):
        name, ok = QInputDialog.getText(self, 'New sample',
            'Please enter the new sample name:')
        if not ok or not name:
            return
        name = unicode(name)
        self.client.ask('eval', 'NewSample(%r)' % name)
        self.timer.start(750)

    @qtsig('')
    def on_actionAddRemark_triggered(self):
        remark, ok = QInputDialog.getText(self, 'New remark',
            'Please enter the remark.  The remark will be add to the logbook '
            'as a heading and will also appear in the data files.')
        if not ok or not remark:
            return
        remark = unicode(remark)
        self.client.ask('eval', 'Remark(%r)' % remark)
        self.timer.start(750)

    @qtsig('')
    def on_actionAddComment_triggered(self):
        dlg = dialogFromUi(self, 'elog_comment.ui', 'panels')
        dlg.helpFrame.setVisible(False)
        dlg.creoleLabel.linkActivated.connect(
            lambda link: dlg.helpFrame.setVisible(True))
        if dlg.exec_() != QDialog.Accepted:
            return
        text = unicode(dlg.freeFormText.toPlainText())
        if not text:
            return
        self.client.ask('eval', 'LogEntry(%r)' % text)
        self.timer.start(750)

    @qtsig('')
    def on_actionAttachFile_triggered(self):
        dlg = dialogFromUi(self, 'elog_attach.ui', 'panels')
        def on_fileSelect_clicked():
            self.selectInputFile(dlg.fileName, 'Choose a file to attach')
            dlg.fileRename.setFocus()
        dlg.fileSelect.clicked.connect(on_fileSelect_clicked)
        if dlg.exec_() != QDialog.Accepted:
            return
        fname = unicode(dlg.fileName.text())
        if not path.isfile(fname):
            return self.showError('The given file name is not a valid file.')
        newname = unicode(dlg.fileRename.text())
        if not newname:
            newname = path.basename(fname)
        desc = unicode(dlg.fileDesc.text())
        filecontent = open(fname, 'rb').read()
        # file content may contain \x1e characters; encode to base64
        remotefn = self.client.ask('transfer', filecontent.encode('base64'))
        self.client.ask('eval', 'LogAttach(%r, [%r], [%r])' %
                        (desc, remotefn, newname))
        self.timer.start(750)
