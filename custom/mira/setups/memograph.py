description = 'memograph (cooling system) readout'
group = 'lowlevel'

devices = dict(
    FAKTemp   = device('frm2.memograph.MemographValue',
                       description = 'Temperature of FAK40 water at inlet to SANS-1',
                       hostname = 'memograph02.care.frm2',
                       group = 1,
                       valuename = 'T_in MIRA',
                       unit = 'degC',
                      ),
)
