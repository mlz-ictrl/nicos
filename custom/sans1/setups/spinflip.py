description = 'Spin Flipper'

includes = []

group = 'optional'

modules = ['nicos_mlz.sans1.spinflipper_commands']

tango_base = 'tango://spinflip.sans1.frm2:10000/box/'
tango_base_truerms = 'tango://sans1hw.sans1.frm2:10000/sans1/'

devices = dict(
# AG1016 amplifier
    P_spinflipper = device('nicos_mlz.sans1.spinflipper.SpinflipperPower',
                           description = 'overall power of ag1016',
                           tangodevice = tango_base + 'amplifier/power',
                           forwardtangodevice = tango_base + 'amplifier/fpower',
                           reversetangodevice = tango_base + 'amplifier/rpower',
                           fmtstr = '%.1f',
                           abslimits = (0.0, 100.0),
                           userlimits = (0.0, 100.0),
                           maxage = 120,
                           pollinterval = 15,
                          ),

    P_spinflipper_forward = device('nicos.devices.generic.ReadonlyParamDevice',
                                   description = 'Paramdevice used to select the forward power',
                                   lowlevel = True,
                                   device = 'P_spinflipper',
                                   parameter = 'forward',
                                   maxage = 120,
                                   pollinterval = 15,
                                  ),

    P_spinflipper_reverse = device('nicos.devices.generic.ReadonlyParamDevice',
                                   description = 'Paramdevice used to select the reverse power',
                                   lowlevel = True,
                                   device = 'P_spinflipper',
                                   parameter = 'reverse',
                                   maxage = 120,
                                   pollinterval = 15,
                                  ),

#    T_spinflipper_AG = device('nicos.devices.tango.AnalogInput',
#                           description = 'temperature of ag1016',
#                           tangodevice = tango_base + 'amplifier/temp',
#                           fmtstr = '%.3f',
#                           maxage = 120,
#                           pollinterval = 15,
#                          ),

# HP33220A
    A_spinflipper_hp = device('nicos.devices.tango.AnalogOutput',
                              description = 'amplitude of the frequency generator',
                              tangodevice = tango_base + 'funcgen/ampl',
                              fmtstr = '%.3f',
                              abslimits = (0, 2.0),
                              userlimits = (0, 2.0),
                              maxage = 120,
                              pollinterval = 15,
                             ),

    F_spinflipper_hp = device('nicos.devices.tango.AnalogOutput',
                              description = 'frequency of the frequency generator',
                              tangodevice = tango_base + 'funcgen/freq',
                              fmtstr = '%.0f',
                              abslimits = (0.0, 4000000.0),
                              userlimits = (0.0, 4000000.0),
                              maxage = 120,
                              pollinterval = 15,
                             ),

# WUT Box
    T_spinflipper = device('nicos_mlz.sans1.wut.WutValue',
                            hostname = 'sans1wut-temp-spinflip.sans1.frm2',
                            port = '1',
                            description = 'temperature of spinflipper',
                            fmtstr = '%.2F',
                            lowlevel = False,
                            loglevel = 'info',
                            unit = 'C',
    ),

# Keysight 34461A
    U_spinflipper = device('nicos_mlz.sans1.k34461a.VoltageMeter',
               description = 'Voltage of 34461A True RMS Meter',
               tangodevice = tango_base_truerms + 'rmsspinflip/io',
               unit = 'V',
               fmtstr = '%.2f',
               pollinterval = 5,
               maxage = 18,
              ),
)
