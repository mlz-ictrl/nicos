description = 'Installs the Triple Axis Calculations into ORION '

# WARNING 555: This is a test version for development

includes = ['orion']

excludes = ['euler', 'eulerorion']

devices = dict(
    ana = device('nicos.devices.generic.mono.Monochromator',
        description = 'Dummy analyzer',
        unit = 'meV'
    ),
    ORION = device('nicos_sinq.sxtal.instrument.TASSXTal',
        description = 'instrument object',
        instrument = 'SINQ ORION',
        responsible = 'Oksana Zaharko <oksana.zaharko@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/orion/',
        a3 = 'som',
        a4 = 'stt',
        sgu = 'sgu',
        sgl = 'sgl',
        mono = 'mono',
        ana = 'ana',
        inelastic = True,
        out_of_plane = True,
        plane_normal = [0.015167, 0.005586, 0.999869],
    ),
    h = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the h of hkl',
        alias = 'ORION.h',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    k = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the k of hkl',
        alias = 'ORION.k',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    l = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the l of hkl',
        alias = 'ORION.l',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
    en = device('nicos.core.device.DeviceAlias',
        description = 'Alias for the en of hkle',
        alias = 'ORION.en',
        devclass = 'nicos.devices.sxtal.instrument.SXTalIndex'
    ),
)
