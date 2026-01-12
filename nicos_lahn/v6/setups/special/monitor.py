description = 'setup for the status monitor'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(
            Field(name='Proposal', key='exp/proposal', width=7),
            Field(name='Title', key='exp/title', width=20, istext=True,
                  maxlen=20),
            Field(name='Current status', key='exp/action', width=40,
                  istext=True, maxlen=40),
            Field(name='Last file', key='exp/lastscan'),
        ),
    ],
    ),
)

_monochromatorblock1 = Block('Monochromator', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='lin_m', name='status'),
        Field(name='Horizontal movement', dev='lin_m'),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='omega_m', name='status'),
        Field(name='Rocking angle', dev='omega_m'),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='wavelenght', name='status'),
        Field(name='Wavelenght', dev='wavelength'),
    ),
],
    setups='monochromator_1',
)

_monochromatorblock2 = Block('Monochromator', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='lin_m', name='status'),
        Field(name='Horizontal movement', dev='lin_m'),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='phi_m', name='status'),
        Field(name='Tilt angle', dev='phi_m'),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='omega_m', name='status'),
        Field(name='Rocking angle', dev='omega_m'),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='high_m', name='status'),
        Field(name='Vertical movement', dev='high_m'),
    ),
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='wavelenght', name='status'),
        Field(name='Wavelenght', dev='wavelength'),
    ),
],
    setups='monochromator_2',
)

_detectorblock = Block('Detector table', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='delta_d', name='status'),
        Field(name='Angle', dev='delta_d'),
    ),
],
    setups='detector',
)

_befilterblock = Block('Be filter', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='high_be', name='status'),
        Field(name='Vertical movement', dev='high_be'),
    ),
],
    setups='befilter',
)

_slit1block = Block('Slit1', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='slit_1'),
        Field(name='(centerx, centery)Widht x Height', dev='slit_1'),
    ),
],
    setups='slit1_1 or slit1_2',
)

_slit2block = Block('Slit2', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='slit_2'),
        Field(name='(centerx, centery)Widht x Height', dev='slit_2'),
    ),
],
    setups='slit2_1 or slit2_2',
)

_slit3block = Block('Slit3', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='slit_3', name='status'),
        Field(name='(centerx, centery)Widht x Height', dev='slit_3'),
    ),
],
    setups='slit3_1 or slit3_2',
)

_sampletableblock1 = Block('Sample table', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='chi', name='status'),
        Field(name='Chi angle', dev='chi'),
        Field(widget='nicos.guisupport.led.StatusLed', dev='high_s', name='status'),
        Field(name='High', dev='high_s'),
        Field(widget='nicos.guisupport.led.StatusLed', dev='omega_s', name='status'),
        Field(name='Omega angle', dev='omega_s'),
    ),
    BlockRow(
        Field(name='Horizontal movement', dev='y'),
        Field(name='Vertical movement', dev='z'),
    ),
],
    setups='sampletable_1',
)

_sampletableblock2 = Block('Sample table', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='high_s', name='status'),
        Field(name='High', dev='high_s'),
    ),
    BlockRow(
        Field(name='Horizontal movement', dev='y'),
        Field(name='Vertical movement', dev='z'),
    ),
],
    setups='sampletable_2',
)

_spinflipper1block = Block('Spin flipper 1', [
    BlockRow(
        Field(widget='nicos.guisupport.led.ValueLed', dev='mezeiflipper1'),
        Field(widget='nicos.guisupport.led.ClickableOutputLed', dev='FLIP', stateActive='1', stateInactive='1.5'),
        Field(widget='nicos.guisupport.led.StatusLed', dev='flip'), Field(name='Flipping current', dev='flip'),
        Field(widget='nicos.guisupport.led.StatusLed', dev='comp'), Field(name='Correction current', dev='comp'),
    ),
],
    setups='spinflipper1',
)

_spinflipper2block = Block(
    'Spin flipper 2', [
        BlockRow(
            Field(
                widget='nicos.guisupport.led.StatusLed', dev='flip2'), Field(
                    name='Flipping current', dev='flip2'), Field(
                        widget='nicos.guisupport.led.StatusLed', dev='comp2'), Field(
                            name='Correction current', dev='comp2'), ), ], setups='spinflipper2', )

_beamstopdblock = Block('Beam stop for detection stage', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='beam_d', name='status'),
        Field(name='angle', dev='beam_d'),
    ),
],
    setups='beamstop_d',
)

_beamstopmblock = Block('Beam stop for monochromation stage', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='beam_m', name='status'),
        Field(name='angle', dev='beam_m'),
    ),
],
    setups='beamstop_m',
)

_polarizerblock = Block('Polarizer', [
    BlockRow(
        Field(name='Translation', dev='trans_po'),
        Field(name='Rotation', dev='rot_po'),
    ),
],
    setups='polarizer',
)

_analysatorblock = Block('Analysator', [
    BlockRow(
        Field(name='Translation', dev='trans_an'),
        Field(name='Rotation', dev='rot_an'),
    ),
],
    setups='analysator',
)

_offspecularanalysatorblock = Block('Off specular analysator', [
    BlockRow(
        Field(widget='nicos.guisupport.led.StatusLed', dev='rot_anoff', name='status'),
        Field(name='Rotation', dev='rot_anoff'),
    ),
],
    setups='offspecularanalysator',
)

module_blocks = []
items = list(configdata('config_secop.secop_devices').items())
node_name = items[0][0]

for module_name, module_info in items[1:]:
    module_description = module_info["description"]
    module_block = BlockRow(
        Field(
            widget='nicos.guisupport.led.StatusLed',
            dev=module_name,
            name='status'),
        Field(
            name=module_description,
            dev=module_name),
    )
    module_blocks.append(module_block)

_sampleenvironmentblock = Block('Sample Environment ('f"{node_name}"')',
                                module_blocks,
                                setups='sample_environment',
                                )

_leftcolumn = Column(
    _beamstopmblock,
    _monochromatorblock1,
    _monochromatorblock2,
    _befilterblock,
)

_middlecolumn = Column(
    _slit1block,
    _polarizerblock,
    _spinflipper1block,
    _slit2block,
    _sampletableblock1,
    _sampletableblock2,
    _slit3block,
)

_rightcolumn = Column(
    _spinflipper2block,
    _offspecularanalysatorblock,
    _analysatorblock,
    _beamstopdblock,
    _detectorblock,
    _sampleenvironmentblock,
)

devices = dict(
    Monitor=device('nicos.services.monitor.qt.Monitor',
                   title='NICOS status monitor',
                   loglevel='info',
                   # Use only 'localhost' if the cache is really running on
                   # the same machine, otherwise use the hostname (official
                   # computer name) or an IP address.
                   cache='localhost',
                   font='Luxi Sans',
                   valuefont='Consolas',
                   padding=0,
                   layout=[
                         Row(_expcolumn),
                         Row(_leftcolumn, _middlecolumn, _rightcolumn),
                   ],
                   ),
)
