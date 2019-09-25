# created by MP
# 04.12.2017 07:53:39
# to call it
# ssh refsans@refsansctrl01 oder 02
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_mp-PO
# not perfect but working

description = 'Everyting at Sampleposition (ex-sample)'
group = 'special'

_big = Column(
    Block('Big Goniometer with Encoder', [
        BlockRow(Field(name='gonio Theta',    dev='gonio_theta',    width=30, unit='Grad'),),
        BlockRow(Field(name='gonio Phi',      dev='gonio_phi',      width=30, unit='Grad'),),
        BlockRow(Field(name='gonio Omega',    dev='gonio_omega',    width=30, unit='Grad'),),
        BlockRow(Field(name='gonio Y',        dev='gonio_y',        width=30, unit='mm'),),
        BlockRow(Field(name='gonio Z',        dev='gonio_z',        width=30, unit='mm'),),
        ],
    ),
)
_top = Column(
    Block('Small Goniometer on Samplechanger', [
        BlockRow(Field(name='gonio_top Theta',dev='gonio_top_theta',width=30, unit='Grad'),),
        BlockRow(Field(name='gonio_top Phi',  dev='gonio_top_phi',  width=30, unit='Grad'),),
        BlockRow(Field(name='gonio_top Z',    dev='gonio_top_z',    width=30, unit='mm'),),
        ],
    ),
)
_mix  = Column(
    Block('sonst1', [
    # Block('Backguard', [
        BlockRow(Field(name='Backguard',      dev='backguard',      width=30, unit='mm'),),
    # ],
    # Block('Samplechanger', [
        BlockRow(Field(name='Samplechanger',  dev='samplechanger',  width=30, unit='mm'),),
    # ],
    # Block('Monitor', [
        BlockRow(Field(name='Monitor typ',  dev='prim_monitor_typ',  width=30),),
        BlockRow(Field(name='Monitor X',  dev='prim_monitor_x',  width=30, unit='mm'),),
        BlockRow(Field(name='Monitor Y',  dev='prim_monitor_y',  width=30, unit='mm'),),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_big, _top, _mix),
        ],
    ),
)
