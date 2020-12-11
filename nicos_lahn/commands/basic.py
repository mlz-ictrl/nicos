from nicos import session
from nicos.commands import usercommand
from nicos.commands.device import maw

__all__ = [
    'setOperationMode',
]

@usercommand
def setOperationMode(option):
    if option == 'tension_scanner':
        maw('mtt',session.getDevice('mtt').absmin,'crystal','BPC',
            'lms',session.getDevice('lms').absmin,'stt',65,
            'lsd',session.getDevice('lsd').absmin)
    elif option == 'half_resolution':
        maw('mtt', 70, 'crystal', 'Ge', 'lms', session.getDevice('lms').absmin,
            'stt', session.getDevice('stt').absmin, 'lsd', 1100)
    elif option == 'high_intensity_ge':
        maw('mtt', session.getDevice('mtt').absmin, 'crystal', 'Ge',
            'lms', session.getDevice('lms').absmin,
            'stt', session.getDevice('stt').absmin, 'lsd', 1100)
    elif option == 'high_intensity_pg':
        maw('mtt', 42, 'crystal', 'PG', 'lms', session.getDevice('lms').absmin,
            'stt', session.getDevice('stt').absmin, 'lsd', 1100)
    else:
        session.log.info('The operation mode is incorrect.')
