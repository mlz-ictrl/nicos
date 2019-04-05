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
        angle = 150,
    ),
    card2 = device('nicos_mlz.kws1.devices.dls.DLSCard',
        description = 'DLS correlator card 2',
        tangodevice = tango_base + 'corr2/spectra',
        angle = 60,
    ),
    shutter = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Laser shutter for DLS',
        tangodevice = tango_base + 'shutter/ctrl',
        mapping = {'open': 1, 'closed': 0},
    ),
    limiter = device('nicos.devices.tango.AnalogOutput',
        description = 'Helper device to limit photon intensity using filter wheel',
        tangodevice = tango_base + 'wheel1/limiter',
    ),
    virtual_limiter = device('nicos.devices.generic.ManualMove',
        description = 'Virtual limiter to use if filter wheel is not present',
        unit = 'kHz',
        abslimits = (0, 1e6),
    ),
    dlssink = device('nicos_mlz.kws1.devices.dls.DLSFileSink',
        detectors = ['DLS'],
    ),
    DLS = device('nicos_mlz.kws1.devices.dls.DLSDetector',
        description = 'DLS detector',
        cards = ['card1', 'card2'],
        limiter = 'limiter',
        shutter = 'shutter',
    ),
    mirror_pos = device('nicos.devices.tango.Motor',
        description = 'Mirror table to select laser',
        tangodevice = tango_base + 'mirror/table',
        fmtstr = '%.2f',
    ),
)

extended = dict(
    representative = 'DLS',
)

alias_config = dict(
)
