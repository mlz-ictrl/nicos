# created by MP
# 04.12.2017 07:53:39
# to call it
# ssh refsans@refsansctrl01 oder 02
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_mp-PO
# not perfet but working

description = 'Ratemeter sds'
group = 'special'

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'localhost',
        valuefont = 'Consolas',
        padding = 5,
        layout = [
            Row(
Column(
    Block('ratemeter', [
        #BlockRow(Field(name='gonio Theta',    dev='gonio_theta',    width=30, unit='Grad'),),
        #BlockRow(Field(name='gonio Phi',      dev='gonio_phi',      width=30, unit='Grad'),),
        #BlockRow(Field(name='gonio Omega',    dev='gonio_omega',    width=30, unit='Grad'),),
        #BlockRow(Field(name='gonio Y',        dev='gonio_y',        width=30, unit='mm'),),
        #BlockRow(Field(name='gonio Z',        dev='gonio_z',        width=30, unit='mm'),),
        BlockRow(Field(name='s d s',      dev='sds',        width=10, unit='cps'),),
        ],
    ),
)            ),
        ],
    ),
)
