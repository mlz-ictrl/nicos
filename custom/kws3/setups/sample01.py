# -*- coding: utf-8 -*-

description = "Sample Area 1m setup"
group = "lowlevel"
display_order = 45

excludes = ['virtual_sample']

tango_base = "tango://phys.kws3.frm2:10000/kws3/"

devices = dict(

    sam01_x          = device("devices.tango.Motor",
                              description = "sample 2nd x-table in vacuum chamber",
                              tangodevice = tango_base + "fzjs7/sam01_x",
                              unit = "mm",
                              precision = 0.01,
                             ),
    sam01_y          = device("devices.tango.Motor",
                              description = "sample 2nd y-table in vacuum chamber",
                              tangodevice = tango_base + "fzjs7/sam01_y",
                              unit = "mm",
                              precision = 0.01,
                             ),
    sam01_ap_x_left  = device("devices.tango.Motor",
                              description = "aperture sample 2nd jj-xray left",
                              tangodevice = tango_base + "fzjs7/sam01_ap_x_left",
                              unit = "mm",
                              precision = 0.01,
                              lowlevel = True,
                             ),
    sam01_ap_x_right = device("devices.tango.Motor",
                              description = "aperture sample 2nd jj-xray right",
                              tangodevice = tango_base + "fzjs7/sam01_ap_x_right",
                              unit = "mm",
                              precision = 0.01,
                              lowlevel = True,
                             ),
    sam01_ap_y_upper = device("devices.tango.Motor",
                              description = "aperture sample 2nd jj-xray upper",
                              tangodevice = tango_base + "fzjs7/sam01_ap_y_upper",
                              unit = "mm",
                              precision = 0.01,
                              lowlevel = True,
                             ),
    sam01_ap_y_lower = device("devices.tango.Motor",
                              description = "aperture sample 2nd jj-xray lower",
                              tangodevice = tango_base + "fzjs7/sam01_ap_y_lower",
                              unit = "mm",
                              precision = 0.01,
                              lowlevel = True,
                             ),
    sam01_ap         = device("devices.generic.Slit",
                              description = "sample 2nd aperture jj-xray",
                              coordinates = "opposite",
                              opmode = "offcentered",
                              left = "sam01_ap_x_left",
                              right = "sam01_ap_x_right",
                              bottom = "sam01_ap_y_lower",
                              top = "sam01_ap_y_upper",
                             ),
)
