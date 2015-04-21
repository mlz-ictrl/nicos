# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

Row = Column = BlockRow = lambda *args: args
Block = lambda *args, **kwds: (args, kwds)
Field = lambda *args, **kwds: args or kwds

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
        BlockRow(Field(name='Power', dev='ReactorPower', format='%.1f', width=6),
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

_plotcolumn = Column(
    Block('Temperature plots', [
        BlockRow(Field(dev='T_jlc3_tube', plot='T',
                       plotwindow=12*3600, plotinterval=20, width=100, height=40),
                 Field(dev='T_jlc3_stick', plot='T'),),
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
