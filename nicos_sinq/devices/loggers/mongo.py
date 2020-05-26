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

"""MongoDB log handler"""

import logging

from nicos.pycompat import urllib


class MongoLogHandler(logging.Handler):
    pass


def create_mongo_handler(config):
    """
    :param config: configuration dictionary
    :return: [MongoLogHandler, ] if 'mongo_logger' is in options,  else []
    """
    from nicos.core import ConfigurationError

    if hasattr(config, 'mongo_logger'):
        url = urllib.parse.urlparse(config.mongo_logger)
        if not url.netloc:
            raise ConfigurationError('mongo_logger: invalid url')
        mongo_handler = MongoLogHandler()
        mongo_handler.setLevel(logging.WARNING)
        return mongo_handler
