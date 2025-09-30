import socket

from nicos import session
from nicos.commands import usercommand
from nicos.core.utils import deprecated


@usercommand
@deprecated(comment='TASP counterbox setup will be changed to new driver in SD 2026 '/
            'and this function will be removed, since resetting is then possible in the device itself')
def reset_counterbox():
    host = 'tasp-ts0'
    port = 3004

    message = '%\r'

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encoded('utf-8'))
    except Exception:
        session.log.error('Resetting the counterbox failed. Please call the support.')
