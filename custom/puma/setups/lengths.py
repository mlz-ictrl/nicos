#  -*- coding: utf-8 -*-

description = 'Collimation and Lengths'

group = 'lowlevel'

includes = ['system']

# !!! keep in sync with custom/puma/lib/spectro.py !!!

devices = dict(
    lsm      = device('devices.generic.ManualMove',
                      description = 'distance source - mono',
                      default = 5633,
                      unit = 'mm',
                      fmtstr = '%.0f',
                      abslimits = (5633, 5633)),
    lms      = device('devices.generic.ManualMove',
                      description = 'distance mono - sample',
                      default = 2090,
                      unit = 'mm',
                      fmtstr = '%.0f',
                      abslimits = (2090, 2100)),
    lsa      = device('devices.generic.ManualMove',
                      description = 'distance sample - ana',
                      default = 880,
                      unit = 'mm',
                      fmtstr = '%.0f',
                      abslimits = (880, 1180)),
    lad      = device('devices.generic.ManualMove',
                      description = 'distance ana - detector',
                      default = 750,
                      unit = 'mm',
                      fmtstr = '%.0f',
                      abslimits = (750, 750)),

    cb1      = device('devices.generic.ManualMove',
                      description = 'vertical divergence before mono',
                      default = 240,
                      unit = 'min',
                      fmtstr = '%6.1f',
                      abslimits = (240, 240)),
    cb2      = device('devices.generic.ManualMove',
                      description = 'vertical divergence after mono',
                      default = 240,
                      unit = 'min',
                      fmtstr = '%6.1f',
                      abslimits = (240, 240)),
    cb3      = device('devices.generic.ManualMove',
                      description = 'vertical divergence before ana',
                      default = 240,
                      unit = 'min',
                      fmtstr = '%6.1f',
                      abslimits = (240, 240)),
    cb4      = device('devices.generic.ManualMove',
                      description = 'vertical divergence after ana',
                      default = 240,
                      unit = 'min',
                      fmtstr = '%6.1f',
                      abslimits = (240, 240)),

    ca1      = device('devices.generic.ManualSwitch',
                      description = 'monochromator collimator before mono',
                      states = ['none', '20m', '40m', '60m']),
    ca2      = device('devices.generic.ManualSwitch',
                      description = 'post monochromator collimator',
                      states = ['none', '14m', '20m', '24m', '30m', '45m', '60m']),
    ca3      = device('devices.generic.ManualSwitch',
                      description = 'pre analyser collimator',
                      states = ['none', '20m', '30m', '45m', '60m', '120m']),
    ca4      = device('devices.generic.ManualSwitch',
                      description = 'post analyser collimator',
                      states = ['none', '10m', '30m', '45m', '60m']),
)
