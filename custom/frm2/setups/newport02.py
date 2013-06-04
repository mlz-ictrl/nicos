description = 'Newport sample stick rotator'

group = 'optional'

includes = ['alias_sth']

nethost = 'newport02'

devices = {
    'sth_%s_m' % nethost : device('devices.taco.Motor',
                                  tacodevice = '//%s/newport/newportmc/motor' % (nethost,),
                                  lowlevel = True,
                                 ),

    'sth_%s' % nethost : device('devices.generic.Axis',
                                motor = 'sth_%s_m' % (nethost,),
                                coder = 'sth_%s_m' % (nethost,),
                                fmtstr = '%.3f',
                                precision = 0.001,
                                unit = 'deg',
                                obs = [],
                                dragerror = 3,
                                maxtries = 5,
                                loopdelay = 0.3,
                                backlash = 0.0,
                               ),
}

startupcode = """
sth.alias = sth_%s
""" % (nethost,)
