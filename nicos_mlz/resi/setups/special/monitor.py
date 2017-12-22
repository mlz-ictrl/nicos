# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'


_reactorBlock = Block('Reactor', [
    BlockRow(Field(name='Reactor power', dev='ReactorPower', width=6),
             )
    ],
)

_shutterBlock = Block('Shutter', [
    BlockRow(Field(name='Prim. shutter', dev='prim_shutt'),
             Field(name='Sec. sutter', dev='sec_shutt'),
             )
    ],
)
_hoverBlock = Block('Hover feet', [
    BlockRow(Field(name='Gonio/opt.Bench', dev='hover_mono'),
             Field(name='Detector', dev='hover_theta'),
             )
    ],
)
_counterBlock = Block('Counter', [
    BlockRow(Field(name='Counter', dev='det1'),
             Field(name='Monitor', dev='mon1'),
             Field(name='Time', dev='timer'),
             ),
    BlockRow(Field(name='Counter rate', dev='det1rate'),
             Field(name='Monitor rate', dev='mon1rate'),
             )
    ],
)


_ls340Block = Block('LakeShore', [
    BlockRow(Field(name='Temperature', dev='T_ls340'),
             Field(name='Target', key='T_ls340/setpoint', unit='K')),
    BlockRow(Field(name='Sensor A', dev='T_ls340_A'),
             Field(name='Sensor B', dev='T_ls340_B')),
    ],
    setups='',
)


_outsideWorldBlock = Block('Outside world', [
    BlockRow(Field(name='Next U-Bahn U6', dev='ubahn', istext=True),
             Field(name='Outside T', dev='meteo')),
    ],
)


_secondRow = Row(
    Column(_reactorBlock),
    Column(_shutterBlock))


_thirdRow = Row(
    Column(_counterBlock),
    Column( _ls340Block),
    )
_forthRow = Row(
    Column(_outsideWorldBlock),
    Column(_hoverBlock),
    )


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor',
        loglevel = 'info',
        cache = 'resictrl.resi.frm2:14869',
        # cache = 'localhost',
        font = 'Luxi Sans',
        fontsize = 10,
        timefontsize = 12,
        valuefont = 'Droid Sans Mono',
        padding = 0,
        layout = [_secondRow, _thirdRow, _forthRow],
    ),
)
