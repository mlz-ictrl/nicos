# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_kws1selector = Block('Selector', [
    BlockRow(Field(name='Preset', dev='kws1/selector', istext=True, width=10)),
    BlockRow(Field(name='Lambda', dev='kws1/selector_lambda'),
             Field(name='Speed', dev='kws1/selector_speed')),
    BlockRow(Field(name='Vac', dev='kws1/selector_vacuum'),
             Field(name='Rotor', dev='kws1/selector_rtemp')),
    BlockRow(Field(name='Flow', dev='kws1/selector_wflow'),
             Field(name='Vibr', dev='kws1/selector_vibrt')),
])

_layout = [
    Row(Column(_kws1selector)),
]


devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'JCNS test monitor',
        loglevel = 'info',
        cache = 'jcnsmon.jcns.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 14,
        padding = 3,
        layout = _layout,
        filename = '/WebServer/jcnswww.jcns.frm2/httpdocs/monitor/test.html',
    ),
)
