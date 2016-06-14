# -*- coding: utf-8 -*-

description = "Polarizer setup"
group = "lowlevel"
display_order = 60

excludes = ['virtual_polarizer']

tango_base = "tango://phys.kws1.frm2:10000/kws1/"

devices = dict(
    polarizer    = device('kws1.polarizer.Polarizer',
                          description = "high-level polarizer switcher",
                          switcher = 'pol_switch',
                          flipper = 'flipper'
                         ),

    pol_xv       = device("devices.tango.Motor",
                         description = "polarizer table front X",
                         tangodevice = tango_base + "fzjs7/polarisator_xv",
                         unit = "mm",
                         precision = 0.05,
                         fmtstr = "%.2f",
                        ),
    pol_yv      = device("devices.tango.Motor",
                         description = "polarizer table front Y",
                         tangodevice = tango_base + "fzjs7/polarisator_yv",
                         unit = "mm",
                         precision = 0.05,
                         fmtstr = "%.2f",
                        ),
    pol_xh      = device("devices.tango.Motor",
                         description = "polarizer table back X",
                         tangodevice = tango_base + "fzjs7/polarisator_xh",
                         unit = "mm",
                         precision = 0.05,
                         fmtstr = "%.2f",
                        ),
    pol_yh      = device("devices.tango.Motor",
                         description = "polarizer table back Y",
                         tangodevice = tango_base + "fzjs7/polarisator_yh",
                         unit = "mm",
                         precision = 0.05,
                         fmtstr = "%.2f",
                        ),
    pol_rot     = device("devices.tango.Motor",
                         description = "polarizer rotation",
                         tangodevice = tango_base + "fzjs7/polarisator_rot",
                         unit = "deg",
                         precision = 0.01,
                         fmtstr = "%.2f",
                        ),
    pol_switch  = device("kws1.polarizer.PolSwitcher",
                         description = "switch polarizer or neutron guide",
                         blockingmove = False,
                         moveables = ["pol_rot", "pol_xv", "pol_yv", "pol_xh", "pol_yh"],
                         readables = [],
                         movepos = [5.0, 5.0, 5.0, 5.0],
                         mapping = {
                             'pol': [155.33, 5.0, 5.0, 5.0, 5.0],
                             'ng':  [335.33, 5.0, 5.0, 5.0, 5.0],
                         },
                         precision = [0.01, 0.05, 0.05, 0.05, 0.05],
                         fallback = 'unknown',
                        ),

    flip_set    = device('devices.tango.DigitalOutput',
                         tangodevice = tango_base + 'fzjdp_digital/flipper_write',
                         lowlevel = True,
                        ),
    flip_ps     = device('devices.tango.PowerSupply',
                         tangodevice = tango_base + 'flipperps/volt',
                         lowlevel = True,
                         abslimits = (0, 11),
                         timeout = 3,
                        ),
    flipper     = device("kws1.flipper.Flipper",
                         description = "spin flipper after polarizer",
                         output = 'flip_set',
                         supply = 'flip_ps',
                        ),
)
