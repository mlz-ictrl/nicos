description = 'LakeShore F71 Teslameter'

devices = dict(
    tesla = device('nicos_sinq.boa.devices.f71teslameter.F71Teslameter',
        description = 'F71 Teslameter',
        host = '129.129.138.153',
        unit = 'mT',
    ),
)
