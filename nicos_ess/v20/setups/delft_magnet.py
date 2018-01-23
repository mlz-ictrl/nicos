description = 'Delft magnet controller with 4 fields.'

devices = dict(
    b1=device('nicos.devices.epics.EpicsWindowTimeoutDevice',
                description='Component B1',
                readpv='DelftM:ActB1',
                writepv='DelftM:B1', targetpv='DelftM:B1-RB',
                precision=0.02, window=5.0, timeout=None, unit='mT'),
    b2=device('nicos.devices.epics.EpicsWindowTimeoutDevice',
                description='Component B2',
                readpv='DelftM:ActB2',
                writepv='DelftM:B2', targetpv='DelftM:B2-RB',
                precision=0.02, window=5.0, timeout=None, unit='mT'),
    b3=device('nicos.devices.epics.EpicsWindowTimeoutDevice',
                description='Component B3',
                readpv='DelftM:ActB3',
                writepv='DelftM:B3', targetpv='DelftM:B3-RB',
                precision=0.02, window=5.0, timeout=None, unit='mT'),
    b4=device('nicos.devices.epics.EpicsWindowTimeoutDevice',
                description='Component B4',
                readpv='DelftM:ActB4',
                writepv='DelftM:B4', targetpv='DelftM:B4-RB',
                precision=0.02, window=5.0, timeout=None, unit='mT'),
)
