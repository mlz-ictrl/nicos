from nicos import session
from nicos.commands import usercommand

__all__ = [
    'refreshDeviceList',
]

@usercommand
def refreshDeviceList(listall=True):
    listSetups = ['andes', 'astor', 'system']
    for name, info in session.getSetupInfo().items():
        if info is None:
            continue
        if info['group'] in ('special', 'configdata'):
            continue
        if info['group'] == 'lowlevel' and not listall:
            continue
        if name in session.loaded_setups and name not in listSetups:
            for dname in info['devices']:
                session.getDevice(dname).poll()
