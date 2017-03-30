# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title',    key='exp/title',    width=20,
                  istext=True, maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
            Field(name='Last file', key='exp/lastscan'),
        ),
    ],
    ),
)

_maria = Column(
    Block('MARIA', [
        BlockRow(
            #Field(widget='nicos.guisupport.led.StatusLed', key='maria/status[0]'),
            Field(name='MARIA online values', dev='maria_online', width=120,
                  istext=True, setups='maria'),
        ),
    ],
    ),
)

_dns = Column(
    Block('DNS', [
        BlockRow(
            #Field(widget='nicos.guisupport.led.StatusLed', key='dns/status[0]'),
            Field(name='DNS online values', dev='dns_online', width=120,
                  istext=True, setups='dns'),
        ),
    ],
    ),
)

_kws2 = Column(
    Block('KWS2', [
        BlockRow(
            #Field(widget='nicos.guisupport.led.StatusLed', key='maria/status[0]'),
            Field(name='KWS2 online values', dev='kws2_online', width=120,
                  istext=True, setups='kws2'),
        ),
    ],
    ),
)

devices = dict(
    Monitor = device(
        'services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        # Use only 'localhost' if the cache is really running on
        # the same machine, otherwise use the hostname (official
        # computer name) or an IP address.
        cache = 'localhost',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        layout = [
            Row(_maria),
            Row(_dns),
            Row(_kws2),
        ],
   ),
)
