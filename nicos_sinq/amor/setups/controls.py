description = 'Devices controlled by Siemens programmanle unit in SINQ AMOR'

readpv = "SQ:AMOR:SPS1:DigitalInput"
commandpv = "SQ:AMOR:SPS1:Push"

devices = dict(
    shutter=device(
        'nicos_sinq.amor.devices.programmable_unit.ProgrammableUnit',
        description='Shutter controlled by SPS',
        epicstimeout=3.0,
        readpv=readpv,
        commandpv=commandpv,
        commandstr="S0000",
        mapping={'ON': 5, 'OFF': 0},
        byte=4,
    ),

    laser=device(
        'nicos_sinq.amor.devices.programmable_unit.ProgrammableUnit',
        description='Laser light controlled by SPS',
        epicstimeout=3.0,
        readpv=readpv,
        commandpv=commandpv,
        commandstr="S0001",
        mapping={'ON': 129, 'OFF': 0},
        byte=15,
    ),

    spinflipper=device(
        'nicos_sinq.amor.devices.programmable_unit.ProgrammableUnit',
        description='Spin flipper RF controlled by SPS',
        epicstimeout=3.0,
        readpv=readpv,
        commandpv=commandpv,
        commandstr="S0007",
        mapping={'ON': 128, 'OFF': 0},
        byte=12,
    ),
)
