# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Mark Koennecke <mark.koennecke@psi.ch>
#   Daniel G. Mazzone <daniel.mazzone@psi.ch>
#   Jakob Lass <jakob.lass@psi.ch>
#
# *****************************************************************************


import os
from string import Template
from time import time

import numpy as np

from nicos import session
from nicos.commands import parallel_safe, usercommand
from nicos.commands.scan import scan
from nicos.core.constants import SIMULATION
from nicos.core.errors import ConfigurationError, InvalidValueError, \
    MoveError, PositionError
from nicos.utils import findResource

from nicos_sinq.sxtal.commands import AddAuxRef, AddRef, CalcUB, getSampleInst

# two theta limits
# DO NOT CHANGE!
# incomingE = [2, 3.6, 3.8, 5.0, 5.5, 6.4, 6.6, 6.8, 6.9, 7.0, 8.0, 8.2, 8.45,
#              8.6, 8.7, 9.5,  9.8, 9.9, 10.5, 11.4, 11.7, 12.0, 12.2, 12.9,
#              13.5, 13.8, 14, 15, 16, 17]
# twoTheta = [-79.5, -79.5, -79.5, -79, -79,  -79, -79, -78, -78, -76.5, -73.0,
#             -71, -70, -66, -64, -64, -62, -60, -54, -54, -52, -51, -51, 48,
#             -47, -46.5, -46.5, -44, -41.5, -39.5]
#
# incomingE = [2, 3.6, 3.8, 5.0, 5.5, 6.45, 6.5, 6.6, 6.65, 6.8, 6.9,
#              7.0, 7.5, 7.7, 8.0, 8.5, 8.6, 8.8, 9, 9.2, 9.4, 9.6, 9.8, 10,
#              10.5, 11, 11.5, 12.0, 12.5, 13, 13.5, 14, 14.5, 15, 15.5, 16,
#              16.5, 17]
#
# twoTheta = [-79.5, -79.5, -79.5, -79, -79, -79, -79, -78.0, -78.0, -78.0, -77,
#             -77, -77, -73.5, -72.5, -72, -70, -66, -64, -64, -64, -63, -62,
#             -60, -57, -56, -54, -52, -50, -47, -47, -46, -44, -43, -42, -41,
#             -40.5, -39.5]
#
# twoThetaLimitInterp = interp1d(incomingE, twoTheta)


logbookTitles = ['File No.', 'Ei', 's2t', 'a3 start', 'a3 stop',
                 'a3 steps', 'a3 step', 'Monitor', 'Temp', 'Mag field']
logbookTitlesFormats = ['{:>10}']*len(logbookTitles)
valueFormats = ['{:10d}', '{:10.3f}', '{:10.3f}', '{:10.3f}',
                '{:10.3f}', '{:10d}', '{:10.3f}', '{:10d}', '{:10.3f}',
                '{:10.3f}']

__all__ = ['loadcalibration', 'SelectDetectorAnalyser',
           'chooseDetectorAnalyser', 'moveDevice', 'changeEi',
           'printToDiscord', 'writeToLogbook', 'CAMEApause', 'CAMEAresume',
           'moves2t', 'checkLimits', 'moves2tPeak', 'moveCAMEA', 'CAMEAscan',
           'prepareCAMEA']


@usercommand
def loadcalibration():
    """
    Load CAMEA calibration files. Only needed in a new installation or
    after a modification of the calibration files.
    """
    dev = ['calib1', 'calib3', 'calib5', 'calib8']
    names = ['Normalization_1.calib', 'Normalization_3.calib',
             'Normalization_5.calib', 'Normalization_8.calib']
    for d, n in zip(dev, names):
        c = session.getDevice(d)
        c.load(findResource(os.path.join('nicos_sinq', 'camea', n)))


@usercommand
def SelectDetectorAnalyser(detNo, anaNo):
    """
    This command selects the detector and analyser to use for calculating
    counts in scans.
    """

    if detNo < 0 or detNo > 103:
        session.log.error('detNo %d out of range 0 - 103', detNo)
        return
    if anaNo < 0 or anaNo > 7:
        session.log.error('anaNo %d out of range 0 - 7', anaNo)
        return
    try:
        calib1 = session.getDevice('calib1')
        a4 = session.getDevice('a4')
        cts = session.getDevice('counts')
        efd = session.getDevice('ef')
        dn = session.getDevice('detNo')
        an = session.getDevice('anaNo')
    except ConfigurationError:
        session.log.error('Camea devices NOT found, cannot proceed')
        return

    idx = 8*detNo + anaNo
    a4offset = calib1.a4offset[idx]
    ef = calib1.energy[idx]
    anaMin = calib1.boundaries[idx*2]
    anaMax = calib1.boundaries[idx*2 + 1]
    a4.a4offset = a4offset
    # This order is implied by RectROIChannel.getReadResult()
    cts.roi = (detNo, anaMin, 1, anaMax - anaMin)
    dn.maw(detNo)
    an.maw(anaNo)
    session.log.info(
        'Driving virtual ef to %.3f and virtual a4 to %.3f', ef, a4())
    efd.maw(ef)


@usercommand
def chooseDetectorAnalyser(HKLE=None, A4=None):
    """
    This command selects the closest detector given an A4 or a peak at 5 meV.

    """
    try:
        calib1 = session.getDevice('calib1')
        s2t = session.getDevice('s2t')
        an = session.getDevice('anaNo')
    except ConfigurationError:
        session.log.error('Camea devices NOT found, cannot proceed')
        return

    if HKLE is None and A4 is None:
        session.log.error('Either HKLE or A4 has to be provided')
        return
    if HKLE is not None:
        try:
            length = len(HKLE)
        except TypeError:
            session.log.error(
                'HKLE expected to be of form [H,K,L,E], but received: %s',
                HKLE)
            return
        if length == 3:
            HKLE = [*HKLE, 0]
        elif length != 4:
            session.log.error(
                'HKLE (%s) has wrong length %s, expected [H,K,L] or [H,K,L,E]',
                HKLE, len(HKLE))
            return

        sample, inst = getSampleInst()
        if not sample:
            session.log.error('No sample found')
            return

        _, A4, _, _, _, _ = inst._extractPos(inst._calcPos(HKLE))
        A4 = A4[1]

    a4values = np.asarray(calib1.a4offset).reshape(104, 8)[:, int(an())]+s2t()

    closestIdx = np.argmin(np.abs(a4values-A4))
    session.log.info('Closest detector to {:.3f} is {:} at {:.3f}'.format(
        A4, closestIdx, a4values[closestIdx]))
    SelectDetectorAnalyser(detNo=closestIdx, anaNo=int(an()))


@usercommand
def moveDevice(device, value, retries=3):
    e = None
    if isinstance(device, str):
        dev = session.getDevice(device)
    else:
        dev = device

    k = 0
    while k < retries:
        k = k + 1
        try:
            dev.maw(value)
            success = True
            break
        except (PositionError, MoveError) as e:
            session.log.info('Got error "%s"', str(e))
            success = False

    if not success:
        session.log.error(
            'Could not move %s to %.3f within %s tries', dev, value, retries)
        if e is not None:
            raise e
    else:
        devName = dev.name
        devUnit = dev.unit
        session.log.info('Wanted %s = %s %s, actual %s = %s %s',
                         devName, value, devUnit, devName, str(dev()), devUnit)


@usercommand
def changeEi(energy, retries=3, retryMC=3):
    """Change incoming energy with a retry three times"""
    device = 'ei'
    e = None
    mch = session.getDevice('mch')
    mcv = session.getDevice('mcv')
    if isinstance(device, str):
        dev = session.getDevice(device)
    else:
        dev = device

    k = 0
    while k < retries:
        k = k + 1
        try:
            dev.maw(energy)
            success = True
            break
        except (PositionError, MoveError, InvalidValueError) as e:
            session.log.info('Got error "%s"', str(e))
            success = False
            MCtries = 0
            while ((mch.isEnabled is False or mcv.isEnabled is False)
                   or MCtries < retryMC):
                mch.enable()
                mcv.enable()
                MCtries += 1

    if not success:
        session.log.error(
            'Could not move %s to %.3f within %d tries', dev, energy, retries)
        if e is not None:
            raise e
    else:
        devName = dev.name
        devUnit = dev.unit
        session.log.info('Wanted %s = %s %s, actual %s = %s %s',
                         devName, energy, devUnit, devName, str(dev()),
                         devUnit)


@usercommand
def printToDiscord(message):
    """
    Print the message to the discord server if it is running.
    """
    if session.mode != SIMULATION:
        with open('/home/camea/Documents/DiscordBot/status.txt', 'a',
                encoding='utf-8') as f:
            f.write(message)


@usercommand
def writeToLogbook(logbook, values):

    with open(logbook, 'a+', encoding='utf-8') as f:
        if f.tell() == 0:  # empty file
            f.write(','.join([fmt.format(v) for fmt, v in zip(
                logbookTitlesFormats, logbookTitles)])+'\n')
        f.write(','.join([fmt.format(v)
                for fmt, v in zip(valueFormats, values)])+'\n')


@usercommand
def CAMEApause():
    """
    Make CAMEA pause in the next script by changing the counter threshold to
    something=10000 large
    """
    cter1 = session.getDevice('cter1')
    cter1.execute('DL   2 10000')
    printToDiscord('The scan has been paused')
    session.log.warning('The scan has been paused')


@usercommand
@parallel_safe
def CAMEAresume():
    """
    Reset the counter threshold to 100 to resume CAMEA
    """
    cter1 = session.getDevice('cter1')
    cter1.execute('DL   2 100')
    printToDiscord('The scan has been resumed')
    session.log.info('The scan has been resumed')


@usercommand
def moves2t(value, retries=3):
    """
    Move the s2t while catching errors. If an error is caught, put CAMEA into
    wait in the next scan and write out error message
    """
    s2t = session.getDevice('s2t')
    ei = session.getDevice('ei')
    ctrl = session.getDevice('eis2tcontroller')
    # Check limits from table above

    limit = ctrl.twoThetaLimitInterp(ei())
    if value < limit:  # Houston, we have a problem
        session.log.error(
            'The desired s2t %.3f deg) is outside the area (limit is at '
            'Ei = %.3f meV is %.3f deg)!\n You, my good sir/madame have '
            'found the wall....', value, ei(), limit)
        return

    errMesgTp = Template('Error while moving s2t: $msg.\n\nTo reset the '
                         's2t error,  reset box, move s2t twice with s2t(x) '
                         'where x is the position you want to be and execute '
                         'CAMEAgo()\n')
    try:
        for i in range(retries):
            try:
                s2t.maw(value)
                success = True
                session.log.info(
                    'Wanted s2t = %s deg, actual s2t = %s deg', value, s2t())
                break
            except (PositionError, MoveError) as e:
                success = False
                msg = e
                time.sleep(5)
        if not success:
            errorMessage = errMesgTp.substitute(msg=msg)
            printToDiscord(errorMessage)
            session.log.error(errorMessage)
            CAMEApause()
        if i > 0:  # There was a retry
            session.log.info('Success after %d tries', i+1)
    except Exception as e:
        errorMessage.substitute(msg=e)
        printToDiscord(errorMessage)
        session.log.error(errorMessage)
        CAMEApause()


@usercommand
def checkLimits(ei, s2t, verbose=True):
    """Check if provided energy and s2t combination is allowed"""

    Ei = ei
    stt = s2t

    s2t = session.getDevice('s2t')
    ei = session.getDevice('ei')
    ctrl = session.getDevice('eis2tcontroller')

    if Ei is None:
        Ei = ei()
    if stt is None:
        stt = s2t()
    errors = False
    if Ei < 2:  # this is not possible
        errors = True
        if verbose:
            session.log.error(
                'The desired Ei (%.3f meV) is unreachable!!!\n'
                'Please check your input and try again.....', Ei)
    if stt > -35:  # this is not possible
        errors = True
        if verbose:
            session.log.error(
                'The desired stt (%.3f deg) is in the direct beam!!!\n'
                'Please check your input and try again.....', stt)
    if errors:
        return False

    # Check limits from table above

    wantedEnergyS2tLimt = ctrl.twoThetaLimitInterp(Ei)
    if stt < wantedEnergyS2tLimt:  # Houston, we have a problem
        if verbose:
            session.log.error(
                'The desired s2t (%.3f deg) is outside the area (limit at '
                'Ei = %.3f meV is %.3f deg)!\nYou, my good sir/madame have '
                'found the wall....', stt, Ei, wantedEnergyS2tLimt)
        return False
    return True


@usercommand
def moves2tPeak(HKLE=None, A4=None):
    """
    Find the best detector closest to the current s2t, move CAMEA there.
    """

    # For alignment it is best to avoid first and last 2 detectors in wedges
    goodDetectors = np.arange(104).reshape(8, 13)[:, 2:-2].flatten()

    if HKLE is None and A4 is None:
        session.log.error('Either HKLE or A4 has to be provided')
        return

    try:
        calib1 = session.getDevice('calib1')
        s2t = session.getDevice('s2t')
        an = session.getDevice('anaNo')
    except ConfigurationError:
        session.log.error('Camea devices NOT found, cannot proceed')
        return

    if HKLE is not None:
        try:
            numArgs = len(HKLE)
        except TypeError:
            session.log.error(
                'HKLE expected to be of form [H,K,L,E], but received: %s',
                HKLE)
            return
        if numArgs == 3:
            HKLE = [*HKLE, 0]
        elif numArgs != 4:
            session.log.error(
                'HKLE (%s) has wrong length %s, expected [H,K,L] or [H,K,L,E]',
                HKLE, len(HKLE))
            return

        sample, inst = getSampleInst()
        if not sample:
            session.log.error('No sample found')
            return

        _, A4, _, _, _, _ = inst._extractPos(inst._calcPos(HKLE))
        A4 = A4[1]

    a4offsets = np.asarray(calib1.a4offset.copy()).reshape(104, 8)

    a4values = a4offsets[:, int(an())].reshape(8, 13)[:, 2:-2].flatten()+s2t()
    goodDetectors = np.arange(104).reshape(8, 13)[:, 2:-2]

    localIdx = np.argmin(np.abs(A4-a4values))
    detIdx = goodDetectors.flatten()[localIdx]

    newS2t = A4-a4values[localIdx]+s2t()

    SelectDetectorAnalyser(int(detIdx), int(an()))
    session.log.info('Best tube found is %s, moving s2t to from %.3f to '
                     ' %.3f', detIdx, s2t(), newS2t)

    s2t.maw(newS2t)


@usercommand
def moveCAMEA(ei=None, s2t=None):
    """
    Move CAMEA safely within the area
    """

    check = checkLimits(ei=ei, s2t=s2t)
    if not check:
        return
    Ei = ei
    stt = s2t

    s2t = session.getDevice('s2t')
    ei = session.getDevice('ei')
    ctrl = session.getDevice('eis2tcontroller')

    if Ei is None:
        Ei = ei()
    if stt is None:
        stt = s2t()

    wantedEnergyS2tLimt = ctrl.twoThetaLimitInterp(Ei)+s2t.offset

    # if no energy is changed, simply move s2t
    if (np.isclose(Ei, ei(), atol=ei.precision)
            and np.isclose(stt, s2t(), atol=s2t.precision)):

        session.log.info('Nothing to move')
    elif np.isclose(Ei, ei(), atol=ei.precision):
        session.log.info('Move only s2t')
        moves2t(stt)
    elif np.isclose(stt, s2t(), atol=s2t.precision):
        session.log.info('Move only ei')
        changeEi(Ei)
    elif Ei > ei():
        # we are increasing Ei, first check if close to final s2t limit,
        # then move out; otherwise drive there directly
        if s2t() > wantedEnergyS2tLimt:
            session.log.info('Move first ei, then s2t')
            changeEi(Ei)
            moves2t(stt)
        else:
            session.log.info('Move first s2t, then ei')
            moves2t(stt)
            changeEi(Ei)
    else:  # we move down in energy, all is goooood
        session.log.info('Move first ei, then s2t')
        changeEi(Ei)
        moves2t(stt)

# pylint: disable=R0917


@usercommand
def CAMEAscan(energies, s2ts, a3Start, a3Stepsize, a3Steps,
              logbook=None, skipScans=0, retries=3, **preset):
    """
    Perform standard CAMEA scan with defined incoming energies (_en1 and _en2)
    at the two s2t positions automatically adding s2ts+4 positions starting
    at an a3 value of a3Start performing a3Steps steps of size a3stepsize with
    a monitor value of monitor_value or time value of time_value. Temperature
    and magnetic field are ONLY used for titles in files and logbook if
    provided! Scans can be skipped.

    Example:

    CAMEAscan([5,5.13],  s2ts=[-40], a3Start=0, a3Stepsize=1, a3Steps=181,
              m=100000, skipScans=0)
    The above command will perform 4 a3 scans with a step size of 1 degree
    starting at 0 and ending at 180, i.e. 181 steps. The monitor value is
    100 000 and no scans are skipped. That is, the following is measured

    Ei, s2t
    5.0, -40
    5.0, -44
    5.13, -44
    5.13, -40
    """
    allowed_presets = ['m', 'monitor', 'monitor_value', 't', 'time', 'time_value']

    # Do some checking to ensure that exactly one preset has been given
    scanParams = None
    logbookMonitor = None
    for key in allowed_presets:
        val = preset.get(key)
        if val is not None:
            if scanParams is None:
                scanParams = {key: val}
                logbookMonitor = val
            else:
                session.log.error('More than one preset has been given: '
                                  '%s and %s', scanParams, {key: val})
                return

    if scanParams is None:
        session.log.error('At least one of %s needs to be specified',
                          ", ".join(allowed_presets))
        return

    # Get devices
    try:
        a3 = session.getDevice('a3')
        ei = session.getDevice('ei')
        s2t = session.getDevice('s2t')
        Exp = session.getDevice('Exp')

    except ConfigurationError:
        session.log.error('Camea devices NOT found, cannot proceed')
        return

    # Get temperature in order to actually do a scan
    try:
        temperature = session.getDevice('T')
    except ConfigurationError:
        temperature = None

    if temperature is None:
        session.log.info("No temperature found, this can't be right, can it?")

    try:
        B = session.getDevice('B')
    except ConfigurationError:
        B = None

    if B is None:
        pass  # session.log.info('No magnet found')

    # Generate list of configurations wanted
    # At each energy perform both s2t and s2t+4
    # At every second energy revers order of s2t measurements
    setups = []

    a3Stop = a3Start + a3Stepsize * (a3Steps - 1)

    for idx, e in enumerate(energies):
        for s2 in s2ts:
            if idx % 2 == 0:  # even
                setups.append([e, s2,   a3Start, a3Stepsize, a3Steps])
                setups.append([e, s2+4, a3Stop, -a3Stepsize, a3Steps])
            else:
                setups.append([e, s2+4, a3Start, a3Stepsize, a3Steps])
                setups.append([e, s2,   a3Stop, -a3Stepsize, a3Steps])

    # check energy-s2t combinations wanted
    checks = []
    for checkEi, checkS2t, *_ in setups:
        if checkEi is None:
            continue
        newCheck = checkLimits(ei=checkEi, s2t=checkS2t, verbose=False)
        checks.append(newCheck)

    if not np.all(checks):  # if any of the checks fail, break script
        erroneous = np.asarray(setups)[np.logical_not(checks)]
        errorSetups = ['Ei = {} meV, s2t = {} degrees, A3 from {} in steps of {} degrees with {} steps'.format(
            e, s, *a3s) for e, s, *a3s in erroneous]
        msg = 'Errors found in wanted scans for:\n{}'.format(
            '\n'.join(errorSetups))
        session.log.error(
            msg)
        return

    totalScans = len(setups)-skipScans
    scanFilesStart = Exp.lastscan+1
    scanFilesLast = scanFilesStart+totalScans-1

    try:  # Catch any error and print to discord

        discordTemplate = Template('Wanted Ei = $eiTarget meV, '
                                   'actual Ei = $eiActual meV\n'
                                   'Wanted s2t $s2tTarget deg, '
                                   'actual s2t = $s2tActual deg\n'
                                   'Starting scan $scanNumber of '
                                   '$totalScans with file number $fileNumber')

        experimentTitle = ['Ei = {:.3f} meV', 's2t = {:.2f} deg']
        experimentTitleDevices = [ei, s2t]
        if temperature is not None:
            experimentTitle.append('T = {:.3f} K')
            experimentTitleDevices.append(temperature)

        if B is not None:
            experimentTitle.append('B = {:.3f} T')
            experimentTitleDevices.append(B)

        for scanNumber, setup in enumerate(setups):
            (eiValue, s2tValue, a3Start, a3Stepsize, a3Steps) = setup

            if scanNumber < skipScans:
                continue

            scanNumMod = scanNumber-skipScans+1
            fileNumber = Exp.lastscan+1

            moveCAMEA(ei=eiValue, s2t=s2tValue)
            discordString = discordTemplate.substitute(eiTarget=eiValue,
                                                       eiActual=ei(),
                                                       s2tTarget=s2tValue,
                                                       s2tActual=s2t(),
                                                       scanNumber=scanNumMod,
                                                       totalScans=totalScans,
                                                       fileNumber=fileNumber)

            printToDiscord(discordString)
            session.log.info(discordString)

            experimentText = [text.format(device()) for text, device in zip(
                experimentTitle, experimentTitleDevices)]

            if len(experimentText) > 0:
                experimentText = ', '.join(experimentText)
            else:
                experimentText = ''
            Exp.title = experimentText

            for _ in range(retries):
                try:
                    scan(a3, a3Start, a3Stepsize, a3Steps, **scanParams)
                    success = True
                    break
                except (OSError) as e:
                    session.log.info('Got error "%s"', e)
                    success = False
            if not success:
                session.log.error(
                    'Could not scan within %d tries', retries)
                continue

            temp = temperature() if temperature is not None else -1
            bfield = B() if B is not None else -1
            values = [Exp.lastscan, ei(), s2t(), a3Start, a3(), a3Steps,
                      a3Stepsize, logbookMonitor, temp, bfield]

            text = ', '.join([s.format(v)
                             for s, v in zip(valueFormats, values)])+'\n'

            printToDiscord(text)
            if logbook is not None:
                try:
                    writeToLogbook(logbook=logbook, values=values)
                except Exception as e:
                    session.log.error(
                        'Writing to logbook failed with following error: '
                        '%s', e)

        endText = 'CAMEA scan set is done, files {:} - {:}'.format(
            scanFilesStart, scanFilesLast)
        printToDiscord(endText)
        session.log.info(endText)

    except Exception as e:
        text = 'Script broken at ei = {:.3f}, s2t = {:.3f}, and a3 = {:.2f} with following error message: "{:}"'.format(
                           ei(), s2t(), a3(), e)
        printToDiscord('MENTIONALL\n'+text)
        session.log.error(text)
        raise (e)


@usercommand
def prepareCAMEA(alignmentPeak1=None, alignmentPeak2=None):

    moveCAMEA(ei=5.0, s2t=-45)

    mch = session.getDevice('mch')
    sgu = session.getDevice('sgu')
    sgl = session.getDevice('sgl')
    mst = session.getDevice('mst')
    msb = session.getDevice('msb')
    msr = session.getDevice('msr')
    msl = session.getDevice('msl')
    Sample = session.getDevice('Sample')
    CAMEA = session.getDevice('CAMEA')

    mch.maw(0)
    mch.fix()

    if sgu is not None and sgl is not None:
        sgu.maw(0)
        sgl.maw(0)
        CAMEA.out_of_plane = False
        session.log.info('gonios are zero')

    session.log.info('CAMEA is ready for alignment')
    session.log.info('remember to release mch after alignment')

    # open the slits
    for d in [mst, msb, msr, msl]:
        d.maw(20)

    session.log.info('slits are wide open')

    # Setup UB
    loadcalibration()
    SelectDetectorAnalyser(82, 7)
    Sample.ubmatrix = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    if alignmentPeak1 is None:
        alignmentPeak1 = [1, 0, 0]
    if alignmentPeak2 is None:
        alignmentPeak2 = [0, 1, 0]
    AddRef((*alignmentPeak1, 0))
    AddAuxRef(alignmentPeak2, 0)
    AddAuxRef(alignmentPeak1, 1)
    CalcUB(2, 1, replace=True)
    session.log.info('Dummy UB has been generated.')
    session.log.info('CAMEA prepared for alignment or a Nature paper. Science is also acceptable...')
