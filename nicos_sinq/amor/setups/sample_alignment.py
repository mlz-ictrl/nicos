description = 'Sample devices in the SINQ AMOR.'

display_order = 50

pvprefix = 'SQ:AMOR:masterMacs1:'

includes = ['base', 'sample_stage']

devices = dict(
    sample_height = device('nicos.core.device.DeviceAlias',
                           description = 'adjust sample z-position',
                           alias = 'szoffset',
                           devclass = 'nicos.core.device.Moveable',
                           ),
    sample_tilt = device('nicos.devices.generic.ParamDevice',
                         description = 'adjust sample rotation in beam direction',
                         device = 'base_defs',
                         parameter = 'sampletilt',
                         copy_status = True,
                         fmtstr = '%6.3f',
                         unit = 'deg',
                         ),
    sample_roll = device('nicos_sinq.devices.epics.motor.SinqMotor',
                         description = 'adjust sample rotation normal to beam direction',
                         motorpv = pvprefix + 'sch',
                         fmtstr = '%6.1f',
                         unit = 'deg',
                         ),
    #sample_azimut = device('nicos_sinq.devices.epics.motor.SinqMotor',
    #                       description = 'Sample phi rotation',
    #                       motorpv = pvprefix + 'sph',
    #                       visibility = (),
    #                       ),
    sah = device('nicos.core.device.DeviceAlias',
                 description = 'adjust sample z-position',
                 devclass = 'nicos.core.device.Moveable',
                 alias = 'szoffset',
                 visibility = ('metadata', 'namespace'),
                 ),
    sat = device('nicos.core.device.DeviceAlias',
                 description = 'adjust sample rotation in beam direction',
                 devclass = 'nicos.core.device.Moveable',
                 alias = 'sample_tilt',
                 visibility = ('metadata', 'namespace'),
                 ),
    sar = device('nicos.core.device.DeviceAlias',
                 description = 'adjust sample rotation normal to beam direction',
                 devclass = 'nicos.core.device.Moveable',
                 alias = 'sample_roll',
                 visibility = ('metadata', 'namespace'),
                 ),
)

alias_config = {
    #'sah': {'sample_height': 90},
    'sat': {'sample_tilt': 10},
    #'sar': {'sample_roll': 10},
}
