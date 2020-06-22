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
#   Jens Krüger <jens.krueger@frm2.tum.de>
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

"""ESS specific NICOS package."""

from nicos_ess.devices.loggers import create_graylog_handler, \
    create_kafka_logging_handler


def determine_instrument(setup_package_path):
    # TODO adapt to ESS systems
    return 'ymir'


def get_log_handlers(config):
    """
    :param config: configuration dictionary
    :return: a list containing one or both of:
        - KafkaLoggingHandler if 'kafka_logger' in options
        - GELFTCPHandler if 'graylog' in options
        or [] if none is present
    """
    handlers = [create_graylog_handler(config),
                create_kafka_logging_handler(config)]

    return [h for h in handlers if h is not None]
