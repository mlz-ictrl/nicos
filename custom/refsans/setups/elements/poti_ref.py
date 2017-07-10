description = 'reference values for the encoder potiometers'

group = 'lowlevel'

nethost = 'refsanssrv.refsans.frm2'
tacodev = '//%s/test' % nethost

devices = dict(
    wegbox_A_1ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_A_1ref',
                           tacodevice = '%s/WB_A/1_6' % tacodev,
                          ),
    wegbox_A_2ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_A_2ref',
                           tacodevice = '%s/WB_A/2_6' % tacodev,
                          ),
    wegbox_B_1ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_B_1ref',
                           tacodevice = '%s/WB_B/1_6' % tacodev,
                          ),
    wegbox_B_2ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_B_2ref',
                           tacodevice = '%s/WB_B/2_6' % tacodev,
                          ),
    wegbox_C_1ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_C_1ref',
                           tacodevice = '%s/WB_C/1_6' % tacodev,
                          ),
    wegbox_C_2ref = device('nicos.devices.taco.AnalogInput',
                           description = 'wegbox_C_2ref',
                           tacodevice = '%s/WB_C/2_6' % tacodev,
                          ),
)
