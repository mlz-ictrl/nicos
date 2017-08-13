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

"""Browser GUI tool."""

from nicos.guisupport.qt import QUrl, QDialog

from nicos.clients.gui.utils import loadUi


class WebsiteTool(QDialog):
    """A dialog that just displays a website using the Qt HTML view.

    Options:

      * ``url`` -- the URL of the web site.
    """

    def __init__(self, parent, client, **settings):
        QDialog.__init__(self, parent)
        loadUi(self, 'website.ui', 'tools')

        site = settings.get('url', '')
        if site:
            self.webView.load(QUrl(site))

        self.closeBtn.clicked.connect(self.close)

    def closeEvent(self, event):
        self.deleteLater()
        self.accept()
