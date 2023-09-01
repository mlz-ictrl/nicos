description = 'Installs the Eulerian cradle into NICOS'

excludes = ['zebratas', 'zebranb', 'zebrakappa']

includes = ['monochromator', 'sample']

sysconfig = dict(instrument = 'ZEBRA',)

pvpref = 'SQ:ZEBRA:mcu'

devices = dict(
    chi = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'CHI rotation',
        motorpv = pvpref + '2:SCH',
        errormsgpv = pvpref + '2:SCH-MsgTxt',
        precision = 0.5,
        can_disable = True,
        auto_enable = True,
    ),
    phi = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'PHI rotation',
        motorpv = pvpref + '2:SPH',
        errormsgpv = pvpref + '2:SPH-MsgTxt',
        precision = 0.5,
        userlimits = (-180, 180),
        can_disable = True,
        auto_enable = True,
    ),
    ZEBRA = device('nicos_sinq.zebra.devices.sinqxtal.SinqEuler',
        description = 'instrument object',
        instrument = 'SINQ ZEBRA',
        responsible = 'Oksana Zaharko <oksana.zaharko@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/zebra/',
        ttheta = 'stt',
        omega = 'om',
        chi = 'chi',
        phi = 'phi',
        mono = 'wavelength',
        center_counter = 'counts',
        center_order = ['om', 'stt', 'chi', 'phi'],
        center_steps = [.1, .1, .2, .2],
        scan_polynom = [0.425, -1.3E-2, 3.44E-4, -3.10E-6, 1.33E-8],
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
ublist.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'CHI', 'PHI'),()) 
messlist.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'CHI', 'PHI'),()) 
satref.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'CHI', 'PHI'),()) 
"""
