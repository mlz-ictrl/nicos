# -*- coding: utf-8 -*-

description = 'SIS detector setup'

group = 'lowlevel'

includes = ['shutter', 'cct6', 'doppler']

sysconfig = dict(datasinks = ['sisasink', 'sisusink', 'sislive'])

tangohost = 'phys.spheres.frm2'
sis = 'tango://%s:10000/spheres/sis/' % tangohost

basename = '%(proposal)s_%(session.experiment.sample.filename)s_'

devices = dict(
    sis = device('nicos_mlz.spheres.devices.sisdetector.SISDetector',
        description = 'detector',
        timers = ['sistimer'],
        images = ['sisimg'],
        shutter = 'shutter',
        liveinterval = 1.,
        autoshutter = True,
        saveintervals = [60, 100, 140, 300],
    ),
    sisimg = device('nicos_mlz.spheres.devices.sisdetector.SISChannel',
        description = 'SIS detector',
        tangodevice = sis + 'counter',
        analyzers = 'Si111',
        monochromator = 'Si111',
        incremental = False,
    ),
    sisasink = device('nicos_mlz.spheres.devices.sissinks.AFileSink',
        description = 'DataSink which writes raw data',
        detectors = ['sis'],
        subdir = 'raw',
        filenametemplate = [basename + '%(scancounter)da%(pointnumber)d',
                            basename + 'a%(pointpropcounter)'],
    ),
    sisusink = device('nicos_mlz.spheres.devices.sissinks.UFileSink',
        description = 'DataSink which writes user data',
        detectors = ['sis'],
        subdir = 'user',
        filenametemplate = [basename + '%(scancounter)du%(pointnumber)d',
                            basename + 'u%(pointpropcounter)'],
        setpointdev = 'setpoint',
        envcontroller = 'c_temperature',
    ),
    sislive = device('nicos_mlz.spheres.devices.sissinks.PreviewSink',
        description = 'Sends image data to LiveViewWidget',
        detectors = ['sis'],
    ),
    flux = device('nicos_mlz.spheres.devices.flux.Flux',
        description = 'Device which stores averages of the regular detectors '
                      'of direct, elastic and inelastic flux',
        tangodevice = sis + 'counter',
        lowlevel = True,
    ),
    sistimer = device('nicos.devices.tango.TimerChannel',
        description='Timer for the SIS detector',
        tangodevice=sis + 'timer',
    ),
)
