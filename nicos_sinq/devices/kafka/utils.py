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
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************

import os

from nicos.core import ConfigurationError
from nicos.utils.credentials.keystore import nicoskeystore


def create_sasl_config():
    """Create a SASL config for connecting to Kafka.

    Note that whereas some SASL mechanisms do not require user/password, the
    three we currently support do.

    :return: A dictionary of configuration parameters.
    """
    protocol = os.environ.get('KAFKA_SSL_PROTOCOL')
    if not protocol:
        return {}

    mechanism = os.environ.get('KAFKA_SSL_MECHANISM')
    cert_filepath = os.environ.get('KAFKA_CERT_PATH')
    username = os.environ.get('KAFKA_USER')
    password = nicoskeystore.getCredential('kafka_auth')

    supported_security_protocols = ['SASL_PLAINTEXT', 'SASL_SSL']
    supported_sasl_mechanisms = ['PLAIN', 'SCRAM-SHA-512', 'SCRAM-SHA-256']

    if protocol not in supported_security_protocols:
        raise ConfigurationError(
            f'Security protocol {protocol} not supported, use one of '
            f'{supported_security_protocols}'
        )

    if not mechanism:
        raise ConfigurationError(
            f'SASL mechanism must be specified for security protocol {protocol}'
        )
    elif mechanism not in supported_sasl_mechanisms:
        raise ConfigurationError(
            f'SASL mechanism {mechanism} not supported, use one of '
            f'{supported_sasl_mechanisms}'
        )

    if not username or not password:
        raise ConfigurationError(
            f'Username and password must be provided to use SASL {mechanism}'
        )

    sasl_config = {
        'security.protocol': protocol,
        'sasl.mechanism': mechanism,
        'sasl.username': username,
        'sasl.password': password,
    }

    if cert_filepath:
        sasl_config['ssl.ca.location'] = cert_filepath

    return sasl_config
