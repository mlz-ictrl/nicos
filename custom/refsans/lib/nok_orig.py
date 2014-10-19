# -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#              $Id: refsans_nok.py,v 1.6 2006/04/06 18:25:14 jkrueger1 Exp $
#
# Description:
#               NICOSMethods for the REFSANS experiment
#
# Author:       Jens Krüger
#               $Author: jkrueger1 $
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2005   Jens Krüger (jens.krueger@frm2.tum.de),
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************
# pylint: skip-file
# This is still a nicos1 module!
""" Module for moving the NOK's and Apertures on REFSANS """

"""
MP was here!
doing cear it!
tun:
11.12.2008 12:34:55 remove extra code
 Objekt:
    _axes            Die achsen werdne hinter her zu __axes
    _counter         int Stand es Encoders?
    _defaultaction   ???
    _device2unit     ??? Umrechung der Einheiten
    _getLastValue
    _lastValue
    _method
    _mutex
    _Nok__Debug      Flag: Debuggen
    _Nok__Diary      externes Objekt
    _Nok__readonly   Flag: readonly
    _omethod
    _result
    _unit2device
    absMax            ??? 0 int
    absMin            ???
    adev
    backlash
    bus
    configuration
    controller
    device
    diary              this function is used for diary
    doInit             must be!
    doIsAllowed
    doRead             ???
    doReset            this function is used for reset
    dosetpos           this function should be used for setpos todo ### test
    doStart            this function is used for move, dont know why
    doStatus           this function should be used for status todo ### test
    doStop             this function should be used for stop todo ### test
    doWait             this function should be used for wait todo ### timeout!
    encoder            not jet access to the encoder
    fmtstr             formatierungsstring zur Darstellung
    functions          dic mit function argumenten und returns
    highlimitswitch    interface
    holdback           ???
    lock
    lowlimitswitch     interface
    motor              access to the motor
    name               the name
    neginclination     int tilt
    NOKAxis            Objekt der Achsen
    parameters         dic Liste der parameter
    pm                 ???
    posinclination     int tilt
    refpos             int Position des Referenzschalters heilige Zahl
    refswitch          interface
    server             Name der Servers NICOS
    statuslist         ??? nix
    switchlist         ??? nix
    typelist           ??? ein bus
    unit
    unitlist
    unlock
    userMax            ??? 0
    userMin            ??? 0
    yes          externes Objekt to logg
 ACHSE:

only with pairs nok.deviceQueryRes...
moving mit jump beloy ref (nok2)
tilt in reffahrt (nok2)

doStart inproof
ctrl_reset.py
 Jens nice Tablee motorbus adresse
 nok4 'adev': {'bus' : ['motorbus2','motorbus'},

stop motor.motor.stop stop geht ansich, aber nur eine Ebene wie mache ich das?
 proof Target: @8 movto 4, shoud be at 6###
logging
simulation, emulation
move testen gleichzeitig
devide into force_low and get ref
create force_high
yes!!!
no .motor.
tuple or []
ablauf optimierung beide move starten dann einam warten!
 Zeit außen log innen
changeing setpos!!!
making deviceQuery*

"""

from nicm_def import Moveable, HWGeneric
from nicm_exceptions import OutofBoundsError, CommunicationError, ArgError
from nicm_exceptions import PositionError

try :
    from _TACOClient import TACOError
except ImportError:
    from TACOClient import TACOError

import TACOStates
import Motor
import Encoder
import time
import IO
import sys #for problem()!

#from configobj import ConfigObj
#from refsans_extension import cl_refsans_extension,cl_refsans_axes_extension
#from MP_tools import try _ConfigObj,SSO
from MP_tools import try_ConfigObj,SSO
from no_lld import cl_no
from do_get import cl_do_get,cl_zeitpunkt
from do_wait import cl_do_wait
from tracing import cl_poti
#from Diary import cl_Diary
#***************************************************
# SOME ERROR TYPE DEFINITIONS (JFM)
class Error(Exception):pass
#***************************************************
try:
    import IPython.ipapi
    ip = IPython.ipapi.get()
    #---------------------------------------------------------------------------
    Developing = ip.user_ns['Developing']
    readonly = ip.user_ns['readonly']
    fake = ip.user_ns['fake']
    startstyle = ip.user_ns['startstyle']
except:
    import __main__
    Developing = __main__.Developing
    readonly = __main__.readonly
    fake = __main__.fake
    startstyle = __main__.startstyle
#---------------------------------------------------------------------------------
LDeveloping = Developing #and False
Lreadonly   = readonly
Lfake       = fake
#---------------------------------------------------------------------------------
#QAD
#def NicmPrint(eins,zwei):
#    __main__.NicmPrint(eins,zwei)
#PM_STANDARD = __main__.PM_STANDARD
#---------------------------------------------------------------------------


LL_ESCAPE = 2 #0.5

#IPCSMS = True
IPCSMS = False

if IPCSMS:
    from IPCSMS_lld import cl_CONT_IPCSMS

class Nok (Moveable,cl_no,cl_do_get,cl_do_wait):
    """
    defines a NOK consisting of one or several axes
    """
    __Debug = LDeveloping
    __readonly = Lreadonly
    __fake = Lfake
    #QAD
    __startstyle = startstyle
    __geometire_file = 'geometrie'
    __resources_file = 'resources' #todo ->cl_no
    #todo should go to resources_file
    #QAD privat oder file
    resources_keys  = ['usermax','usermin','speed','accel','offset','stepsperunit','direction']
    __file_sufix     = '.inf'
    __SMSsend        = False

    #---------------------------------------------------------------------------
    __doget_help = {'help':        'this dic, * not possible jet',\
                    'read':        'pos with mask and everything',\
                    'status':      'status with everything',\
                    'taco':        'pure tacostatus, as from Jens',\
                    'achse':       'pure pos of achses, no mask',\
                    'encoder_pos': 'pure encoder pos of achses, no mask',\
                    'simple':      'one state for all axes, but the worsed rules',\
                    'flags':       'status of all switches',\
                    'diary':       'only the string for Line',\
                   }


    typelist = {
        "bus": HWGeneric
        #,"bus2": HWGeneric #if one has to, everybody has to have two
    }

    #-------------------------------------------------------------------------------
    Zustand  = 'release'
    Historie = []
    #Historie.insert(0,'')
    Historie.insert(0,'14.01.2012 12:21:46 problem() recurxive NOTAus')
    Historie.insert(0,'13.01.2012 07:38:46 no loggin in axes but in upper')
    Historie.insert(0,'12.01.2012 08:02:05 do_wait developing')
    Historie.insert(0,'05.01.2012 09:10:08 serverlock and news')
    Historie.insert(0,'03.01.2012 09:30:55 Bug in doStart for single masks')
    Historie.insert(0,'03.01.2012 09:13:39 do_get_flags konvertierung in altes Format')
    Historie.insert(0,'30.11.2011 10:16:44 clean up for nok an pb mask to do_get as do_maskenerkennung')
    Historie.insert(0,'30.11.2011 08:58:09 auto str for UpdateResource')
    Historie.insert(0,'30.11.2011 07:59:05 changes parametes to param')
    Historie.insert(0,'29.11.2011 14:56:28 new arg vor move')
    Historie.insert(0,'29.11.2011 08:28:21 doget still gelegt')
    Historie.insert(0,'21.11.2011 07:59:06 deleted autoreset in wait')
    Historie.insert(0,'15.11.2011 15:03:25 make doSart easier by using get')
    Historie.insert(0,'24.08.2011 11:23:04 adding resources_keys direction')
    Historie.insert(0,'24.08.2011 09:58:05 new Server tacoVersion: [2.5.8] new code')
    Historie.insert(0,'15.06.2011 14:22:12 using global inf')
    Historie.insert(0,'25.02.2011 09:12:43 MP in den achsen change enc to motor')
    Historie.insert(0,'07.02.2011 09:38:06 rest arg: use_encoer')
    Historie.insert(0,'24.01.2011 08:30:22 Details at dosetpos type("") and simple==fail')
    Historie.insert(0,'11.01.2011 11:02:39 BUGFIX')
    Historie.insert(0,'07.01.2011 07:57:01 remove doClear; __proof_resources')
    Historie.insert(0,'05.01.2011 10:16:54 self.doStart(pos,force) wegen PotiALARM !removed 10.01.2011 13:26:36 wegen do_get besser')
    Historie.insert(0,'04.01.2011 11:17:17 doClear')
    Historie.insert(0,'19.10.2010 13:43:04 remove lokal doGetPar')
    Historie.insert(0,'07.10.2010 08:57:44 remove tracer in doget but hack for encoder')
    Historie.insert(0,'06.10.2010 14:05:19 new mehtods due to ip')
    Historie.insert(0,'08.09.2010 08:43:42 adding __fake')
    Historie.insert(0,'30.08.2010 08:18:21 cl_do_get')
    Historie.insert(0,'25.08.2010 09:03:03 try_ConfigObj cl_no logging Start')
    Historie.insert(0,'24.08.2010 14:58:27 speed up and startstyle')
    Historie.insert(0,'20.08.2010 12:07:51 SMS for Poti')
    Historie.insert(0,'16.06.2010 09:48:44 programm new Reset! raise in methode')
    Historie.insert(0,'15.06.2010 08:07:35 there is no enc. So dont use it!')
    Historie.insert(0,'20.04.2010 10:47:50 change diary because of doGet')
    Historie.insert(0,'26.03.2010 10:56:27 speedswitch: fullspeed, refspeed, goodspeed untested')
    Historie.insert(0,'08.01.2010 08:20:23 __readonly reorg: only in motorstart')
    Historie.insert(0,'07.01.2010 08:53:26 stop')
    Historie.insert(0,'18.11.2009 07:14:39 get')
    Historie.insert(0,'26.10.2009 14:32:09 add sleep(0.5) in wait for poti')
    Historie.insert(0,'10.08.2009 14:17:19 bugfix in status')
    Historie.insert(0,'25.06.2009 08:40:16 status gives mask if condition = stop; sorry no tupel anymore')
    Historie.insert(0,'17.02.2009 16:10:27 improve logging yes every print become ll_log(text,self.__Debug) or True if needed')
    Historie.insert(0,'19.11.2008 08:25:47 IPCSMS bleibt, QAD')
    Historie.insert(0,'07.11.2008 09:16:18 LL_ESC 2')
    Historie.insert(0,'29.10.2008 16:30:34 diary')
    Historie.insert(0,'27.10.2008 15:49:38 refsans_extension.py')
    #-------------------------------------------------------------------------------

    class NOKAxis(cl_no):
        """
        private class to modelling the special NOK axis
        """
        __Debug = LDeveloping
        __readonly = Lreadonly
        __startstyle = startstyle

        def __init__(self,upper,index):
            #def __init__(self, sbus, smot, senc, ssll, sshl, ssref) :
            """
            defines a Axis, expects:
            sBus bus device
            sMot devname of Motor
            sEnc devname of Encoder
            sSll devname of Low-Limit-Switch
            sShl devname of High-Level-Switch
            sSref devname of Reference-Switch
            """
            Debug = self.__Debug #and False

            self.name = '%s_%d'%(upper.name,index) #for no
            self.upper = upper
            self.recursive_break = 0

            if Debug: print 'formal<'
            if Debug: print index,
            old = False #not Debug
            indexname = ['r','s']
            if False: #Debug:
                try:
                    #if Debug:
                    print 'new','test/'+upper.name+'/'+'m'+indexname[index],
                    #print sp+':','test/'+upper.name+'/'+indexname[index]+subparts[sp]
                    self.motor     = Motor.Motor(    'test/'+upper.name+'/'+'m'+indexname[index])
                    print '1m','test/'+upper.name+'/'+'e'+indexname[index],'ACHTUNG enc spinnt',
                    self.enc       = Encoder.Encoder('test/'+upper.name+'/'+'e'+indexname[index])
                    print '1e',
                    #QAD aber wegen Setpos MP 30.08.2010 13:45:04
                    print '1e',
                    self.sll       = IO.DigitalInput('test/'+upper.name+'/'+'s'+indexname[index]+'ll')
                    print '1ll',
                    self.shl       = IO.DigitalInput('test/'+upper.name+'/'+'s'+indexname[index]+'hl')
                    print '1hl',
                    self.sref      = IO.DigitalInput('test/'+upper.name+'/'+'s'+indexname[index]+'ref')
                    print '1bl',
                    self._backlash = upper.backlash
                    print '1ref',
                    self._refPoint = upper.refpos[index]
                    print '1'
                except:
                    old = True
                    if Debug: print 'formal<'

            if True: #old:
                #if Debug:
                print 'old',upper.motor[index],
                self.motor     = Motor.Motor(upper.motor[index])
                self.enc       = Encoder.Encoder(upper.encoder[index])
                #QAD aber wegen Setpos MP 30.08.2010 13:45:04
                self.sll       = IO.DigitalInput(upper.lowlimitswitch[index])
                self.shl       = IO.DigitalInput(upper.highlimitswitch[index])
                self.sref      = IO.DigitalInput(upper.refswitch[index])
                self._backlash = upper.backlash
                self._refPoint = upper.refpos[index]

            if not IPCSMS: self.bus = upper.bus
            if Debug: print 'ENC:cl_poti',
            self.encoder = cl_poti(self.name)

            self.flags = {\
                          'HIGH':self.shl,\
                          'REF':self.sref,\
                          'LOW':self.sll,\
                          }

            if not self.__Debug:
                try :
                    Taco = self.motor.deviceState()
                    if Debug:print TACOStates.stateDescription(Taco)
                    if Taco == TACOStates.FAULT :
                    #self.motor.deviceReset()
                        print 'is in FAULT'
                    if Taco != TACOStates.ON:
                        if self.motor.isDeviceOff(): self.motor.deviceOn()
                        if self.motor.isDeviceOff(): self.motor.deviceOn()
                    if self.enc.isDeviceOff():   self.enc.deviceOn()
                    if self.enc.isDeviceOff():   self.enc.deviceOn()
                    if self.sll.isDeviceOff():   self.sll.deviceOn()
                    if self.shl.isDeviceOff():   self.shl.deviceOn()
                    if self.sref.isDeviceOff():  self.sref.deviceOn()
                except :
                    pass
            else:
                    #if Debug: print 'new Achs init for startstyle'
                try :
                    if SSO(self.__startstyle,'quick'):
                        if Debug: print 'Servertest',
                        Taco = self.motor.deviceState()
                        if Taco == TACOStates.FAULT :
                            #self.motor.deviceReset()
                            print 'is in FAULT'
                    if SSO(self.__startstyle,'normal'):
                        if Debug: print 'Server full',
                        if Taco != TACOStates.ON:
                            if self.motor.isDeviceOff(): self.motor.deviceOn()
                            if self.motor.isDeviceOff(): self.motor.deviceOn()
                        if self.enc.isDeviceOff():   self.enc.deviceOn()
                        if self.enc.isDeviceOff():   self.enc.deviceOn()
                        if self.sll.isDeviceOff():   self.sll.deviceOn()
                        if self.shl.isDeviceOff():   self.shl.deviceOn()
                        if self.sref.isDeviceOff():  self.sref.deviceOn()
                    else: print TACOStates.stateDescription(Taco),
                except :
                    pass
            self.no('_NOKAxis__','motor')
            if Debug: print 'Achse done>',
            #if Debug: print '2 self.encoder',self.encoder

        def setbacklash(self, val) :
            """
            sets the backlash for the axis
            @param val
            """
            self._backlash = val

        def read (self):
            """MP 29.12.2009 08:13:27 Structur!
            lesefehler und Konvertierungsfehler
            """
            if self.__Debug: maxRead = 2 #@0 fail
            else:            maxRead = 10
            Readcount = 1
            #25.02.2011 09:11:54 line = 'COM:encread'
            line = 'COM:motorread'
            if True:
                while True:
                    try:
                        val = self.motor.read()
                        return float(val) #MP kurz und gut 27.06.2011 08:49:51 ja, besser!
                    except:
                        val = self.problem('read',sys)
                        return float(val) #MP kurz und gut 27.06.2011 08:49:51 ja, besser!
            else:
                while True:
                    try:
                        f = self.motor.read() #MP from enc to motor 25.02.2011 09:11:48
                        try:
                            f = float(f)
                            if line != 'COM:motorread': self.ll_log(line,True)
                            return f  #MP 25.03.2011 14:20:09 hier knallt es warum?
                        except:
                            line += ' convert:>%s<%d>'%(str(f),Readcount)
                    except:
                        try:    st = self.motor.deviceStatus() #MP from enc to motor 25.02.2011
                        except: st = 'ex'                      #MP 25.06.2011 21:47:17
                        line += ' R:<%s>'%st
                    time.sleep(Readcount)
                    Readcount +=1
                    if Readcount > maxRead:
                        try:
                            #self.news_spread('encread Disaster')
                            pass
                        except: pass
                        break
            self.ll_log(line,True)
            raise Error(line)

        def setrefpoint(self, val) :
            """
            defines the position of the reference point
            @param val
            """
            self._refPoint = val

        def _movestep1(self, units) :
            """
            This function checks the current position of the axis and decides
            what's to do. If the new position is above the current it does nothing.
            Otherwise it tries to move to a position below the disired position.
            If this is not possible it moves to the lower user limit
            @param units desired position
            """
            Debug = self.__Debug
            #if (self.read() <= units): #MP 29.12.2009 08:29:59 enc
            if (self.motor.read() <= units): #MP 15.06.2010 08:07:03 no enc
                if Debug and False:
                    self.ll_log("movestep1 returns 0 -> new pos is above or equel current "+str(units),Debug)
                return 0
            else :
                #print "read user min"
                llimit = float(self.motor.deviceQueryResource("usermin"))
                try:
                    if llimit > units or llimit > (units - self._backlash): self.motorstart(llimit)
                    else :                                                  self.motorstart(units - self._backlash)
                except TACOError as e:
                    return 1
            return 0

        def _movestep2(self, units) :
            """
            This function moves the axis to the given position
            @param units
            """
            Debug = self.__Debug and False
            self.motorstart(units)
            #try:              self.motorstart(units)
            #except TACOError: return 1
            return 0

        def motorstart (self, units):
            """MP 29.12.2009 08:13:27 Structur!
            lesefehler
            !!! Bereichsfehler
            """
            Debug = self.__Debug and False
            if Debug: print 'motorstart',self.name,units
            if self.__readonly: self.ll_log('motorstart '+str(units)+' BLOCKED',True)
            else:               self.motor.start(units)
            if Debug: print 'done'
            return
            maxRead = 1
            Readcount = 1
            line = ''
            while True:
                try:
                    self.motor.start(units)
                    if line != '': self.ll_log('COM:motorstart '+line,False)
                    return
                except:
                    line = 'R:<%d>'%Readcount
                time.sleep(Readcount)
                Readcount +=1
                if Readcount > maxRead:
                    try:
                    #self.news_spread('motorstart Disaster')
                        pass
                    except: pass
                    break
            self.ll_log(line,True)
            raise Error(line)

        def state(self) :
            """returns the state of the axis, i.e. the motor"""
            ###alt
            #try :              return self.motor.deviceState()
            #except TACOError : raise CommunicationError("Could not read the state")

            maxRead = 1
            Readcount = 1
            line = 'COM:state '
            while True:
                try:
                    s = self.motor.deviceState()
                    if Readcount>1: self.ll_log(line+'R:<%d>'%Readcount,False)
                    if s == TACOStates.FAULT:
                        self.serverlock()
                        #self.problem('state',(None,'TACO server is FAULT'))
                    return s
                except:
                    s = self.problem('state',sys)
                    #self.serverlock()
                    return s
                if Readcount > maxRead: break #sleep sparen
                else:                   time.sleep(Readcount)
                Readcount +=1
            line += 'Disaster'
            try:
                self.news_spread(self.name+line)
            except: pass
            self.ll_log(line,True)
            raise Error(line)


        def status (self,Typ='TACO') :
            """returns the state of the axis, i.e. the motor"""
            #if (Type(Typ) != Type([]))and(Type(Typ) != Type(())): Typ = [Typ]
            #for a in range(len(Typ)): Typ[a] = Typ.upper()
            try :  Taco = self.state() #MP 07.01.2010 09:28:09
            except TACOError : raise CommunicationError("Could not read the state")
            if   'TACO' == Typ.upper(): return TACOStates.stateDescription(Taco)
            if   'HIGH' == Typ.upper(): return self.shl.read()
            elif 'REF'  == Typ.upper(): return self.sref.read()
            elif 'LOW'  == Typ.upper(): return self.sll.read()
            line = TACOStates.stateDescription(Taco)
            if Taco == TACOStates.DEVICE_NORMAL or \
               Taco == TACOStates.ON:
                I = self.shl.read()
                if I: line += ' High:'+str(I)
                I = self.sref.read()
                if I: line += ' REF:' +str(I)
                I = self.sll.read()
                if I: line += ' LOW:' +str(I)
            return line

        def readsteps(self):
            """
            This method reads the current motor counter
            """
            try :
                return self.motor.deviceQueryResource("counter")
            except TACOError :
                raise CommunicationError("Could not read the steps")

        def setpos (self, pos) :
            """
            Sets the position of motor and encoder to a given value without
            moving the axis
            @param pos
            """
            #self.yes.enter_setpos(pos)
            self.enter_setpos(pos)
            try :
                if self.motor.isDeviceOff() :
                    self.motor.deviceOn()
                if self.__readonly: self.ll_log('setpos BLOCKED',True)
                else:               self.motor.setpos(pos)
                #!!! self.enc.setPosition(pos) #!!!
            except TACOError :
                #!!!
                self.ll_log("Could not really set the position.")
                CommunicationError("Could not really set the position.")
            #self.yes.exit_setpos()
            self.exit_setpos()

        def _refmovestart (self) :
            """
            start the reference finding move
            moves axis out of switches if in
            """
            Debug = self.__Debug and False
            sad = int(self.motor.deviceQueryResource("busaddr"))
            curspeed = int(self.motor.deviceQueryResource("speed")) # / 2
            if self.sll.read() == 1 :
                Border = float(self.motor.deviceQueryResource("usermin"))
                Value  = self.motor.read()
                if Value + LL_ESCAPE < Border: Value = Border
                #print 'refmove to',Value + LL_ESCAPE
                self.motorstart(Value + LL_ESCAPE)
                self.wait()
            elif self.shl.read() == 1 :
                Border = float(self.motor.deviceQueryResource("usermax"))
                Value  = self.motor.read()
                if Value - LL_ESCAPE > Border: Value = Border
                #print 'refmove to',Value - LL_ESCAPE
                self.motorstart(Value - LL_ESCAPE)
                self.wait()
            try :
                if IPCSMS: self.MOTORctrl.forward()
                else:      self.bus.send(sad, 34)
            except:
                print "Could not set 'forward' on address %d" % sad
                raise
            try :
                if IPCSMS: self.MOTORctrl.startref(curspeed)
                else:      self.bus.send(sad, 47, curspeed, 3)
            except :
                print "Could not start reference move on address %d" % sad
                raise

        def wait (self):
            """
            wait until the moving of the axis has stopped
            """
            #print 'enter wait 0.25'
            time.sleep(0.25)
            #self.yes.enter_wait()
            self.enter_wait()
            while 1 :
                try :
                    state = self.state()
                except TACOError :
                    continue
                if state == TACOStates.ON :
                    break
                if state == TACOStates.DEVICE_NORMAL :
                    break
                elif state == TACOStates.DEVICE_OFF :
                    try :
                        self.motor.deviceOn()
                    except TACOError :
                        continue
                elif state == TACOStates.FAULT :
                    try :
                        pass #MP 21.11.2011 07:58:50 self.motor.deviceReset()
                    except TACOError :
                        continue
                time.sleep(0.1)
            #self.yes.exit_wait()
            self.exit_wait()

        def test(self):
            """
            Could be used to test if all needed devices are accessible
            """
            try:
                self.motor.read()
                #self.read() #MP 29.12.2009 08:30:46
                self.sll.read()
                self.shl.read()
                self.sref.read()
                return 1
            except TACOError :
                return 0

        def printstatus(self) :
            """
            Gives some information about the current state of the axis.
            """
            try :
                print "Motor position : ", self.motor.read()
                #print "Encoder Position : ", self.read() #MP 29.12.2009 08:31:05
                print "Low limit switch : ", self.sll.read()
                print "High limit switch : ", self.shl.read()
                print "Reference switch : ", self.sref.read()
            except TACOError :
                print "Could not get the status"

        #-----------------------------------------------------------------------
        def doSetPar (self,lable,Data):
            """keep deviceState"""
            Debug = self.__Debug and False
            if Debug: print 'AXES setpar ',lable,' to ',Data
            #self.yes.enter_setpar(self.motor.deviceQueryResource(lable),Data)
            line = 'setpar %s from %s to %s'%(str(lable),self.motor.deviceQueryResource(lable),str(Data))
            if self.__readonly:
                self.ll_log(line+' BLOCKED',True)
                return
            self.ll_log(line,Debug)
            if self.motor.deviceState() == TACOStates.DEVICE_OFF:
                makeON = False
            else:
                makeON = True
                self.motor.deviceOff()
            if Debug: print 'deviceState:',TACOStates.stateDescription(self.motor.deviceState())
            if Debug: print 'makeON =',makeON
            self.motor.deviceUpdateResource(lable,str(Data))
            if Debug: print 'witten'
            if makeON: self.motor.deviceOn()
        #-----------------------------------------------------------------------
        def problem (self,ort,exc_info):
            Debug = self.__Debug #and False
            if self.__readonly: return None
            merken = exc_info.exc_info()[:]
            line  = 'problem'
            line += ' ort >%s<'%ort
            try:    line += ' MSG >%s<'%str(exc_info.exc_info()[1])
            except: line += ' MSG >%s<'%str(exc_info.exc_info())
            line += ' Debug %s'%str(Debug)
            self.ll_log(line,Debug)
            time.sleep(1.0)
            if True or Debug:
                if   '><'                                                              in line:
                    print 'und?'             #ist zu sehen
                    raise Error('Keybord!')  #wird abgefangen!
                elif   'cannot execute command : Lost connection to the device server' in line: pass #self.serverlock()
                elif   'RPC client call timed out'                                     in line: pass
                if self.recursive_break > 5:
                    self.ll_log('recursive_break',True)
                    self.serverlock()
                else:
                    self.recursive_break += 1
                    if    ort == 'status':res = self.state() #recursive infinite!
                    elif  ort == 'read':
                        self.state() #to catch FAULT
                        res = float(self.read())  #recursive infinite!
                    else:                 res = None
                    self.recursive_break = 0
                    return res

        #-----------------------------------------------------------------------
        def serverlock (self):
            """this metode of parts waits until deviceOFF sleep(10*60) deviceON
            """
            ###
            #-------------------------------------------------------------------
            def server_wait_state (will,Debug=False):
                while True:
                    try:    state=self.motor.deviceState()
                    except: state='readerror'
                    if Debug:
                        if type(state) == type(''): print state
                        else:                       print TACOStates.stateDescription(state)
                    for i in will:
                        if state == i:return
                    time.sleep(10)
            #-------------------------------------------------------------------
            if self.__readonly: return
            Debug = self.__Debug
            if Debug: sleeptime = 10
            else:     sleeptime = 10  #*60
            #-------------------------------------------------------------------
            line = self.name+' serverlock wait for OFF'
            self.upper.ll_log(line,True)
            self.upper.news_spread(line)
            server_wait_state([TACOStates.DEVICE_OFF],Debug)
            #-------------------------------------------------------------------
            line = self.name+' serverlock nap for %dsec so back @ >%s<'%(sleeptime,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()++sleeptime)))
            self.upper.ll_log(line,True)
            time.sleep(sleeptime)
            #-------------------------------------------------------------------
            line = self.name+' serverlock wait for ON'
            self.upper.ll_log(line,True)
            server_wait_state([TACOStates.DEVICE_NORMAL,TACOStates.ON],Debug)
            #-------------------------------------------------------------------
            line = self.name+' serverlock leaving'
            self.upper.ll_log(line,True)
            self.upper.news_spread(line)
            #-------------------------------------------------------------------

        #-----------------------------------------------------------------------
        def ll_log (self,line,screen=False):self.upper.ll_log(self.name+'>'+line,screen)

        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------


    #---------------------------------------------------------------------------
    def doSoftware (self):
        res = cl_no.doSoftware(self)
        #res = {}
        #res['debug']     = self.__Debug
        #res['readonly']  = self.__readonly
        #res['Startstyle']= self.__startstyle
        #res['Zustand']   = self.Zustand
        #res['Historie']  = self.Historie[-1]
        ##res.update(cl_no.software(self))
        try:
            self.mask
            res['Table']        = self.masktable
            res['Width']        = self.width
            res['Mask']         = self.mask
            res['beamtoleranz'] = self.beamtoleranz
        except: pass
        return res

    #---------------------------------------------------------------------------
    def doInit (self, mode, startstyle=''):
        """
        constructor. Creates a complete NOK object the names of the used devices must
        follow the convention, otherwise it breaks.
        @param nbr number of the NOK
        @param prefix prefix of the TACO device name
        """
        #***********************************************************************
        Debug = self.__Debug #and False
        Zeitmessung = Debug and False
        res = 'doInit nok'
        if Debug: print res,
        Debug = False
        if startstyle == '':startstyle=self.__startstyle
        dauer = cl_zeitpunkt()
        #***********************************************************************
        self._axes = []
        self.naxes = len(self.motor)
        if self.naxes != len(self.encoder) or self.naxes != len(self.refswitch) or self.naxes > 2 \
            or self.naxes != len(self.refpos) or self.naxes != len(self.lowlimitswitch) or \
            self.naxes != len(self.highlimitswitch) :
            raise OutofBoundsError("Parameter length mismatch")
        #***********************************************************************
        dauer.read('Loop',Zeitmessung)
        #if Debug: print 'proof controller',
        for j in range(self.naxes):
            #dauer.read('NOKAxis anlegen wie gehabt, todo ###',Zeitmessung)
            _axis = self.NOKAxis(self,j)
            # richtigen Controller anlegen ctrl_Reset -> IPCSMS
            if IPCSMS:
                _axis.MOTORctrl = cl_CONT_IPCSMS(self,_axis.motor.deviceQueryResource("busaddr"))
                #print 'JA!' ### todo wo anders?, da: gobal, dann loop achsen
                #if SSO(startstyle,'quick'):
                if SSO(startstyle,'proof'):
                    try:    _axis.MOTORctrl.proof_controller(),
                    except: 'proof_controller fail',
            self._axes.append(_axis)

        #***********************************************************************
        self.no('_Nok__','motor','','_axes')
        cl_do_get.doInit(self,mode,self.__doget_help,'_axes')
        dauer.read('no do_get',Zeitmessung)
        #***********************************************************************
        dauer.read('Geometrie laden',Zeitmessung)
        try:
            try:
                try:    self.OBF_geo
                except: self.OBF_geo = self.try_ConfigObj(self.__geometire_file+self.__file_sufix)
                maskchange     = 1 #steuert reinit
                try:    self.masktable
                except: maskchange = 0
                Tmasktable    = self.OBF_geo[self.name+'_mask']
                Twidth        = float(self.OBF_geo['beamheight'])
                Tbeamtoleranz = float(self.OBF_geo['toleranz'])
            except:
                raise Error('Fehler config file')
                #keine ausreichende Eintraege im Config File
                #pass
            #                             move(A)
            self.typ = 'mask'  #for slit  [A,old]
            #self.typ = 'kanal' for NOKs  [A,  A] auch kanal kann masken habe: [NL RK TK VK]
            #self.typ = 'achse' wie gehabet compatible
            if Debug and False:
                print #formal
                print 'for Convert',Tmasktable
            try:
                for k in Tmasktable.keys():
                    if Debug: print 'mask %5s'%k,
                    for a in range(len(Tmasktable[k])):Tmasktable[k][a] = float(Tmasktable[k][a])
                    if Debug: print 'read',
                    try:   open   = Tmasktable[k][2]
                    except:open   = 0.0
                    try:   offset = Tmasktable[k][3]
                    except:offset = 0.0
                    #if False: #wie gehabt
                    if self.naxes == 1:
                        if Debug: print 'extract',
                        if True: #erweitern, alles speichern
                            Tmasktable[k].append(Tmasktable[k][1])
                            Tmasktable[k][1] = Tmasktable[k][0]
                        if Debug: print 'calculate',
                        Tmasktable[k][0] = Tmasktable[k][0] + offset
                        """ die indizex:
                        in geometrie.inf stehen die Werte 1 bis 2
                        0 Wert for achse [0]
                        1 offset for maske achse [0]
                        2 korrektur high
                        """
                        #if not Debug:
                        #    print 'Developing'
                        #    raise Error('Developing')
                    elif self.naxes == 2:
                        if Debug: print 'extract',
                        if True: #erweitern, alles speichern
                            Tmasktable[k].append(Tmasktable[k][2])
                            Tmasktable[k].append(Tmasktable[k][3])
                            Tmasktable[k][2] = Tmasktable[k][0]
                            Tmasktable[k][3] = Tmasktable[k][1]
                        if Debug: print 'calculate',
                        Tmasktable[k][0] = Tmasktable[k][0] + open/2 + offset
                        Tmasktable[k][1] = Tmasktable[k][1] - open/2 + offset
                        """ die indizex:
                        in geometrie.inf stehen die Werte 2 bis 5
                        0 Wert for achse [0]
                        1 Wert for achse [1]
                        2 offset for maske achse [0]
                        3 offset for maske achse [1]
                        4 korrektur open
                        5 korrektur high
                        """
                    else:
                        line = 'suspishus element %d'%self.naxes
                        if Debug: print #formal
                        print line
                        raise Error(line)
                    #while len(Tmasktable[k])>2:Tmasktable[k].pop()
                    if Debug: print '<'
            except:
                if Debug: print 'Fehler Convert config file'
            if Debug and False: print 'nach Convert',Tmasktable
            self.mask = '' #nur Init
            if maskchange                     and \
              Tmasktable    == self.masktable and \
              Twidth        == self.width     and \
              Tbeamtoleranz == self.beamtoleranz:# and not self.__Debug:
                maskchange = 2
            else:
                if maskchange:
                    old = self.do_get('read') #read extra but seldom
                    #old = self.doget('read') #read extra but seldom
            self.masktable    = Tmasktable
            self.width        = Twidth
            self.beamtoleranz = Tbeamtoleranz
        except:
            if Debug: print 'Geometrie laden fail so simple achse'
            self.typ = 'achse' #wie bisher
        #-----------------------------------------------------------------------
        if SSO(startstyle,'normal'):
            dauer.read('numeric',Zeitmessung)
            #try:    dic = self.doget(['simple','read'],SSO(startstyle,'show')) # proof Poti
            try:    dic = self.do_get(['simple','read'],SSO(startstyle,'show')) # proof Poti
            except:
                print
                dic = {'simple':'fatal doget fail proof: positon, Encoder, resources'}
            numeric = None
            if dic['simple'] != 'ready': print 'no numeric init >%s< '%dic['simple'],
            else:                        numeric = dic['read'] #pos mit alten Parameter (masken)
            try:    print self.mask,
            except: print 'achse',
        else: self.maskoffset = None
        if SSO(startstyle,'show'): print numeric,
        #if Debug: print #formal
        #-----------------------------------------------------------------------
        dauer.read('recourcen laden (proof) todo',Zeitmessung)
        #-----------------------------------------------------------------------
        dauer.read('Zustand loggen',Zeitmessung)
        self.ll_log(str(self.doSoftware())) #Zustand beim Start loggen
        #-----------------------------------------------------------------------
        dauer.read('Mask change?',Zeitmessung)
        if   maskchange == 0: res = 'init'
        elif maskchange == 1: res = 'old:'+str(old)+'new:'+str(numeric)
        elif maskchange == 2: res = ' ok '
        else:                 raise Error('ill maskchange code >%s<'%str(maskchange))
        print res,
        #-----------------------------------------------------------------------
        dauer.read('loading Parameter from resourses.inf',Zeitmessung)
        resources = self.try_ConfigObj(self.__resources_file+self.__file_sufix)
        try:    self.param = resources[self.name]
        except: print 'NO parameters',
        dauer.read('Pfertig',Zeitmessung)
        if SSO(startstyle,'proof'):
            info=' proof FAIL!'
            if self.proof_resources(False): info=' proofed'
            else:                           print
            print info,
            res += info
        self.diary = self.doDiary
        return res

    #---------------------------------------------------------------------------
    def doget (self,argList=[],Logging = True): return self.do_get(argList,Logging)
    def doDiary (self):  return {'Line':self.do_get('diary'),'Name':self.name,'Time':600}
    def doRead (self):   return self.do_get('read') #MP 07.01.2011 10:21:06
    def doStatus (self): return self.do_get('status') #MP 30.11.2011 10:46:47

    #---------------------------------------------------------------------------
    def doStart (self, a_pos, usemask = True):#, force=False): #usemask 11.01.2011 08:24:32
        """
        moves all axes to the given postitions
        singel numbers are: for noks both axes; for doubleslits open
        take:      used:   nok       eg b1             Hint
        6.0                [6.0,6.0] [6.0,old]
        [6.0,0.1]          [6.0,0.1] [6.0,0.1]
        6.0,'slit'         fail      [6.0,old],'slit'
        [6.0,0.1],'slit'   fail      [6.0,0.1],'slit'
        [6.0,'slit']       fail      [6.0,old],'slit'
        [6.0,0.1,'slit']   fail      [6.0,0.0],'slit'  this is for D4A
        MP 30.11.2011 13:50:08 what is used for what? _pb
        a_pos :argument
        never! units
        pos   :used as hight of doubleslit
        """
        """Konzept:
        Starting
        *reading element
        *logging
        *Pending move [raise|stop|info]
        mask         calculating mask [achse|slit|...]
        limits
        *inclination
        *userboarder
        move
        *backlock    suspischus: switch touched?
        Finalisation [wait,run]
        """
        #-----------------------------------------------------------------------
        Debug = self.__Debug #and False
        pending_move_stop = True
        raise_on_error = not self.__Debug #todo global machen mit Konzept
        if (type(a_pos) != type([])) and (type(a_pos) != type(())): a_pos = [a_pos]
        if type(a_pos[-1]) == type(''):usemask = a_pos.pop(-1)
        if   usemask == False: usemask = 'achse'
        elif usemask == 'achse':pass
        elif (type(usemask) == type('')) and (usemask not in self.masktable.keys()):
            line = 'unknown mask >%s<'%usemask
            self.ll_log(line)
            raise Error(line)
        if Debug: print 'naxes',self.naxes,'a_pos',a_pos,'usemask',usemask




        #-----------------------------------------------------------------------
        #if Debug: print 'vor',self.mask,self.maskoffset
        get=self.enter_move(a_pos)
        #if Debug: print 'nach',self.mask,self.maskoffset
        if Debug: print '_nok doStart:',
        #-----------------------------------------------------------------------
        if self.typ == 'mask':
            if Debug: print 'typ == mask'
            #if self.maskoffset == None:
            #if not usemask:
            if usemask == 'achse':
                while len(a_pos) < len(self._axes): a_pos.append(a_pos[0])
                self.ll_log('achsenmove',Debug)
                #pos = a_pos[:] #units BUG!
                #QAD MP 03.01.2012 09:27:03
                #reactor = a_pos[0]
                #sample  = a_pos[1]
                self.maskoffset = self.masktable[self.mask]
            else:
                if   self.naxes == 1:
                    #if type(usemask) == type(''):
                    if usemask == True:usemask = self.mask
                    if Debug: print usemask,self.mask
                    pos = self.masktable[usemask][0] + a_pos[0]
                    self.ll_log('print P:%s U:%s '%(str(pos),str(a_pos)),True)
                    a_pos= [pos]
                elif self.naxes == 2:
                    #hight ++
                    if len(a_pos) == 1 : hight = get['read'][1]  #MP 15.11.2011 15:03:51
                    else :               hight = a_pos[1]
                    #if type(usemask) == type(''):
                    if usemask == True:usemask = self.mask
                    if Debug: print usemask,self.mask
                    reactor = hight + self.masktable[usemask][0] - (self.width - a_pos[0]) / 2.0
                    sample  = hight + self.masktable[usemask][1] + (self.width - a_pos[0]) / 2.0
                    #else:
                    #    reactor = hight + self.maskoffset[0] - (self.width - a_pos[0]) / 2.0
                    #    sample  = hight + self.maskoffset[1] + (self.width - a_pos[0]) / 2.0
                    self.ll_log('print H:%s R:%s S:%s U:%s '%(str(hight),str(reactor),str(sample),str(a_pos)),True)
                    #hight --
                    a_pos= [reactor, sample]
                else:
                    line = 'naxes %s'%self.naxes
                    print line
                    raise Error(line)
        else:
            if Debug: print 'typ:',self.typ
            while len(a_pos) < len(self._axes): a_pos.append(a_pos[0])
        #if Debug: print 'a_pos:',a_pos,get
        #-----------------------------------------------------------------------
        if len(a_pos) > 1:
            diff = a_pos[1] - a_pos[0]
            if self.posinclination > 0 and diff > 0 and diff > self.posinclination :
                raise OutofBoundsError("Given target position would increase the positive inclination")
            elif self.neginclination < 0 and diff < 0 and diff < self.neginclination :
                raise OutofBoundsError("Given target position would decrease the negative inclination")
        if Debug: print 'passed inclination Test'
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        if get['simple'] != 'ready':
            if pending_move_stop:
                #self.doStop() #old moveing
                pass
            else:
                line = 'pending movment no stop interrupting comand not >%s<'%get['simple']
                self.exit_move(line)
                if raise_on_error: raise Error(line)
                else:              return line
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        if Debug: print 'start first move'
        for i in range(len(self._axes)): self._axes[i]._movestep1(a_pos[i])
        if Debug: print 'and Wait'
        self.doWait()
        akt_pos = self.__achsread()
        for i in range(len(self._axes)):
            if float(akt_pos[i]) > a_pos[i]:
                self.ll_log('move suspischus'+str(i)+' '+str(akt_pos)+' '+str(a_pos)+' '+str(self.status()),True)
                if self.__readonly: print 'pass'
                else:               return
        #if Debug: self.ll_log('extra Info: '+str(self.read())+' '+str(self.status()),True)
        #print a_pos
        #-----------------------------------------------------------------------
        if Debug: print 'start second move'
        for i in range(len(self._axes)):
            res = self._axes[i]._movestep2(a_pos[i])
            if Debug: print '_movestep2 i=%d res='%i,res
        #07.01.2010 08:59:04 MP
        #if False:
        if True:
            if Debug: print 'and Wait'
            self.doWait()
            for i in range(len(self._axes)):
                if (float(akt_pos[i]) - a_pos[i]) > 0.00125:
                    self.ll_log('move unreached'+str(i)+' '+str(akt_pos)+' '+str(a_pos)+' '+str(self.status()),True)
        #-----------------------------------------------------------------------
        self.exit_move()
        return

    #---------------------------------------------------------------------------
    def doWait (self):
        self.enter_wait()
        for axis in self._axes:axis.wait()
        time.sleep(0.5) #26.10.2009 14:31:51 tribute to poti
        return self.exit_wait()

    #---------------------------------------------------------------------------
    def doStop (self):
        #self.ll_log('sorry no stop!!!',True)
        #raise 'sorry no stop!!!'
        """
        File "/opt/taco/lib64/python2.5/site-packages/Motor.py", line 13, in stop
        self.execute( TACOCommands.STOP)
        TACOClient.TACOError: Client not connected
        """
        Debug = self.__Debug or True
        min = 3
        notausgang = 10
        movement = False
        self.ll_log('Enter STOP')
        S = ''
        while True:
            time.sleep(1.0) #1 zu kurz
            ok = True
            l = ''
            for axis in self._axes:
                try:   S = axis.motor.deviceStatus() #status()
                except:
                    notausgang -= 1
                    if Debug: print 'status notausgang -= 1'
                l += S+' '
                if S == 'moving':
                    movement = True
                    try:    axis.motor.stop()
                    except:
                        notausgang -= 1
                        if Debug: print 'STOP notausgang -= 1'
                    time.sleep(0.2)
                    ok = False
            if Debug: print l
            if ok:
                min -= 1
                if min <= 0:break
            else: min = 2
            if notausgang <= 0:
                line = 'Notausgang in stop'
                self.ll_log(line,True)
                raise Error(line)
        self.ll_log('STOP performed. movement: %s'%str(movement),Debug)

    #---------------------------------------------------------------------------
    def doDump (self,log=False):
        """Prelimanary. do not use this funcion, untill you know wath you are doing"""
        """every dump-function should write Parameters from the controller
        with can be changed by user or change in a file to get a backup
        this is only usefull for parts how has so values eg not for the chopper
        ofcours istrument does it for all parts from instrument.inf"""
        ddata=[]
        for axis in self._axes:
            ddata.append(axis.MOTORctrl.ctrlDebug())
        #if log: self.yes.dump(self.name,ddata)
        if log: self.dump(self.name,ddata)
        return ddata

    #---------------------------------------------------------------------------
    def doSetPar (self,name,value):
        Debug = self.__Debug #and False
        self.ll_log('setpar: Name:%s Value:%s'%(str(name),str(value)),Debug)
        #if not hasattr(self,name):
        #    self.ll_log("unkown parameter name '"+name+"' : check spelling")
        #    __main__.NicmPrint(__main__.PM_STANDARD,"unkown parameter name '"+name+"' : check spelling")
        #    return
        if name in['mask']:
            try:    self.mask
            except: return
            if value == 'achse':
                self.ll_log('mask changend to achse',Debug)
                self.maskoffset = None
            else:
                try :
                    self.ll_log('mask changend to '+str(value),Debug)
                    self.wait()
                    #MP 08.01.2010 08:55:58
                    #MP 24.01.2011 11:17:07 kein Fehler!
                    pos = self.do_get(['status','read'],False)['read']#self.__read()
                    if Debug: print 'test for good numbers'
                    try:    use = self.width * self.beamtoleranz
                    except: use = 12 *1.5
                    for a in range(len(pos)):
                        if pos[a] > use:pos[a] = 0.0
                    #pos = self.doget('read',False)#self.__read()
                    #pos = [pos[0],pos[1]] #16.04.2009 14:12:03 MP
                    self.maskoffset = self.masktable[value]
                    try:
                        self.doStart(pos)
                        self.wait()
                        setattr(self, name, value)
                    except:
                        self.ll_log("could not move to"+str(pos),Debug)
                        self.__NicmPrint("could not move to"+str(pos))
                except :
                    self.ll_log("No such position (%s) defined! " % value,Debug)
                    self.__NicmPrint("No such position (%s) defined! " % value)
        elif name in ['width', 'masktable'] :
            self.ll_log('Attribut '+name+' set '+value)
            setattr(self, name, value)
        else:
            if Debug: print 'try devices'
            if True: #try: #das hier war das alte direction und so
                #res = []
                if type(value) == type(''): value = [value]
                if Debug: print 'start test loop'
                #for count in range(len(value)):
                #    if type(value[count]) != type(''):
                #        print 'Part',count,'only string',value[count]
                #        return
                if Debug: print 'start loop'
                for count,axis in enumerate(self._axes):
                    try:    value[count]
                    except: value.append(value[0])
                    if Debug: print 'Achse',count,'name',name,'Wert',value[count]
                    axis.doSetPar(name,value[count])
                    if Debug: print 'ok'
            else: #except:
                self.ll_log("not a user changeable parameter!")
                self.ll_log("command ignored!")
                self.__NicmPrint("not a user changeable parameter!")
                self.__NicmPrint("command ignored!")
    #---------------------------------------------------------------------------
    def doInfo (self,typ=None):
        #-----------------------------------------------------------------------
        def vabs (a):
            res = []
            for c in range(len(a)):res.append(abs(a[c]))
            return res
        #-----------------------------------------------------------------------
        def sub (a,b):
            if len(a) != len(b):raise 'len in sub'
            res = []
            for c in range(len(a)):res.append(a[c]-b[c])
            return res
        #-----------------------------------------------------------------------
        def dauer(t,Text=''):
            if t == 0:
                print '%s'%Text
                return time.time()
            u = time.time()
            print '%s %.4f'%(Text,(u-t))
            return u
        #-----------------------------------------------------------------------
        Debug = self.__Debug
        if typ == None: Typlist = ['usermax','_refPoint','usermin']
        elif type(typ) == type([]):Typlist = typ
        elif typ == 'limit':Typlist = ['limitmax','usermax','_refPoint','usermin','limitmin']
        elif typ == 'all':Typlist = ['limitmax','usermax','_refPoint','usermin','limitmin','stepsperunit','offset','accel','speed','backlash','direction','busaddr']
        if Debug: tt = dauer(0,'Dauer?')
        Pram = {}
        Pram['My Name is']=self.name
        Data = self.do_get('all',False)
        Pram['My axes are at']=Data['achse']
        Pram['I am at']       =Data['read']
        Pram['I feel']=self.do_get('all')
        Pram['I do like']     =Data['status']
        for a in Typlist: Pram[a]=self.doGetPar(a)
        try:    Pram['Poti']=str(Data['Poti'])
        except: Pram['Poti']='can not be read'

        Pram['I am a']=self.typ
        try:
            self.mask
            Pram['mask']=self.mask
            Pram['maskoffset']=self.maskoffset
        except: pass
        for a in ['max','min']:
            try:    Pram['dif_'+a]=vabs(sub(Pram['limit'+a],Pram['user'+a])),':'+a
            except: pass
        if Debug: tt = dauer(tt,'done')
        return Pram
    #-----------------------------------------------------------------------
    def doPotitest (self,argument):
        try:    self.t.fulltest
        except: return 'no tracer'
        return self.t.fulltest(argument[0],argument[1],argument[2],argument[3])
        #klingt komisch, ist aber so
    #-----------------------------------------------------------------------
    def doKalib (self,data,doRESET = True): ###
        self.ll_log('Begin kalib',True)
        try:    self.t.kalib
        except: return 'no tracer'
        if doRESET:
            self.ll_log('start reset',True)
            try:    res=self.doReset(False) #ohne Poti
            except: self.ll_log('reset fail but accept',True)
        else:
            self.ll_log('no reset',True)
        self.ll_log('reset finisch, start kalib',True)
        f=self.t.kalib(data)
        #!!! MP 28.12.2009 00:22:02
        #try:    f=self.t.kalib(data)
        #except: return 'tracer failed'
        self.ll_log('tracer finisch, start reorg',True)
        try:    self.t.reorgfile(f)
        except: return 'reorg failed'
        self.ll_log('reorg finisch',True)
        return 'kalib finisch'
    #-----------------------------------------------------------------------
    def __achsread (self):
        """keine masken
        """
        val = self.do_get('achse')
        #Historisch todo MP 07.01.2011 10:40:59
        if type(val) != type([]):val = [val]
        return val
    #-----------------------------------------------------------------------
    def __achsmove(self,pos):
        """keine masken"""
        self.doStart(pos,False)

    #---------------------------------------------------------------------------
    def doReset (self,use_encoder=True):
        """
        moves a NOK's axes to the point where the reference-switch triggers
        new 06.11.2008 10:36:37 MP
        tun status von ICPM testen 512?
        Ablauf reset:
         move Start
         move ref
         move check
         move Zero
        """
        #-----------------------------------------------------------------------
        def add (a,b):
            if len(a) != len(b):raise 'len in add'
            res = []
            for c in range(len(a)):res.append(a[c]+b[c])
            return res
        #-----------------------------------------------------------------------
        def equ (a,b):
            if type(b) != type([]): b = [b] #() lokal
            if len(b) == 1:
                #raise 'equ aufblasen' #MP 01.03.2010 21:50:55
                b = list(b[0] for n in range(len(a)))
            if len(a) != len(b):
                print 'a',a
                print 'b',b
                raise 'len in equ'
            res = []
            for c in range(len(a)):
                if a[c] != b[c]:return False
            return True
        #-----------------------------------------------------------------------
        def sub (a,b):
            if len(a) != len(b):
                print 'a',a
                print 'b',b
                raise 'len in sub'
            res = []
            for c in range(len(a)):res.append(a[c]-b[c])
            return res
        #-----------------------------------------------------------------------
        def mul (a,b):
            if type(b) != type([]): b = [b] #() lokal
            if len(b) == 1:
                #raise 'mul aufblasen' #MP 01.03.2010 21:50:55
                b = list(b[0] for n in range(len(a)))
            if len(a) != len(b):
                print 'a',a
                print 'b',b
                raise 'len in mul'
            res = []
            for c in range(len(a)):res.append(a[c]*b[c])
            return res
        #-----------------------------------------------------------------------
        def div (a,b,r=True):
            if type(b) != type([]): b = [b] #() lokal
            if len(b) == 1:
                b = list(b[0] for n in range(len(a)))
            if len(a) != len(b):
                print 'a',a
                print 'b',b
                raise 'len in div'
            res = []
            for c in range(len(a)):
                if r:  res.append(a[c]/b[c])
                else:
                    try:    res.append(a[c]/b[c])
                    except: res.append('div by zero')
            return res
        #-----------------------------------------------------------------------
        def choose (a,b,c):
            if len(a) != len(b) or len(a) != len(c):
                print 'a',a
                print 'b',b
                print 'c',c
                raise 'len in choose'
            res = []
            for d in range(len(a)):
                if c[d]:res.append(a[d])
                else:   res.append(b[d])
            return res
        #-----------------------------------------------------------------------
        #-----------------------------------------------------------------------
        def format (Data,typ=3):
            try:    return ' %.3f'%Data
            except:
                res = ''
                for a in range(len(Data)):
                    res += ' %.3f'%Data[a]
                return res
        #-----------------------------------------------------------------------
        def do_get_flags(dic,Lable):
            """QAD konvert the flags from do_get to older format
            eg do_get_flags(dic,'LOW')
            dic = [{'HIGH': 0L, 'LOW': 0L, 'REF': 0L}, {'HIGH': 0L, 'LOW': 1L, 'REF': 0L}]
            Label = 'LOW'
            return [0L, 1L]
            """
            ret = []
            for i in range(len(dic)): ret.append(dic[i][Lable])
            return ret
        #-----------------------------------------------------------------------
        #def Poti_convert (Data):
        #    Data = Data['Poti']
        #    res = []
        #    for a in range(len(Data)): res.append(Data[a]['Position'])
        #    return res
        #-----------------------------------------------------------------------

        #-----------------------------------------------------------------------
        Debug = self.__Debug #and False
        self.ll_log('***************',False)
        self.ll_log('* Start Reset *',True)
        self.ll_log('***************',False)
        speedswitch   = True
        force_low     = True
        #use_encoder   = True and self.__Debug
        runtimetest = Debug and False #wirklich gut?
        if runtimetest: self.ll_log('runtimetest',True)
        #Notausgang
        try:
            self.param['goodspeed']
            self.param['fullspeed']
            self.param['refspeed']
        except:
            if speedswitch == True: self.ll_log('no speedswitch missing Parameter',Debug)
            speedswitch = False
        #-----------------------------------------------------------------------
        #Variablen to work, ok it is Phyton, we do not need to declarate ;-)
        #if Debug:
        #    Speed    = [] #debug
        naxes = len(self._axes)
        somewhat   = list(3.3 for n in range(naxes)) #backlash = 2 #nok2 3.4
        Zero       = list(0 for n in range(naxes))
        SWon       = list(1 for n in range(naxes))
        trys     = 1  #scale for somwath under ref depens on negES-usermin
        jumppoints = [[],[]]
        #QAD die kleiner inlination gilt für beide
        inclination = min([abs(self.posinclination),abs(self.neginclination)])
        #-----------------------------------------------------------------------
        #proof resources
        #if Debug: print 'doInit(proof)' #wegen mask
        #self.doInit('proof')
        try:
            self.mask
            self.mask = ''
            self.ll_log('Mask cleared',Debug) ###
        except:
            if Debug: print 'no MASK'
        if Debug: print 'proof_resources'
        if self.proof_resources():pass
        else:
            line = 'Disaster: resources: deny reset! ask MP'
            self.ll_log(line,True)
            return line
        #-----------------------------------------------------------------------
        try:    self.ll_log('Backlash'+str(self.doGetPar('backlash')),True)
        except: self.ll_log('Backlash no',True)

        if speedswitch: self.ll_log('switching of speed: '+str(self.param),True)
        else:           self.ll_log('no switching of speed, speed is'+str(self.doGetPar('speed')))
        self.ll_log('accel is'+str(self.doGetPar('accel')))

        #-----------------------------------------------------------------------
        ### todo clear number of readings! make use of do_get
        if True or Debug:
            print 'DEBUGFLAG = True'
            get = self.do_get(['read','status','simple','achse','encoder'])
            if get['simple'] != 'ready' and use_encoder:
                self.ll_log('moving, please try later (no Stop avilabl jet) >%s<'%str(get['simple']),True)
                return 'moving, please try later (no Stop avilabl jet) '
            truePosold=get['achse']
            if use_encoder:
                if 'encoder' in get.keys(): force_low     = False
                self.ll_log('use_encoder force_low ='+str(force_low),True)
        else:
            temp = self.status() ###
            if (temp != tuple('on' for axis in self._axes)) and\
               ('stop' not in temp) and\
               ('mask' not in temp):
            #if not('stop' in temp or 'mask' in temp):
                self.ll_log('moving, please try later (no Stop avilabl jet) '+str(temp),True)
                return 'moving, please try later (no Stop avilabl jet) '
            #if Debug: print 'creating points to move'

            truePosold=self.__achsread() #hier hat alles angefangen
        truePos=truePosold

        #-----------------------------------------------------------------------
        minPos     = self.doGetPar("usermin")
        maxPos     = self.doGetPar("usermax")
        refPoint   = self.doGetPar("_refPoint")
        self.ll_log('DebugInfo'\
                #' speed:'+str(Speed)+\
                ' minPos:'+str(minPos)+\
                ' maxPos:'+str(maxPos)+\
                ' refPoint:'+str(refPoint)+\
                ' END',Debug)

        restWay = mul(sub(maxPos,minPos),2)
        self.ll_log(' restWay:'+str(restWay),True)
        #for count in range(len(self._axes)):restWay.append(maxPos[count]-minPos[count])

        if force_low:
            #todo Notausgang
            if speedswitch: self.doSetPar('speed',self.param['fullspeed'])
            self.ll_log('start force low',True)
            #aktSW = self.status('low') #MP 02.01.2012 07:50:24
            #aktSW = self.do_get('flags')['LOW']
            aktSW = do_get_flags(self.do_get('flags'),'LOW')
            #print 'aktSW',aktSW
            #print 'SWon',SWon
            #return 'bis hier her'
            while not equ(aktSW,SWon):
                self.ll_log('LOOP',True)
                if min(restWay) <= 0:
                    self.ll_log('prufen maxWay: i give up',True)
                    if speedswitch: self.doSetPar('speed',self.param['goodspeed'])
                    return 'prufen maxWay: i give up'
                self.ll_log('prufen maxWay: ok',True)

                get = self.do_get(['status','achse'])
                self.ll_log('setpos(maxPos)'+str(get['achse'])+' '+str(get['status']),Debug)
                #for count,axis in enumerate(self._axes): axis.motor.setpos(maxPos[count])
                self.dosetpos(sub(maxPos,somewhat))
                aktPOS = self.__achsread()
                restWay=sub(restWay,aktPOS)
                truePos=sub(truePos,aktPOS)
                self.ll_log(str(aktPOS)+' '+' truePos: '+str(truePos),Debug)

                self.ll_log('moving to close to minPos',True)
                print 'aktSW',aktSW,'aktPOS',aktPOS,'minPos',minPos,'somewhat',somewhat
                if not runtimetest:
                    if max(aktSW)==0: self.__achsmove(add(minPos,somewhat))#,True)
                    else:             self.__achsmove(choose(aktPOS,add(minPos,somewhat),aktSW))#,True)
                    self.wait()
                aktPOS=self.__achsread()
                restWay=add(restWay,aktPOS)
                truePos=add(truePos,aktPOS)
                #aktSW = self.status('low') #MP 02.01.2012 07:50:44
                #aktSW = self.do_get('flags')['LOW']
                aktSW = do_get_flags(self.do_get('flags'),'LOW')
                if runtimetest: break
            self.ll_log('ready'+' read:'+str(self.__achsread())+' status:'+str(self.status())+' truePos:'+str(truePos)+' END',Debug)
            #print 'minPos for',minPos
            self.dosetpos(minPos)
            #print 'minPos nach',minPos
            #restWay = []
            #for count in range(len(self._axes)):restWay.append(maxPos[count]-minPos[count])
            restWay = mul(sub(maxPos,minPos),2)
            self.ll_log('restWay:'+str(restWay),True)
            self.ll_log('low reached',True)

        #jumppoints
        self.ll_log('calculating on or two "jumppoints"',Debug)
        #Historisch Nonsens jumppoints[0].append(min(refPoint)-somewhat[0]*trys)
        #inclination 0 ==> keine Grenze!
        if (inclination == 0)or(abs(min(refPoint)-max(refPoint)) < inclination):
            jumppoints[0] = sub(refPoint,somewhat)
            for a in range(trys-1):
                jumppoints[0] = sub(jumppoints[0],somewhat)
        else:
            for axis in self._axes:
                jumppoints[0].append(min(refPoint)-somewhat[0]*trys)
                jumppoints[1].append(max(refPoint)-somewhat[0]*trys)
        if len(jumppoints[1])==0:del jumppoints[1]
        self.ll_log('jumppoints: '+str(jumppoints),True)
        if len(jumppoints) == 1:Multi = False
        else:
            Multi = True
            sref = refPoint[:]
            sref.sort()
        for a in range(len(jumppoints)):
            if Multi:
                Multiakt = refPoint.index(sref[a])
                self.ll_log('jump to %d. jumppoint for axes %d'%(a+1,Multiakt),True)
            else:
                self.ll_log('jump to jumppoint'+str(jumppoints[a]),True)
            if not runtimetest:
                self.__achsmove(jumppoints[a])#,True)
                self.wait()
            if Multi:
                if self._axes[Multiakt].sref.read() > 0:
                    self.ll_log('jump into ref!',True)
                    if speedswitch: self.doSetPar('speed',self.param['goodspeed'])
                    return 'jump into ref!'
            else:
                if max([axis.sref.read() for axis in self._axes]) > 0:
                    self.ll_log('jump into ref!',True)
                    if speedswitch: self.doSetPar('speed',self.param['goodspeed'])
                    return 'jump into ref!'
            nochmal = True
            if speedswitch: self.doSetPar('speed',self.param['refspeed'])
            while nochmal:
                if self.name == 'b1':Debug = True
                if min(restWay) <= 0:
                    self.ll_log('prufen maxWay: i give up',True)
                    if speedswitch: self.doSetPar('speed',self.param['goodspeed'])
                    return 'prufen maxWay: i give up'
                self.ll_log('prufen maxWay: ok',True)
                restWay=add(restWay,self.__achsread())
                self.ll_log(\
                      ' read:'+str(self.__achsread())+\
                      ' status:'+str(self.status())+\
                      ' END',Debug)
                self.ll_log('START REF move',True)
                if not runtimetest:
                    if Multi: self._axes[Multiakt]._refmovestart()
                    else:
                        for axis in self._axes: axis._refmovestart()
                    #if Debug: self.ll_log('wait',True)
                    self.wait()
                restWay=sub(restWay,self.__achsread())
                self.ll_log(''+\
                      ' min:'+str(min(restWay))+\
                      ' restWay:'+str(restWay)+\
                      ' read:'+str(self.__achsread())+\
                      #' status:'+str(self.status('all'))+\ MP 02.01.2012 07:51:09
                      ' status:'+str(self.do_get('all'))+\
                      ' END',Debug)
                if Multi: nochmal = (self._axes[Multiakt].sref.read() != 1)
                else:     nochmal = ([axis.sref.read() for axis in self._axes] != SWon)
                #27.12.2009 11:56:38 MP b1 debug:
                if Debug:
                    line=self.name+' N:'+str(nochmal)+' R:'+str([axis.sref.read() for axis in self._axes])
                    self.ll_log(line)
                    if False:
                        try:
                            self.news_spread(line)
                        except: pass
                if runtimetest:break
            if Multi: self._axes[Multiakt].setpos(refPoint[Multiakt])  #.motor
            else:
                for count,axis in enumerate(self._axes): axis.setpos(refPoint[count])  #.motor
            self.ll_log('%d/%d ref reached'%(a+1,len(jumppoints)),True)

        if speedswitch: self.doSetPar('speed',self.param['goodspeed'])
        self.ll_log('reset final move to Zero started',True)
        if not runtimetest:
            self.__achsmove(Zero)
            self.wait()

        #format leading ' '
        try:    Fehlpos = ' Fehlpos:'+format(sub(truePosold,truePos))
        except: Fehlpos = ' Fehlpos: no access'
        if runtimetest: self.ll_log('runtimetest',True)
        get = self.do_get('all')
        if get['simple'] == 'ready':
            line = 'Reset finished' #+aktmul+messmul
            self.ll_log('******************',False)
            self.ll_log('* '+line+' *',Debug)
            self.ll_log('******************',False)
            return line
        else:
            line =         'Reset fail'
            self.ll_log('****************',False)
            self.ll_log('* '+line+    ' *',Debug)
            self.ll_log('* '+line+    ' *',Debug)
            self.ll_log('* '+line+    ' *',Debug)
            self.ll_log('****************',False)
            print get
            raise Error(line)

    #---------------------------------------------------------------------------
    #Resettools with poti used in doClear
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    def dosetpos (self,Labellok,axes=[0,1]):
        """this funktions set the given axes to the value
        You can even use labels. Casesensitive
        if no axes is specified, you have to give the value for both axes
        eg
        setposLab(5.0,0)       : set Axes[0] to 5.0     read() = [5.0,???]
        setposLab(1.1)         : sets all Axes to 5.0   read() = [5.0,5.0]
        setposLab('low')       : sets all Axes to lowES read() = [lowEs,lowEs]
        setposLab('ref')       : sets all Axes to refES read() = [ref,ref]
        setposLab('ref',1)     : set Axes[1] to refES   read() = [???,ref]
        setposLab('encoder')   : sets all Axes to Poti  read() = [Potentiometer,Potentiometer]
        setposLab('encoder',0) : set Axes[0] to Poti    read() = [Potentiometer,???]
        """
        #-----------------------------------------------------------------------
        def Poti_convert (Data):
            Data = Data['Poti']
            res = []
            for a in range(len(Data)): res.append(Data[a]['Position'])
            return res
        #-----------------------------------------------------------------------
        Debug = self.__Debug #and False
        #-----------------------------------------------------------------------
        if Debug: print 'Argumenttest'
        if axes == [0,1] and len(self._axes) == 1:axes = [0]
        if type(axes)  != type([]): axes = [axes]
        if type(Labellok) == type([]): Label = Labellok[:]
        else:                          Label = [Labellok]
        if len(Label) > len(axes):raise Error('to many data for axes %s %s'%(str(Label),str(axes)))
        while len(Label) < 2: Label.append(Label[0]) #Label gibt es immer genug
        #-----------------------------------------------------------------------
        if Debug: print 'Data geathering'
        if Debug: print Label,axes
        get = self.do_get(['encoder_pos','simple'])

        if   'fail'  in get['simple']:pass
        elif 'ready' != get['simple']:raise Error('moving deny setpos')

        if 'encoder' in Label:
            try:
                poti = get['encoder_pos']
                if type(poti)  != type([]): poti = [poti]
            except: raise Error('could not read Poti')
        for achse in axes:
            if   type(Label[achse]) == type(0.0): pass  #float
            elif type(Label[achse]) == type(0): pass    #intger
            elif type(Label[achse]) == type(''):        #string
                if Label[achse] == 'encoder': Label[achse] = poti[achse]
                else:                         raise Error('can not set Label >%s<'%Label)
                #Label[achse] = self._axes[achse].doGetPar(Label[achse])
            else: raise Error('wrong type %s for Achse %d in %s'%(str(type(Label[achse])),axes,str(Label)))
        #-----------------------------------------------------------------------
        if Debug: print 'execution'
        if Debug: print 'data for axes >%s< >%s<'%(str(Label),str(axes))
        #-----------------------------------------------------------------------
        if Debug:
            for achse in axes: print Label[achse],'at',achse,
        line = 'dosetpos: arg: '+str(Labellok)+' real: '
        for achse in axes:
            self._axes[achse].setpos(Label[achse])
            line += '%d: %s '%(achse,str(Label[achse]))
        self.ll_log(line)
        if Debug: print 'ready'
    #---------------------------------------------------------------------------
    def doadjustment (self):
        self.doInit(self._mode)
        try:    return self.masktable
        except: return {}
    #---------------------------------------------------------------------------
    #def  __NicmPrint(__main__.PM_STANDARD,"could not move to"+str(pos))
    #def  __NicmPrint(code,str)
    def  __NicmPrint(str):
        try:
            NicmPrint       = ip.user_ns['NicmPrint']
            PM_STANDARD     = ip.user_ns['PM_STANDARD']
        except:
            pass
            #import __main__
            #NicmPrint   = __main__.NicmPrint
            #PM_STANDARD = __main__.PM_STANDARD
        NicmPrint(PM_STANDARD,str)
    #---------------------------------------------------------------------------
    def doCommtest (self,arg):
        Debug = self.__Debug
        iter = arg[0]
        wait = arg[1]
        self.ll_log('doCommtest %d %f'%(iter,wait),True)
        for i in range(iter,0,-1):
            line = '%5d '%i+str(self.do_get())
            self.ll_log(line,True)
            time.sleep(wait)
        self.ll_log('doCommtest done',True)
    #---------------------------------------------------------------------------
