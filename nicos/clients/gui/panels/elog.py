# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI electronic logbook window."""

import html
from os import path

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import dialogFromUi, loadUi
from nicos.guisupport.qt import QActionGroup, QDesktopServices, QDialog, \
    QFontDatabase, QInputDialog, QLineEdit, QMainWindow, QMenu, QPrintDialog, \
    QPrinter, QPushButton, Qt, QTextDocument, QTextEdit, QTimer, QToolBar, \
    QUrl, QWebEnginePage, QWebEngineView, pyqtSlot

if QWebEngineView is None:
    raise ImportError('Qt webview component is not available')


class ELogPanel(Panel):
    """Provides a HTML widget for the electronic logbook."""

    panelName = 'Electronic logbook'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, 'panels/elog.ui')
        self.preview = QWebEngineView(self)
        self.frame.layout().addWidget(self.preview)

        self.timer = QTimer(self, singleShot=True,
                            timeout=self.on_timer_timeout)
        self.propdir = None

        self.menus = None
        self.bar = None

        if client.isconnected:
            self.on_client_connected()
        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)
        client.experiment.connect(self.on_client_experiment)

        self.activeGroup = QActionGroup(self)
        self.activeGroup.addAction(self.actionAddComment)
        self.activeGroup.addAction(self.actionAddRemark)
        self.activeGroup.addAction(self.actionAttachFile)
        self.activeGroup.addAction(self.actionNewSample)

        page = self.preview.page()
        if hasattr(page, 'setForwardUnsupportedContent'):  # QWebKit only
            page.setForwardUnsupportedContent(True)
            page.unsupportedContent.connect(self.on_page_unsupportedContent)

    def getMenus(self):
        if not self.menus:
            menu1 = QMenu('&Browser', self)
            menu1.addAction(self.actionBack)
            menu1.addAction(self.actionForward)
            menu1.addSeparator()
            menu1.addAction(self.actionRefresh)
            menu1.addAction(self.actionPrint)
            menu2 = QMenu('&Logbook', self)
            menu2.addAction(self.actionAddComment)
            menu2.addAction(self.actionAddRemark)
            menu2.addSeparator()
            menu2.addAction(self.actionAttachFile)
            menu2.addSeparator()
            menu2.addAction(self.actionNewSample)
            self.menus = [menu1, menu2]

        return self.menus

    def getToolbars(self):
        if not self.bar:
            bar = QToolBar('Logbook')
            bar.addAction(self.actionBack)
            bar.addAction(self.actionForward)
            bar.addSeparator()
            bar.addAction(self.actionRefresh)
            bar.addAction(self.actionPrint)
            bar.addSeparator()
            bar.addAction(self.actionAddComment)
            bar.addAction(self.actionAddRemark)
            bar.addSeparator()
            bar.addAction(self.actionNewSample)
            bar.addAction(self.actionAttachFile)
            bar.addSeparator()
            box = QLineEdit(self)
            btn = QPushButton('Search', self)
            bar.addWidget(box)
            bar.addWidget(btn)

            def callback():
                if hasattr(QWebEnginePage, 'FindWrapsAroundDocument'):  # WebKit
                    self.preview.findText(box.text(),
                                          QWebEnginePage.FindWrapsAroundDocument)
                else:
                    # WebEngine wraps automatically
                    self.preview.findText(box.text())
            box.returnPressed.connect(callback)
            btn.clicked.connect(callback)
            self.bar = bar

        return [self.bar]

    def setViewOnly(self, viewonly):
        self.activeGroup.setEnabled(not viewonly)

    def on_timer_timeout(self):
        if hasattr(self.preview.page(), 'mainFrame'):  # QWebKit only
            try:
                frame = self.preview.page().mainFrame().childFrames()[1]
            except IndexError:
                self.log.error('No logbook seems to be loaded.')
                self.on_client_connected()
                return
            scrollval = frame.scrollBarValue(Qt.Orientation.Vertical)
            was_at_bottom = \
                scrollval == frame.scrollBarMaximum(Qt.Orientation.Vertical)

            # restore current scrolling position in document on reload
            def callback(new_size):
                nframe = self.preview.page().mainFrame().childFrames()[1]
                if was_at_bottom:
                    nframe.setScrollBarValue(
                        Qt.Orientation.Vertical,
                        nframe.scrollBarMaximum(Qt.Orientation.Vertical))
                else:
                    nframe.setScrollBarValue(Qt.Orientation.Vertical, scrollval)
                self.preview.loadFinished.disconnect(callback)
            self.preview.loadFinished.connect(callback)
        self.preview.reload()

    def on_client_connected(self):
        self._update_content()

    def on_client_experiment(self, data):
        self._update_content()

    def _update_content(self):
        self.propdir = self.client.eval('session.experiment.proposalpath', '')
        if not self.propdir:
            return
        logfile = path.abspath(path.join(
            self.propdir, 'logbook', 'logbook.html'))
        if path.isfile(logfile):
            self.preview.load(QUrl('file://' + logfile))
        else:
            self.preview.setHtml(
                '<style>body { font-family: sans-serif; }</style>'
                '<p><b>The logbook HTML file does not seem to exist.</b></p>'
                '<p>Please check that the file is created and accessible on '
                '<b>your local computer</b> at %s.  Then click '
                '"refresh" above.' % html.escape(path.normpath(logfile)))

    def on_page_unsupportedContent(self, reply):
        if reply.url().scheme() != 'file':
            return
        filename = reply.url().path()
        if filename.endswith('.dat'):
            with open(filename, encoding='utf-8', errors='replace') as fp:
                content = fp.read()
            window = QMainWindow(self)
            window.resize(600, 800)
            window.setWindowTitle(filename)
            widget = QTextEdit(window)
            widget.setFontFamily('Monospace')
            window.setCentralWidget(widget)
            widget.setText(content)
            window.show()
        else:
            # try to open the link with host computer default application
            try:
                QDesktopServices.openUrl(reply.url())
            except Exception:
                pass

    def on_refreshLabel_linkActivated(self, link):
        if link == 'refresh':
            self.on_timer_timeout()
        elif link == 'back':
            self.preview.back()
        elif link == 'forward':
            self.preview.forward()

    @pyqtSlot()
    def on_actionRefresh_triggered(self):
        # if for some reason, we have the wrong proposal path, update here
        propdir = self.client.eval('session.experiment.proposalpath', '')
        if propdir and propdir != self.propdir:
            self._update_content()
        else:
            self.on_timer_timeout()

    @pyqtSlot()
    def on_actionBack_triggered(self):
        self.preview.back()

    @pyqtSlot()
    def on_actionForward_triggered(self):
        self.preview.forward()

    @pyqtSlot()
    def on_actionNewSample_triggered(self):
        name, ok = QInputDialog.getText(self, 'New sample',
                                        'Please enter the new sample name:')
        if not ok or not name:
            return
        self.client.eval('NewSample(%r)' % name)
        self.timer.start(750)

    @pyqtSlot()
    def on_actionAddRemark_triggered(self):
        remark, ok = QInputDialog.getText(
            self, 'New remark',
            'Please enter the remark.  The remark will be added to the logbook '
            'as a heading and will also appear in the data files.')
        if not ok or not remark:
            return
        self.client.eval('Remark(%r)' % remark)
        self.timer.start(750)

    @pyqtSlot()
    def on_actionAddComment_triggered(self):
        dlg = dialogFromUi(self, 'panels/elog_comment.ui')
        dlg.helpFrame.setVisible(False)
        if hasattr(dlg.viewer, 'setMarkdown'):
            dlg.editor.textChanged.connect(
                lambda : dlg.viewer.setMarkdown(dlg.editor.toPlainText()))
        else:
            dlg.viewer.hide()
        dlg.mdLabel.linkActivated.connect(
            lambda link: dlg.helpFrame.setVisible(True))
        f = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        f.setFixedPitch(True)
        dlg.editor.setFont(f)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        text = dlg.editor.toPlainText()
        if not text:
            return
        self.client.eval('LogEntry(%r)' % text)
        self.timer.start(750)

    @pyqtSlot()
    def on_actionAttachFile_triggered(self):
        dlg = dialogFromUi(self, 'panels/elog_attach.ui')

        def on_fileSelect_clicked():
            self.selectInputFile(dlg.fileName, 'Choose a file to attach')
            dlg.fileRename.setFocus()
        dlg.fileSelect.clicked.connect(on_fileSelect_clicked)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        fname = dlg.fileName.text()
        if not path.isfile(fname):
            return self.showError('The given file name is not a valid file.')
        newname = dlg.fileRename.text()
        if not newname:
            newname = path.basename(fname)
        desc = dlg.fileDesc.text()
        with open(fname, 'rb') as fp:
            filecontent = fp.read()
        remotefn = self.client.ask('transfer', filecontent)
        if remotefn is not None:
            self.client.eval('_LogAttach(%r, [%r], [%r])' %
                             (desc, remotefn, newname))
        self.timer.start(750)

    @pyqtSlot()
    def on_actionPrint_triggered(self):
        # Let the user select the desired printer via the system printer list
        printer = QPrinter()
        dialog = QPrintDialog(printer)

        if not dialog.exec():
            return

        mainFrame = self.preview.page().mainFrame()
        childFrames = mainFrame.childFrames()

        # Workaround for Qt versions < 4.8.0
        printWholeSite = True
        if hasattr(QWebEngineView, 'selectedHtml'):
            if self.preview.hasSelection():
                printWholeSite = False

        # use whole frame if no content is selected or selecting html is not
        # supported
        if printWholeSite:
            # set 'content' frame active as printing an inactive web frame
            # doesn't work properly

            if len(childFrames) >= 2:
                childFrames[1].setFocus()

                # thanks to setFocus, we can get the print the frame
                # with evaluated javascript
                html = childFrames[1].toHtml()
        else:
            html = self.preview.selectedHtml()

            # construct head
            head = '<head>'

            # extract head from child frames
            for frame in childFrames:
                headEl = frame.findFirstElement('head')
                head += headEl.toInnerXml()

            head += '</head>'

            # concat new head and selection
            # the result may be invalid html; needs improvements!
            html = head + html

        # prepend a header to the log book
        html.replace('</head>', '</head><h1>NICOS Log book</h1>')

        # let qt layout the content
        doc = QTextDocument()
        doc.setHtml(html)

        doc.print_(printer)
