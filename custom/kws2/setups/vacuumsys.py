description = 'vacuum system monitoring'

group = 'lowlevel'

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    pressure_p20 =  device('devices.tango.Sensor',
                           description = 'pressure at pump 21',
                           tangodevice = tango_base + 'FZJDP_Analog/pressure_p20',
                           unit = 'mbar',
                           fmtstr = '%.1e',
                           lowlevel = True,
                          ),

    pressure_p21 =  device('devices.tango.Sensor',
                           description = 'pressure in collimation container',
                           tangodevice = tango_base + 'FZJDP_Analog/pressure_p21',
                           unit = 'mbar',
                           fmtstr = '%.1e',
                           lowlevel = True,
                          ),

    pressure_p22 =  device('devices.tango.Sensor',
                           description = 'pressure in sample chamber',
                           tangodevice = tango_base + 'FZJDP_Analog/pressure_p22',
                           unit = 'mbar',
                           fmtstr = '%.1e',
                           lowlevel = True,
                          ),

    pressure_p23 =  device('devices.tango.Sensor',
                           description = 'pressure in detector tube',
                           tangodevice = tango_base + 'FZJDP_Analog/pressure_p23',
                           unit = 'mbar',
                           fmtstr = '%.1e',
                           lowlevel = True,
                          ),

    pressure_p24 =  device('devices.tango.Sensor',
                           description = 'pressure in chopper housing',
                           tangodevice = tango_base + 'FZJDP_Analog/pressure_p24',
                           unit = 'mbar',
                           fmtstr = '%.1e',
                           lowlevel = True,
                          ),

    pressure_p25 =  device('devices.tango.Sensor',
                           description = 'pressure in lens chamber',
                           tangodevice = tango_base + 'FZJDP_Analog/pressure_p25',
                           unit = 'mbar',
                           fmtstr = '%.1e',
                           lowlevel = True,
                          ),

    pressure_p26 =  device('devices.tango.Sensor',
                           description = 'pressure in collimation container',
                           tangodevice = tango_base + 'FZJDP_Analog/pressure_p26',
                           unit = 'mbar',
                           fmtstr = '%.1e',
                           lowlevel = True,
                          ),
)
