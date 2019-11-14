description = 'memograph readout'

includes = []

group = 'lowlevel'

tangohost = 'phys.spheres.frm2'
# tangohost = 'localhost'
memograph = 'tango://%s:10000/spheres/memograph/' % tangohost

devices = dict(
    t_in_memograph = device('nicos.devices.tango.Sensor',
        tangodevice = memograph + 't_in',
        description = 'inlet temperature memograph',
        fmtstr = '%.2F',
    ),
    t_out_memograph = device('nicos.devices.tango.Sensor',
        tangodevice = memograph + 't_out',
        description = 'outlet temperature memograph',
        fmtstr = '%.2F',
    ),
    p_in_memograph = device('nicos.devices.tango.Sensor',
        tangodevice = memograph + 'p_in',
        description = 'inlet pressure memograph',
        fmtstr = '%.2F',
    ),
    p_out_memograph = device('nicos.devices.tango.Sensor',
        tangodevice = memograph + 'p_out',
        description = 'outlet pressure memograph',
        fmtstr = '%.2F',
    ),
    flow_in_memograph = device('nicos.devices.tango.Sensor',
        tangodevice = memograph + 'flow_in',
        description = 'inlet flow memograph',
        fmtstr = '%.2F',
    ),
    flow_out_memograph = device('nicos.devices.tango.Sensor',
        tangodevice = memograph + 'flow_out',
        description = 'outlet flow memograph',
        fmtstr = '%.2F',
    ),
    leak_memograph = device('nicos.devices.tango.Sensor',
        tangodevice = memograph + 'leak',
        description = 'leakage memograph',
        fmtstr = '%.2F',
    ),
    cooling_memograph = device('nicos.devices.tango.Sensor',
        tangodevice = memograph + 'cooling',
        description = 'cooling power memograph',
        fmtstr = '%.2F',
    ),
)
