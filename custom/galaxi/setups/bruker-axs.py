# -*- coding: utf-8 -*-

description = 'GALAXI Bruker AXS X-Ray'

group = 'basic'

includes = []

tango_host = 'tango://localhost:10000'
tango_url =  tango_host + '/galaxi/'

devices = dict(

    gen_voltage  = device('devices.tango.AnalogOutput',
                          description = 'XrayGenerator',
                          tangodevice = tango_url + 'XRayGenerator/voltage',
                          unit = 'kV',
                         ),
    gen_current  = device('devices.tango.AnalogOutput',
                          description = 'XrayGenerator',
                          tangodevice = tango_url + 'XRayGenerator/current',
                          unit = 'mA',
                         ),
    spotpos      = device('devices.tango.AnalogInput',
                          description = 'XRaySpotPosition',
                          tangodevice = tango_url + 'XRaySpotPos/1',
                         ),
    time         = device('devices.tango.AnalogInput',
                          description = 'XRay info time',
                          tangodevice = tango_url + 'XRayInfo/time',
                         ),
    interval     = device('devices.tango.AnalogInput',
                          description = 'XRay info intervall',
                          tangodevice = tango_url + 'XRayInfo/interval',
                         ),
    uptime       = device('devices.tango.AnalogInput',
                          description = 'XRay info uptime',
                          tangodevice = tango_url + 'XRayInfo/uptime',
                         ),
    stigmator    = device('devices.tango.AnalogInput',
                          description = 'XRay info stigmator',
                          tangodevice = tango_url + 'XRayInfo/stigmator',
                         ),
    vacuum       = device('devices.tango.AnalogInput',
                          description = 'XRay info stigmator',
                          tangodevice = tango_url + 'XRayInfo/vacuum',
                          fmtstr = '%.4g',
                         ),
    shutter      = device('devices.tango.NamedDigitalOutput',
                          description = 'XRayShutter',
                          tangodevice = tango_url + 'XRayShutter/1',
                          mapping = dict( open=1, close=2 ),
                         ),
    tubecond     = device('galaxi.conditioner.TubeConditioner',
                          description = 'XRayTubeCondition',
                          tangodevice = tango_url + 'XRayTubeCond/1',
                          interval = 'interval',
                          time = 'time',
                          unit = '',
                         ),
)

startupcode = '''
'''
