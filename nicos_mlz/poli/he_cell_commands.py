#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Andrew Sazonov <andrew.sazonov@frm2.tum.de>
#   Georg Brandl <g.brandl@fz-juelich.de>
#
# *****************************************************************************

"""3He cell specific commands for POLI."""

from os import path
from time import strftime

from nicos import session
from nicos.commands import usercommand
from nicos.commands.basic import pause
from nicos.commands.device import maw
from nicos.commands.measure import count
from nicos.commands.output import printinfo

from nicos_mlz.poli.commands import pos

__all__ = [
    'AddHeCells',
    'RemoveHeCells',
    'AddHeCellToPolariser',
    'AddHeCellToPolariserHkl',
    'RemoveHeCellFromPolariser',
    'RemoveHeCellFromPolariserHkl',
]


def analyser_trans(cells0, cells1):
    """Transmission of analyser cell."""
    try:
        result = cells1[3] / cells0[3] * 100
    except ZeroDivisionError:
        result = float('Inf')
    return result


def polariser_trans(cells1, cells2):
    """Transmission of polariser cell."""
    try:
        result = cells2[2] / cells1[2] * 100
    except ZeroDivisionError:
        result = float('Inf')
    return result


def format_datetime():
    return strftime('%Y/%m/%d %H:%M')


def cells_file():
    """Return full path to the cells file."""
    return path.join(session.experiment.proposalpath, 'data', 'cells.txt')


LARGE_COMMENT = '#' + '=' * 148 + '\n'
SMALL_COMMENT = '#' + '-' * 148 + '\n'


def AddCountsToCellsFile(analyser, polariser, counts):
    """Add cells info to the file."""
    timer, mon1, mon2, ctr1 = counts
    hkl = session.instrument.read()
    gamma = session.getDevice('gamma')
    omega = session.getDevice('omega')
    chi1 = session.getDevice('chi1')
    chi2 = session.getDevice('chi2')
    if 'xtrans' in session.devices:
        xtransval = session.getDevice('xtrans')()
    else:
        xtransval = 0
    if 'ytrans' in session.devices:
        ytransval = session.getDevice('ytrans')()
    else:
        ytransval = 0
    with open(cells_file(), 'a') as f:
        f.write('{:10d}{:11d}{:10.2f}{:10d}{:10d}{:10d}'
                '{:>12}{:>7}{:8.1f}{:8.1f}'
                '{:8.1f}{:8.1f}{:8.1f}{:8.1f}'
                '{:7.1f}{:7.1f}{:7.1f}\n'
                .format(analyser, polariser, timer, mon1, mon2, ctr1,
                        strftime('%Y/%m/%d'), strftime('%H:%M'), gamma(), omega(),
                        chi1(), chi2(), xtransval, ytransval,
                        hkl[0], hkl[1], hkl[2]))


def AddHeaderToCellsFile(analyser_cell_name, analyser_cell_pressure,
                         polariser_cell_name, polariser_cell_pressure, wavelen):
    """Add header info to the file."""
    with open(cells_file(), 'a') as f:
        f.write(LARGE_COMMENT)
        f.write('# Analyser/decpol cell ({}) pressure = {} bar,  Polariser '
                'cell ({}) pressure = {} bar,  Wavelength = {} Angstrom\n'
                .format(analyser_cell_name, analyser_cell_pressure,
                        polariser_cell_name, polariser_cell_pressure, wavelen))
        f.write(LARGE_COMMENT)
        f.write('#{:>9}{:>11}{:>10}{:>10}{:>10}{:>10}{:>12}{:>7}'
                '{:>8}{:>8}{:>8}{:>8}{:>8}{:>8}{:>7}{:>7}{:>7}\n'
                .format('analyser', 'polariser', 'timer', 'mon1', 'mon2', 'ctr1',
                        'date', 'time', 'gamma', 'omega', 'chi1', 'chi2',
                        'xtrans', 'ytrans', 'h', 'k', 'l'))
        f.write(LARGE_COMMENT)


def AddPolariserHeaderToCellsFile(polariser_cell_name, polariser_cell_pressure,
                                  wavelen):
    """Add header info to the file."""
    with open(cells_file(), 'a') as f:
        f.write(LARGE_COMMENT)
        f.write('# Polariser cell ({}) pressure = {} bar,  '
                'Wavelength = {} Angstrom\n'
                .format(polariser_cell_name, polariser_cell_pressure, wavelen))
        f.write(LARGE_COMMENT)
        f.write('#{:>9}{:>11}{:>10}{:>10}{:>10}{:>10}{:>12}{:>7}'
                '{:>8}{:>8}{:>8}{:>8}{:>8}{:>8}{:>7}{:>7}{:>7}\n'
                .format('analyser', 'polariser', 'timer', 'mon1', 'mon2', 'ctr1',
                        'date', 'time', 'gamma', 'omega', 'chi1', 'chi2',
                        'xtrans', 'ytrans', 'h', 'k', 'l'))
        f.write(LARGE_COMMENT)


def AddTransToCellsFile(analyser_cell_transmission, polariser_cell_transmission):
    """Add transmission info to the file."""
    with open(cells_file(), 'a') as f:
        f.write(SMALL_COMMENT)
        f.write('# Analyser/decpol cell: Transmission = {:.2f} %,  Polariser '
                'cell: Transmission = {:.2f} %\n'
                .format(analyser_cell_transmission, polariser_cell_transmission))
        f.write(SMALL_COMMENT)


def AddPolariserTransToCellsFile(polariser_cell_transmission):
    """Add transmission info to the file."""
    with open(cells_file(), 'a') as f:
        f.write(SMALL_COMMENT)
        f.write('# Polariser cell: Transmission = {:.2f} %\n'.format(polariser_cell_transmission))
        f.write(SMALL_COMMENT)


def AddFooterToCellsFile():
    """Add footer info to the file."""
    with open(cells_file(), 'a') as f:
        f.write('\n\n')


LARGE_SEP = '=' * 100
SMALL_SEP = '-' * 100


@usercommand
def AddHeCells(h_index, k_index, l_index, count_time,
               analyser_cell_name, analyser_cell_pressure,
               polariser_cell_name, polariser_cell_pressure):
    """Add new 3He cells to analyser and polariser."""
    gamma = session.getDevice('gamma')
    wavelength = session.getDevice('wavelength')
    det = session.getDevice('det')
    printinfo(LARGE_SEP)
    printinfo('Add new 3He cells')
    printinfo(SMALL_SEP)
    printinfo('Go to hkl ({} {} {})'.format(h_index, k_index, l_index))
    printinfo(SMALL_SEP)
    pos(h_index, k_index, l_index)
    gamma_hkl = gamma()
    gamma_cell = 60.0
    printinfo(SMALL_SEP)
    printinfo('Measurement without cells. {}'.format(format_datetime()))
    printinfo(SMALL_SEP)
    cells0 = count(det, count_time)
    wavelen = wavelength()
    AddHeaderToCellsFile(analyser_cell_name, analyser_cell_pressure,
                         polariser_cell_name, polariser_cell_pressure, wavelen)
    AddCountsToCellsFile(False, False, cells0)
    maw(gamma, gamma_cell)
    pause('Insert cell {} into analyser/decpol.'.format(analyser_cell_name))
    maw(gamma, gamma_hkl)
    printinfo(SMALL_SEP)
    printinfo('Measurement with 1 cell: {} [{} bar] in analyser/decpol. {}'
              .format(analyser_cell_name, analyser_cell_pressure,
                      format_datetime()))
    printinfo(SMALL_SEP)
    cells1 = count(det, count_time)
    AddCountsToCellsFile(True, False, cells1)
    analyser_cell_transmission = analyser_trans(cells0, cells1)
    maw(gamma, gamma_cell)
    pause('Analyser/decpol cell {}:\n   Pressure = {} bar, '
          'Transmission = {:8.2f} %.\n\nNow, insert cell {} into polariser.'
          .format(analyser_cell_name, analyser_cell_pressure,
                  analyser_cell_transmission, polariser_cell_name))
    maw(gamma, gamma_hkl)
    printinfo(SMALL_SEP)
    printinfo('Measurement with 2 cells: {} [{} bar] in analyser/decpol and '
              '{} [{} bar] in polariser. {}'
              .format(analyser_cell_name, analyser_cell_pressure,
                      polariser_cell_name, polariser_cell_pressure,
                      format_datetime()))
    printinfo(SMALL_SEP)
    cells2 = count(det, count_time)
    AddCountsToCellsFile(True, True, cells2)
    polariser_cell_transmission = polariser_trans(cells1, cells2)
    AddTransToCellsFile(analyser_cell_transmission, polariser_cell_transmission)
    pause('Cells are inserted.\n\nAnalyser/decpol cell {}:\n'
          '   Pressure = {} bar, Transmission = {:8.2f} %,\n\n'
          'Polariser cell {}:\n   Pressure = {} bar, Transmission = {:8.2f} %'
          .format(analyser_cell_name, analyser_cell_pressure,
                  analyser_cell_transmission, polariser_cell_name,
                  polariser_cell_pressure, polariser_cell_transmission))
    printinfo(SMALL_SEP)
    printinfo('Cells are inserted.')
    printinfo('Analyser/decpol cell {}: pressure = {} bar, transmission = {:9.4f} %'
              .format(analyser_cell_name, analyser_cell_pressure,
                      analyser_cell_transmission))
    printinfo('Polariser cell {}: pressure = {} bar, transmission = {:9.4f} %'
              .format(polariser_cell_name, polariser_cell_pressure,
                      polariser_cell_transmission))
    printinfo(LARGE_SEP)


@usercommand
def RemoveHeCells(h_index, k_index, l_index, count_time):
    """Remove old 3He cells from polariser and analyser."""
    gamma = session.getDevice('gamma')
    det = session.getDevice('det')
    printinfo(LARGE_SEP)
    printinfo('Remove old 3He cells')
    printinfo(SMALL_SEP)
    printinfo('Go to hkl ({} {} {})'.format(h_index, k_index, l_index))
    printinfo(SMALL_SEP)
    pos(h_index, k_index, l_index)
    gamma_hkl = gamma()
    gamma_cell = 60.0
    printinfo(SMALL_SEP)
    printinfo('Measurement with 2 cells: in analyser/decpol and polariser. {}'
              .format(format_datetime()))
    printinfo(SMALL_SEP)
    cells2 = count(det, count_time)
    AddCountsToCellsFile(True, True, cells2)
    maw(gamma, gamma_cell)
    pause('Remove cell from polariser.')
    maw(gamma, gamma_hkl)
    printinfo(SMALL_SEP)
    printinfo('Measurement with 1 cell: in analyser/decpol. {}'
              .format(format_datetime()))
    printinfo(SMALL_SEP)
    cells1 = count(det, count_time)
    AddCountsToCellsFile(True, False, cells1)
    polariser_cell_transmission = polariser_trans(cells1, cells2)
    maw(gamma, gamma_cell)
    pause('Polariser cell:\n   Transmission = {:8.2f} %.\n\n'
          'Now, remove cell from analyser/decpol.'
          .format(polariser_cell_transmission))
    maw(gamma, gamma_hkl)
    printinfo(SMALL_SEP)
    printinfo('Measurement without cells. {}'.format(format_datetime()))
    printinfo(SMALL_SEP)
    cells0 = count(det, count_time)
    AddCountsToCellsFile(False, False, cells0)
    analyser_cell_transmission = analyser_trans(cells0, cells1)
    AddTransToCellsFile(analyser_cell_transmission, polariser_cell_transmission)
    AddFooterToCellsFile()
    pause('Cells are removed.\n\nPolariser cell:\n'
          '   Transmission = {:8.2f} %,\n\nAnalyser/decpol cell:\n'
          '   Transmission = {:8.2f} %'
          .format(polariser_cell_transmission, analyser_cell_transmission))
    printinfo(SMALL_SEP)
    printinfo('Cells are removed.')
    printinfo('Polariser cell: transmission = {:9.4f} %'
              .format(polariser_cell_transmission))
    printinfo('Analyser/decpol cell: transmission = {:9.4f} %'
              .format(analyser_cell_transmission))
    printinfo(LARGE_SEP)


@usercommand
def AddHeCellToPolariserHkl(h_index, k_index, l_index, count_time,
                            polariser_cell_name, polariser_cell_pressure):
    """Add new 3He cell to polariser (only)."""
    gamma = session.getDevice('gamma')
    wavelength = session.getDevice('wavelength')
    det = session.getDevice('det')
    printinfo(LARGE_SEP)
    printinfo('Add new 3He cell to polariser (only)')
    printinfo(SMALL_SEP)
    printinfo('Go to hkl ({} {} {})'.format(h_index, k_index, l_index))
    printinfo(SMALL_SEP)
    pos(h_index, k_index, l_index)
    gamma_hkl = gamma()
    gamma_cell = 60.0
    printinfo(SMALL_SEP)
    printinfo('Measurement without cell. {}'.format(format_datetime()))
    printinfo(SMALL_SEP)
    cells0 = count(det, count_time)
    wavelen = wavelength()
    AddPolariserHeaderToCellsFile(polariser_cell_name, polariser_cell_pressure,
                                  wavelen)
    AddCountsToCellsFile(False, False, cells0)
    maw(gamma, gamma_cell)
    pause('Insert cell {} into polariser and press "Continue script" after that.'
          .format(polariser_cell_name))
    maw(gamma, gamma_hkl)
    printinfo(SMALL_SEP)
    printinfo('Measurement with 1 cell: {} [{} bar] in polariser. {}'
              .format(polariser_cell_name, polariser_cell_pressure,
                      format_datetime()))
    printinfo(SMALL_SEP)
    cells1 = count(det, count_time)
    AddCountsToCellsFile(False, True, cells1)
    polariser_cell_transmission = polariser_trans(cells0, cells1)
    AddPolariserTransToCellsFile(polariser_cell_transmission)
    pause('Cell is inserted.\n\nPolariser cell {}:\n'
          '   Pressure = {} bar, Transmission = {:8.2f} %'
          .format(polariser_cell_name, polariser_cell_pressure,
                  polariser_cell_transmission))
    printinfo(SMALL_SEP)
    printinfo('Cell is inserted.')
    printinfo('Polariser cell {}: pressure = {} bar, transmission = {:9.4f} %'
              .format(polariser_cell_name, polariser_cell_pressure,
                      polariser_cell_transmission))
    printinfo(LARGE_SEP)


@usercommand
def AddHeCellToPolariser(count_time, polariser_cell_name, polariser_cell_pressure):
    """Add new 3He cell to polariser (only)."""
    gamma = session.getDevice('gamma')
    wavelength = session.getDevice('wavelength')
    det = session.getDevice('det')
    printinfo(LARGE_SEP)
    printinfo('Add new 3He cell to polariser (only)')
    printinfo(SMALL_SEP)
    gamma_cell = 60.0
    printinfo(SMALL_SEP)
    printinfo('Measurement without cell. {}'.format(format_datetime()))
    printinfo(SMALL_SEP)
    cells0 = count(det, count_time)
    wavelen = wavelength()
    AddPolariserHeaderToCellsFile(polariser_cell_name, polariser_cell_pressure,
                                  wavelen)
    AddCountsToCellsFile(False, False, cells0)
    maw(gamma, gamma_cell)
    pause('Insert cell {} into polariser and press "Continue script" after that.'
          .format(polariser_cell_name))
    printinfo(SMALL_SEP)
    printinfo('Measurement with 1 cell: {} [{} bar] in polariser. {}'
              .format(polariser_cell_name, polariser_cell_pressure,
                      format_datetime()))
    printinfo(SMALL_SEP)
    cells1 = count(det, count_time)
    AddCountsToCellsFile(False, True, cells1)
    polariser_cell_transmission = polariser_trans(cells0, cells1)
    AddPolariserTransToCellsFile(polariser_cell_transmission)
    pause('Cell is inserted.\n\nPolariser cell {}:\n'
          '   Pressure = {} bar, Transmission = {:8.2f} %'
          .format(polariser_cell_name, polariser_cell_pressure,
                  polariser_cell_transmission))
    printinfo(SMALL_SEP)
    printinfo('Cell is inserted.')
    printinfo('Polariser cell {}: pressure = {} bar, transmission = {:9.4f} %'
              .format(polariser_cell_name, polariser_cell_pressure,
                      polariser_cell_transmission))
    printinfo(LARGE_SEP)


@usercommand
def RemoveHeCellFromPolariserHkl(h_index, k_index, l_index, count_time):
    """Remove old 3He cell from polariser (only)."""
    gamma = session.getDevice('gamma')
    det = session.getDevice('det')
    printinfo(LARGE_SEP)
    printinfo('Remove old 3He cell from polariser (only)')
    printinfo(SMALL_SEP)
    printinfo('Go to hkl ({} {} {})'.format(h_index, k_index, l_index))
    printinfo(SMALL_SEP)
    pos(h_index, k_index, l_index)
    gamma_hkl = gamma()
    gamma_cell = 60.0
    printinfo(SMALL_SEP)
    printinfo('Measurement with 1 cell: in polariser. {}'
              .format(format_datetime()))
    printinfo(SMALL_SEP)
    cells1 = count(det, count_time)
    AddCountsToCellsFile(False, True, cells1)
    maw(gamma, gamma_cell)
    pause('Remove cell from polariser and press "Continue script" after that.')
    maw(gamma, gamma_hkl)
    printinfo(SMALL_SEP)
    printinfo('Measurement without cells. {}'.format(format_datetime()))
    printinfo(SMALL_SEP)
    cells0 = count(det, count_time)
    AddCountsToCellsFile(False, False, cells0)
    polariser_cell_transmission = polariser_trans(cells0, cells1)
    AddPolariserTransToCellsFile(polariser_cell_transmission)
    AddFooterToCellsFile()
    pause('Cell is removed.\n\nPolariser cell:\n   Transmission = {:8.2f} %'
          .format(polariser_cell_transmission))
    printinfo(SMALL_SEP)
    printinfo('Cell is removed.')
    printinfo('Polariser cell: transmission = {:9.4f} %'
              .format(polariser_cell_transmission))
    printinfo(LARGE_SEP)


@usercommand
def RemoveHeCellFromPolariser(count_time):
    """Remove old 3He cell from polariser (only)."""
    gamma = session.getDevice('gamma')
    det = session.getDevice('det')
    printinfo(LARGE_SEP)
    printinfo('Remove old 3He cell from polariser (only)')
    printinfo(SMALL_SEP)
    gamma_cell = 60.0
    printinfo(SMALL_SEP)
    printinfo('Measurement with 1 cell: in polariser. {}'
              .format(format_datetime()))
    printinfo(SMALL_SEP)
    cells1 = count(det, count_time)
    AddCountsToCellsFile(False, True, cells1)
    maw(gamma, gamma_cell)
    pause('Remove cell from polariser and press "Continue script" after that.')
    printinfo(SMALL_SEP)
    printinfo('Measurement without cells. {}'.format(format_datetime()))
    printinfo(SMALL_SEP)
    cells0 = count(det, count_time)
    AddCountsToCellsFile(False, False, cells0)
    polariser_cell_transmission = polariser_trans(cells0, cells1)
    AddPolariserTransToCellsFile(polariser_cell_transmission)
    AddFooterToCellsFile()
    pause('Cell is removed.\n\nPolariser cell:\n   Transmission = {:8.2f} %'
          .format(polariser_cell_transmission))
    printinfo(SMALL_SEP)
    printinfo('Cell is removed.')
    printinfo('Polariser cell: transmission = {:9.4f} %'
              .format(polariser_cell_transmission))
    printinfo(LARGE_SEP)
