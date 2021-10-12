description = 'setup for the status monitor'
group = 'special'

instrs = sorted(['BioDiff', 'DNS', 'Panda', 'JNSE', 'KWS1', 'KWS2', 'KWS3',
                 'Poli', 'Maria', 'Treff', 'Spheres'])

blocks = []
plotfields = []
for instr in instrs:
    key = instr.lower() + '/cooling_'
    blocks.append(Block('Cooling %s' % instr, [
        BlockRow(Field(name='T_in', dev=key + 't_in'),
                 Field(name='T_out', dev=key + 't_out'),
                 Field(name='P_in', dev=key + 'p_in'),
                 Field(name='P_out', dev=key + 'p_out'),
                 Field(name='flow_in', dev=key + 'flow_in'),
                 Field(name='flow_out', dev=key + 'flow_out'),
                 Field(name='power', dev=key + 'power'),
                 ),
    ]))

    plotfields.append(Field(plot='temp', name=instr + ' in', key=key + 't_in/value'))
    plotfields.append(Field(plot='temp', name=instr + ' out', key=key + 't_out/value'))

plotfields[0]._options['plotwindow'] = 24*3600
plotfields[0]._options['width'] = 50
plotfields[0]._options['height'] = 40

plot = Block('Temperatures', [
    BlockRow(*plotfields)
])

layout = [
    Row(Column(*blocks), Column(plot)),
]


devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'JCNS Memograph monitor',
        loglevel = 'info',
        cache = 'jcnsmon.jcns.frm2',
        font = 'Droid Sans',
        valuefont = 'Droid Sans Mono',
        fontsize = 14,
        padding = 3,
        layout = layout,
        expectmaster = False,
        filename = '/WebServer/jcnswww.jcns.frm2/httpdocs/monitor/memograph.html',
        noexpired = False,
    ),
)
