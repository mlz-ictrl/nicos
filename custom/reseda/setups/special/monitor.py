description = 'RESEDA status monitor'

group = 'special'

Row = Column = Block = BlockRow = lambda *args: args
Field = lambda *args, **kwds: args or kwds

_expcolumn = Column(
##    Block('RESEDA Experiment', [
##        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
##                 Field(name='Title',    key='exp/title',    width=20,
##                       istext=True, maxlen=20),
##                 Field(name='Current status', key='exp/action', width=30,
##                       istext=True),
##                 Field(name='Last file', key='filesink/lastfilenumber'))]),
)

_motorblock = Block(
    'Motors',
    [BlockRow(Field(name='M1', dev='m1', unit='Deg'),
              Field(name='M2', dev='m2', unit='Deg'),
              Field(name='M3', dev='m3', unit='mm'),
              Field(name='M4', dev='m4', unit='mm'),
             ),
     BlockRow(Field(name='M5', dev='m5', unit='Deg'),
              Field(name='M6', dev='m6', unit='Deg'),
              Field(name='M7', dev='m7', unit='Deg'),
             ),
    ],
    'motors')

_frequenciesblock = Block(
    'Frequencies',
    [BlockRow(Field(name='F0', dev='F0', unit='Hz', width=8, format="%.0f"),
              Field(name='F1', dev='F1', unit='Hz', width=8, format="%.0f"),
              Field(name='F2', dev='F2', unit='Hz', width=8, format="%.0f"),
              Field(name='RF0', dev='RF0', unit='V', width=8),
              Field(name='RF1', dev='RF1', unit='V', width=8),
              Field(name='RF2', dev='RF2', unit='V', width=8),
             ),
    ],
    'frequencies')


_tempblock = Block(
    'Temperature',
    [BlockRow(Field(key='t/setpoint', name='Setpoint'),
              Field(name='TA', dev='TA', unit='K'),
              Field(name='TB', dev='TB', unit='K'),
              Field(name='TC', dev='TC', unit='K'),
              Field(name='TD', dev='TD', unit='K'),
             ),
     BlockRow(Field(dev='TA', plot='TA', interval=300, width=50),
              # Field(key='t/setpoint', name='SetP', plot='TA', interval=300),
             ),

     BlockRow(Field(dev='TD', plot='TD', interval=300, width=50),
             )
    ],
    'temperature')

_currentblock = Block(
    'Current',
    [BlockRow(Field(name='B0', dev='B01', unit='A', width=10),
              Field(name='B0', dev='B02', unit='V', width=10),
              Field(name='B2', dev='B21', unit='A', width=10),
              Field(name='B2', dev='B22', unit='V', width=10),
             ),
    ],
    'powersupply')

_powersupplyblock = Block(
    'Power Supply',
    [BlockRow(Field(name='B5', dev='B51_c', unit='A', width=10),
              Field(name='B5', dev='B51_v', unit='V', width=10),
              Field(name='B6', dev='B52_c', unit='A', width=10),
              Field(name='B6', dev='B52_v', unit='V', width=10),
              Field(name='B7', dev='B53_c', unit='A', width=10),
              Field(name='B7', dev='B53_v', unit='V', width=10),
             ),

    BlockRow(Field(name='B8', dev='B61_c', unit='A', width=10),
             Field(name='B8', dev='B61_v', unit='V', width=10),
             Field(name='B9', dev='B62_c', unit='A', width=10),
             Field(name='B9', dev='B62_v', unit='V', width=10),
             Field(name='B10', dev='B63_c', unit='A', width=10),
             Field(name='B10', dev='B63_v', unit='V', width=10),
            ),

    BlockRow(Field(name='B11', dev='B71_c', unit='A', width=10),
             Field(name='B11', dev='B71_v', unit='V', width=10),
             Field(name='B12', dev='B72_c', unit='A', width=10),
             Field(name='B12', dev='B72_v', unit='V', width=10),
             Field(name='B13', dev='B73_c', unit='A', width=10),
             Field(name='B13', dev='B73_v', unit='V', width=10),
            ),

    BlockRow(Field(name='B14', dev='B81_c', unit='A', width=10),
             Field(name='B14', dev='B81_v', unit='V', width=10),
             Field(name='B15', dev='B82_c', unit='A', width=10),
             Field(name='B15', dev='B82_v', unit='V', width=10),
            ),

    BlockRow(Field(name='B16', dev='B91_c', unit='A', width=10),
             Field(name='B16', dev='B91_v', unit='V', width=10),
             Field(name='B17', dev='B92_c', unit='A', width=10),
             Field(name='B17', dev='B92_v', unit='V', width=10),
            ),

    BlockRow(Field(name='B18', dev='B101_c', unit='A', width=10),
             Field(name='B18', dev='B101_v', unit='V', width=10),
             Field(name='B19', dev='B102_c', unit='A', width=10),
             Field(name='B19', dev='B102_v', unit='V', width=10),
            ),

    BlockRow(Field(name='B20', dev='B111_c', unit='A', width=10),
             Field(name='B20', dev='B111_v', unit='V', width=10),
             Field(name='B21', dev='B112_c', unit='A', width=10),
             Field(name='B21', dev='B112_v', unit='V', width=10),
            ),
    ],
    'powersupply')

_scatteringblock = Block(
    'Scattering',
    [BlockRow(Field(name='Sel', dev='Sel', unit='rpm', width=10, format="%.0f"),
              Field(name='Lambda', dev='Lambda', width=10, unit='A'),
              Field(name='Q1', dev='Q1', width=10, unit='1/A'),
              Field(name='Q2', dev='Q2', width=10, unit='1/A'),
             ),
    ],
    'frequencies')


_capacitanceblock = Block(
    'Capacitance',
    [BlockRow(Field(name='C0', dev='C00', unit='', width=10),
              Field(name='C0', dev='C01', unit='', width=10),
              Field(name='C1', dev='C10', unit='', width=10),
              Field(name='C1', dev='C11', unit='', width=10),
              Field(name='C2', dev='C20', unit='', width=10),
              Field(name='C2', dev='C21', unit='', width=10)
              ),],
    'capacitance')


_attenuatorsblock = Block(
    'Attenuators',
    [BlockRow(Field(name='Att0', dev='Att0', unit=''),
              Field(name='Att1', dev='Att1', unit=''),
              Field(name='Att2', dev='Att2', unit='')
              ),],
    'atts_slits')


_rightcolumn = Column(_currentblock, _powersupplyblock, _attenuatorsblock,
                      _capacitanceblock,
                      # _scatteringblock, _motorblock,
                     )

_leftcolumn = Column(_tempblock, _frequenciesblock,
                     # _capacitanceblock
                    )


devices = dict(
    Monitor = device('services.monitor.qt.Monitor',
                     title = 'RESEDA',
                     loglevel = 'info',
                     cache = 'resedahw',
                     font = 'Luxi Sans',
                     fontsize = 18,
                     valuefont = 'Consolas',
                     padding = 5,
                     layout = [Row(_expcolumn), Row(_rightcolumn, _leftcolumn)])
)
