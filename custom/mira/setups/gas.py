description = 'Gas flow for the (Cascade) PSD detector'
group = 'lowlevel'

includes = []

tango_host = 'tango://mira1.mira.frm2:10000'

devices = dict(
    ar = device('devices.tango.AnalogOutput',
                description = 'Ar gas flow through the detector',
                tangodevice = '%s/mira/gasmix/arflow' % tango_host,
                abslimits = (0, 250),
                userlimits = (0, 250),
                unit = 'mln/min',
               ),
    ar_temp = device('devices.tango.Sensor',
                     description = 'Ar gas temperature (through the detector)',
                     tangodevice = '%s/mira/gasmix/artemp' % tango_host,
                     unit = 'C',
                    ),

    co2 = device('devices.tango.AnalogOutput',
                 description = 'CO2 gas flow through the detector',
                 tangodevice = '%s/mira/gasmix/co2flow' % tango_host,
                 abslimits = (0, 50),
                 userlimits = (0, 50),
                 unit = 'mln/min',
                ),
    co2_temp = device('devices.tango.Sensor',
                      description = 'CO2 gas temperature (through the detector)',
                      tangodevice = '%s/mira/gasmix/co2temp' % tango_host,
                      unit = 'C',
                     ),
)
