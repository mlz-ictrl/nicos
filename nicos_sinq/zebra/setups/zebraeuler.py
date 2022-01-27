description = 'Installs the Eulerian cradle into NICOS'

excludes = ['zebratas', 'zebranb']

requires = ['monochromator', 'sample']

sysconfig = dict(instrument = 'ZEBRA',)

devices = dict(
    ZEBRA = device('nicos_sinq.sxtal.instrument.EulerSXTal',
        description = 'instrument object',
        instrument = 'SINQ ZEBRA',
        responsible = 'Oksana Zaharko <oksana.zaharko@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/zebra/',
        ttheta = 'stt',
        omega = 'som',
        chi = 'sch',
        phi = 'sph',
        mono = 'wavelength',
        center_counter = 'counts',
        center_steps = [.1, .1, .2, .2]
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
maw(zebramode, 'bi')
"""
