# -*- coding: utf-8 -*-
description = 'ANTARES Pilz security system states'

group = 'optional'

includes = []

tango_base = 'tango://slow.antares.frm2:10000/antares/'

devices = dict(
    emergency_io = device('devices.tango.DigitalInput',
                          description = 'Tango device for Emergency readout',
                          tangodevice = tango_base + 'fzjdp_digital/PilzEmergencyStop',
                          lowlevel = True,
                         ),
    emergency = device('devices.generic.ReadonlySwitcher',
                       description = 'Emergency readout',
                       readable = 'emergency_io',
                       mapping = dict(zip([', '.join(
                                ['Emergency stop %d pressed'
                                    % k for k in range(1,6) if v&(2**(k-1))])
                                           or 'ok'
                                for v in range(32)],range(32))),
                       precision = 0,
                      ),

    # searchbuttons
    tourbutton1_io = device('devices.tango.DigitalInput',
                            description = 'Tango device for Tourbutton1',
                            tangodevice = tango_base + 'fzjdp_digital/PilzSecTourButton1',
                            lowlevel = True,
                           ),
    tourbutton1 = device('devices.generic.ReadonlySwitcher',
                         description = 'Tourbutton1',
                         readable = 'tourbutton1_io',
                         mapping = dict(unpressed=1, pressed=0),
                         precision = 0,
                        ),

    tourbutton2_io = device('devices.tango.DigitalInput',
                            description = 'Tango device for Tourbutton2',
                            tangodevice = tango_base + 'fzjdp_digital/PilzSecTourButton2',
                            lowlevel = True,
                           ),
    tourbutton2 = device('devices.generic.ReadonlySwitcher',
                         description = 'Tourbutton2',
                         readable = 'tourbutton2_io',
                         mapping = dict(unpressed=1, pressed=0),
                         precision = 0,
                        ),

    tourbutton3_io = device('devices.tango.DigitalInput',
                            description = 'Tango device for Tourbutton3',
                            tangodevice = tango_base + 'fzjdp_digital/PilzSecTourButton3',
                            lowlevel = True,
                           ),
    tourbutton3 = device('devices.generic.ReadonlySwitcher',
                         description = 'Tourbutton3',
                         readable = 'tourbutton3_io',
                         mapping = dict(unpressed=1, pressed=0),
                         precision = 0,
                        ),

    # door state
    door_rot_io = device('devices.tango.DigitalInput',
                         description = 'Tango device for Rotating door',
                         tangodevice = tango_base + 'fzjdp_digital/PilzDoorRot',
                         lowlevel = True,
                        ),
    door_rot = device('devices.generic.ReadonlySwitcher',
                      description = 'Rotating door',
                      readable = 'door_rot_io',
                      mapping = dict(closed=1, open=0),
                      precision = 0,
                     ),

    door_slide_io = device('devices.tango.DigitalInput',
                           description = 'Tango device for Sliding door',
                           tangodevice = tango_base + 'fzjdp_digital/PilzDoorSlide',
                           lowlevel = True,
                          ),
    door_slide = device('devices.generic.ReadonlySwitcher',
                        description = 'Sliding door',
                        readable = 'door_slide_io',
                        mapping = dict(closed=1, open=0),
                        precision = 0,
                       ),

    pilz_state_io = device('devices.tango.DigitalInput',
                           description = 'Tango device for Pilz state',
                           tangodevice = tango_base + 'fzjdp_digital/PilzFailure',
                           lowlevel = True,
                          ),
    pilz_state = device('devices.generic.ReadonlySwitcher',
                        description = 'Pilz state',
                        readable = 'pilz_state_io',
                        mapping = dict(ok=0, failure=1),
                        precision = 0,
                       ),
)


startupcode = '''
'''
