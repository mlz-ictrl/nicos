description = 'High Resolution Detector Box'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    scintillatortx = device('nicos.devices.tango.Motor',
                 description = 'Translation of scintillator box in X direction',
                 tangodevice = tango_base + 'fzjs7/FOV',
                 abslimits = (0, 200),
                 userlimits = (0, 200),
                 precision = 0.01,
                ),
)
