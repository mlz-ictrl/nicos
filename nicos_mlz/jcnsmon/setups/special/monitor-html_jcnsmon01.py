description = 'setup for the status monitor'
group = 'special'

ccm8v = Block('8T Oxford magnet (ccm8v)', [
    BlockRow(Field(name='Field', dev='se/b_ccm8v'),
             Field(name='Hall', dev='se/ccm8v_bhall')),
    '---',
    BlockRow(Field(name='VTI', dev='se/t_ccm8v_vti'),
             Field(name='VTI heat', dev='se/t_ccm8v_vti_heater'),
             Field(name='VTI NV', dev='se/t_ccm8v_vti_nv')),
    BlockRow(Field(name='Stick', dev='se/t_ccm8v_stick'),
             Field(name='Stick heat', dev='se/t_ccm8v_stick_heater')),
    '---',
    BlockRow(Field(name='Coils', dev='se/ccm8v_tmag'),
             Field(name='Dewar', dev='se/ccm8v_pdewar'),
             Field(name='Coldhead', dev='se/ccm8v_tcoldhead')),
    BlockRow(Field(name='LHe', dev='se/ccm8v_lhe'),
             Field(name='LN2', dev='se/ccm8v_ln2')),
])

ccm8vplot = Block('ccm8v', [
    BlockRow(Field(plot='ccm8v', name='B', key='se/b_ccm8v/value', plotwindow=3600, width=50, height=40),
             Field(plot='ccm8v', name='LHe', key='se/ccm8v_lhe/value'),
             Field(plot='ccm8v', name='LN2', key='se/ccm8v_ln2/value')),
])

layout = [
    Row(Column(ccm8v, ccm8vplot)),
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
        expectmain = False,
        filename = '/WebServer/jcnswww.jcns.frm2/httpdocs/monitor/jcnsmon01'
                   '.html',
        noexpired = True,
    ),
)
