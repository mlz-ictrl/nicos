sysconfig = dict(
    instrument = 'sxtal',
)

devices = dict(
    sxtal = device('nicos.devices.sxtal.instrument.SXTalBase',
        mono = "mono",
        responsible = "I. Responsible <invalid@invalid.org>"
    ),
    mono = device('nicos.devices.generic.mono.Monochromator',
        abslimits = [0.1, 20],
        unit = "A"
    ),
)
