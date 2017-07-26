# -*- coding: utf-8 -*-

description = 'GALAXI Bruker AXS X-Ray'

group = 'basic'

tango_base = 'tango://localhost:10000/galaxi/'

devices = dict(

    gen_voltage  = device('nicos.devices.tango.AnalogOutput',
                          description = 'XrayGenerator',
                          tangodevice = tango_base + 'XRayGenerator/voltage',
                          unit = 'kV',
                         ),
    gen_current  = device('nicos.devices.tango.AnalogOutput',
                          description = 'XrayGenerator',
                          tangodevice = tango_base + 'XRayGenerator/current',
                          unit = 'mA',
                         ),
    spotpos      = device('nicos.devices.tango.AnalogInput',
                          description = 'XRaySpotPosition',
                          tangodevice = tango_base + 'XRaySpotPos/1',
                         ),
    time         = device('nicos.devices.tango.AnalogInput',
                          description = 'XRay info time',
                          tangodevice = tango_base + 'XRayInfo/time',
                         ),
    interval     = device('nicos.devices.tango.AnalogInput',
                          description = 'XRay info intervall',
                          tangodevice = tango_base + 'XRayInfo/interval',
                         ),
    uptime       = device('nicos.devices.tango.AnalogInput',
                          description = 'XRay info uptime',
                          tangodevice = tango_base + 'XRayInfo/uptime',
                         ),
    stigmator    = device('nicos.devices.tango.AnalogInput',
                          description = 'XRay info stigmator',
                          tangodevice = tango_base + 'XRayInfo/stigmator',
                         ),
    vacuum       = device('nicos.devices.tango.AnalogInput',
                          description = 'XRay info stigmator',
                          tangodevice = tango_base + 'XRayInfo/vacuum',
                          fmtstr = '%.4g',
                         ),
    shutter      = device('nicos.devices.tango.NamedDigitalOutput',
                          description = 'XRayShutter',
                          tangodevice = tango_base + 'XRayShutter/1',
                          mapping = dict( open=1, close=2 ),
                         ),
    tubecond     = device('nicos_mlz.galaxi.devices.conditioner.TubeConditioner',
                          description = 'XRayTubeCondition',
                          tangodevice = tango_base + 'XRayTubeCond/1',
                          interval = 'interval',
                          time = 'time',
                          unit = '',
                         ),
)
