description = 'Non-electronically adjustable parameters of the detector'

group = 'optional'

devices = dict(
    scintillator = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Scintillator installed in the camera box',
        states = ['050um LiF:ZnS',
                  '100um LiF:ZnS',
                  '150um LiF:ZnS',
                  '200um LiF:ZnS',
                  '300um LiF:ZnS',
                  '020um Gd2O2S2',
                  'other',
                  ],
    ),
    lens = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Lens installed in the camera box',
        states = ['Leica 100mm F2.8',
                  'Leica 100mm with macro adapter',
                  'Zeiss 100mm F1.8',
                  'other',
                  ],
    ),
    camerabox = device('nicos.devices.generic.manual.ManualSwitch',
        description = 'Used camera box',
        states = ['Black Box',
                  'Neo Box - 1 mirror config',
                  'Neo Box - 2 mirror config',
                  'Large detector in chamber 2',
                  'other',
                  ],
    ),
)
