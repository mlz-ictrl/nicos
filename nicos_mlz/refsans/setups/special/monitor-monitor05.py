# coding: utf-8

description = 'Facility Managing (05)'
group = 'special'

_shgacol = Column(
    Block('gamma', [
        BlockRow(Field(name='position', dev='shutter_gamma_motor', width=8)),
        BlockRow(Field(name='poti_pos', dev='shutter_gamma_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='shutter_gamma_acc', width=8)),
        ],
    ),
)
_nok2col = Column(
    Block('nok2', [
        BlockRow(Field(name='position', dev='nok2r_motor', width=8),
                 Field(name='position', dev='nok2s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok2r_analog', width=8),
                 Field(name='poti_pos', dev='nok2s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='nok2r_acc', width=8),
                 Field(name='accuracy', dev='nok2s_acc', width=8)),
        ],
    ),
)
_nok3col = Column(
    Block('nok3', [
        BlockRow(Field(name='position', dev='nok3r_motor', width=8),
                 Field(name='position', dev='nok3s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok3r_analog', width=8),
                 Field(name='poti_pos', dev='nok3s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='nok3r_acc', width=8),
                 Field(name='accuracy', dev='nok3s_acc', width=8)),
        ],
    ),
)
_nok4col = Column(
    Block('nok4', [
        BlockRow(Field(name='position', dev='nok4r_motor', width=8),
                 Field(name='position', dev='nok4s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok4r_analog', width=8),
                 Field(name='poti_pos', dev='nok4s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='nok4r_acc', width=8),
                 Field(name='accuracy', dev='nok4s_acc', width=8)),
        ],
    ),
)
_nok6col = Column(
    Block('nok6', [
        BlockRow(Field(name='position', dev='nok6r_motor', width=8),
                 Field(name='position', dev='nok6s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok6r_analog', width=8),
                 Field(name='poti_pos', dev='nok6s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='nok6r_acc', width=8),
                 Field(name='accuracy', dev='nok6s_acc', width=8)),
        ],
    ),
)
_nok7col = Column(
    Block('nok7', [
        BlockRow(Field(name='position', dev='nok7r_motor', width=8),
                 Field(name='position', dev='nok7s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok7r_analog', width=8),
                 Field(name='poti_pos', dev='nok7s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='nok7r_acc', width=8),
                 Field(name='accuracy', dev='nok7s_acc', width=8)),
        ],
    ),
)
_nok8col = Column(
    Block('nok8', [
        BlockRow(Field(name='position', dev='nok8r_motor', width=8),
                 Field(name='position', dev='nok8s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok8r_analog', width=8),
                 Field(name='poti_pos', dev='nok8s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='nok8r_acc', width=8),
                 Field(name='accuracy', dev='nok8s_acc', width=8)),
        ],
    ),
)
_nok9col = Column(
    Block('nok9', [
        BlockRow(Field(name='position', dev='nok9r_motor', width=8),
                 Field(name='position', dev='nok9s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='nok9r_analog', width=8),
                 Field(name='poti_pos', dev='nok9s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='nok9r_acc', width=8),
                 Field(name='accuracy', dev='nok9s_acc', width=8)),
        ],
    ),
)
_zb2col = Column(
    Block('zb2', [
        BlockRow(Field(name='position', dev='zb2_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='zb2_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='zb2_acc', width=8)),
        ],
    ),
)
_zb3col = Column(
    Block('zb3', [
        BlockRow(Field(name='position', dev='zb3r_motor', width=8),
                 Field(name='position', dev='zb3s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='zb3r_analog', width=8),
                 Field(name='poti_pos', dev='zb3s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='zb3r_acc', width=8),
                 Field(name='accuracy', dev='zb3s_acc', width=8)),
        ],
    ),
)
_bs1col = Column(
    Block('bs1', [
        BlockRow(Field(name='position', dev='bs1r_motor', width=8),
                 Field(name='position', dev='bs1s_motor', width=8),),
        BlockRow(Field(name='poti_pos', dev='bs1r_analog', width=8),
                 Field(name='poti_pos', dev='bs1s_analog', width=8)),
        BlockRow(Field(name='accuracy', dev='bs1r_acc', width=8),
                 Field(name='accuracy', dev='bs1s_acc', width=8)),
        ],
    ),
)

_refcolumn = Column(
    Block('References', [
        BlockRow(Field(dev='nok_refa1', name='ref_A1'),),
        BlockRow(Field(dev='nok_refa2', name='ref_A2'),),
        BlockRow(Field(dev='nok_refb1', name='ref_B1'),),
        BlockRow(Field(dev='nok_refb2', name='ref_B2'),),
        BlockRow(Field(dev='nok_refc1', name='ref_C1'),),
        BlockRow(Field(dev='nok_refc2', name='ref_C2'),),
        ],
    ),
)
_memograph = Column(
    Block('memograph', [
        BlockRow(Field(name='flow_in', dev='flow_memograph_in'),
                 Field(name='flow_out', dev='flow_memograph_out'),
                 Field(name='diff', dev='leak_memograph'),),
        BlockRow(Field(name='t_in', dev='t_memograph_in'),
                 Field(name='t_out', dev='t_memograph_out'),
                 Field(name='power', dev='cooling_memograph'),),
        BlockRow(Field(name='p_in', dev='p_memograph_in'),
                 Field(name='p_out', dev='p_memograph_out'),),
        ],
    ),
)

_pumpstand = Column(
    Block('pumpstand', [
        BlockRow(Field(name='CB', dev='pressure_CB'),
                 Field(name='SFK', dev='pressure_SFK'),
                 Field(name='SR', dev='pressure_SR'),),
        BlockRow(Field(name='CB', dev='pump_CB'),
                 Field(name='SFK', dev='pump_SFK'),
                 Field(name='SR', dev='pump_SR'),),
        BlockRow(Field(name='CB', dev='chamber_CB'),
                 Field(name='SFK', dev='chamber_SFK'),
                 Field(name='SR', dev='chamber_SR'),),
        ],
    ),
)

_chopper = Column(
    Block('chopper', [
        BlockRow(Field(name='Fatal', key='chopper/fatal', width=10),),
        BlockRow(Field(name='conditon 1', key='chopper_speed/condition', width=10),),
        BlockRow(Field(name='conditon 2', key='chopper2/condition', width=10),),
        BlockRow(Field(name='conditon 3', key='chopper3/condition', width=10),),
        BlockRow(Field(name='conditon 4', key='chopper4/condition', width=10),),
        BlockRow(Field(name='conditon 5', key='chopper5/condition', width=10),),
        BlockRow(Field(name='conditon 6', key='chopper6/condition', width=10),),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        showwatchdog = False,
        title = description,
        loglevel = 'info',
        cache = 'refsansctrl.refsans.frm2.tum.de',
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
            Row(
                _refcolumn,
                _pumpstand,
                _memograph,
                _chopper,
                ),
        ],
    ),
)
