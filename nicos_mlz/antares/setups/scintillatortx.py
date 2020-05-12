description = 'Scintillator translation for Hi-Res detector box'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    scintillatortx = device('nicos.devices.tango.Motor',
        description = 'Translation of scintillator box in X direction',
        tangodevice = tango_base + 'fzjs7/FOV',
        abslimits = (-150, 250),
        userlimits = (-150, 250),
        precision = 0.01,
    ),
)
