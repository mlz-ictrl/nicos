# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Sample',   key='sample/samplename', width=15,
                       istext=True, maxlen=15),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Last scan', key='exp/lastscan'),
                ),
        ],
    ),
)

_firstcolumn = Column(
    Block('Beam', [
        BlockRow(Field(name='Power', dev='ReactorPower', width=6),
                 Field(name='6-fold', dev='Sixfold', min='open', width=6),
                 Field(dev='NL6', min='open', width=6)),
        BlockRow(Field(name='Experiment shutter', dev='expshutter')),
        ],
        setups='reactor'),

    Block('Instrument angles', [
        BlockRow('sample_rot'),
        BlockRow('det_rot'),
        # BlockRow('cradle_lo', 'cradle_up'),
        ],
    ),
)

_secondcolumn = Column(
    Block('Detector', [
        BlockRow('mon1', 'timer'),
        ],
    ),

    Block('Field/flipper', [
        BlockRow('field', 'flipper'),
        ],
    ),
)

_thirdcolumn = Column(

    Block('Selector', [
        BlockRow('selector_speed', 'selector_lift'),
        BlockRow('selector_vibrt'),
        ],
        setups='astrium',
    ),

    Block('Cryostat (jlc3)', [
        BlockRow(Field(name='Temp. setpoint', key='T_jlc3_tube/setpoint',
                       unitkey='T_jlc3_tube/unit', format='%.2f'),
                 Field(name='Temp. at tube', dev='T_jlc3_tube')),
        BlockRow(Field(name='Temp. at sample stick', dev='T_jlc3_stick')),
        BlockRow(Field(name='P', key='T_jlc3_tube/p'), Field(name='I', key='T_jlc3_tube/i'),
                 Field(name='D', key='T_jlc3_tube/d')),
        BlockRow(Field(name='He pressure', dev='T_jlc3_C', unit='mbar')),
        ],
        setups='jlc3',
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'DNS status',
        loglevel = 'info',
        cache = 'phys.dns.frm2',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        padding = 0,
        layout = [
            Row(_expcolumn),
            Row(_firstcolumn, _secondcolumn, _thirdcolumn),
        ],
    ),
)
