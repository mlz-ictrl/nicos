# -*- coding: utf-8 -*-

description = 'Dynamic light scattering addon'
group = 'optional'

includes = ['alias_T']

sysconfig = dict(
    datasinks = ['dls_sink'],
)

tango_base = 'tango://dls01:10000/dls/'
pvprefix = 'UBI-CHEM:MC-MCU-01:'

devices = dict(
    dls_card1 = device('nicos_mlz.kws1.devices.dls.DLSCard',
        description = 'DLS correlator card 1',
        tangodevice = tango_base + 'corr1/spectra',
        angles = [150, 0],
        wheels = [],
    ),
    dls_card2 = device('nicos_mlz.kws1.devices.dls.DLSCard',
        description = 'DLS correlator card 2',
        tangodevice = tango_base + 'corr2/spectra',
        angles = [60, 0],
        wheels = [],
    ),
    dls_shutter = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Laser shutter for DLS',
        tangodevice = tango_base + 'shutter/open',
        mapping = {'open': 1, 'closed': 0},
    ),
    dls_limiter = device('nicos.devices.tango.AnalogOutput',
        description = 'Helper device to limit photon intensity using filter wheel',
        tangodevice = tango_base + 'wheel1/limiter',
    ),
    dls_virtual_limiter = device('nicos.devices.generic.ManualMove',
        description = 'Virtual limiter to use if filter wheel is not present',
        unit = 'kHz',
        abslimits = (0, 1e6),
    ),
    dls_sink = device('nicos_mlz.kws1.devices.dls.DLSFileSink',
        detectors = ['DLS'],
    ),
    DLS = device('nicos_mlz.kws1.devices.dls.DLSDetector',
        description = 'DLS detector',
        cards = ['dls_card1', 'dls_card2'],
        limiters = ['dls_limiter'],
        shutter = 'dls_shutter',
        wavelengthmap = {'': 650},
    ),
    dls_trans_x = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'X axis via EPICS',
        unit = 'mm',
        fmtstr = '%.2f',
        epicstimeout = 3.0,
        precision = 0.1,
        motorpv = pvprefix + 'm1',
        errormsgpv = pvprefix + 'm1-MsgTxt',
        errorbitpv = pvprefix + 'm1-Err',
        reseterrorpv = pvprefix + 'm1-ErrRst'
    ),
    dls_trans_y = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'Y axis via EPICS',
        unit = 'mm',
        fmtstr = '%.2f',
        epicstimeout = 3.0,
        precision = 0.1,
        motorpv = pvprefix + 'm2',
        errormsgpv = pvprefix + 'm2-MsgTxt',
        errorbitpv = pvprefix + 'm2-Err',
        reseterrorpv = pvprefix + 'm2-ErrRst'
    ),
    dls_TA = device('nicos.devices.tango.Sensor',
        description = 'LS224 sensor A',
        tangodevice = tango_base + 'ls224/ch1',
    ),
    dls_TB = device('nicos.devices.tango.Sensor',
        description = 'LS224 sensor B',
        tangodevice = tango_base + 'ls224/ch2',
    ),
    dls_TC = device('nicos.devices.tango.Sensor',
        description = 'LS224 sensor C',
        tangodevice = tango_base + 'ls224/ch3',
    ),
    dls_TD = device('nicos.devices.tango.Sensor',
        description = 'LS224 sensor D',
        tangodevice = tango_base + 'ls224/ch4',
    ),
)

extended = dict(
    representative = 'DLS',
)

alias_config = dict(
    Ts = {'dls_TA': 100},
)
