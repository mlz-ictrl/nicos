# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=10),
            Field(name='Title', key='exp/title', width=50, istext=True),
            Field(name='Current status', key='exp/action', width=30, istext=True),
        ),
        BlockRow(
            Field(name='Sample', key='sample/samplename', width=40,
                 istext=True, maxlen=40),
            Field(name='Remark',   key='exp/remark',   width=40,
                 istext=True, maxlen=40),
        ),
        ],
    ),
)

_translationColumn = Column(
    Block('Sample translation', [
        BlockRow(Field(dev='stx'),),
        BlockRow(Field(dev='sty'),),
        BlockRow(Field(dev='sry'),),
        ],
        setups='servostar',
    ),
)

_detectorblock = Column(
    Block('Detector', [
        BlockRow(
            Field(name='Last Image', key='exp/lastpoint'),
        ),
        BlockRow(
            Field(dev='ccdTemp'), Field(name='CCD status', key='ccd/status[1]', width=15),
        ),
        BlockRow(
            Field(name='bin', key='ccd.bin'),
            Field(name='flip (H,V)', key='ccd.flip'),
            Field(name='rotation', key='ccd.rotation'),
        ),
        BlockRow(
            Field(name='roi', key='ccd.roi'),
            Field(name='hsspeed', key='ccd.hsspeed', width=4),
            Field(name='vsspeed', key='ccd.vsspeed', width=4),
            Field(name='pgain', key='ccd.pgain', width=4),
        ),
        ],
        setups='detector',
    ),
)

_ubahnColumn = Column(
    Block('U-Bahn', [
        BlockRow(Field(dev='UBahn'),),
        ],
        setups='ubahn',
    ),
)


devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     filename = '/nectarcontrol/status.html',
                     interval = 10,
                     prefix = 'nicos/',
                     cache = 'nectarhw.nectar.frm2',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 0,
                     layout = [[_expcolumn],[_translationColumn, _detectorblock, _ubahnColumn]],
                    ),
)
