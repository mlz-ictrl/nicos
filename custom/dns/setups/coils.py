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
        flip_currents = device('devices.generic.ParamDevice',
                               description = 'Helper device for setting the'
                               'currents on the flipper device as a moveable',
                               device = 'flipper',
                               parameter = 'currents',
                               unit = 'A',
                               lowlevel = True,
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
        field = device('devices.generic.MultiSwitcher',
                       moveables = ["A", "B", "C", "ZB", "ZT",
                                    "flip_currents", "flipper"],
                       mapping = {
                          "off": (0, 0, 0, 0, 0,
                                  (0, 0), "off"),
                          "zero field": (0, .11, -.50, -2.21, -2.21,
                                         (.97, .56), "on"),
                          "x7": (0, -2, -.77, -2.21, -2.21,
                                 (0.90, 0.40), "on"),
                          "-x7": (0, 2.22, -.23, -2.21, -2.21,
                                  (1.05, 0.38), "on"),
                          "y7": (0, 1.6, -2.77, -2.21, -2.21,
                                 (0.85, 0.48), "on"),
                          "-y7": (0, -1.38, 1.77, -2.21, -2.21,
                                  (0.98, 0.38), "on"),
                          "z7": (0, .11, -.50, 0.0, 0.0,
                                      (0.90, 0.45), "on"),
                          "-z7": (0, .11, -.5, -4.42, -4.42,
                                  (1.20, 0.20), "on"),
                       },
                       precision = [.1, .1, .1, .1, .1,
                                    0, 0],
                      ),
               )
