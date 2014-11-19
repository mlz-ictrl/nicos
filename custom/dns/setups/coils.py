# -*- coding: utf-8 -*-

__author__  = "Christian Felder <c.felder@fz-juelich.de>"


description = "Coil setup"
group = "optional"

includes = ["toellner"]

_TANGO_HOST = 'tango://phys.dns.frm2:10000'
_POLCHANGE = {
                "+": 0,
                "-": 1,
              }

devices = dict(
        flipper = device('devices.polarized.flipper.MezeiFlipper',
                         description = 'Neutron spin flipper',
                         flip = "Fi",
                         corr = "Co",
                        ),
        polch_Fi  = device('devices.tango.NamedDigitalOutput',
                           description = 'Pole changer for Flipper Field',
                           tangodevice = ('%s/dns/FZJDP_Digital/Polum2'
                                          % _TANGO_HOST),
                           mapping = _POLCHANGE,
                           lowlevel = True
                          ),
        Fi = device('dns.toellner.CurrentToellner',
                    description = 'Flipper Field',
                    tangodevice = '%s/dns/gpib/21' % _TANGO_HOST,
                    abslimits = (-3.2,3.2),
                    polchange = 'polch_Fi',
                    channel = 2,
                   ),
        polch_Co  = device('devices.tango.NamedDigitalOutput',
                           description = 'Pole changer for Flipper Compensation',
                           tangodevice = ('%s/dns/FZJDP_Digital/Polum1'
                                          % _TANGO_HOST),
                           mapping = _POLCHANGE,
                           lowlevel = True
                          ),
        Co = device('dns.toellner.CurrentToellner',
                    description = 'Flipper Compensation Field',
                    tangodevice = '%s/dns/gpib/21' % _TANGO_HOST,
                    abslimits = (-3.2,3.2),
                    polchange = 'polch_Co',
                    channel = 1,
                   ),
               )
