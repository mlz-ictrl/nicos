'''
Created on 06.06.2011

@author: pedersen
'''

from nicos import session
from nicos.scan import Scan, TimeScan, ContinuousScan, ManualScan
from nicos.device import Device, Measurable, Moveable, Readable
from nicos.errors import UsageError
from nicos.commands import usercommand

from nicos.resi import residevice

@usercommand
def measuredataset(dev,**kw):
    ''' Mesasure a single crystal dataset

    dev: residevice instance [req]

    use one of:

    dataset: array of reflections to measure

    thmin: min 2-theta
    thmax: max 2-theta

    dmin: min d-spacing
    dmax: max d-spacing

    optional:
    stime: scan time
    delta: scan width
    step: step width

    '''
    print 'measure',kw
    if not kw:
        raise UsageError('at least two arguments are required')

    if kw.has_key('dataset'):
        ds=kw['dataset']
        del kw['dataset']
    elif kw.has_key('thmin'):
        if not kw.has_key('thmax'):
            raise UsageError('thmin and thmax need to be given both')
        else:
            ds=dev._hardware.getScanDataset(thmax=kw['thmax'],thmin=kw['thmin'])
            del kw['thmax']
            del kw['thmin']
    elif kw.has_key('thmax'):
        if not kw.has_key('thmin'):
            raise UsageError('thmin and thmax need to be given both')
        else:
            ds=dev._hardware.getScanDataset(thmax=kw['thmax'],thmin=kw['thmin'])
            del kw['thmax']
            del kw['thmin']
    elif kw.has_key('dmin'):
        if not kw.has_key('dmax'):
            raise UsageError('dmin and dmax need to be given both')
        else:
            ds=dev._hardware.getScanDataset(dmax=kw['dmax'],dmin=kw['dmin'])
            del kw['dmax']
            del kw['dmin']
    elif kw.has_key('dmax'):
        if not kw.has_key('dmin'):
            raise UsageError('dmin and dmax need to be given both')
        else:
            ds=dev._hardware.getScanDataset(dmax=kw['dmax'],dmin=kw['dmin'])
            del kw['dmax']
            del kw['dmin']

    if not isinstance(dev,residevice.ResiDevice):
        raise UsageError('This command only works with the resi device')

    dev._hardware.DoScan(ds=ds,**kw)