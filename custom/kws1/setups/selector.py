#  -*- coding: utf-8 -*-

description = 'setup for the velocity selector'
group = 'lowlevel'

excludes = ['virtual_selector']

presets = configdata('config_selector.SELECTOR_PRESETS')

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    selector        = device('kws1.switcher.SelectorSwitcher',
                             description = 'select selector presets',
                             blockingmove = False,
                             moveables = ['selector_speed'],
                             presets = presets,
                             mapping = dict((k, [v['speed']])
                                            for (k, v) in presets.items()),
                             fallback = 'unknown',
                             precision = [10.0],
                            ),

    selector_speed  = device('devices.tango.WindowTimeoutAO',
                             description = 'Selector speed control',
                             tangodevice = tango_base + 'selector/speed',
                             unit = 'rpm',
                             fmtstr = '%.0f',
                             warnlimits = (11000, 27300),
                             abslimits = (11000, 27300),
                             precision = 10,
                            ),

    selector_lambda = device('kws1.selector.SelectorLambda',
                             description = 'Selector wavelength control',
                             seldev = 'selector_speed',
                             unit = 'A',
                             fmtstr = '%.2f',
                             constant = 2227.5,
                            ),

    selector_rtemp  = device('devices.tango.AnalogInput',
                             description = 'Temperature of the selector rotor',
                             tangodevice = tango_base + 'selector/rotortemp',
                             unit = 'degC',
                             fmtstr = '%.1f',
                             warnlimits = (10, 40),
                            ),
    selector_winlt  = device('devices.tango.AnalogInput',
                             description = 'Cooling water temperature at inlet',
                             tangodevice = tango_base + 'selector/waterintemp',
                             unit = 'degC',
                             fmtstr = '%.1f',
                             warnlimits = (15, 22),
                            ),
    selector_woutt  = device('devices.tango.AnalogInput',
                             description = 'Cooling water temperature at outlet',
                             tangodevice = tango_base + 'selector/waterouttemp',
                             unit = 'degC',
                             fmtstr = '%.1f',
                             warnlimits = (15, 26),
                            ),
    selector_wflow  = device('devices.tango.AnalogInput',
                             description = 'Cooling water flow rate through selector',
                             tangodevice = tango_base + 'selector/flowrate',
                             unit = 'l/min',
                             fmtstr = '%.1f',
                             warnlimits = (1.0, 10),
                            ),
    selector_vacuum = device('devices.tango.AnalogInput',
                             description = 'Vacuum in the selector',
                             tangodevice = tango_base + 'selector/vacuum',
                             unit = 'mbar',
                             fmtstr = '%.5f',
                             warnlimits = (0, 0.02),
                            ),
    selector_vibrt  = device('devices.tango.AnalogInput',
                             description = 'Selector vibration',
                             tangodevice = tango_base + 'selector/vibration',
                             unit = 'mm/s',
                             fmtstr = '%.2f',
                             warnlimits = (0, 0.6),
                            ),
)
