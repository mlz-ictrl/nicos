# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# MP zum kommutieren
# last modified 05.04.2018 10:38:26
# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_chopper

description = 'REFSANS chopper monitor commute'
group = 'special'

# Legende fuer _chconfigcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

_chconfigcol = Column(
    Block(' chopper configuration ', [
        BlockRow(
            Field(name='lambda min', dev='chopper_lambda_min', width=14, unit='AA'),
            Field(name='lambda max', dev='chopper_lambda_max', width=14, unit='AA'),
            Field(name='resolution', dev='lambda_resolution', width=14),
            Field(name='flight path', dev='chopper_to_detector', width=14, unit='mm'),
            ),
        ],
    ),
    Block(' chopper configuration ', [
        BlockRow(
            Field(name='Modus', key='chopper/mode', width=24),
            Field(name='real', dev='chopper2_pos', width=24),
            ),
        ],
    ),
)

_disk1col = Column(
    Block('disk 1', [
        BlockRow(Field(name='speed',  dev='chopper1',  width=6.5, unit='rpm')),
        BlockRow(Field(name='CPT',  dev='cpt1',  width=6.5, unit='rpm')),
        BlockRow(Field(name='gear',   key='chopper1/gear',   width=6.5)),
        BlockRow(Field(name='mode', key='chopper1/mode', width=6.5)),
        BlockRow(Field(name='current', key='chopper1/current', width=6.5, unit='A')),
        ],
    ),
)

_disk2col = Column(
    Block('disk 2', [
        BlockRow(Field(name='phase',  dev='chopper2_phase',  width=6.5, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt2',  width=6.5, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper2/gear',   width=6.5)),
        BlockRow(Field(name='mode', key='chopper2/mode', width=6.5)),
        BlockRow(Field(name='current', key='chopper2/current', width=6.5, unit='A')),
        ],
    ),
)

_disk3col = Column(
    Block('disk 3', [
        BlockRow(Field(name='phase',  key='chopper3/phase',  width=6.5, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt3',  width=6.5, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper3/gear',   width=6.5)),
        BlockRow(Field(name='mode', key='chopper3/mode', width=6.5)),
        BlockRow(Field(name='current', key='chopper3/current', width=6.5, unit='A')),
        ],
    ),
)

_disk4col = Column(
    Block('disk 4', [
        BlockRow(Field(name='phase',  key='chopper4/phase',  width=6.5, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt4',  width=6.5, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper4/gear',   width=6.5)),
        BlockRow(Field(name='mode', key='chopper4/mode', width=6.5)),
        BlockRow(Field(name='current', key='chopper4/current', width=6.5, unit='A')),
        ],
    ),
)

_disk5col = Column(
    Block('disk 5', [
        BlockRow(Field(name='phase',  key='chopper5/phase',  width=6.5, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt5',  width=6.5, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper5/gear',   width=6.5)),
        BlockRow(Field(name='mode', key='chopper5/mode', width=6.5)),
        BlockRow(Field(name='current', key='chopper5/current', width=6.5, unit='A')),
        ],
    ),
)

_disk6col = Column(
    Block('disk 6', [
        BlockRow(Field(name='phase',  key='chopper6/phase',  width=6.5, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt6',  width=6.5, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper6/gear',   width=6.5)),
        BlockRow(Field(name='mode', key='chopper6/mode', width=6.5)),
        BlockRow(Field(name='current', key='chopper6/current', width=6.5, unit='A')),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl01.refsans.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            # Row(_chconfigcol),
            Row(_disk1col, _disk2col, _disk3col, _disk4col,
                _disk5col, _disk6col),
        ],
    ),
)
