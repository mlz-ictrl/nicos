description = 'memograph02 readout'

includes = []

group = 'lowlevel'

memograph_host = '%s.care.frm2' % setupname

devices = {
    'tap02_t_in':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'T_in RESEDA1',
            description = 'inlet temperature memograph',
            fmtstr = '%.2F',
            warnlimits = (-1, 17.5),  #-1 no lower value
        ),
    'tap02_t_out':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'T_out RESEDA1',
            description = 'outlet temperature memograph',
            fmtstr = '%.2F',
        ),
    'tap02_p_in':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'P_in RESEDA1',
            description = 'inlet pressure memograph',
            fmtstr = '%.2F',
        ),
    'tap02_p_out':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'P_out RESEDA1',
            description = 'outlet pressure memograph',
            fmtstr = '%.2F',
        ),
    'tap02_flow_in':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'FLOW_in RESEDA1',
            description = 'inlet flow memograph',
            fmtstr = '%.2F',
            warnlimits = (0.2, 100),  #100 no upper value
        ),
    'tap02_flow_out':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'FLOW_out RESEDA1',
            description = 'outlet flow memograph',
            fmtstr = '%.2F',
        ),
    'tap02_leak':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'Leak RESEDA1',
            description = 'leakage memograph',
            fmtstr = '%.2F',
            warnlimits = (-1, 1),  #-1 no lower value
        ),
    'tap02_cooling':
        device('frm2.memograph.MemographValue',
            hostname = memograph_host,
            group = 3,
            valuename = 'Cooling RESEDA1',
            description = 'cooling memograph',
            fmtstr = '%.2F',
        ),
}
