#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""Graphical proposal management tool."""

__version__ = "$Revision$"

import os
import re
import shutil
import zipfile
import tempfile
import traceback
from os import path

from PyQt4.QtCore import SIGNAL, QDate, Qt
from PyQt4.QtGui import QDialog, QListWidgetItem, QIntValidator, \
     QDoubleValidator, QRadioButton, QMessageBox, QProgressDialog
from PyQt4.uic import loadUi

from nicos.gui.tools.uitools import DlgPresets, runDlgStandalone, selectOutputFile

def toint(ctl):
    try:
        return int(str(ctl.text()))
    except:
        return 0

def tofloat(ctl):
    try:
        return float(str(ctl.text()))
    except:
        return 0.0


class ProposalInput(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        loadUi(path.join(path.dirname(__file__), 'proposal.ui'), self)

        self.connect(self.options, SIGNAL('itemClicked(QListWidgetItem*)'),
                     self.optionsSelected)
        self.connect(self.createtas, SIGNAL('clicked()'), self.createTasFile)
        self.connect(self.selectarchivefile, SIGNAL('clicked()'),
                     self.selectArchiveFile)
        self.connect(self.archivedata, SIGNAL('clicked()'),
                     self.archiveDataFiles)
        self.connect(self.createstartup, SIGNAL('clicked()'),
                     self.createStartupFile)

        for opmode, explanation in custom.TASOPMODELIST:
            self.opmode.addItem('%s (%s)' % (opmode, explanation))
        for unit in custom.ETRANSFERUNITS:
            self.etransfer.addItem(unit)

        for lv in self.headerdevs, self.datapointdevs, self.logdevs, self.options:
            lv.clear()

        for opt in custom.OPTIONS:
            item = QListWidgetItem(opt, self.options)
            item.setCheckState(Qt.Unchecked)

        self.setInstSelection()
        self.instrument = 0
        self.sel_options = []
        self.setDevSelection()

        intval = QIntValidator(self)
        dblval = QDoubleValidator(self)

        for le in [self.proposal, self.scat1, self.scat2, self.scat3,
                   self.h1, self.k1, self.l1, self.h2, self.k2, self.l2]:
            le.setValidator(intval)
        for le in [self.a, self.b, self.c, self.alpha, self.beta, self.gamma,
                   self.psi0]:
            le.setValidator(dblval)

        self.presets = DlgPresets('proposalinput', [
            (self.proposal, ''), (self.user, ''), (self.sampleinfo, ''),
            (self.emailaddr, ''), (self.sampledetectordist, '1240'),
            (self.samplename, ''), (self.etransfer, 0), (self.opmode, 0),
            (self.scat1, '-1'), (self.scat2, '1'), (self.scat3, '0'),
            (self.a, ''), (self.b, ''), (self.c, ''), (self.alpha, ''),
            (self.beta, ''), (self.gamma, ''), (self.h1, ''), (self.k1, ''),
            (self.l1, ''), (self.h2, ''), (self.k2, ''), (self.l2, ''),
            (self.psi0, '0'), (self.archivefile, ''),
        ])
        self.presets.load()

        self.datefrom.setDate(QDate.currentDate())
        self.dateuntil.setDate(QDate.currentDate())

    def setDevSelection(self):
        self.devlist = []
        lvs = (self.headerdevs, self.datapointdevs, self.logdevs)
        for lv in lvs:
            lv.clear()
        for (dev, info) in custom.DEVICES.iteritems():
            if info[0] in (-1, self.instrument):
                use = 0
                if not info[1]:
                    use = 1
                else:
                    for option in info[1]:
                        if option in self.sel_options:
                            use = 1
                            break
                if not use:
                    continue
                self.devlist.append(dev)
                for (i, lv) in enumerate(lvs):
                    item = QListWidgetItem(dev, lv)
                    item.setCheckState(info[2][i] and Qt.Checked or Qt.Unchecked)
                    #lv.insertItem(item)

    def setInstSelection(self):
        self.instrumentCtls = []
        for name in custom.INSTRUMENTS:
            ctl = QRadioButton(name, self.instframe)
            self.instrumentCtls.append(ctl)
            self.connect(ctl, SIGNAL('clicked(bool)'), self.instSelected)
            self.instframe.layout().addWidget(ctl)
        self.instrumentCtls[0].setChecked(True)

    def instSelected(self, *ignored):
        for i, ctl in enumerate(self.instrumentCtls):
            if ctl.isChecked():
                self.instrument = i
        self.setDevSelection()

    def optionsSelected(self, item):
        if not item:
            return
        self.sel_options = []
        for i in range(self.options.count()):
            item = self.options.item(i)
            if item.checkState() == Qt.Checked:
                self.sel_options.append(item.text())
        self.setDevSelection()

    def createStartupFile(self):
        self.presets.save()
        propnr = str(self.proposal.text())
        try:
            int(propnr)
        except:
            QMessageBox.warning(self, 'Error', 'Proposal number must be integer.')
            return
        user = str(self.user.text())
        if not user:
            QMessageBox.warning(self, 'Error', 'Please enter a user name.')
            return
        emailaddr = str(self.emailaddr.text())
        emailaddr = ', '.join(repr(addr.strip()) for addr in emailaddr.split(','))

        intv = str(self.interval.text())
        try:
            intv = int(intv)
        except:
            intv = 30

        proppath = path.join(custom.TCSPATH, str(propnr))
        try:
            if not os.path.isdir(proppath):
                os.mkdir(proppath)

        except Exception, err:
            QMessageBox.warning(self, 'Error', 'Could not create %s: %s.' %
                                (proppath, err))
            return

        devlists = []
        for lv in (self.headerdevs, self.datapointdevs, self.logdevs):
            devlists.append([])
            for i in range(lv.count()):
                item = lv.item(i)
                if item.checkState() == Qt.Checked:
                    devlists[-1].append(str(item.text()))

        sampleinfo = str(self.sampleinfo.text())
        try:
            sampledetectordist = int(self.sampledetectordist.text())
        except:
            QMessageBox.warning(self, 'Error', 'Sample-detector distance must be '
                                'integer.')
            return

        expdevs = [dev for dev in self.devlist if custom.DEVICES[dev][3]]

        try:
            f = open(proppath + '/init.py', 'w')
            f.write('''\
# NICOS initialization file for proposal %s
DataBox.newexperiment(user=%r, proposal=%r)
DataBox.setSampleInfo(%r)
DataBox.setSampleDetectorDistance(%r)
%s
%s
%sDataBox.instrumentparamslist = [%s]
DataBox.defdevlist = [%s]
%s
%s
''' % (propnr, user, propnr, sampleinfo, sampledetectordist,
       custom.INSTRUMENT_COMMANDS[self.instrument],
       emailaddr and 'SetMailReceivers(%s)\n' % emailaddr or '',
       expdevs and 'NicmFactory(%s)\n' % ', '.join(map(repr, expdevs)) or '',
       ', '.join(devlists[0]), ', '.join(devlists[1]),
       custom.HAS_SAVED_ADJUSTS and '''# DataBox.clearAdjusts()  # enable for the first time only
DataBox.loadAdjusts()''' or '',
       '\n'.join('startlogging(%s, %s)' % (dev, intv) for dev in devlists[2]),
       ))
            f.close()
        except Exception, err:
            QMessageBox.warning(self, 'Error', 'Could not create init.py: %s.' % err)
            return

        QMessageBox.information(self, 'Created startup file',
                                'You can now load %s in the ' % (proppath+'/init.py') +
                                'user editor to setup Nicos to your experiment.')
        self.close()

    def createTasFile(self):
        self.presets.save()
        propnr = str(self.proposal.text())
        try:
            int(propnr)
        except:
            QMessageBox.warning(self, 'Error', 'Proposal number must be integer.')
            return

        samplename = str(self.samplename.text())
        samplefn = re.sub('[^a-zA-Z0-9_-]', '', samplename.replace(' ', '_'))
        proppath = path.join(custom.TCSPATH, str(propnr))
        samplepath = proppath + '/sample-%s.py' % samplefn
        opmode = str(self.opmode.currentText())
        opmode = opmode[:opmode.find(' ')]

        f = open(samplepath, 'w')
        f.write('''\
# NICOS sample setup file for sample %s
SetSampleName(%r)
SetSample(%s, %s, %s, %s, %s, %s)
SetOrient(%s, %s, %s, %s, %s, %s, %s)
SetScatSense([%s, %s, %s])
SetEnergyTransferUnit(%r)
SetOpMode(%r)
''' % (samplename, samplename,
       self.a.text(), self.b.text(), self.c.text(),
       self.alpha.text(), self.beta.text(), self.gamma.text(),
       self.h1.text(), self.k1.text(), self.l1.text(),
       self.h2.text(), self.k2.text(), self.l2.text(), self.psi0.text(),
       self.scat1.text(), self.scat2.text(), self.scat3.text(),
       str(self.etransfer.currentText()), opmode))
        f.close()

        QMessageBox.information(self, 'Created startup file',
                                'You can now load %s in the ' % samplepath +
                                'user editor to setup Nicos to your sample.')
        self.close()


    def archiveDataFiles(self):
        pdlg = QProgressDialog('Archiving files...', 'Cancel', 0, 100000, self)
        pdlg.setCancelButton(None)
        pdlg.show()
        try:
            self._archiveDataFiles(pdlg)
        except:
            tb = traceback.format_exc()
            QMessageBox.warning(self, 'Error', 'Error while archiving:\n\n' + tb)
        pdlg.destroy()

    def _archiveDataFiles(self, pdlg):
        self.presets.save()
        propnr = str(self.proposal.text())
        try:
            int(propnr)
        except:
            QMessageBox.warning(self, 'Error', 'Proposal number must be integer.')
            return

        arcfile = str(self.archivefile.text())
        if path.exists(arcfile):
            if QMessageBox.question(
                self, 'Overwrite file?', 'Output file already exists. '
                'Overwrite it?', QMessageBox.Yes, QMessageBox.No) \
                == QMessageBox.No:
                return
        if not arcfile:
            QMessageBox.warning(self, 'Error', 'Archive name must not be empty.')
            return

        datefrom = self.datefrom.date()
        dateuntil = self.dateuntil.date()

        if datefrom > dateuntil:
            QMessageBox.warning(self, 'Error', '"From" date must be before '
                                '"Until" date.')
            return

        tempdir = tempfile.mkdtemp()

        pdlg.setValue(0)
        prog = 0

        datafiles = custom.DATA_FILES(propnr,
            (datefrom.year(), datefrom.month(), datefrom.day()),
            (dateuntil.year(), dateuntil.month(), dateuntil.day()))

        print datafiles
        step = 70000.0 / len(datafiles)
        for fpname in datafiles:
            prog += step
            pdlg.setValue(int(prog))
            if path.isfile(fpname):
                shutil.copyfile(fpname,
                    path.join(tempdir, path.basename(fpname)))
            elif path.isdir(fpname):
                shutil.copytree(fpname,
                    path.join(tempdir, path.basename(fpname)))

        prog = 70000
        days = range(datefrom.daysTo(dateuntil)+1)
        step = 10000.0 / len(days)
        for i in days:
            prog += step
            pdlg.setValue(int(prog))
            d = datefrom.addDays(i)
            fmt1 = d.toString("ddMMyyyy")
            fmt2 = d.toString("yyyy-MM-dd")
            if custom.NICOSLOGPATH:
                for fname in [
                    path.join(custom.NICOSLOGPATH, 'cmd%s.log' % fmt1),
                    path.join(custom.NICOSLOGPATH, 'error%s.log' % fmt1)
                    ]:
                    if path.exists(fname):
                        shutil.copyfile(
                            fname, path.join(tempdir, path.basename(fname)))
            if custom.DAEMONLOGPATH:
                for fname in [
                    path.join(custom.DAEMONLOGPATH, 'licd.out-%s' % fmt2),
                    path.join(custom.DAEMONLOGPATH, 'licd.log-%s' % fmt2)
                    ]:
                    if path.exists(fname):
                        shutil.copyfile(
                            fname, path.join(tempdir, path.basename(fname)))

        prog = 80000
        step = 20000.0
        zf = zipfile.ZipFile(arcfile, 'w')
        for root, dirs, files in os.walk(tempdir):
            xroot = root[len(tempdir):].strip('/') + '/'
            for file in files:
                zf.write(path.join(root, file), xroot + file)
        zf.close()

        shutil.rmtree(tempdir)

        QMessageBox.information(self, 'Info', 'The archive file %s was created '
                                'successfully.' % arcfile)

        self.close()


    def selectArchiveFile(self):
        selectOutputFile(self.archivefile, self, 'Select a target file name:')


if __name__ == '__main__':
    runDlgStandalone(ProposalInput)
