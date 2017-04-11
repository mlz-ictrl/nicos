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

"""NICOS GUI help window."""

from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import QUrl, pyqtSignature as qtsig

try:
    from PyQt4.QtWebKit import QWebPage
except ImportError:
    QWebPage = None

from nicos.clients.gui.utils import loadUi


class HelpWindow(QMainWindow):

    def __init__(self, parent, client):
        QMainWindow.__init__(self, parent)
        loadUi(self, 'helpwin.ui', 'dialogs')
        self.client = client
        self.history = []
        self._next_scrollpos = None

    def showHelp(self, data):
        pseudourl, html = data
        if self._next_scrollpos is None:
            self.history.append((self.webView.url().toString(),
                                 self.webView.page().mainFrame().scrollPosition()))
            if len(self.history) > 100:
                self.history = self.history[-100:]
        self.webView.setHtml(html, QUrl(pseudourl))
        self.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        if self._next_scrollpos is not None:
            self.webView.page().mainFrame().setScrollPosition(self._next_scrollpos)
            self._next_scrollpos = None
        self.show()

    def on_webView_linkClicked(self, url):
        if url.toString().startswith('#'):
            frame = self.webView.page().mainFrame()
            self.history.append((self.webView.url().toString(),
                                 frame.scrollPosition()))
            el = frame.findFirstElement(url.toString())
            frame.setScrollPosition(el.geometry().topLeft())
        else:
            target = url.toString()
            self.client.eval('session.showHelp(%r)' % target)

    @qtsig('')
    def on_backBtn_clicked(self):
        if not self.history:
            return
        target, scrollpos = self.history[-1]
        if not target or target == 'about:blank':
            return
        del self.history[-1]
        self._next_scrollpos = scrollpos
        self.client.eval('session.showHelp(%r)' % target)

    @qtsig('')
    def on_contentsBtn_clicked(self):
        self.client.eval('session.showHelp("index")')

    @qtsig('')
    def on_searchBtn_clicked(self):
        self.webView.findText(self.searchBox.text(),
                              QWebPage.FindWrapsAroundDocument)

    def on_searchBox_returnPressed(self):
        self.webView.findText(self.searchBox.text(),
                              QWebPage.FindWrapsAroundDocument)

    @qtsig('')
    def on_closeBtn_clicked(self):
        self.close()
