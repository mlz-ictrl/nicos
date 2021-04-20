# -*- coding: utf-8 -*-

description = 'Dynamic light scattering setup'
group = 'basic'

includes = []

sysconfig = dict(
    datasinks = ['dlssink'],
)

tango_base = 'tango://localhost:10000/dls/'

devices = dict(
    card1 = device('nicos_mlz.kws1.devices.dls.DLSCard',
        description = 'DLS correlator card 1',
        tangodevice = tango_base + 'corr1/spectra',
        angles = [75, 0],
        wheels = ['wheel_laser'],
        unit = '',
    ),
    card2 = device('nicos_mlz.kws1.devices.dls.DLSCard',
        description = 'DLS correlator card 2',
        tangodevice = tango_base + 'corr2/spectra',
        angles = [115, 100],
        wheels = ['wheel_laser', 'wheel_det1', 'wheel_det2'],
        unit = '',
    ),
    shutter = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Laser shutter for DLS',
        tangodevice = tango_base + 'shutter/ctrl',
        mapping = {'open': 1, 'closed': 0},
    ),
    wheel_laser = device('nicos.devices.entangle.DigitalOutput',
        description = 'Filter wheel in front of laser',
        tangodevice = tango_base + 'wheel0/pos',
        fmtstr = '%d',
    ),
    wheel_det1 = device('nicos.devices.entangle.DigitalOutput',
        description = 'Filter wheel in front of detector 1',
        tangodevice = tango_base + 'wheel1/pos',
        fmtstr = '%d',
    ),
    wheel_det2 = device('nicos.devices.entangle.DigitalOutput',
        description = 'Filter wheel in front of detector 2',
        tangodevice = tango_base + 'wheel2/pos',
        fmtstr = '%d',
    ),
    limiter_laser = device('nicos.devices.entangle.AnalogOutput',
        description = 'Helper device to limit photon intensity using filter wheel',
        tangodevice = tango_base + 'wheel0/limiter',
    ),
    limiter_det1 = device('nicos.devices.entangle.AnalogOutput',
        description = 'Helper device to limit photon intensity using filter wheel',
        tangodevice = tango_base + 'wheel1/limiter',
    ),
    limiter_det2 = device('nicos.devices.entangle.AnalogOutput',
        description = 'Helper device to limit photon intensity using filter wheel',
        tangodevice = tango_base + 'wheel2/limiter',
    ),
    #virtual_limiter = device('nicos.devices.generic.ManualMove',
    #    description = 'Virtual limiter to use if filter wheel is not present',
    #    unit = 'kHz',
    #    abslimits = (0, 1e6),
    #),
    dlssink = device('nicos_mlz.kws1.devices.dls.DLSFileSink',
        detectors = ['DLSdet'],
    ),
    DLSdet = device('nicos_mlz.kws1.devices.dls.DLSDetector',
        description = 'DLS detector',
        cards = ['card1', 'card2'],
        limiters = ['limiter_laser', 'limiter_det1', 'limiter_det2'],
        shutter = 'shutter',
        lasersel = 'laser',
        wavelengthmap = {'red': 650, 'green': 550},
    ),
    mirror_pos = device('nicos.devices.entangle.Motor',
        description = 'Mirror table to select laser',
        tangodevice = tango_base + 'mirror/table',
        fmtstr = '%.2f',
        precision = 0.1,
    ),
    laser = device('nicos.devices.generic.Switcher',
        description = 'Selected laser from mirror table',
        moveable = 'mirror_pos',
        mapping = {'red': 0, 'green': 21.9},
        precision = 0.1,
    ),
)

startupcode = '''
SetDetectors(DLSdet)
'''

extended = dict(
    representative = 'DLSdet',
)
