description = 'fallback for fail save'
group = 'special'

_expcolumn = Column(
    Block('Experiment fallback for fail save', [
        BlockRow(Field(name='Proposal', key='exp/proposal', width=7),
                 Field(name='Title',    key='exp/title',    width=20,
                       istext=True, maxlen=20),
                 Field(name='Current status', key='exp/action', width=50,
                       istext=True, maxlen=40),
                 Field(name='Last file', key='det/lastfilenumber'),
            )
        ],
        # setups='experiment'
    ),
)

# NOK's
_noklist = 'shutter_gamma nok2 nok3 nok4 nok5a zb0 nok5b zb1 nok6 zb2 nok7 zb3 nok8 bs1 nok9'.split()
_nok_array = []
for i in range(4):
    if _noklist:
        _r = []
        for j in range(4):
            if _noklist:
                nok = _noklist.pop(0)
                _r.append(Field(dev=nok, width=16))
        _nok_array.append(BlockRow(*_r))

_nokcolumn = Column(Block('NOK-System fallback for fail save', _nok_array))

_flippercolumn = Column(
    Block('Flipper fallback for fail save', [
          BlockRow( Field(dev='frequency'),
                    Field(dev='current'),
                    Field(dev='flipper', name='Flipping_State'),
                  )
          ]),
)

_refcolumn = Column(
    Block('References fallback for fail save', [
        BlockRow( Field(dev='nok_refa1', name='ref_A1'),
                  Field(dev='nok_refb1', name='ref_B1'),
                  Field(dev='nok_refc1', name='ref_C1'),),
        BlockRow( Field(dev='nok_refa2', name='ref_A2'),
                  Field(dev='nok_refb2', name='ref_B2'),
                  Field(dev='nok_refc2', name='ref_C2'),),
        ],
    ),
)

devices = dict(
    Monitor = device('nicos.services.monitor.qt.Monitor',
        title = 'NICOS status monitor fallback for fail save',
        loglevel = 'info',
        cache = 'refsansctrl.refsans.frm2.tum.de',
        prefix = 'nicos/',
        font = 'Luxi Sans',
        valuefont = 'Consolas',
        fontsize = 12,
        padding = 5,
        layout = [
            Row(_expcolumn),
            Row(_nokcolumn, _refcolumn),
            Row(_flippercolumn),
        ],
    ),
)
