description = 'Be filter control'

group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/'

excludes = ['virtual_filter']

devices = dict(
    be_filter   = device('devices.tango.NamedDigitalOutput',
                         description = 'Beryllium filter',
                         tangodevice = tango_base + 'FZJDP_Digital/BeFilter',
                         mapping = {
                            "in" : 1,
                            "out": 0,
                         }
                        ),
    be_heater   = device('devices.tango.NamedDigitalOutput',
                         description = 'Beryllium heater',
                         tangodevice = tango_base + 'FZJDP_Digital/BeHeater',
                         mapping = {
                            "off" : 0,
                            "on"  : 1,
                         }
                        ),
    T_be_filter = device('devices.tango.AnalogInput',
                         description = 'Beryllium filter/crystal temperature',
                         tangodevice = tango_base + 'FZJDP_Analog/TBeFilter',
                         fmtstr = '%.0f',
                         unit = 'K',
                         pollinterval = 5,
                         maxage = 6,
                        ),
    T_be_heater = device('devices.tango.AnalogInput',
                         description = 'Beryllium heater temperature',
                         tangodevice = tango_base + 'FZJDP_Analog/TBeHeater',
                         fmtstr = '%.0f',
                         unit = 'K',
                         pollinterval = 5,
                         maxage = 6,
                        ),
)
