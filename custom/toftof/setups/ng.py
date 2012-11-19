description = 'elliptical neutron guide nose'
includes = ['system']

nethost= 'toftofsrv.toftof.frm2'

devices = dict(
    ng_left    = device('devices.taco.Motor',
                   tacodevice = '//%s/toftof/pm/motleft' % (nethost,),
                   fmtstr = "%7.3f",
                   abslimits = (-20000.0, 20000.)),
    ng_right    = device('devices.taco.Motor',
                   tacodevice = '//%s/toftof/pm/motright' % (nethost,),
                   fmtstr = "%7.3f",
                   abslimits = (-20000.0, 20000.)),
    ng_bottom    = device('devices.taco.Motor',
                   tacodevice = '//%s/toftof/pm/motbottom' % (nethost,),
                   fmtstr = "%7.3f",
                   abslimits = (-20000.0, 20000.)),
    ng_top   = device('devices.taco.Motor',
                   tacodevice = '//%s/toftof/pm/mottop' % (nethost,),
                   fmtstr = "%7.3f",
                   abslimits = (-20000.0, 20000.)),
)
