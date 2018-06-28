description = 'setup for the status monitor'
group = 'special'

jvm2 = Block('8T Oxford magnet (jvm2)', [
    BlockRow(Field(name='Field', dev='se/b_jvm2'),
             Field(name='Hall', dev='se/jvm2_bhall')),
    '---',
    BlockRow(Field(name='VTI', dev='se/t_jvm2_vti'),
             Field(name='VTI heat', dev='se/t_jvm2_vti_heater'),
             Field(name='VTI NV', dev='se/t_jvm2_vti_nv')),
    BlockRow(Field(name='Stick', dev='se/t_jvm2_stick'),
             Field(name='Stick heat', dev='se/t_jvm2_stick_heater')),
    '---',
    BlockRow(Field(name='Coils', dev='se/jvm2_tmag'),
             Field(name='Dewar', dev='se/jvm2_pdewar'),
             Field(name='Coldhead', dev='se/jvm2_tcoldhead')),
    BlockRow(Field(name='LHe', dev='se/jvm2_lhe'),
             Field(name='LN2', dev='se/jvm2_ln2')),
])

jvm2plot = Block('jvm2', [
    BlockRow(Field(plot='jvm2', name='B', key='se/b_jvm2/value', plotwindow=3600, width=50, height=40),
             Field(plot='jvm2', name='LHe', key='se/jvm2_lhe/value'),
             Field(plot='jvm2', name='LN2', key='se/jvm2_ln2/value')),
])

layout = [
    Row(Column(jvm2, jvm2plot)),
]


devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'JCNS SE monitor 1',
        loglevel = 'info',
        cache = 'jcnsmon.jcns.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 14,
        padding = 3,
        layout = layout,
        expectmaster = False,
        filename = '/WebServer/jcnswww.jcns.frm2/httpdocs/monitor/jcnsmon01'
                   '.html',
    ),
)
