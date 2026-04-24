description = 'Sample devices in the SINQ AMOR.'

display_order = 50

pvprefix = 'SQ:AMOR:masterMacs1:'

includes = ['base', 'sample_stage']

devices = dict(
    sample_height = device('nicos.core.device.DeviceAlias',
                           description = 'adjust sample z-position',
                           devclass = 'nicos.core.device.Moveable',
                           alias = 's_zoffset',
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
                         valid_pos_after_reference = True,
                         ),
    #sample_azimut = device('nicos_sinq.devices.epics.motor.SinqMotor',
    #                       description = 'Sample phi rotation',
    #                       motorpv = pvprefix + 'sph',
    #                       visibility = (),
    #                       ),
    sah = device('nicos.core.device.DeviceAlias',
                 description = 'adjust sample z-position',
                 devclass = 'nicos.core.device.Moveable',
                 visibility = ('metadata', 'namespace'),
                 alias = 's_zoffset',
                 ),
    sat = device('nicos.core.device.DeviceAlias',
                 description = 'adjust sample rotation in beam direction',
                 devclass = 'nicos.core.device.Moveable',
                 visibility = ('metadata', 'namespace'),
                 ),
    sar = device('nicos.core.device.DeviceAlias',
                 description = 'adjust sample rotation normal to beam direction',
                 devclass = 'nicos.core.device.Moveable',
                 visibility = ('metadata', 'namespace'),
                 ),
)

alias_config = {
        'sat': {'sample_tilt': 10},
        'sar': {'sample_roll': 10},
    }
