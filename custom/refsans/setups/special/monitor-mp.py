#pylint: skip-file
description = 'diary just everything'
group = 'special'

_expcolumn = Column(
    Block('Experiment', [
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
_noklist = 'nok1 nok2 nok3 disc3 disc4 nok4 b1 nok5a zb0 nok5b zb1 nok6 zb2 nok7 zb3 nok8 bs1 nok9 sc2 b2'.split()
_nok_array = []
for i in range(5):
    if _noklist:
        _r = []
        for j in range(4):
            if _noklist:
                nok = _noklist.pop(0)
                _r.append(Field(dev=nok, width=16))
                #_r.append(Field(dev='status'))
                ##_r.append(Field(dev=nok,dev='status', width=16))
        _nok_array.append(BlockRow(*_r))
        _r = []
    _r.append(Field(dev=nok, width=16))
else:
    _nok_array.append(BlockRow(*_r))

_nokcolumn = Column(Block('optic', _nok_array))

# sample
_samplelist = 'theta phi chi y z top_theta top_phi top_z bg monitor probenwechsler'.split()
_sample_array = []
for i in range(6):
    if _samplelist:
        _r = []
        for j in range(3):
            if _samplelist:
                sample = _samplelist.pop(0)
                _r.append(Field(dev=sample,width=10))
        _sample_array.append(BlockRow(*_r))

_samplecolumn = Column(Block('sample', _sample_array))

#_samplecolumn = Column(
#    Block('sample',[
#      BlockRow( Field(dev='theta'),
#                Field(dev='phi'),
#                Field(dev='chi'),
#                Field(dev='y'),
#                Field(dev='z'),
#              )
#      ])
#)

_flippercolumn = Column(
    Block('Flipper', [
          BlockRow( Field(dev='frequency'),
                    #Field(dev='current'),
                    #Field(dev='flipper', name='Flipping_State'),
                  ),
          BlockRow( Field(dev='current'),
                    #Field(dev='flipper', name='Flipping_State'),
                  ),
          BlockRow( Field(dev='flipper', name='Flipping_State'),
                  ),
          ]),
)

_countercolumn = Column(
    Block('counter', [
          BlockRow( Field(dev='timer',name='MDLL'),
                    Field(dev='mon1'),
                    #Field(dev='flipper', name='Flipping_State'),
                  )
          ]),
)
_vakuumcolumn = Column(
    Block('chamber', [
          BlockRow( Field(dev='center_center_0',name='CB'),
                    #Field(dev='center_center_1',name='SFK'),
                    #Field(dev='center_center_2',name='SR'),
                  ),
          BlockRow( Field(dev='center_center_1',name='SFK'),
                    #Field(dev='center_center_2',name='SR'),
                  ),
          BlockRow( Field(dev='center_center_2',name='SR'),
                  ),
          ]),
)

_shuttercolumn = Column(
    Block('shutter',[
      BlockRow( Field(dev='shutter')
              )
      ])
)

_tubecolumn = Column(
    Block('detector',[
      BlockRow( Field(dev='table_m',name='table'),),
      BlockRow( Field(dev='tube_m',name='tube'),),
      ])
)

_h2column =  Column(
    Block('h2',[
      BlockRow( Field(dev='h2o',name='open'),),
      BlockRow( Field(dev='h2l',name='lateral'),),
      ])
)

_refcolumn = Column(
    Block('References', [
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
    Monitor = device('services.monitor.qt.Monitor',
                     title = description,
                     loglevel = 'info',
                     cache = 'refsans10.refsans.frm2',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     fontsize = 12,
                     padding = 5,
                     layout = [
                               Row(_expcolumn,_shuttercolumn),
                               Row(_nokcolumn,_samplecolumn), #  _refcolumn),
                               Row(_countercolumn,_h2column,_flippercolumn,_tubecolumn,_vakuumcolumn),
                               #Row(_vakuumcolumn),
                              ],
                    ),
)
