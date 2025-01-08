description = 'Installs the Kappa goniometer into NICOS'

excludes = ['zebratas', 'zebranb', 'zebraeuler']

includes = ['monochromator', 'sample']

sysconfig = dict(instrument = 'ZEBRA',)

pvpref = 'SQ:ZEBRA:kappa:'

devices = dict(
    omk = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Kappa omega rotation',
        motorpv = pvpref + 'omk',
        errormsgpv = pvpref + 'omk-MsgTxt',
        precision = 0.02,
        can_disable = True,
    ),
    kappa = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Kappa  rotation',
        motorpv = pvpref + 'kappa',
        errormsgpv = pvpref + 'kappa-MsgTxt',
        precision = 0.02,
        can_disable = True,
    ),
    phik = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Kappa phi rotation',
        motorpv = pvpref + 'phik',
        errormsgpv = pvpref + 'phik-MsgTxt',
        precision = 0.02,
        can_disable = True,
    ),
    ZEBRA = device('nicos_sinq.sxtal.instrument.KappaSXTal',
        description = 'instrument object',
        instrument = 'SINQ ZEBRA',
        responsible = 'Oksana Zaharko <oksana.zaharko@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/zebra/',
        stt = 'stt',
        omega = 'omk',
        kappa = 'kappa',
        kphi = 'phik',
        mono = 'wavelength',
        center_counter = 'counts',
        center_steps = [.1, .1, .2, .2],
        kappa_angle = 54.,
        right_hand = True,
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
maw(zebramode, 'kappa')
ublist.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'PHI'),())
messlist.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'PHI'),())
satref.column_headers=(('H', 'K', 'L'), ('STT', 'OM', 'PHI'),())
"""
