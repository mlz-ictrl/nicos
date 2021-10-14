# -*- coding: utf-8 -*-
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

sysconfig = dict(
    datasinks=['FileWriterControl'],
    experiment='Exp',
)

devices = dict(
    KafkaFileWriter=device('nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description='Status for nexus file writing',
        brokers=['someserver:9092'],
        statustopic='TEST_writerStatus',
    ),
    Exp=device('nicos.devices.experiment.Experiment',
        description='experiment object',
        dataroot='data',
        sample='Sample',
    ),
    Sample=device('nicos.devices.sample.Sample',
        description='The currently used sample',
    ),
    NexusStructure=device(
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureTemplate',
        description='Provides the NeXus structure',
        templatesmodule='nicos_ess.ymir.nexus.nexus_templates',
        templatename='ymir_default',
    ),
    FileWriterStatus=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterStatus',
        description='Status for file-writer',
        brokers=['1.2.3.4:9092'],
        statustopic='TEST_controlTopic',
        unit='',
    ),
    FileWriterControl=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterControlSink',
        description='Control for file-writer',
        brokers=['1.2.3.4:9092'],
        unit='',
        pool_topic='TEST_jobPool',
        nexus='NexusStructure',
        status='FileWriterStatus',
    ),
    motor=device(
        'nicos.devices.generic.VirtualMotor',
        unit='deg',
        curvalue=0,
        abslimits=(0, 5),
    ),
    timer=device(
        'nicos.devices.generic.VirtualTimer',
        lowlevel=True,
    ),
    ctr1=device(
        'nicos.devices.generic.VirtualCounter',
        lowlevel=True,
        type='counter',
        countrate=2000.,
        fmtstr='%d',
    ),
    det=device(
        'nicos.devices.generic.Detector',
        timers=['timer'],
        counters=['ctr1'],
        maxage=3,
        pollinterval=0.5,
    ),
)
