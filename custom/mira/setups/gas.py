description = 'Gas flow for the (Cascade) PSD detector'
group = 'optional'

includes = []

nethost = 'mirasrv.mira.frm2'

devices = dict(
    ar = device('devices.taco.io.AnalogOutput',
                description = 'Ar gas flow through the detector',
                tacodevice = '//%s/mira/redy/ar' % nethost,
                abslimits = (0, 100),
                userlimits = (0, 100),
                unit = 'mln/min',
               ),
    ar_temp = device('devices.taco.temperature.TemperatureSensor',
                     description = 'Ar gas temperature (through the detector)',
                     tacodevice = '//%s/mira/redy/artemp' % nethost,
                     unit = 'C',
                    ),

    co2 = device('devices.taco.io.AnalogOutput',
                 description = 'CO2 gas flow through the detector',
                 tacodevice = '//%s/mira/redy/co2' % nethost,
                 abslimits = (0, 50),
                 userlimits = (0, 50),
                 unit = 'mln/min',
                ),
    co2_temp = device('devices.taco.temperature.TemperatureSensor',
                      description = 'CO2 gas temperature (through the detector)',
                      tacodevice = '//%s/mira/redy/co2temp' % nethost,
                      unit = 'C',
                     ),
)
