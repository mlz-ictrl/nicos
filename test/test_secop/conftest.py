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
#   Alexander Zaft <a.zaft@fz-juelich.de>
#
# *****************************************************************************

from time import monotonic, sleep

import pytest

from nicos.utils import tcpSocket

from test.utils import killSubprocess, secop_port, startSubprocess


def secnode_wait_cb():
    start = monotonic()
    wait = 10
    sock = None
    while monotonic() < start + wait:

        try:
            sock = tcpSocket(f'localhost:{secop_port}', 0)
        except OSError:
            sleep(0.02)
        else:
            break
        finally:
            if sock:
                sock.close()
    else:
        raise Exception('secnode failed to start within %s sec' % wait)


@pytest.fixture(scope='function')
def secnode():
    """Start a test secnode"""

    server = startSubprocess('secnode', wait_cb=secnode_wait_cb)
    yield
    killSubprocess(server)
