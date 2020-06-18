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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""Graylog log handler"""

import logging
import traceback

from nicos.pycompat import urllib

try:
    from graypy import GELFTCPHandler


    class ESSGELFTCPHandler(GELFTCPHandler):
        @staticmethod
        def _add_full_message(gelf_dict, record):
            full_message = None
            # try to format exception information if present
            if record.exc_info:
                try:
                    full_message = "\n".join(
                        traceback.format_exception(*record.exc_info))
                except TypeError as _:
                    full_message = "Can't format exception traceback"
            if record.exc_text:
                full_message = record.exc_text
            if full_message:
                gelf_dict["full_message"] = full_message

except ImportError:
    ESSGELFTCPHandler = None


def create_graylog_handler(config):
    from nicos.core import ConfigurationError

    if ESSGELFTCPHandler is None:
        return
    if hasattr(config, 'graylog'):
        url = urllib.parse.urlparse(config.graylog)
        if not url.netloc:
            raise ConfigurationError('graylog: invalid url')
        graylog_handler = ESSGELFTCPHandler(url.hostname, url.port or 12201)
        graylog_handler.setLevel(logging.WARNING)
        return graylog_handler
