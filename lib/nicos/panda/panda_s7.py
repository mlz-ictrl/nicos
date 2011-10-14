#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#
# *****************************************************************************

"""PANDA S7 Interface for NICOS."""

__version__ = "$Revision$"

from time import sleep, time as currenttime

from nicos import status
from nicos.utils import intrange, oneof
from nicos.device import Device, Param, Readable, Moveable
from nicos.errors import NicosError, ProgrammingError, TimeoutError
from nicos.abstract import Motor as NicosMotor, Coder as NicosCoder
from nicos.axis import Axis
from nicos.taco import TacoDevice

from ProfibusDP import IO as ProfibusIO


class S7Bus( TacoDevice, Device ):
	"""Abstract class for communication with S7 over Profibusetherserver"""
	taco_class = ProfibusIO

	def read( self, a_type, startbyte, offset=0 ):
		if a_type=='float':
			return self._dev.readFloat( startbyte )
		elif a_type=='byte':
			return self._dev.readByte( startbyte )
		elif a_type=='bit':
			return self._dev.readBit( [startbyte, offset] )
		else:
			raise ProgrammingError( self, 'wrong data type for READ' )

	def readback( self, a_type, startbyte, offset=0 ):
		if a_type=='float':
			return self._dev.dpReadbackFloat( startbyte )
		elif a_type=='byte':
			return self._dev.dpReadbackByte( startbyte )
		elif a_type=='bit':
			return self._dev.dpReadbackBit( [startbyte, offset] )
		else:
			raise ProgrammingError( self, 'wrong data type for READBACK' )

	def write( self, value, a_type, startbyte, offset=0 ):
		if a_type=='float':
			self._dev.writeFloat( [startbyte, value] )
		elif a_type=='byte':
			self._dev.writeByte( [value, startbyte] )
		elif a_type=='bit':
			self._dev.writeBit( [startbyte, offset, value] )
		else:
			raise ProgrammingError( self, 'wrong data type for WRITE' )

class S7Coder( NicosCoder ):
	"""
	class for the angle readouts of mtt connected to the S7
	"""
	parameters = {
		'startbyte': Param( 'Adressoffset in S7-image (0 or 4)', type=oneof(int, 0, 4 ), mandatory=True, default=4 ),
		'sign': Param('Sign of returned Encoder Value', type=oneof(int, -1, 1 ), default=-1 ),
	}

	attached_devices = {
		'bus': S7Bus,
	}

	def doRead( self ):
		"""
		read the encoder value
		"""
		return self._adevs['bus'].read('float', self.startbyte)*self.sign

	def doStatus(self):
		if -140 < self.doRead() < -20:
			return status.OK, 'Status Ok'
		return status.ERROR, 'Value Out of range, check Coder!'


class S7Motor( NicosMotor ):
	"""
	class for the control of the S7-Motor moving mtt
	"""
	parameters = {
		'timeout'    : Param('Timeout in seconds for moving the motor or getting a reaction', type=intrange( 1, 3601 ), default=360 ),
		'sign'         : Param('Sign of moving direction Value', type=oneof(float, -1.0, 1.0 ), default=-1.0 ),
		'precision' : Param('Precision of the device value', type=float, unit='main', settable=False, category='precisions', default=0.001),
		'fmtstr'      : Param('Format string for the device value', type=str, default='%.3f', settable=False),
	}

	attached_devices = {
		'bus': S7Bus,
	}

	def doStop (self):
		"""
		stop the motor movement
		"""
		self.log.debug('stopping...')
		bus=self._adevs['bus']
		bus.write( 1, 'bit', 0, 3 )      # Stopbit setzen
		sleep( 1 )  # abwarten bis er steht
		bus.write( self.read()*self.sign, 'float', 8 )  # Istwert als Sollwert schreiben
		bus.write( 0, 'bit', 0, 3 )            # hebe stopbit auf
		bus.write( 1, 'bit', 0, 2 )            # Start Sollwertfahrt (Sollwert=Istwert....)
		sleep( 0.1 )
		bus.write( 0, 'bit', 0, 2 )            # Startbit Sollwertfahrt aufheben

	def doAbort (self):
		bus=self._adevs['bus']
		#bus.write( 0, 'bit', 0, 2 )
		bus.write( 1, 'bit', 0, 3 )

	def doWait(self):
		waittime=0
		while self._posreached()==False:
			if waittime>self.timeout:
				raise TimeoutError(self, 'maximum time for S7 Motor movement reached, check hardware!')
			sleep(1)
			waittime+=1

	def _gettarget(self):
		"""
		returns current target
		"""
		return self._adevs['bus'].readback( 'float', 8 )

	def _printstatusinfo(self):
		bus=self._adevs['bus']
		#define a little helper
		def f( value, nonzero, zero ):
			return nonzero if value else zero
		b20=bus.read( 'byte' ,20 );self.log.info('Byte 20 = 0b'+''.join([ str((b20>>i)&0x01) for i in range(7,-1,-1)]))
		self.log.info( 'Steuerspannung: \t%s'				%f( b20 & 0x01, 'an', 'aus' ))
		self.log.info( 'Not-Aus: \t%s'					%f( b20 & 0x02, 'gedrueckt', 'Ok' ))
		self.log.info( 'Fernbedienung: \t%s'				%f( b20 & 0x04, 'an', 'aus' ))
		self.log.info( 'Wartungsmodus: \t%s'				%f( b20 & 0x08, 'an', 'aus' ))
		self.log.info( 'Vor-Ortbedienung: \t%s'				%f( b20 & 0x10, 'an', 'aus' ))
		self.log.info( 'Sammelfehler: \t%s'				%f( b20 & 0x20, 'an', 'aus' ))
		self.log.info( 'MTT (Ebene) dreht \t%s'				%f( b20 & 0x40, '!', 'nicht.' ))
		self.log.info( 'Motor ausgeschwenkt:\t%s'			%f( b20 & 0x80, 'Ja', 'Nein' ))

		b21=bus.read( 'byte' ,21 );self.log.info('Byte 21 = 0b'+''.join([ str((b21>>i)&0x01) for i in range(7,-1,-1)]))
		self.log.info( 'Mobilblockarm dreht \t%s'			%f( b21 & 0x01, '!', 'nicht.' ))
		self.log.info( '     Magnet: \t%s'					%f( b21 & 0x02, 'an', 'aus' ))
		self.log.info( '     Klinke cw: \t%s'				%f( b21 & 0x04, 'an', 'aus' ))
		self.log.info( '     Klinke ccw: \t%s'				%f( b21 & 0x08, 'an', 'aus' ))
		self.log.info( '     Endschalter cw: \t%s'			%f( b21 & 0x10, 'an', 'aus' ))
		self.log.info( '     Endschalter ccw: \t%s'			%f( b21 & 0x20, 'an', 'aus' ))
		self.log.info( '     Notendschalter cw: \t%s'		%f( b21 & 0x40, 'an', 'aus' ))
		self.log.info( '     Notendschalter ccw: \t%s'		%f( b21 & 0x80, 'an', 'aus' ))

		b22=bus.read( 'byte' ,22 );self.log.info('Byte 22 = 0b'+''.join([ str((b22>>i)&0x01) for i in range(7,-1,-1)]))
		self.log.info( '	Referenz: \t%s'				%f( b22 & 0x01, 'an', 'aus' ))
		self.log.info( '	0deg: \t%s'					%f( b22 & 0x02, 'Ja', 'Nein' ))
		self.log.info( '    Endschalter Klinke cw: \t%s'		%f( b22 & 0x04, 'an', 'aus' ))
		self.log.info( '    Endschalter Klinke ccw: \t%s'	%f( b22 & 0x08, 'an', 'aus' ))
		self.log.info( '	Arm faehrt: \t%s'				%f( b22 & 0x10, 'Ja', 'Nein' ))
		self.log.info( 'Strahlenleck cw: \t%s'				%f( b22 & 0x20, '\033[1mJa\033[0m', 'Nein'))
		self.log.info( 'Max MB-Wechsel cw: \t%s'			%f( b22 & 0x40, 'Ja', 'Nein' ))
		self.log.info( 'Min MB-Wechsel cw: \t%s'			%f( b22 & 0x80, 'Ja', 'Nein' ))

		b23=bus.read( 'byte' ,23 );self.log.info('Byte 23 = 0b'+''.join([ str((b23>>i)&0x01) for i in range(7,-1,-1)]))
		self.log.info( 'MB vor Fenster cw:               %s'	%f( b23 & 0x01, 'Ja', 'Nein' ))
		self.log.info( 'MB vor Fenster ccw:              %s'	%f( b23 & 0x02, 'Ja', 'Nein' ))
		self.log.info( 'Max MB-Wechsel cw:               %s'	%f( b23 & 0x04, 'Ja', 'Nein' ))
		self.log.info( 'Min MB-Wechsel cw:               %s'	%f( b23 & 0x08, 'Ja', 'Nein' ))
		self.log.info( 'Strahlenleck ccw:                %s'	%f( b22 & 0x20, '\033[1mJa\033[0m', 'Nein'))
		self.log.info( 'Freigabe Bewegung intern:        %s'	%f( b23 & 0x20, 'Ja', 'Nein' ))
		self.log.info( 'Freigabe extern überbrückt:      %s'	%f( b23 & 0x40, 'Ja', 'Nein' ))
		self.log.info( 'Freigabe extern:                 %s'	%f( b23 & 0x80, 'Ja', 'Nein' ))

		b24=bus.read( 'byte' ,24 );self.log.info('Byte 24 = 0b'+''.join([ str((b24>>i)&0x01) for i in range(7,-1,-1)]))
		self.log.info( 'Endschalter MB-Ebene cw:         %s'	%f( b24 & 0x01, 'Ja', 'Nein' ))
		self.log.info( 'NotEndschalter MB-Ebene cw:      %s'	%f( b24 & 0x02, 'Ja', 'Nein' ))
		self.log.info( 'Endschalter MB-Ebene ccw:        %s'	%f( b24 & 0x04, 'Ja', 'Nein' ))
		self.log.info( 'NotEndschalter MB-Ebene ccw:     %s'	%f( b24 & 0x08, 'Ja', 'Nein' ))
		self.log.info( 'Referenzschalter MB-Ebene:       %s'	%f( b24 & 0x10, 'Ja', 'Nein' ))
		self.log.info( 'NC Fehler:                       %s'	%f( b24 & 0x20, 'Ja', 'Nein' ))
		self.log.info( 'Sollwert erreicht:               %s'	%f( b24 & 0x40, 'Ja', 'Nein' ))
		self.log.info( 'reserviert, offiziell ungenutzt: %s'	%f( b24 & 0x80, '1', '0' ))



	def doStatus (self):
		"""
		asks hardware and figurees out status
		"""
		bus=self._adevs['bus']
		# first get all needed statusbytes
		b20 = bus.read( 'byte', 20 )
		b21 = bus.read( 'byte', 21 )
		b22 = bus.read( 'byte', 22 )
		b23 = bus.read( 'byte', 23 )
		b24 = bus.read( 'byte', 24 )
		# pruefe Wartungsmodus
		if b20 & 0x08 == 0x08:
			wm = True
		else:
			wm = False

		self.log.debug('Statusbytes=0x%02x:%02x:%02x:%02x:%02x, Wartungsmodus '%(b20,b21,b22,b23,b24) + ('an' if wm else 'aus') )

		if b20 & 0x40:
			self.log.debug('MTT actively moving')
			return status.BUSY,'MTT actively moving'

		if b24 & 0x40:
			self.log.debug('on Target')
			return status.OK,'Idle'

		# we have to distinguish between Wartungsmodus and normal operation
		if wm:	# Wartungsmodus
			if ( (b20 & ~0x40) != 0b00010001) or (( b24 & 0b10111111 ) != 0) or (( b23 & 0b00000011 ) != 0):
				self.printwarning( self.name+' in Error state!, ignored due to Wartungsmodus!!!')
				# continue checking....
		else:	# Normal operation
			#~ if ( b20 != 0b00010001 ) or (( b24 & 0b10111111 ) != 0) or (( b23 & 0b00010011 ) != 0) or (( b22 & 0b00100000) != 0):
			if ( (b20 & ~0x40) != 0b00010001 ) or (( b24 & 0b10111111 ) != 0) or (( b23 & 0b00000011 ) != 0):
				self.log.debug('MTT in Error State, check with mtt._printstatusinfo() !')
				return status.ERROR, 'MTT in Error State, check with mtt._printstatusinfo() !'
			#~ if (( b24 & 0b01000000 ) == 0 ):
				#~ return status.BUSY, 'Target not (yet) reached (Zielwert erreicht = 0)'

		if not( self._posreached() ):
			self.log.debug('Not on Target (position != target)')
			return status.BUSY, 'Not on Target (position != target)'


		self.log.debug('Idle')
		return status.OK, 'Idle'

	def _posreached(self):
		'''
		helper to figure out if we reached our target position
		'''
		bus=self._adevs['bus']
		if abs( bus.read( 'float', 4 ) - bus.readback( 'float', 8 ) )<=0.001:
			return True
		return False

	def _minisleep(self):
		sleep(0.1)

	def doStart(self,position):
		"""
		start the motor movement
		"""
		if self.status()[0]==status.BUSY:
			self.wait()
		if self.status()[0]==status.ERROR:
			raise NicosError(self, 'S7 motor in error state')
		self.log.debug('starting to '+self.fmtstr%position + ' %s'%self.unit )
		#sleep(0.2)
		#20091116 EF: round to 1 thousands, or SPS doesn't switch air off
		position = float( self.fmtstr % position ) * self.sign
		bus=self._adevs['bus']
		# Sollwert schreiben
		bus.write( position, 'float', 8 )
		self._minisleep()
		self.log.debug( "new target: "+self.fmtstr % self._gettarget() )

		bus.write(0,'bit',0,3)            # hebe stopbit auf
		self._minisleep()
		bus.write(1,'bit',0,2)            # Start Sollwertfahrt
		self._minisleep()
		bus.write(0,'bit',0,2)            # Startbit Sollwertfahrt aufheben

	def doRead (self):
		"""
		read the incremental encoder
		"""
		bus=self._adevs['bus']
		self.log.debug( 'read: '+ self.fmtstr % (self.sign*( bus.read( 'float', 4 ) )) + ' %s'%self.unit )
		return self.sign*( bus.read( 'float', 4 ) )


class Panda_mtt( Axis ):
	"""
	class for the control of the S7-Motor moving mtt
	"""
	parameters = {
		'timeout'    : Param('Timeout in seconds for moving the motor or getting a reaction', type=intrange( 1, 3601 ), default=360 ),
		'sign'         : Param('Sign of moving direction Value', type=oneof(float, -1.0, 1.0 ), default=-1.0 ),
		'precision' : Param('Precision of the device value', type=float, unit='main', settable=False, category='precisions', default=0.001),
		'fmtstr'      : Param('Format string for the device value', type=str, default='%.3f', settable=False),
		'air_on'      : Param('Value to send to air_enable device to switch on the air', type=anytype, default='on' ),
		'air_off'    : Param('Value to send to air_enable device to switch off the air', type=anytype, default='off' ),
		'air_is_on' : Param('Value from air_sensor indicating air is really on', type=anytype, default='off' ),
		'startdelay': Param('Delay after switching air on', type=float, mandatory=True, unit='s'),
		'stopdelay':  Param('Delay before switching air off', type=float, mandatory=True, unit='s'),
		'air_timeout':  Param('Timeout for switching air on or off', type=float, mandatory=False, unit='s', default=5),
		'roundtime':  Param('Delay between each checks', type=float, mandatory=False, unit='s', default=0.1),
	}

	attached_devices = {
#		'coder': Readable,
#		'motor': Moveable,
		'air_enable'  : Moveable,
		'air_sensor' : Readable,
	}

	def _AirIsOn(self):
		return self._adevs['air_sensor'].doRead() == self.air_is_on

	def _preMoveAction(self):
		""" This method will be called before the motor will be moved.
		We wait the minimum time, switch on the air and check that it is there"""
		for d in [self._adevs['motor'],self._adevs['coder']]:
			d.poll()
		sleep( self.startdelay )
		self.log.debug('switching air to ON')
		self._adevs['air_enable'].move( self.air_on )	# switch air on
		timewaited=0
		while timewaited <= self.air_timeout:
			if self._AirIsOn():
				self.log.debug('Air is ON')
				self._timeouttime=currenttime()+self.doTime( self.read(), self.target )	# set timeout time
				return
			self.log.debug('waiting for air')
			sleep( self.roundtime )
			timewaited+=self.roundtime
		raise Exception('air did not come up') #-> Error, don't attempt to move!

	def _postMoveAction(self):
		""" This method will be called after the axis reached the position or
		will be stopped.
		we wait the minimum time, switch off the air and check that it's gone"""
		sleep( self.stopdelay )
		self.log.debug('switching air to OFF')
		self._adevs['air_enable'].move( self.air_off )	# switch air off
		timewaited=0
		for d in [self._adevs['motor'],self._adevs['coder']]:
			d.poll()
		while timewaited <= self.air_timeout:
			if not(self._AirIsOn()):
				self.log.debug('Air is OFF')
				return
			self.log.debug('waiting for air')
			sleep( self.roundtime )
			timewaited+=self.roundtime
		self.log.warning('Air did not switch off properly!')
		return True		# XXX Air didn't stop -> Is this really an Error? Or merely a Warning?
		#~ return False		# XXX Air didn't stop -> Is this really an Error? Or merely a Warning?

	def doTime(self, here, there):
		t= (abs( here - there )/0.14  # 7 seconds per degree continous moving
			 + 12*( int( abs( here - there )/11 )+2.5)	# 12 seconds per monoblockchange + reserve
			 + self.stopdelay + self.startdelay + 2*self.air_timeout ) # don't forget those!!!
		# 2009/08/24 EF for small movements, an additional 0.5 monoblock time might be required
		# for the arm to move to the right position
		self.log.debug('calculated Move-Timeout is %d seconds'%t)
		return t

	def _duringMoveAction(self, position):
		""" This method will be called during every cycle in positioning thread
		Continously check the air_state during movement
		If Air fails, abort!
		"""
		self.log.debug('checking status')
		self.poll()
		if not(self._AirIsOn()):
			raise Exception('air went out') # if Air goes out, abort!
		self.log.debug('checking timeout: %d > %d ?'%(self._timeouttime,currenttime()))
		if self._timeouttime < currenttime():
			raise TimeoutError(self, 'Timeout reached!')
		return

	def doReset(self):
		''' for Convinience, switch off Air upon reset'''
		Axis.doReset(self)
		if self.doStatus()[0]==status.OK:
			self._adevs['air_enable'].move( self.air_off )	# switch air off, if (and only if) Idle
