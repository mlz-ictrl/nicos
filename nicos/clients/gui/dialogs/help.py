# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI help window."""

from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QMainWindow, QUrl, QWebEnginePage, \
    QWebEngineView, pyqtSlot

if QWebEngineView is None:
    raise ImportError('Qt webview component is not available')


class HelpPage(QWebEnginePage):
    """Subclass to intercept navigation requests."""

    def __init__(self, client, history, parent):
        self.client = client
        self.history = history
        self.orig_url = QUrl('about:blank')
        self._setting_html = False
        # (pylint detects QWebEnginePage as being None...)
        # pylint: disable=non-parent-init-called
        QWebEnginePage.__init__(self, parent)

    def setHtml(self, html, url):
        self._setting_html = True
        QWebEnginePage.setHtml(self, html, url)
        self._setting_html = False
        self.orig_url = url

    def acceptNavigationRequest(self, url, *args):
        if self._setting_html:
            return True
        if url.toString().startswith('data:text/html'):
            return True
        else:
            target = url.toString()
            self.client.eval('session.showHelp(%r)' % target)
        return False


class HelpWindow(QMainWindow):

    def __init__(self, parent, client):
        QMainWindow.__init__(self, parent)
        loadUi(self, 'dialogs/helpwin.ui')
        self.history = []
        self.webView = QWebEngineView(self)
        self.webView.setPage(HelpPage(client, self.history, self.webView))
        self.frame.layout().addWidget(self.webView)
        self.client = client
        self._next_scrollpos = None

    def showHelp(self, data):
        pseudourl, html = data
        if self._next_scrollpos is None:
            self.history.append((self.webView.page().orig_url.toString(),
                                 self.webView.page().scrollPosition()))
            if len(self.history) > 100:
                self.history = self.history[-100:]
        if self._next_scrollpos is not None:
            html += '<script>window.scrollTo(%s, %s)</script>' % (
                self._next_scrollpos.x(), self._next_scrollpos.y())
            self._next_scrollpos = None
        self.webView.page().setHtml(html, QUrl(pseudourl))
        self.show()

    @pyqtSlot()
    def on_backBtn_clicked(self):
        if not self.history:
            return
        target, scrollpos = self.history[-1]
        if not target or target == 'about:blank':
            return
        del self.history[-1]
        self._next_scrollpos = scrollpos
        self.client.eval('session.showHelp(%r)' % target)

    @pyqtSlot()
    def on_contentsBtn_clicked(self):
        self.client.eval('session.showHelp("index")')

    @pyqtSlot()
    def on_searchBtn_clicked(self):
        self._search()

    def on_searchBox_returnPressed(self):
        self._search()

    def _search(self):
        self.webView.findText(self.searchBox.text())

    @pyqtSlot()
    def on_closeBtn_clicked(self):
        self.close()
