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
#
# *****************************************************************************

"""Browser GUI tool."""

from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QDialog, QUrl, QWebEngineView

if QWebEngineView is None:
    raise ImportError('Qt webview component is not available')


class WebsiteTool(QDialog):
    """A dialog that just displays a website using the Qt HTML view.

    Options:

      * ``url`` -- the URL of the website.
    """

    def __init__(self, parent, client, **settings):
        QDialog.__init__(self, parent)
        loadUi(self, 'tools/website.ui')
        self.webView = QWebEngineView(self)
        self.layout().addWidget(self.webView)
        self.backBtn.clicked.connect(self.webView.back)
        self.fwdBtn.clicked.connect(self.webView.forward)

        site = settings.get('url', '')
        if site:
            self.webView.load(QUrl(site))

        self.closeBtn.clicked.connect(self.close)

    def closeEvent(self, event):
        self.deleteLater()
        self.accept()
