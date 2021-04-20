description = 'Temporary Cd-filter control'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'
tango_base_beckhoff = 'tango://antareshw.antares.frm2:10000/antares/beckhoff02/beckhoff02_'

devices = dict(

    In_beam_valve = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Opens valve for movement into the beam' ,
        tangodevice = tango_base_beckhoff + 'out5',
        mapping = dict(On = 1, Off = 0),
    ),    

    Out_beam_valve = device('nicos.devices.entangle.NamedDigitalOutput',
        description = 'Opens valve for movement out of the beam' ,
        tangodevice = tango_base_beckhoff + 'out6',
        mapping = dict(On = 1, Off = 0),
    ),                       
        
)
