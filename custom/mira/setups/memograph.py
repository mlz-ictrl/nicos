description = 'memograph (cooling system) readout'
group = 'lowlevel'

devices = dict(
    FAKTemp   = device('frm2.memograph.MemographValue',
                       description = 'Temperature of FAK40 water at inlet to SANS-1',
                       hostname = 'memograph03.care.frm2',
                       group = 2,
                       valuename = 'T_in SANS1',
                       unit = 'degC',
                      ),
)
