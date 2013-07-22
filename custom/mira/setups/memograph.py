description = 'memograph (cooling system) readout'
group = 'lowlevel'

devices = dict(
    FAKTemp   = device('frm2.memograph.MemographValue',
                       hostname = 'memograph03.care.frm2',
                       group = 2,
                       valuename = 'T_in SANS-1',
                       unit = 'degC'),
)
