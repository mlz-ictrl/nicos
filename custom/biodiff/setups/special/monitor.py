# This setup file configures the nicos status monitor.

description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title', key='exp/title', width=20,
                       istext=True, maxlen=20),
                 Field(name='Sample', key='sample/samplename', istext=True),
                 Field(name='Remark', key='exp/remark', istext=True),
                 Field(name='Current status', key='exp/action', width=40,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='exp/lastimage',
                       width=20),
                 )
        ],
    ),
)


_reactorBlock = Block('Reactor', [
    BlockRow(Field(name='Reactor power', dev='ReactorPower', format='%.1f', width=6),
             Field(name='6-fold-shutter', dev='Sixfold', istext=True),
             Field(name='NL-1', dev='NL1', min='open', istext=True),
             )
    ],
)

_shutterBlock = Block('Shutter', [
    BlockRow(Field(name='Photo-shutter', dev='photoshutter'),
             Field(name='Gamma-shutter', dev='gammashutter'),
             )
    ],
)

_sampleTableBlock = Block('Sample table', [
    BlockRow(Field(name='omega', dev='omega_sampletable',)),
    BlockRow(Field(name='x', dev='x_sampletable',)),
    BlockRow(Field(name='y', dev='y_sampletable',)),
    ],
)

_kappaBlock = Block('Mini-kappa', [
    BlockRow(Field(name='kappa', dev='minikappa_kappa',)),
    BlockRow(Field(name='phi', dev='minikappa_phi',)),
    BlockRow(Field(name='omega', dev='minikappa_omega',)),
    ],
    setups='kappa',
)

_sampleStepperBlock = Block('Sample stepper', [
    BlockRow(Field(name='omega', dev='omega_samplestepper')),
    ],
)

_activeDetectorBlock = Block('Active detector', [
    BlockRow(Field(name='Detector', key='exp/detlist', item=0)),
    ],
)

_slitsBlock = Block('Slits', [
    BlockRow(Field(name='Slit dia1', dev='d_diaphragm1')),
    BlockRow(Field(name='Slit dia2', dev='d_diaphragm2')),
    ],
)

_cryoStreamBlock = Block('Cryo-stream', [
    BlockRow(Field(name='Temperature', dev='T_cryostream'),
             Field(name='Target', key='T_cryostream/target', unit='K')),
    BlockRow(Field(name='LN2', dev='cryostream_LN2')),
    ],
    setups='cryostream',
)

_ls332Block = Block('LakeShore', [
    BlockRow(Field(name='Temperature', dev='T_ls332'),
             Field(name='Target', key='T_ls332/target', unit='K')),
    BlockRow(Field(name='Sensor A', dev='T_ls332_A'),
             Field(name='Sensor B', dev='T_ls332_B')),
    ],
    setups='ls332',
)

_selectorBlock = Block('Selector', [
    BlockRow(Field(name='Speed', dev='selector_speed')),
    BlockRow(Field(name='Lambda', dev='selector_lambda')),
    BlockRow(Field(name='Vac', dev='selector_vacuum'),
             Field(name='Rotor T', dev='selector_rtemp')),
    BlockRow(Field(name='Flow', dev='selector_wflow'),
             Field(name='Vibration', dev='selector_vibrt')),
    ],
    setups='astrium',
)

_outsideWorldBlock = Block('Outside world', [
    BlockRow(Field(name='Next U-Bahn U6', dev='ubahn', istext=True),
             Field(name='Outside T', dev='meteo')),
    ],
)

_pictureBlock = Block('Sampletable Directions', [
    BlockRow(Field(widget='nicos.guisupport.display.PictureDisplay',
                   filepath = 'custom/biodiff/lib/gui/omega_x_y.png',
                   )
             ),
    ],
)


_secondRow = Row(
    Column(_reactorBlock),
    Column(_shutterBlock))

_thirdRow = Row(
    Column(_sampleTableBlock),
    Column(_pictureBlock),
    Column(_kappaBlock),
    Column(_sampleStepperBlock, _activeDetectorBlock),
    Column(_slitsBlock))

_forthRow = Row(
    Column(_cryoStreamBlock, _ls332Block),
    Column(_selectorBlock),
    Column(_outsideWorldBlock),
    )


devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     cache = 'phys.biodiff.frm2:14869',
                     font = 'Luxi Sans',
                     fontsize = 19,
                     valuefont = 'Droid Sans Mono',
                     padding = 0,
                     layout = [Row(_expcolumn), _secondRow, _thirdRow, _forthRow],
                    ),
)
