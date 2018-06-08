# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_kws1selector = Block('Selector KWS1', [
    BlockRow(Field(name='Preset', dev='kws1/selector', istext=True, width=10)),
    BlockRow(Field(name='Lambda', dev='kws1/selector_lambda'),
             Field(name='Speed', dev='kws1/selector_speed')),
    BlockRow(Field(name='Vac', dev='kws1/selector_vacuum'),
             Field(name='Rotor', dev='kws1/selector_rtemp')),
    BlockRow(Field(name='Flow', dev='kws1/selector_wflow'),
             Field(name='Vibr', dev='kws1/selector_vibrt')),
])

_kws2selector = Block('Selector KWS2', [
    BlockRow(Field(name='Preset', dev='kws2/selector', istext=True, width=10)),
    BlockRow(Field(name='Lambda', dev='kws2/selector_lambda'),
             Field(name='Speed', dev='kws2/selector_speed')),
    BlockRow(Field(name='Vac', dev='kws2/selector_vacuum'),
             Field(name='Rotor', dev='kws2/selector_rtemp')),
    BlockRow(Field(name='Flow', dev='kws2/selector_wflow'),
             Field(name='Vibr', dev='kws2/selector_vibrt')),
])

_mariaselector = Block('Selector MARIA', [
    BlockRow(Field(name='Lambda', dev='maria/selector_lambda'),
             Field(name='Speed', dev='maria/selector_speed')),
    BlockRow(Field(name='Vac', dev='maria/selector_vacuum'),
             Field(name='Rotor', dev='maria/selector_rtemp')),
    BlockRow(Field(name='Flow', dev='maria/selector_wflow'),
             Field(name='Vibr', dev='maria/selector_vibrt')),
])

_selectorplot = Block('Vacuum', [
    BlockRow(Field(plot='selector', name='kws1',
                   key='kws1/selector_vacuum/value',
                   plotwindow=3600, width=50, height=40),
            Field(plot='selector2', name='kws2',
                   key='kws2/selector_vacuum/value',
                   plotwindow=3600, width=50, height=40),
             Field(plot='selector3', name='maria',
                   key='maria/selector_vacuum/value',
                   plotwindow=3600, width=50, height=40),
    ),
])

layout = [
    Row(Column(_kws1selector), Column(_kws2selector), Column(_mariaselector)),
    Row(Column( _selectorplot)),
]


devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'JCNS Selector monitor',
        loglevel = 'info',
        cache = 'jcnsmon.jcns.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 14,
        padding = 3,
        layout = layout,
        expectmaster = False,
    ),
)
