description = 'Chopper Phase Select'
group = 'optional'

devices = dict(
        phase_mode=
            device('nicos_ess.devices.epics.extensions.EpicsMappedFloatMoveable',
                   description='Phase Mode Select',
                   readpv='HZB-V20:TS-EVR-01:DlyGen1-Delay-SP',
                   writepv='HZB-V20:TS-EVR-01:DlyGen1-Delay-SP',
                   mapping={"Option 'A'": 11905.76,
                            "Option 'B'": 35714.29,
                            "Option 'C'": 59523.81},
                   ),
        phase_direct=
            device('nicos_ess.devices.epics.base.EpicsAnalogMoveableEss',
                    description='Phase Mode Direct Value Override',
                    readpv='HZB-V20:TS-EVR-01:DlyGen1-Delay-SP',
                    writepv='HZB-V20:TS-EVR-01:DlyGen1-Delay-SP',
                    lowlevel=True,
                    ),
)

