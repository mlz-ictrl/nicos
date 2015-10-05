# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Current status', key='exp/action', width=40,
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
        setups='reactor',
    ),

    Block('Instrument angles', [
        BlockRow('sample_rot'),
        BlockRow('det_rot'),
        # BlockRow('cradle_lo', 'cradle_up'),
        ],
    ),
)

_secondcolumn = Column(
    Block('Detector', [
        BlockRow('mon0', 'timer'),
        ],
    ),

    Block('Field/flipper', [
        BlockRow('field', 'flipper'),
        ],
    ),

    Block('Selector', [
        BlockRow('selector_speed', 'selector_lift'),
        BlockRow('selector_vibrt'),
        ],
        setups='astrium',
    ),

)

_thirdcolumn = Column(

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
    Block('3He insert (cci3he2)', [
        BlockRow(Field(name='Setpoint', key='T_cci3he2/setpoint', unitkey='T_cci3he2/unit', format='%.2f'),
                 Field(name='T', dev='T'), Field(name='Ts', dev='Ts')),
        BlockRow(Field(name='P', key='t/p', width=4), Field(name='I', key='t/i', width=4),
                 Field(name='D', key='t/d', width=4),
                 Field(name='turbo', dev='cci3he2_p1'),
                 Field(name='cycle', dev='cci3he2_p4'),
                 ),
        ],
        setups='cci3he2',
    ),
    Block('3He-4He insert (cci3he4he1)', [
        BlockRow(Field(name='Setpoint', key='t/setpoint', unitkey='t/unit', format='%.2f'),
                 Field(name='T', dev='T'), Field(name='Ts', dev='Ts')),
        BlockRow(Field(name='P', key='t/p', width=4), Field(name='I', key='t/i', width=4),
                 Field(name='D', key='t/d', width=4),
                 Field(name='turbo', dev='cci3he4he1_p1'),
                 Field(name='cycle', dev='cci3he4he1_p4'),
                 ),
        ],
        setups='cci3he4he1',
    ),
    Block('3He-4He insert (cci3he4he2)', [
        BlockRow(Field(name='Setpoint', key='t/setpoint', unitkey='t/unit', format='%.2f'),
                 Field(name='T', dev='T'), Field(name='Ts', dev='Ts')),
        BlockRow(Field(name='P', key='t/p', width=4), Field(name='I', key='t/i', width=4),
                 Field(name='D', key='t/d', width=4),
                 Field(name='turbo', dev='cci3he4he2_p1'),
                 Field(name='cycle', dev='cci3he4he2_p4'),
                 ),
        ],
        setups='cci3he4he2',
    ),
    Block('3He insert (cci3he1)', [
        BlockRow(Field(name='Setpoint', key='T_cci3he1/setpoint', unitkey='T_cci3he1/unit', format='%.2f'),
                 Field(name='T', dev='T'), Field(name='Ts', dev='Ts')),
        BlockRow(Field(name='P', key='t/p', width=4), Field(name='I', key='t/i', width=4),
                 Field(name='D', key='t/d', width=4),
                 Field(name='turbo', dev='cci3he1_p1'),
                 Field(name='cycle', dev='cci3he1_p4'),
                 ),
        ],
        setups='cci3he1',
    ),
    Block('3He insert (cci3he3)', [
        BlockRow(Field(name='Setpoint', key='t/setpoint', unitkey='t/unit', format='%.2f'),
                 Field(name='T', dev='T'), Field(name='Ts', dev='Ts')),
        BlockRow(Field(name='P', key='t/p', width=4), Field(name='I', key='t/i', width=4),
                 Field(name='D', key='t/d', width=4),
                 Field(name='turbo', dev='cci3he3_p1'),
                 Field(name='cycle', dev='cci3he3_p4'),
                 ),
        ],
        setups='cci3he3',
    ),

)

_plotcolumn = Column(
    Block('Temperature plots', [
        BlockRow(Field(dev='T_jlc3_tube', plot='T',
                       plotwindow=12*3600, plotinterval=20, width=100, height=40),
                 Field(dev='Ts', plot='T')),
        BlockRow(Field(dev='Ts', plot='Ts',
                       plotwindow=12*3600, plotinterval=20, width=100, height=40)),
        ],
        setups='jlc3',
    ),
    Block('Selector plot', [
        BlockRow(Field(dev='selector_speed', plot='Sel',
                       plotwindow=12*3600, plotinterval=60, width=100, height=40),),
        ],
        setups='astrium',
    ),
)

devices = dict(
    Monitor = device('services.monitor.html.Monitor',
                     title = 'NICOS status monitor for DNS',
                     loglevel = 'info',
                     cache = 'phys.dns.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     filename = '/dnscontrol/webroot/index.html',
                     fontsize = 17,
                     layout = [
                         Row(_expcolumn),
                         Row(_firstcolumn, _secondcolumn, _thirdcolumn),
                         Row(_plotcolumn),
                     ],
                    ),
)
