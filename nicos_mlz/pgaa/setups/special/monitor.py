description = 'setup for the status monitor for PGAA'
group = 'special'

_pgaageneral = Column(
    Block('General', [
        BlockRow(
                 Field(name='Reactor', dev='ReactorPower', width=8),
                 Field(name='6 Fold Shutter', dev='Sixfold', width=8),
                 Field(name='NL4b', dev='NL4b', width=8),
#               ),
#       BlockRow(
#                Field(name='T in', dev='t_in_memograph', width=8, unit='C'),
#                Field(name='T out', dev='t_out_memograph', width=8, unit='C'),
#                Field(name='Cooling', dev='cooling_memograph', width=8, unit='kW'),
#               ),
#       BlockRow(
#                Field(name='Flow in', dev='flow_in_memograph', width=8, unit='l/min'),
#                Field(name='Flow out', dev='flow_out_memograph', width=8, unit='l/min'),
#                Field(name='Leakage', dev='leak_memograph', width=8, unit='l/min'),
#               ),
#       BlockRow(
#                Field(name='P in', dev='p_in_memograph', width=8, unit='bar'),
#                Field(name='P out', dev='p_out_memograph', width=8, unit='bar'),
                 Field(name='Crane Pos', dev='Crane', width=8),
                ),
        ],
    ),
)

_pressuresample = Column(
    Block('Sample ', [
        BlockRow(
            Field(name='Vacuum', dev='chamber_pressure'),
            ),
        ],  # setups = '',
    )
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'PGAA status monitor',
        loglevel = 'info',
        cache = 'tequila.pgaa.frm2',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 16,
        padding = 5,
        layout = [
                  Row(_pgaageneral),
                  Row(_pressuresample,),
                 ],
    ),
)
