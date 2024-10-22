description = 'setup for the status monitor, HTML version'
group = 'special'

_heblock = Block('Helium Levels', [
    BlockRow(Field(key='ppms9/level/value', name='PPMS9', unit='%'),
            Field(key='ppms14/level/value', name='PPMS14', unit='%'),
            Field(key='matfun/level/value', name='Matfun', unit='%'),
            Field(dev='twenty/magnet_lhl', name='20T'),),
    BlockRow(Field(dev='twenty/magnet_lhl', name='20T', secondaxes=True, plot='lhe', plotwindow=3600*24, width=50, height=40),
            Field(dev='matfun/level', plot='lhe', name='MATFUN', plotwindow=3600*24, width=50, height=40),
            Field(dev='ppms14/level', plot='lhe', name='PPMS14', plotwindow=3600*24, width=50, height=40),
            Field(dev='ppms9/level', plot='lhe', name='PPMS9', plotwindow=3600*24, width=50, height=40),
    ),
    ],
)

_20tblock = Block('20T', [
    BlockRow(Field(key='twenty/exp/proposal', name='Proposal'), Field(key='twenty/exp/localcontact', name='LC')),
    BlockRow(Field(key='twenty/exp/title', name='Title')),
    BlockRow(Field(key='twenty/exp/users', name='Users')),
    BlockRow(Field(dev='twenty/ts', name='Sample'), Field(dev='twenty/t', name='VTI'), Field(dev='twenty/cv_pressure', name='p'),),
    BlockRow(Field(dev='twenty/t_ambient-273', name='Room'), Field(dev='twenty/t_dewar', name='Dewar'), Field(dev='twenty/t_minisorb', name='Sorb.Pump'),),
    BlockRow(Field(dev='twenty/b', name='B', big=True, max=16, warnmax=9),),
    ],
)

_infoblock = Block('News', [
    BlockRow(Field(name='News', roll='https://mgml.eu/roll', refresh=1,),),
    ],
)

_ppms9block = Block('PPMS 9', [
    BlockRow(Field(key='ppms9/experiment/value', name='Proposal'),),
    BlockRow(Field(key='ppms9/user/value', name='User'),Field(key='ppms9/lc/value', name='LC'),),
    BlockRow(Field(dev='ppms9/t', name='T'),Field(dev='ppms9/b*0.0001', name='B'),),
    BlockRow(Field(dev='ppms9/b*0.0001', plot='t1', name='B (T)', secondaxes=True, plotwindow=3600*3, width=30, height=40),
             Field(dev='ppms9/t', plot='t1', name='T (K)'),),
    ],
)
_ppms14block = Block('PPMS 14', [
    BlockRow(Field(key='ppms14/experiment/value', name='Proposal'),),
    BlockRow(Field(key='ppms14/user/value', name='User'),Field(key='ppms14/lc/value', name='LC'),),
    BlockRow(Field(dev='ppms14/t', name='T'),Field(dev='ppms14/b*0.0001', name='B'),),
    BlockRow(Field(dev='ppms14/b*0.0001', plot='t2', name='B (T)', secondaxes=True, plotwindow=3600*3, width=30, height=40),
             Field(dev='ppms14/t', plot='t2', name='T (K)'),),
    ],
)
_matfunblock = Block('Matfun', [
    BlockRow(Field(key='matfun/experiment/value', name='Proposal'),),
    BlockRow(Field(key='matfun/user/value', name='User'),Field(key='matfun/lc/value', name='LC'),),
    BlockRow(Field(dev='matfun/t', name='T'),Field(dev='matfun/b*0.0001', name='B'),),
    BlockRow(Field(dev='matfun/b*0.0001', plot='t3', name='B (T)', secondaxes=True, plotwindow=3600*3, width=30, height=40),
             Field(dev='matfun/t', plot='t3', name='T (K)'),),
    ],
)

_colX = Column(_20tblock, _infoblock)


_colA = Column(_ppms9block)
_colB = Column(_ppms14block)
_colC = Column(_matfunblock)

devices = dict(
    Monitor = device('nicos.services.monitor.html2.Monitor',
        title = 'Master status monitor',
        filename = '/mnt/statmons/master.html',
        loglevel = 'info',
        interval = 30,
        cache = 'kfes12.troja.mff.cuni.cz',
        prefix = 'nicos/',
        font = 'Helvetica',
        valuefont = 'Consolas',
        fontsize = 17,
        expectmaster = False,
        layout = [[Column(_heblock), Column(_20tblock), Column(_infoblock)],
                  [_colA, _colB, _colC]],
    ),
)
