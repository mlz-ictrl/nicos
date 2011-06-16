'''
Created on 30.05.2011

@author: pedersen
'''

import sys
sys.path.append('/home/resi/pedersen/workspace_python/singlecounter')
sys.path.append('/home/resi/pedersen/workspace_python/nonius_new/app')
from nicos.device import Moveable,Param #@UnusedImport
from sc_scan_new import HuberScan
class ResiDevice(Moveable):
    '''
    classdocs
    '''
    name=None

    def doPreinit(self):
        '''
        Constructor
        '''

        self._hardware=HuberScan()
        self._hardware.LoadRmat()
#    self._hardware.SetCellParam(a=4.9287, b=4.9287, c=5.3788, alpha=90.000, beta=90.000, gamma=120.000)
        self._hardware.cell.conventionalsystem = 'triclinic'
        self._hardware.cell.standardize = 0
        self._hardware.cell.pointgroup = '1'
        self._hardware.bisect.cell = self._hardware.cell
        #self.loglevel='debug'

    def doRead(self):
        return self._hardware.GetPosition()

    def doMove(self,target):
        return self._hardware.Goto(pos=target)

    def doStart(self,target):
        self._hardware.Goto(pos=target)

    def doInfo(self):
        info=list()
        info.append(('experiment','position',self._hardware.GetPosition()))
        info.append(('experiment','reflex',self._hardware.current_reflex))
        info.append(('sample','cell',self._hardware.cell))
        return info