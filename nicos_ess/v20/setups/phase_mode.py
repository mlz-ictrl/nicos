description = 'Chopper Phase Select'

devices = dict(
        phase_mode=
            device('nicos_ess.devices.epics.extensions.EpicsMappedMoveable',
                   description='Phase Mode Select',
                   readpv='HZB-V20:Chop-HZB:PhaseSelS',
                   writepv='HZB-V20:Chop-HZB:PhaseSelS',
                   mapping={"Option 'A'": 0,
                            "Option 'B'": 1,
                            "Option 'C'": 2},
                   ),
)

