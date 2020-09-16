description = 'Newport sample stick rotator'

group = 'plugplay'

includes = ['alias_sth']

nethost = setupname

devices = {
    'sth_%s_m' % setupname: device('nicos.devices.tango.Motor',
        tangodevice = 'tango://%s:10000/box/newport/motor1' % (nethost,),
        refpos = 0.0,
        lowlevel = True,
    ),
    'sth_%s' % setupname: device('nicos.devices.generic.Axis',
        description = 'Newport rotation axis',
        motor = 'sth_%s_m' % (setupname,),
        fmtstr = '%.3f',
        precision = 0.01,
        unit = 'deg',
        dragerror = 3,
        maxtries = 5,
        loopdelay = 0.3,
        backlash = 0.0,
    ),
}

alias_config = {
    'sth': {'sth_%s' % setupname: 200},
}

extended = dict(
    representative = 'sth_%s' % setupname,
)
