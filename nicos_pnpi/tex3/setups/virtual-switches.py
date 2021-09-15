description = 'Switches for diom modules'

excludes = ['switches']

devices = dict(
    diom1 = device('nicos_pnpi.tex3.devices.diom.DIOMVirtual',
                   description = 'DIOM PhyMotion module 1',
                   unit = '',
                   fmtstr = '%d',
                   ),
    diom2 = device('nicos_pnpi.tex3.devices.diom.DIOMVirtual',
                   description = 'DIOM PhyMotion module 2',
                   unit = '',
                   fmtstr = '%d',
                   ),


    shutter = device('nicos.devices.generic.ManualSwitch',
                    description = 'virtual shutter',
                    states = ['unknown', 'open', 'close'],
                    requires = {'level': 0},
                    ),
    air_detector = device('nicos.devices.generic.ManualSwitch',
                          description = 'virtual air switch of the detecotor',
                          states = ['unknown', 'on', 'off'],
                          requires = {'level': 0},
                          ),
    air_sample = device('nicos.devices.generic.ManualSwitch',
                        description = 'virtual air switch of the sample table',
                        states = ['unknown', 'on', 'off'],
                        requires = {'level': 0},
                        ),
)
