description = 'at samplecamper [slit k1]'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
#
## smccorvusserver b2 exports
#
    b2 = device('refsans.nok_support.DoubleMotorNOK',
                description = 'b2 at sample pos',
                nok_start = 11049.50,
                nok_length = 13.0,
                nok_end = 11064.50,
                nok_gap = 1.0,
                inclinationlimits = (-1000, 1000),   # invented values, PLEASE CHECK!
                masks = dict(
                             k1 = [0, -85, -2.81, -0.24], #MH 22.02.2017 14:35:12 scan
                             slit = [0, 0, -2.734, -2.15], #JFM 15.11.2016 15:02:29 manuell
                            ),
                motor_r = 'b2r',
                motor_s = 'b2s',
                nok_motor = [11049.50, 11064.50],
                backlash = 0,   # is this configured somewhere?
                precision = 0.05,
               ),
    b2r = device('nicos.devices.generic.Axis',
                 description = 'b2, reactorside',
                 motor = 'smccorvus_b2mr',
                 coder = 'smccorvus_b2er',
                 backlash = 0,
                 precision = 0.05,
                 unit = 'mm',
                 lowlevel = True,
                ),
    b2s = device('nicos.devices.generic.Axis',
                 description = 'b2, sampleside',
                 motor = 'smccorvus_b2ms',
                 coder = 'smccorvus_b2es',
                 backlash = 0,
                 precision = 0.05,
                 unit = 'mm',
                 lowlevel = True,
                ),
    smccorvus_b2er = device('nicos.devices.taco.Coder',
                            description = 'Device test/smccorvus/b2er of Server smccorvusserver b2',
                            tacodevice = '//%s/test/smccorvus/b2er' % nethost,
                            lowlevel = True,
                           ),

    smccorvus_b2mr = device('nicos.devices.taco.Motor',
                            description = 'Device test/smccorvus/b2mr of Server smccorvusserver b2',
                            tacodevice = '//%s/test/smccorvus/b2mr' % nethost,
                            abslimits = (-294, 222),
                            lowlevel = True,
                           ),

    smccorvus_b2es = device('nicos.devices.taco.Coder',
                            description = 'Device test/smccorvus/b2es of Server smccorvusserver b2',
                            tacodevice = '//%s/test/smccorvus/b2es' % nethost,
                            lowlevel = True,
                           ),

    smccorvus_b2ms = device('nicos.devices.taco.Motor',
                            description = 'Device test/smccorvus/b2ms of Server smccorvusserver b2',
                            tacodevice = '//%s/test/smccorvus/b2ms' % nethost,
                            abslimits = (-296, 213),
                            lowlevel = True,
                           ),

)
