# coding: utf-8

# created by Martin Haese, Tel FRM 10763
# last modified 11.04.2018 14:09:38
# to call it
# ssh -X refsans@refsansctrl01 oder 02
# cd /refsanscontrol/src/nicos-core
# INSTRUMENT=nicos_mlz.refsans bin/nicos-monitor -S monitor_optic

description = 'all analog encoder to take care of'
group = 'special'

_shgacol = Column(
    Block('gamma', [
        BlockRow(Field(name='position', dev='nok1_motor', width=8)),
        BlockRow(Field(name='poti_pos', dev='nok1_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='nok1_acc', width=8)),
        ],
    ),
)
_nok2col = Column(
    Block('nok2', [
        BlockRow(Field(name='position', dev='nok2r_motor', width=8),
                 Field(name='position', dev='nok2s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok2r_obs', width=8),
                 Field(name='poti_pos', dev='nok2s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='nok2r_acc', width=8),
                 Field(name='accuracy', dev='nok2s_acc', width=8)),
        ],
    ),
)
_nok3col = Column(
    Block('nok3', [
        BlockRow(Field(name='position', dev='nok3r_motor', width=8),
                 Field(name='position', dev='nok3s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok3r_obs', width=8),
                 Field(name='poti_pos', dev='nok3s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='nok3r_acc', width=8),
                 Field(name='accuracy', dev='nok3s_acc', width=8)),
        ],
    ),
)
_nok4col = Column(
    Block('nok4', [
        BlockRow(Field(name='position', dev='nok4r_motor', width=8),
                 Field(name='position', dev='nok4s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok4r_obs', width=8),
                 Field(name='poti_pos', dev='nok4s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='nok4r_acc', width=8),
                 Field(name='accuracy', dev='nok4s_acc', width=8)),
        ],
    ),
)
_nok6col = Column(
    Block('nok6', [
        BlockRow(Field(name='position', dev='nok6r_motor', width=8),
                 Field(name='position', dev='nok6s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok6r_obs', width=8),
                 Field(name='poti_pos', dev='nok6s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='nok6r_acc', width=8),
                 Field(name='accuracy', dev='nok6s_acc', width=8)),
        ],
    ),
)
_nok7col = Column(
    Block('nok7', [
        BlockRow(Field(name='position', dev='nok7r_motor', width=8),
                 Field(name='position', dev='nok7s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok7r_obs', width=8),
                 Field(name='poti_pos', dev='nok7s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='nok7r_acc', width=8),
                 Field(name='accuracy', dev='nok7s_acc', width=8)),
        ],
    ),
)
_nok8col = Column(
    Block('nok8', [
        BlockRow(Field(name='position', dev='nok8r_motor', width=8),
                 Field(name='position', dev='nok8s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok8r_obs', width=8),
                 Field(name='poti_pos', dev='nok8s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='nok8r_acc', width=8),
                 Field(name='accuracy', dev='nok8s_acc', width=8)),
        ],
    ),
)
_nok9col = Column(
    Block('nok9', [
        BlockRow(Field(name='position', dev='nok9r_motor', width=8),
                 Field(name='position', dev='nok9s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok9r_obs', width=8),
                 Field(name='poti_pos', dev='nok9s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='nok9r_acc', width=8),
                 Field(name='accuracy', dev='nok9s_acc', width=8)),
        ],
    ),
)
_zb2col = Column(
    Block('zb2', [
        BlockRow(Field(name='position', dev='zb2_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='zb2_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='zb2_acc', width=8)),
        ],
    ),
)
_zb3col = Column(
    Block('zb3', [
        BlockRow(Field(name='position', dev='zb3r_m', width=8),
                 Field(name='position', dev='zb3s_m', width=8),),
        BlockRow(Field(name='poti_pos', dev='zb3r_obs', width=8),
                 Field(name='poti_pos', dev='zb3s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='zb3r_acc', width=8),
                 Field(name='accuracy', dev='zb3s_acc', width=8)),
        ],
    ),
)
_bs1col = Column(
    Block('bs1', [
        BlockRow(Field(name='position', dev='bs1r_motor', width=8),
                 Field(name='position', dev='bs1s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='bs1r_obs', width=8),
                 Field(name='poti_pos', dev='bs1s_obs', width=8)),
        BlockRow(Field(name='accuracy', dev='bs1r_acc', width=8),
                 Field(name='accuracy', dev='bs1s_acc', width=8)),
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
            Row(_shgacol,
                _nok2col,
                _nok3col,
                _nok4col,
                _nok6col,_zb2col,
                ),
            Row(
                _nok7col,_zb3col,
                _nok8col, _bs1col,
                _nok9col,
                ),
        ],
    ),
)
