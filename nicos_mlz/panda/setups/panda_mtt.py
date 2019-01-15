# -*- coding: utf-8 -*-

description = 'setup for Beckhoff PLC mtt devices on PANDA'

group = 'lowlevel'

tango_base = 'tango://phys.panda.frm2:10000/panda/'
plc = tango_base + 'beckhoff_mtt/plc_'

devices = dict(
    diagnostics = device('nicos.devices.tango.DigitalInput',
        description = 'Status of all position switches.',
        tangodevice = plc + 'diagnostics',
        lowlevel = True,
        fmtstr = '%#x',
        unit = '',
    ),
    diag_automove = device('nicos.devices.tango.DigitalInput',
        description = 'Diagnostic information for function block '
        '"MTT_Auto_Move".',
        tangodevice = plc + 'diag_automove',
        lowlevel = True,
        fmtstr = '%#x',
        unit = '',
    ),
    diag_bccw = device('nicos.devices.tango.DigitalInput',
        description = 'Diagnostic information for function block '
        '"MB_WECHSEL_TO_CCW".',
        tangodevice = plc + 'diag_bccw',
        lowlevel = True,
        fmtstr = '%#x',
        unit = '',
    ),
    diag_bcw = device('nicos.devices.tango.DigitalInput',
        description = 'Diagnostic information for function block '
        '"MB_WECHSEL_TO_CW".',
        tangodevice = plc + 'diag_bcw',
        lowlevel = True,
        fmtstr = '%#x',
        unit = '',
    ),
    diag_switches = device('nicos.devices.tango.DigitalInput',
        description = 'Status of all limit and reference switches.',
        tangodevice = plc + 'diag_switches',
        lowlevel = True,
        fmtstr = '%#x',
        unit = '',
    ),
    klinke_ccw = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Device for the movement of the pressed air actuator '
        'opening "Klinke CCW".',
        tangodevice = plc + 'klinke_ccw',
        lowlevel = True,
        fmtstr = '%d',
        unit = '',
        mapping = {'off': 0, 'on': 1},
    ),
    klinke_cw = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Device for the movement of the pressed air actuator '
        'opening "Klinke CW".',
        tangodevice = plc + 'klinke_cw',
        lowlevel = True,
        fmtstr = '%d',
        unit = '',
        mapping = {'off': 0, 'on': 1},
    ),
    max_ref_angle = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Maximum absolute value of the angle that is used for '
        'the block gap search algorithm during MTT referencing in CW direction.',
        tangodevice = plc + 'max_ref_angle',
        lowlevel = True,
        fmtstr = '%d',
        unit = '',
        mapping = {'off': 0, 'on': 1},
    ),
    mb_arm_magnet = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Device for switching the magnet in the mobile arm on '
        'and off.',
        tangodevice = plc + 'mb_arm_magnet',
        lowlevel = True,
        fmtstr = '%d',
        unit = '',
        mapping = {'off': 0, 'on': 1},
    ),
    mb_arm_raw = device('nicos.devices.tango.Motor',
        description = 'Mobile arm axis "MB_ARM".',
        tangodevice = plc + 'mb_arm_raw',
        lowlevel = True,
    ),
    mb_arm_inc_encoder = device('nicos.devices.tango.Sensor',
        description = 'Normalized value of the "MB_ARM" axis incremental '
        'encoder.',
        tangodevice = plc + 'mbarmincencoder',
        lowlevel = True,
        unit = 'steps',
    ),
    mb_arm_error = device('nicos.devices.tango.DigitalInput',
        description = 'Beckhoff error code for axis "MB_ARM".',
        tangodevice = plc + 'diag_arm_err',
        lowlevel = True,
        fmtstr = '%#x',
        unit = '',
    ),
    mtt = device('nicos_mlz.panda.devices.debug.InvertablePollMotor',
        description = 'Virtual MTT axis that exchanges block automatically '
                      '(must be used in "automatic" mode).',
        tangodevice = plc + 'mtt',
        unit = 'deg',
        invert = False,
        polldevs = [
            "diagnostics", "diag_switches",
            "mb_arm_magnet", "mb_arm_raw",
        ],
    ),
    mtt_abs_encoder = device('nicos.devices.tango.Sensor',
        description = 'Normalized value of the "MTT_RAW" axis absolute '
        'encoder.',
        tangodevice = plc + 'mttabsencoder',
        unit = 'steps',
    ),
    mtt_inc_encoder = device('nicos.devices.tango.Sensor',
        description = 'Normalized value of the "MTT_RAW" axis incremental '
        'encoder.',
        tangodevice = plc + 'mttincencoder',
        lowlevel = True,
        unit = 'steps',
    ),
    mtt_err = device('nicos.devices.tango.DigitalInput',
        description = 'Beckhoff error code for axis "MTT_RAW".',
        tangodevice = plc + 'diag_mtt_err',
        lowlevel = True,
        fmtstr = '%#x',
        unit = '',
    ),
    mtt_raw = device('nicos.devices.tango.Motor',
        description = 'Raw MTT axis without automatic block exchange (must be '
        ' used in manual mode).',
        tangodevice = plc + 'mtt_raw',
        lowlevel = True,
        unit = 'deg',
    ),
    n_blocks_cw = device('nicos.devices.tango.DigitalOutput',
        description = 'Number of blocks on the CW side of the block gap '
        '(channel for the incoming beam).',
        tangodevice = plc + 'n_blocks_cw',
        lowlevel = True,
        fmtstr = '%d',
        unit = 'blocks',
    ),
    opmode = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'Current MTT operational mode.',
        tangodevice = plc + 'opmode',
        requires = {'level': 'admin'},
        lowlevel = True,
        fmtstr = '%d',
        unit = '',
        mapping = {
            'automatic mode': 0,
            'manual mode': 1,
            'radiant leak allowed': 2,
        },
    ),
)

startupcode = '''
CreateDevice('diagnostics')
CreateDevice('diag_automove')
CreateDevice('diag_bccw')
CreateDevice('diag_bcw')
CreateDevice('diag_switches')
CreateDevice('klinke_ccw')
CreateDevice('klinke_cw')
CreateDevice('max_ref_angle')
CreateDevice('mb_arm_magnet')
CreateDevice('mb_arm_raw')
CreateDevice('mb_arm_error')
CreateDevice('mb_arm_inc_encoder')
CreateDevice('mtt_inc_encoder')
CreateDevice('mtt_err')
CreateDevice('mtt_raw')
CreateDevice('n_blocks_cw')
CreateDevice('opmode')
'''
