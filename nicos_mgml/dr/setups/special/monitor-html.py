description = 'setup for the status monitor, HTML version'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=30,
                       istext=True),
                 Field(name='Last scan file', key='exp/lastscan',
                       setups='tas or vstressi'),
                 Field(name='Last image file', key='exp/lastpoint',
                       setups='sans or refsans'),
                ),
        BlockRow(
                 Field(name='Next bus departure',    key='bus/value',    width=20,
                       istext=True, maxlen=20),
                ),
        ],
    ),
)

_fieldcolumn = Column(Block('Applied field', [
    BlockRow(Field(name='', dev='B', css='font-size: 60;')),
    ],
    setups='magnet',))

_magnetblock = Block('Main magnet', [
    BlockRow(Field(name='B', dev='B_main'),
             Field(key='B_main/target', name='Target', unit='T'),
             Field(key='B_main/ramp', name='Ramp', unit='T/min'),
             Field(name='Persistent', dev='magnet_persistent'),
             ),
    BlockRow(
             Field(key='B_main/status[1]', name='status'),
             ),
    BlockRow(Field(dev='B', plot='B', plotwindow=3600*3, width=50, height=40),),
    ],
    setups='magnet',
)

_tempblock = Block('Temperature', [
    BlockRow(Field(dev='T'), Field(key='t/setpoint', name='Setpoint'),
                   Field(dev='T_1K'),Field(dev='T_finger')),
    BlockRow(Field(dev='T', plot='T', plotwindow=3600*3, width=50, height=50))
    ],
    setups='ls372',
)

_cryoconblock = Block('Temperature', [
    BlockRow(Field(dev='T_ambient'), Field(dev='T_dewar'), Field(dev='T_shield')),
    BlockRow(Field(dev='T_ambient', plot='R', plotwindow=3600*24, width=50, height=50),)
    ],
    setups='cryocon',
)

_heblock = Block('Helium Level', [
    BlockRow(Field(dev='magnet_lhl'),),
    BlockRow(Field(dev='magnet_lhl', plot='L', plotwindow=3600*24, width=50, height=50),)
    ],
    setups='helium',
)

_colA = Column(_magnetblock)

_colB = Column(_tempblock)

_colC = Column(_heblock)

_colD = Column(_cryoconblock)

devices = dict(
    Monitor = device('nicos.services.monitor.html.Monitor',
        title = 'DR9T status monitor',
        filename = '/mnt/statmons/dr.html',
        loglevel = 'info',
        interval = 5,
        cache = 'localhost:14869',
        prefix = 'nicos/',
        font = 'Helvetica',
        valuefont = 'Consolas',
        fontsize = 17,
        layout = [[_fieldcolumn, _expcolumn],
                  [_colA,  _colB, _colC, _colD]],
    ),
)
