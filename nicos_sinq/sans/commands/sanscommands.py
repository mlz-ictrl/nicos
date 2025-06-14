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
#   Joachim Kohlbrecher <joachim.kohlbrecher@psi.ch>
#
# *****************************************************************************

import datetime
import socket
import subprocess
import time
from math import atan, pi, sin, sqrt

import numpy as np

from nicos import session
from nicos.commands import helparglist, usercommand
from nicos.commands.basic import NewSetup, sleep
from nicos.commands.device import maw
from nicos.commands.measure import live, preset
from nicos.commands.output import printerror, printinfo, printwarning
from nicos.commands.scan import manualscan
from nicos.core import ConfigurationError, UsageError, status
from nicos.core.mixins import HasPrecision
from nicos.services.daemon.script import parseScript
from nicos.utils import createSubprocess

__all__ = ['scandev', 'DoIt', 'detoffset', 'detcalib', 'tofel', 'antitofel',
           'wait4dev', 'glambda', 'CalcLambda', 'qrange', 'count2', 'holder',
           'ASCIIplot', 'getDevice']


@usercommand
def ASCIIplot():
    """
    Command to make a simple plot in the terminal.
    """
    printinfo(hasGnuplot())
    x = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                 11, 12, 13, 14, 15, 16, 17, 18, 19])
    y = np.array([1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1, 0, 2, 3, 4, 5, 8, 8, 8, 8])
    txt = txtplot(x, y, 'x', 'y', height=30, width=120)
    for t in txt:
        printinfo(t)


def txtplot(x, y, xlab, ylab, width=120, height=40, xterm_mode=False):
    """Plot data with gnuplot's dumb ASCII terminal."""
    if not x.size:
        raise ValueError('Empty plot')
    if len(x) != len(y):
        raise ValueError('Unequal lengths of X and Y values')

    try:
        gnuplot = createSubprocess(['gnuplot', '--persist'], shell=False,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        if xterm_mode:
            cmd = ['set term xterm']
        else:
            cmd = ['set term dumb ' + str(width) + ' ' + str(height)]

#            cmd = ['set term dumb '+str(width)+' '+str(height)]
#            cmd = ['set term dumb 120 40']
#            print(cmd)
        cmd.append('set xlabel "' + xlab + '"')
        cmd.append('set ylabel "' + ylab + '"')
        cmd.append('plot "-" with linespoints notitle')
        for xy in zip(x, y):
            cmd.append('%s %s' % xy)
        cmd.append('e\n')

        cmd = '\n'.join(cmd).encode()
        out = gnuplot.communicate(cmd)[0]
        lines = [line for line in out.decode().splitlines() if line]
        if xterm_mode:
            lines += ['Plotting in xterm Tektronix window.',
                      '\x1b_If you can only see a lot of incomprehensible '
                      'text, use xterm instead of your current terminal '
                      'emulator.\x1b\\']
        return lines

    except OSError:
        raise RuntimeError('Could execute gnuplot for text plot') from None


def hasGnuplot():
    """Check for the presence of gnuplot in the environment.

    To be used with the `requires` decorator.
    """
    try:
        gpProcess = createSubprocess(b'gnuplot', shell=True,
                                     stdin=subprocess.PIPE, stdout=None)
        gpProcess.communicate(b'exit')
        if gpProcess.returncode:
            return False
    except (OSError, ValueError):
        return False
    return True


@usercommand
@helparglist("htype, position=0, prefix='', clear=True")
def holder(htype, position=0, prefix='', clear=True):
    """

       defines aliases to easily position samples of several standard sample
       holders

       htype:    name of the standard sample holder
       position: actual index of sample position in the beam.
       prefix:   all aliases start with a character followed by a number
        indicating the index. A character different then the standard prefix
        can be defined by this parameter.
       clear:    This parameter is set by default to True and a call of holder
        clears all previous aliases. To keep all previous aliases this
        parameters needs to be set to False.
    """
    if not isinstance(prefix, str):
        printerror('argument prefix needs to be an integer!')
        return
    if not isinstance(position, int):
        printerror('argument position needs to be an integer!')
        return
    if not isinstance(htype, str):
        printerror('first argument htype is not a string!')
        return

    if not isinstance(clear, bool):
        printerror('argument clear needs to be of type boolean!')
        return

    stopo = getDevice('stopo')
    if clear:
        stopo.clear()

    holder_dict = {
        'mfu': ['m', 9, 41],
        'qs110': ['p', 23, 21.5],
        'qs120': ['r', 17, 29],
        'qs404': ['w', 17, 29],
        'solid': ['s', 16, 31],
        'olaf': ['o', 10, 39]
    }

# need a way to find out the instrument name on which this script is running
# this would help to predefine the motors to read out for defining the aliases
    sample_table_dict = {
        'sans.psi.ch': ['spos', 'xu', 'xo', 'z'],
        'sans-llb.psi.ch': ['spos', 'stx', 'sty']
    }

    try:
        mholder = holder_dict[str.lower(htype)]
    except BaseException:
        printerror('htype is not a known sample holder. '
                   'Aliases needs to be defined manually')
        return

    if socket.getfqdn() == 'sans-llb.psi.ch':
        table_motors = sample_table_dict[socket.getfqdn()]
    elif socket.getfqdn() == 'sans.psi.ch':
        table_motors = sample_table_dict[socket.getfqdn()]
    else:
        printwarning('So far only the sample tables for "SINQ SANS-1" and '
                     '"SINQ SANS-LLB" are configured for this routine!')
        return
    vst = []
    devname = []
    for idev in range(len(table_motors)):
        try:
            st = getDevice(table_motors[idev])
            devname = devname + [table_motors[idev]]
            vst = vst + [st.read()]
        except BaseException:
            printwarning('Devive ' + table_motors[idev] + ' not found!')

    printinfo(vst, devname)
    if devname[0] != table_motors[0]:
        printerror('Device ' + table_motors[0] + ' not available!')
        return
    if prefix == '':
        an = mholder[0]
    else:
        an = prefix

    for i in range(mholder[1]):
        if len(table_motors) == 4:
            stopo.define_position(an + str(i), (table_motors[3], vst[3]),
                                  (table_motors[2], vst[2]),
                                  (table_motors[1], vst[1]),
                                  (table_motors[0], vst[0] +
                                   (i - position) * mholder[2]))
        elif len(table_motors) == 3:
            stopo.define_position(an + str(i),
                                  (table_motors[2],
                                   vst[2]),
                                  (table_motors[1],
                                   vst[1]),
                                  (table_motors[0],
                                   vst[0] + (i - position) * mholder[2]))
        elif len(table_motors) == 2:
            stopo.define_position(an + str(i),
                                  (table_motors[1],
                                   vst[1]),
                                  (table_motors[0],
                                   vst[0] + (i - position) * mholder[2]))
        else:
            stopo.define_position(an + str(i), (table_motors[0], vst[0] +
                                                (i - position) * mholder[2]))
    stopo.show()


@usercommand
@helparglist("dev, target, [waitNICOScommand='sleep(10)']")
def wait4dev(dev, target, waitNICOScommand='sleep(10)'):
    """Move device to target within precision of device and execute the a NICOS
       command until reaching target value or device problems.

       dev:              movable device name supplied as a string
       target:           real value to which the device should be moved
       waitNICOScommand: valid NICOS command executing during waiting time.
                         The default command is 'sleep(10)'n given precision.
    """
    if not isinstance(waitNICOScommand, str):
        printerror('waitNICOScommand is not a string!')
        return
    else:
        DD = session.getDevice(dev)
        if not isinstance(DD, HasPrecision):
            raise UsageError(DD, "doesn't have a precision")
        variable = DD.read()
        DD.move(target)
        code, _ = parseScript(waitNICOScommand)
        while isinstance(waitNICOScommand, str):
            stat, msg = DD.status()
            if stat == status.OK:
                printinfo('%s reached target value %s (actual: %s).' % (
                    DD, DD.format(target, True), DD.format(variable, True)))
                try:
                    printinfo('Required precision is +-%s' %
                              DD.formatParameter('precision', DD.precision))
                except BaseException:
                    pass
                break
            elif stat == status.BUSY:
                printwarning('%s = %s is still moving. Executing meanwhile %r' % (
                    DD, DD.format(variable), waitNICOScommand))

                for _, c in enumerate(code):
                    exec(c, session.namespace)
            else:
                printerror('%s stopped with message:\n%s' % (DD, msg))
                break


@usercommand
@helparglist('dev, start, end, step, NICOScommand')
def scandev(dev, start, end, step, NICOScommand):
    """scan dev in the range between start and end with stepwidth step and
    execute NICOScommand at each step
    """
    if not isinstance(NICOScommand, str):
        printerror('NICOScommand is not a string!')
        return
    if not isinstance(start, (float, int)):
        printerror('start is not a number!')
        return
    if not isinstance(end, (float, int)):
        printerror('end is not a number!')
        return
    if not isinstance(step, (float, int)):
        printerror('step is not a number!')
        return
    DD = getDevice(dev)
    if abs(step) > DD.precision:
        npos = np.round(np.abs((end - start) / float(step))) + 1
    else:
        raise UsageError('step must be bigger than ' + str(DD.precision))
    # nxsink = session.getDevice('nxsink')
    # nxsink.settypes = ['point', ]

    # get and print start time
    t0 = time.time()
    dt_obj0 = datetime.datetime.fromtimestamp(t0)
    printinfo(f'Starting at {dt_obj0.strftime("%H:%M:%S")}')

    with manualscan():
        for ind in range(npos):
            # print scan progress
            printinfo('')
            print(f'Position {ind+1} of {int(npos)}')
            print(f'Moving {dev} to {np.round(start + ind * step,3)} '
                  f'in scandev from {np.round(start,3)} to {np.round(end,3)} '
                  f'in steps of {np.round(step,3)}')
            t1 = time.time()  # get time before scan

            maw(dev, start + ind * step)
            code, _ = parseScript(NICOScommand)
            for _, c in enumerate(code):
                exec(c, session.namespace)

            # get scan timing and estimate completion time
            t2 = time.time()
            print(f'Scan took {np.round(t2-t1,2)} s')
            tf = t0 + np * (t2 - t0) / (ind + 1)
            dt_obj = datetime.datetime.fromtimestamp(tf)
            print(f'Estimated scan completion time: '
                  f'{dt_obj.strftime("%H:%M:%S")} '
                  f'(started at {dt_obj0.strftime("%H:%M:%S")})')
            print(f'{datetime.timedelta(seconds=np.round(t2-t0))} elapsed out '
                  'of est. total time of ' +
                  str(datetime.timedelta(seconds=np.round(npos * (t2 - t0) /
                                                          (ind + 1)))))

    # nxsink.settypes = ['point', 'scan']
    printinfo('')
    print(f'Scan completed at {dt_obj.strftime("%H:%M:%S")}.')
    printinfo('')


@usercommand
@helparglist('n, NICOScommand')
def DoIt(n, NICOScommand):
    """execute a NICOScommand n-times

       example:> DoIt(10,'count(t=10)')
    """
    for _ in range(n):
        code, _ = parseScript(NICOScommand)
        for _, c in enumerate(code):
            exec(c, session.namespace)


@usercommand
def detcalib():
    """during detector electronic comissioning calibrated thresholds for each
    wire have been determined, which needs to be transferred to the electronics
    after each restart.
       The values are stored in /nicos/nicos_sinq/sans/detector.calib
    """
    printinfo('start to send SANS-1 calibration data to detector'
              ' (detector.calib)')
    dev = session.getDevice('port14')
    with open('/home/nicos/nicos/nicos_sinq/sans/detector.calib',
              encoding='utf-8') as detcalib_file:
        for line in detcalib_file:
            cmdstr = line.strip() + '\r'
            printinfo(f'>{dev.execute(cmdstr)}< >{cmdstr}<')
            sleep(0.01)
        antitofel()
        printinfo('done')


@usercommand
def tofel():
    """switch detector electronics to stroboscopic mode for data aquisition
    """
    NewSetup('detector_strobo')
    dev = session.getDevice('port14')
    cmdstr = 'EL1D\r'
    printinfo(f'>{dev.execute(cmdstr)}< >cmdstr<')
    sleep(3)
    cmdstr = 'TIWI 8\r'
    printinfo(f'>{dev.execute(cmdstr)}< >TIWI 8<')
    sleep(3)
    cmdstr = 'COIN 7\r'
    printinfo(f'>{dev.execute(cmdstr)}< >COIN 7<')
    sleep(3)


@usercommand
def antitofel():
    """switch detector electronics to static mode for data aquisition
    """
    NewSetup('detector')
    dev = session.getDevice('port14')
    cmdstr = 'EL2D\r'
    printinfo(f'>{dev.execute(cmdstr)}< >EL2D<')
    sleep(3)
    cmdstr = 'TIWI 8\r'
    printinfo(f'>{dev.execute(cmdstr)}< >TIWI 8<')
    sleep(3)
    cmdstr = 'COIN 7\r'
    printinfo(f'>{dev.execute(cmdstr)}< >COIN 7<')
    sleep(3)


@usercommand
@helparglist('devicename')
def getDevice(devicename):
    """make device available

       example:> z=getDevice('z')
    """
    try:
        d = session.getDevice(devicename)
    except ConfigurationError:
        session.log.error(
            '%s device NOT found, cannot proceed', devicename)
        return
    return d


@usercommand
@helparglist('device, value, retries=3')
def moveDevice(device, value, retries=3):
    """
       Move device to value and try it up to retries=3 times)
    """
    if isinstance(device, str):
        dev = getDevice(device)
        if dev is None:
            return
    else:
        dev = device
    for _ in range(retries):
        try:
            dev.maw(value)

            success = True
            break
        except BaseException:
            success = False
    if not success:
        session.log.error(
            'Could not move %s to %.3f within %d tries',
            dev,
            value,
            retries)
    else:
        devName = dev.name
        devUnit = dev.unit
        session.log.info('Wanted %s = %.3f %s', devName, value, devUnit)
        session.log.info('Actual %s = %s %s', devName, str(dev()), devUnit)


@usercommand
@helparglist('value')
def detoffset(value):
    """calculate and set detx.offset using value of ruler on sample table
    """
    detx = getDevice('detx')
    yo = getDevice('yo')
    detx.offset = 1732.0 - value - yo()


@usercommand
@helparglist('[lambda]')
def glambda(lambdaNM=0):
    """calculates the correction factor for 1mm water at 20C for absolute
    scaling. If lambda is not supplied or smaller or equal 0 the actual
    wavelength is used.
    """
    if lambdaNM <= 0:
        wl = getDevice('vs_lambda')
        wavelength = wl()
    else:
        wavelength = lambdaNM

    gl = 1.642 - 0.7825 * wavelength + 0.3159 * wavelength * wavelength
    printinfo('g(' + str(round(wavelength, 3)) + ') = ' + str(round(gl, 3)))
    return gl


@usercommand
@helparglist('[xi], [RPM]')
def CalcLambda(xi=0, RPM=0):
    """calculates the wavelength for a given tilt angle xi and rotation
    speed RPM. The tilt angle xi has since upgrade from SICS to NICOS opposite
    sign convention.
       If RPM is not supplied or smaller or equal 0 the actual speed is used.
       \u03be	\u0394\u03bb/\u03bb	A(\u03be)	B(\u03be)
        15	0.12	19812	0.0218
        10	0.115	17774	0.0182
         5	0.095	15493	0.0163
         0	0.1	12716	0.01097
        -5	0.155	9342	0.0269
       -10	0.3	5293	0.0869
    """

    xi_val = -xi

    if RPM <= 0:
        speed = getDevice('vs_speed')
        speed_val = speed()
    else:
        speed_val = RPM

    tsq = xi_val * xi_val
    tter = xi_val * tsq
    tquat = tter * xi_val

    A = 0.01223 + (0.000360495 * xi_val) + (0.000313819 * tsq) + \
        (0.0000304937 * tter) + (0.000000931533 * tquat)

    B = 12721.11905 - (611.74127 * xi_val) - (12.44417 * tsq) - \
        (0.12411 * tter) + (0.00583 * tquat)

    xiLambda = A + B / speed_val
    printinfo(
        'lambda(xi=' +
        str(xi_val) +
        ',RPM=' +
        str(RPM) +
        ') = ' +
        str(xiLambda))
    return xiLambda


@usercommand
@helparglist('[wl], [x[, [rmin], [y]')
def qrange(wl=0, x=0, rmin=0, y=-1):
    """calculates the available q-range on the detector.
       If wl, y or x are not supplied or smaller or equal 0 the actual
       wavelength and detector positions are used.
       If rmin is not supplied the beamstop type is read out and half of its
       diagonal is used as rmin
    """
    if wl <= 0:
        wl = getDevice('vs_lambda')
        wavelength = wl()
    else:
        wavelength = wl

    if x <= 0:
        detx = getDevice('detx')
        SD = detx()
    else:
        SD = x

    if rmin <= 0:
        bsc = getDevice('bsc')
        if bsc() == 1:
            rm = 20 * sqrt(2)
        elif bsc() == 2:
            rm = 35 * sqrt(2)
        elif bsc() == 3:
            rm = 42.5 * sqrt(2)
        else:
            rm = 50 * sqrt(2)
    else:
        rm = rmin

    if y < 0:
        dety = getDevice('dety')
        yoffset = dety()
    else:
        yoffset = y

    rmax1 = 480 * sqrt(2)
    rmax1 = 480 / sin(atan(480.0 / (480.0 + yoffset)))
    rmax2 = 480 / sin(atan(480.0 / 960.0))
    Qmin = 4 * pi / wavelength * sin(atan(rm / SD) / 2.0)
    Qmax1 = 4 * pi / wavelength * sin(atan(rmax1 / SD) / 2.0)
    Qmax2 = 4 * pi / wavelength * sin(atan(rmax2 / SD) / 2.0)

    printinfo('Qmin =' + str(round(Qmin, 5)) +
              'nm^-1 (rmin=' + str(round(rm, 2)) + 'mm)')
    printinfo('Qmax1=' + str(round(Qmax1, 5)) +
              'nm^-1 (rmax1=' + str(round(rmax1, 2)) + 'mm)')
    printinfo('Qmax2=' + str(round(Qmax2, 5)) +
              'nm^-1 (rmax2=' + str(round(rmax2, 2)) + 'mm)')
    printinfo(f'wavelength={wavelength}')
    printinfo(f'detector position (x,y)=({SD},{yoffset})')
    return [Qmin, Qmax1, Qmax2]


@usercommand
@helparglist('[Bstart], [damping], [Bmin], [waittime], [minramprate]')
def degauss(Bstart=0,
            damping=-0.6666,
            Bmin=0.001,
            waittime=2,
            minramprate=0.01):
    """demagnetize a magnet by alternating and decaying field values

       Bstart:      if start value is zero the demagnetization starts at the
                    actual value, otherwise the magnet first moves to
                    B=startvalue
       damping:     The damping or decay factor is set by default to
                    -2/3=-0.6666. At each field change its value is changed by
                    this factor. -1 < damping < 0
       Bmin:        after reaching a field of |B|<=|Bmin| the field is set to
                    zero next
       waittime:    waiting time after each field change
       minramprate: minimum ramprate. Input value needs to be >= 0
    """
    if not isinstance(Bstart, (float, int)):
        printerror('Bstart is not a number!')
        return
    if not isinstance(damping, (float, int)):
        printerror('damping is not a number!')
        return
    if not isinstance(Bmin, (float, int)):
        printerror('Bmin is not a number!')
        return
    if not isinstance(waittime, (float, int)):
        printerror('waittime is not a number!')
        return
    if not isinstance(minramprate, (float, int)):
        printerror('minramprate is not a number!')
        return
    if (minramprate <= 0):
        session.log.error(
            'wrong input value: minramprate = %.3f <= 0',
            minramprate)
        return
    if (damping <= -1) or (damping >= 0):
        session.log.error('input value damping = %.3f, condition -1<damping<0'
                          ' needs to be fullfiled', damping)
        return

    B = session.getDevice('se_mf')
    if B is None:
        return

    if B.limit < abs(Bstart):
        session.log.error(
            'input value Bstart=%.3f needs to be smaller than limit of magnet '
            'B.limit=%.3f',
            Bstart,
            B.limit)

    try:
        tmppersmode = B.persmode
        tmpramp = B.ramp
        B.persmode = 0
    except BaseException:
        session.log.warning('se_mf device does not has persistence mode')

    session.log.info('Starting degauss procedure .. ')
    if Bstart != 0:
        maw(B, Bstart)
    else:
        Bstart = B()

    multerror = False
    while abs(Bstart) > abs(Bmin):
        Bstart = Bstart * damping
        try:
            if B.ramp > 2 * abs(Bstart) and 2 * abs(Bstart) > minramprate:
                B.ramp = 2 * abs(Bstart)
        except BaseException:
            if not multerror:
                session.log.warning(
                    'se_mf device does not has a ramp parameter.')
                multerror = True
        maw(B, Bstart)
        sleep(waittime)
    B.ramp = tmpramp
    B.persmode = tmppersmode
    maw(B, 0)
    session.log.info('.. degaussing finished')


@usercommand
@helparglist('totsum [,tmax=3600] [,poll=1]')
def count2(totsum, tmax=3600, poll=1):
    """ Count until the detector has accumulated a total number of events at of
        at least a total sum of events on the whole detector around totsum.
        The acquisition should not exceed the time of max seconds.
        The status will be polled every poll-seconds.
    """
    if not isinstance(totsum, (float, int)):
        printerror('totsum is not a number!')
        return
    if not isinstance(tmax, (float, int)):
        printerror('tmax is not a number!')
        return
    if not isinstance(poll, (float, int)):
        printerror('poll is not a number!')
        return
    count_dict = {
        'sans.psi.ch': ['sansdet', 10],
        'sans-llb.psi.ch': ['sansllbdet', 5]
    }
    whereami = count_dict[socket.getfqdn()]
    detman = getDevice(whereami[0])
    preset(t=tmax)

    # get and print start time
    t0 = time.time()
    dt_obj0 = datetime.datetime.fromtimestamp(t0)
    printinfo(f'Starting at {dt_obj0.strftime("%H:%M:%S")}')
    count2progress = np.zeros(10, dtype=int)
    live(detman)
    totalsum = 0
    while totalsum < totsum:
        sleep(poll)
        if detman.isCompleted():
            break
        mlist = detman.read()
        totalsum = mlist[whereami[1]]
#        printinfo(totalsum)
        for iprog in range(9):
            if float(1.0 * totalsum / totsum) > float(iprog + 1.) / 10.0:
                if (count2progress[iprog] == 0):
                    print('####### Progress {:2.1%}'.format(float(
                        totalsum / totsum)) + ': ' + str(totalsum) + ' of ' +
                        str(totsum) + ' counts detected.')
                    count2progress[iprog] = 1
                    t1 = time.time()  # get progess time
                    if (totalsum > 0):
                        tf = t0 + (t1 - t0) / float(totalsum / totsum)
                        dt_obj = datetime.datetime.fromtimestamp(tf)
                        print(f'Estimated count completion time: '
                              f'{dt_obj.strftime("%H:%M:%S")} (started at '
                              f'{dt_obj0.strftime("%H:%M:%S")})')
                        print(f'{datetime.timedelta(seconds=np.round(t1-t0))} '
                              f'elapsed out of est. total time of '
                              f'{datetime.timedelta(seconds=np.round(tf-t0))}')
    detman.finish()
    mlist = detman.read()
    totalsum = mlist[whereami[1]]
    printinfo('finished measurement with ' + str(totalsum) +
              ' counts summed over the detector ' + whereami[0])
