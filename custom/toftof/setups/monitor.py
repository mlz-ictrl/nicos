description = 'setup for the status monitor'
group = 'special'

_expcolumn = [
    ('Experiment', [
        [{'name': 'Proposal', 'key': 'exp/proposal', 'width': 7},
         {'name': 'Title', 'key': 'exp/title', 'width': 20,
          'istext': True, 'maxlen': 20},
         {'name': 'Current status', 'key': 'exp/action', 'width': 30,
          'istext': True},
         {'name': 'Last file', 'key': 'filesink/lastfilenumber'}]]),
]

_warnings = [
    ('a1/value', '> 20', 'a1 value > 20'),
]

_axisblock = (
    'Axis devices',
    [['a1', 'm1', 'c1'],
     ['a2', 'm2']],
    'misc')

_detectorblock = (
    'Detector devices',
    [[{'name': 'timer', 'dev': 'timer'},
      {'name': 'ctr1', 'dev': 'ctr1', 'min': 100, 'max': 500},
      {'name': 'ctr2', 'dev': 'ctr2'}]],
    'detector')

_otherblock = (
    'Other devices',
    [[{'dev': 'slit', 'width': 20, 'name': 'Slit'}],
     [{'dev': 'sw', 'width': 4, 'name': 'Switcher'}]],
    'misc')

_rightcolumn = [
    _axisblock,
    _detectorblock,
]

_leftcolumn = [
    _otherblock,
]

devices = dict(
    Monitor = device('nicos.monitor.qt.Monitor',
                     title = 'NICOS status monitor',
                     loglevel = 'info',
                     server = 'cpci1.toftof.frm2:14869',
                     prefix = 'nicos/',
                     font = 'Luxi Sans',
                     valuefont = 'Consolas',
                     padding = 5,
                     layout = [[_expcolumn], [_rightcolumn, _leftcolumn]],
                     warnings = _warnings,
                     notifiers = [])
)
