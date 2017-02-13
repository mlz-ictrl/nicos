description = 'memograph04 readout'

includes = []

group = 'lowlevel'

memograph_host = '%s.care.frm2' % setupname

devices = {
    'tap04_t_ing':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'T_in RESEDA2',
            description = 'inlet temperature memograph',
            fmtstr = '%.2F',
            warnlimits = (-1, 17.5),  #-1 no lower value
        ),
    'tap04_t_outg':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'T_out RESEDA2',
            description = 'outlet temperature memograph',
            fmtstr = '%.2F',
        ),
    'tap04_p_ing':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'P_in RESEDA2',
            description = 'inlet pressure memograph',
            fmtstr = '%.2F',
        ),
    'tap04_p_outg':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'P_out RESEDA2',
            description = 'outlet pressure memograph',
            fmtstr = '%.2F',
        ),
    'tap04_flow_ing':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'FLOW_in RESEDA2',
            description = 'inlet flow memograph',
            fmtstr = '%.2F',
            warnlimits = (0.2, 100),  #100 no upper value
        ),
    'tap04_flow_outg':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'FLOW_out RESEDA2',
            description = 'outlet flow memograph',
            fmtstr = '%.2F',
        ),
    'tap04_leakg':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'Leak RESEDA2',
            description = 'leakage memograph',
            fmtstr = '%.2F',
            warnlimits = (-1, 1),  #-1 no lower value
        ),
    'tap04_coolingg':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'Cooling RESEDA2',
            description = 'cooling memograph',
            fmtstr = '%.2F',
        ),
}
