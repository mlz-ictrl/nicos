description = 'neutron guide changer or collimator'

group = 'lowlevel'

includes = []

nethost = 'toftofsrv.toftof.frm2'

devices = dict(
    ngc_motor = device('devices.taco.Motor',
                       description = 'The TACO motor for the neutron guide'
                                     ' changing mechnism',
                       tacodevice = '//%s/toftof/huber/ccmot' % (nethost,),
                       fmtstr = "%7.3f",
                       userlimits = (-140.8, 0.),
                       abslimits = (-141.8, 0.),
                       requires = {'level': 'admin'},
                       unit = 'mm',
                       lowlevel = True,
                      ),

    ngc = device('toftof.neutronguide.NeutronGuideSwitcher',
                 description = 'The neutron guide changer/collimator',
                 moveable = 'ngc_motor',
                 mapping = {'linear': -15.7, 'focus': -140.4,},
                 requires = {'level': 'admin'},
                ),
)
