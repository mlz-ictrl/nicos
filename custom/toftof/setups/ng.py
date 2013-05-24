description = 'elliptical neutron guide nose'

group = 'optional'

includes = []

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    ng_left    = device('devices.taco.Motor',
                        description = 'Left mirror bender of the flexible'
                                    ' neutron guide',
                        tacodevice = '//%s/toftof/pm/motleft' % (nethost,),
                        fmtstr = "%7.3f",
                        abslimits = (-20000.0, 20000.),
                       ),
    ng_right    = device('devices.taco.Motor',
                         description = 'Right mirror bender of the flexible'
                                    ' neutron guide',
                         tacodevice = '//%s/toftof/pm/motright' % (nethost,),
                         fmtstr = "%7.3f",
                         abslimits = (-20000.0, 20000.),
                        ),
    ng_bottom   = device('devices.taco.Motor',
                         description = 'Bottom mirror bender of the flexible'
                                    ' neutron guide',
                         tacodevice = '//%s/toftof/pm/motbottom' % (nethost,),
                         fmtstr = "%7.3f",
                         abslimits = (-20000.0, 20000.),
                        ),
    ng_top      = device('devices.taco.Motor',
                         description = 'Top mirror bender of the flexible'
                                    ' neutron guide',
                         tacodevice = '//%s/toftof/pm/mottop' % (nethost,),
                         fmtstr = "%7.3f",
                         abslimits = (-20000.0, 20000.),
                        ),
)
