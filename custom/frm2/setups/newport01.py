description = 'Newport sample stick rotator'

group = 'plugplay'

includes = ['alias_sth']

nethost = setupname

devices = {
    'sth_%s_m' % setupname: device('nicos_mlz.frm2.newport.Motor',
                                   tacodevice = '//%s/box/newportmc/motor' % (nethost,),
                                   lowlevel = True,
                                  ),

    'sth_%s' % setupname: device('nicos.devices.generic.Axis',
                                 description = 'Newport rotation axis',
                                 motor = 'sth_%s_m' % (setupname,),
                                 coder = 'sth_%s_m' % (setupname,),
                                 fmtstr = '%.3f',
                                 precision = 0.01,
                                 unit = 'deg',
                                 obs = [],
                                 dragerror = 3,
                                 maxtries = 5,
                                 loopdelay = 0.3,
                                 backlash = 0.0,
                                ),
}

alias_config = {
    'sth': {'sth_%s' % setupname: 200},
}
