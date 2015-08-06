description = 'ANTARES garfield magnet'

group = 'plugplay'

includes = ['alias_B']

taco_host = setupname

devices = dict(
    amagnet_onoff = device('antares.switches.ToggleSwitch',
                      description = 'Garfield magnet: on/off switch',
                      tacodevice = '//%s/amagnet/beckhoff/onoff' % taco_host,
                      readback = '//%s/amagnet/beckhoff/honoff' % taco_host,
                      mapping = { 1 : 'on', 0 : 'off'},
                      lowlevel = True,
                     ),
    amagnet_polarity = device('antares.switches.ReadbackSwitch',
                      description = 'Garfield magnet: polarity (+/-) switch',
                      tacodevice = '//%s/amagnet/beckhoff/posneg' % taco_host,
                      readback = '//%s/amagnet/beckhoff/hpos' % taco_host,
                      mapping = { 1 : '+', 2 : '-'},
                      rwmapping = { 0 : 2 },
                      lowlevel = True,
                     ),
    amagnet_connection = device('antares.switches.ReadbackSwitch',
                      description = 'Garfield magnet: connection switch',
                      tacodevice = '//%s/amagnet/beckhoff/serpar' % taco_host,
                      readback = '//%s/amagnet/beckhoff/hpar' % taco_host,
                      mapping = { 1 : 'par', 2 : 'ser'},
                      rwmapping = { 0 : 2 },
                      #~ lowlevel = True,
                     ),
    #~ amagnet_temp1 = device('devices.taco.AnalogInput',
                         #~ description = 'Taco device for temperature 1',
                         #~ tacodevice = '//%s/amagnet/beckhoff/temp1' % taco_host,
                         #~ unit = 'K',
                        #~ ),
    #~ amagnet_temp2 = device('devices.taco.AnalogInput',
                         #~ description = 'Taco device for temperature 2',
                         #~ tacodevice = '//%s/amagnet/beckhoff/temp2' % taco_host,
                         #~ unit = 'K',
                        #~ ),

    #~ amagnet_temp3 = device('devices.taco.AnalogInput',
                         #~ description = 'Taco device for temperature 3',
                         #~ tacodevice = '//%s/amagnet/beckhoff/temp3' % taco_host,
                         #~ unit = 'K',
                        #~ ),

    #~ amagnet_temp4 = device('devices.taco.AnalogInput',
                         #~ description = 'Taco device for temperature 4',
                         #~ tacodevice = '//%s/amagnet/beckhoff/temp4' % taco_host,
                         #~ unit = 'K',
                        #~ ),
    amagnet_current = device('devices.taco.CurrentSupply',
                         description = 'Taco device for the magnet power supply (current mode)',
                         tacodevice = '//%s/amagnet/lambda/out' % taco_host,
                         unit = 'A',
                         abslimits = (0, 200),
                         lowlevel = True,
                        ),
    # by convention this needs to be B_%(setupname)s
    B_amagnet = device('frm2.magnet.GarfieldMagnet',
                         description = 'magnetic field device, handling polarity switching and stuff',
                         currentsource = 'amagnet_current',
                         onoffswitch = 'amagnet_onoff',
                         polswitch = 'amagnet_polarity',
                         unit = 'T',
                         # B(I) = c[0]*I + c[1]*erf(c[2]*I) + c[3]*atan(c[4]*I)
                         # 2014/02/10: calibration from 9002_00009120.dat .. 9002_00009122.dat
                         #~ calibration = (0.0018467, -0.0346142, 0.021774, 0.0638581, 0.0541159),
                         # 2014/09/11: calibration_garfield.dat from Sebastion M. (sans1)
                         calibration = (0.00186485, -0.0289753, -0.0587453, -0.0143078, -0.0399828),
                         userlimits = (-0.35, 0.35),
                        ),
)
alias_config = [
    ('B', 'B_amagnet', 100),
]
