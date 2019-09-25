# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# MP zum kommutieren
# last modified 05.04.2018 10:38:26
# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_chopper

description = 'chopper commute'
group = 'special'

# Legende fuer _chconfigcol
# dev='...' stellt hier nur die moeglichen Werte dar, keine devices

Lwidth_low = 15.0

_disk1col = Column(
    Block('disk 1', [
        BlockRow(Field(name='speed',  dev='chopper_speed',  width = Lwidth_low, unit='rpm')),
        BlockRow(Field(name='CPT',  dev='cpt1',  width = Lwidth_low, unit='rpm')),
        BlockRow(Field(name='gear',   key='chopper_speed/gear',   width = Lwidth_low)),
        BlockRow(Field(name='mode', key='chopper_speed/mode', width = Lwidth_low)),
        BlockRow(Field(name='condition', key='chopper_speed/condition', width = Lwidth_low)),
        BlockRow(Field(name='status', key='chopper_speed/status', width = Lwidth_low)),
        BlockRow(Field(name='current', key='chopper_speed/current', width = Lwidth_low, unit='A')),
        BlockRow(Field(name='START delay', key='chopper/delay', unit='deg', width=10)),
        ],
    ),
)

_disk2col = Column(
    Block('disk 2', [
        BlockRow(Field(name='phase',  key='chopper2/phase',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt2',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper2/gear',   width = Lwidth_low)),
        BlockRow(Field(name='mode', key='chopper2/mode', width = Lwidth_low)),
        BlockRow(Field(name='condition', key='chopper2/condition', width = Lwidth_low)),
        BlockRow(Field(name='status', key='chopper2/status', width = Lwidth_low)),
        BlockRow(Field(name='current', key='chopper2/current', width = Lwidth_low, unit='A')),
        BlockRow(Field(name='speed',  dev='chopper2',  width = Lwidth_low, unit='rpm')),
        ],
    ),
)

_disk3col = Column(
    Block('disk 3', [
        BlockRow(Field(name='phase',  key='chopper3/phase',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt3',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper3/gear',   width = Lwidth_low)),
        BlockRow(Field(name='mode', key='chopper3/mode', width = Lwidth_low)),
        BlockRow(Field(name='condition', key='chopper3/condition', width = Lwidth_low)),
        BlockRow(Field(name='status', key='chopper3/status', width = Lwidth_low)),
        BlockRow(Field(name='current', key='chopper3/current', width = Lwidth_low, unit='A')),
        BlockRow(Field(name='speed',  dev='chopper3',  width = Lwidth_low, unit='rpm')),
        ],
    ),
)

_disk4col = Column(
    Block('disk 4', [
        BlockRow(Field(name='phase',  key='chopper4/phase',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt4',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper4/gear',   width = Lwidth_low)),
        BlockRow(Field(name='mode', key='chopper4/mode', width = Lwidth_low)),
        BlockRow(Field(name='condition', key='chopper4/condition', width = Lwidth_low)),
        BlockRow(Field(name='status', key='chopper4/status', width = Lwidth_low)),
        BlockRow(Field(name='current', key='chopper4/current', width = Lwidth_low, unit='A')),
        BlockRow(Field(name='speed',  dev='chopper4',  width = Lwidth_low, unit='rpm')),
        ],
    ),
)

_disk5col = Column(
    Block('disk 5', [
        BlockRow(Field(name='phase',  key='chopper5/phase',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt5',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper5/gear',   width = Lwidth_low)),
        BlockRow(Field(name='mode', key='chopper5/mode', width = Lwidth_low)),
        BlockRow(Field(name='condition', key='chopper5/condition', width = Lwidth_low)),
        BlockRow(Field(name='status', key='chopper5/status', width = Lwidth_low)),
        BlockRow(Field(name='current', key='chopper5/current', width = Lwidth_low, unit='A')),
        BlockRow(Field(name='speed',  dev='chopper5',  width = Lwidth_low, unit='rpm')),
        ],
    ),
)

_disk6col = Column(
    Block('disk 6', [
        BlockRow(Field(name='phase',  key='chopper6/phase',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='CPT',  dev='cpt6',  width = Lwidth_low, unit='deg')),
        BlockRow(Field(name='gear',   key='chopper6/gear',   width = Lwidth_low)),
        BlockRow(Field(name='mode', key='chopper6/mode', width = Lwidth_low)),
        BlockRow(Field(name='condition', key='chopper6/condition', width = Lwidth_low)),
        BlockRow(Field(name='status', key='chopper6/status', width = Lwidth_low)),
        BlockRow(Field(name='current', key='chopper6/current', width = Lwidth_low, unit='A')),
        BlockRow(Field(name='speed',  dev='chopper6',  width = Lwidth_low, unit='rpm')),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl01.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_disk1col, _disk2col, _disk3col, _disk4col,
                _disk5col, _disk6col),
        ],
    ),
)
