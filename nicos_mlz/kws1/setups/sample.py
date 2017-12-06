# -*- coding: utf-8 -*-

description = 'Sample aperture and table'
group = 'lowlevel'
display_order = 35

excludes = ['virtual_sample']

tango_base = 'tango://phys.kws1.frm2:10000/kws1/'

devices = dict(
    ap_sam_x0 = device('nicos.devices.tango.Motor',
        description = 'sample aperture horz. blade 0',
        tangodevice = tango_base + 'fzjs7/new_ap_sam_x0',
        unit = 'mm',
        precision = 0.01,
        lowlevel = True,
    ),
    ap_sam_y0 = device('nicos.devices.tango.Motor',
        description = 'sample aperture vert. blade 0',
        tangodevice = tango_base + 'fzjs7/new_ap_sam_y0',
        unit = 'mm',
        precision = 0.01,
        lowlevel = True,
    ),
    ap_sam_x1 = device('nicos.devices.tango.Motor',
        description = 'sample aperture horz. blade 1',
        tangodevice = tango_base + 'fzjs7/new_ap_sam_x1',
        unit = 'mm',
        precision = 0.01,
        lowlevel = True,
    ),
    ap_sam_y1 = device('nicos.devices.tango.Motor',
        description = 'sample aperture vert. blade 1',
        tangodevice = tango_base + 'fzjs7/new_ap_sam_y1',
        unit = 'mm',
        precision = 0.01,
        lowlevel = True,
    ),
    ap_sam = device('nicos.devices.generic.Slit',
        description = 'sample aperture',
        coordinates = 'opposite',
        opmode = 'offcentered',
        left = 'ap_sam_y0',
        right = 'ap_sam_y1',
        bottom = 'ap_sam_x0',
        top = 'ap_sam_x1',
    ),
    sam_trans_x = device('nicos.devices.tango.Motor',
        description = 'sample translation left-right',
        tangodevice = tango_base + 'fzjs7/sample_axis_1',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.1f',
    ),
    sam_trans_y = device('nicos.devices.tango.Motor',
        description = 'sample translation up-down',
        tangodevice = tango_base + 'fzjs7/sample_axis_2',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.1f',
    ),
)
