description = 'Devices to control the spin in SINQ AMOR'

devices = dict(
    rfflipper=device(
        'nicos_sinq.amor.devices.programmable_unit.ProgrammableUnit',
        description='Spin flipper RF controlled by SPS',
        epicstimeout=3.0,
        readpv='SQ:AMOR:SPS1:DigitalInput',
        commandpv='SQ:AMOR:SPS1:Push',
        commandstr="S0007",
        byte=12,
        bit=7,
        mapping={'SPIN DOWN': 0, 'SPIN UP': 1}
    ),
)
