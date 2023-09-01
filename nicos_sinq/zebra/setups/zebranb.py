description = 'Installs normal beam geometry into ZEBRA'

includes = ['monochromator', 'sample']

excludes = ['zebraeuler', 'zebratas', 'zebrakappa']

sysconfig = dict(instrument = 'ZEBRA',)

devices = dict(
    chi = device('nicos.devices.generic.ManualMove',
        description = 'Simulated chi motor',
        abslimits = (70, 212.5),
        default = 180,
        unit = 'degree',
    ),
    phi = device('nicos.devices.generic.ManualMove',
        description = 'Simulated phi motor',
        abslimits = (-180, 180),
        default = 0,
        unit = 'degree',
    ),
    ZEBRA = device('nicos_sinq.zebra.devices.sinqxtal.SinqNB',
        description = 'instrument object',
        instrument = 'SINQ ZEBRA',
        responsible = 'Oksana Zaharko <oksana.zaharko@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/zebra/',
        gamma = 'stt',
        omega = 'om',
        nu = 'nu',
        mono = 'wavelength',
        center_order = ['om', 'stt', 'nu'],
        center_steps = [.1, .1, .1],
        scan_polynom = [0.425, -1.34E-2, 3.44E-6, -3.10E-6, 1.33E-8, .1, 1],
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'ZEBRA.h',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'ZEBRA.k',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'ZEBRA.l',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
)

startupcode = """
maw(zebramode, 'nb')
ublist.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'NU'),())
messlist.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'NU'),())
satref.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'NU'),())
maw(chi, 180, phi, 0)
"""
