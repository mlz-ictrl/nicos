description = 'setup for the status monitor'
group = 'special'

ccm8v = SetupBlock('ccm8v', 'se')

ccm8vplot = Block('ccm8v', [
    BlockRow(Field(plot='ccm8v', name='B', key='se/b_ccm8v/value',
                   plotwindow=3600, width=50, height=40),
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
        expectmaster = False,
        filename = '/WebServer/jcnswww.jcns.frm2/httpdocs/monitor/jcnsmon01'
                   '.html',
        noexpired = True,
    ),
)

extended = dict(
    dont_check_devicenames = True,
)
