# -*- coding: utf-8 -*-

description = "General sample aliases"
group = "lowlevel"
display_order = 32

excludes = ['virtual_sample']

devices = dict(
    sam_x        = device("devices.generic.DeviceAlias",
                          description = "currently active sample x table",
                         ),
    sam_y        = device("devices.generic.DeviceAlias",
                          description = "currently active sample y table",
                         ),
    sam_ap       = device("devices.generic.DeviceAlias",
                          description = "currently active sample aperture",
                         ),
)
