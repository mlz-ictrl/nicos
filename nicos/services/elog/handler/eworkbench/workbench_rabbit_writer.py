# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   Josef Baudisch <josef.baudisch@frm2.tum.de>
#
# *****************************************************************************


import io
import numpy as np
from scipy.signal import argrelmax, argrelmin
from PIL import Image

from nicos.core import Param
from nicos.services.elog.handler import Handler as BaseHandler
from nicos.services.elog.utils import formatMessage
from nicos.services.elog.utils import formatMessagePlain

from nicos.services.elog.handler.eworkbench.rabbit_producer import \
    RabbitProducer


class RabbitWriter:
    def __init__(self):
        self.note_id = None
        self.element_pk = None
        self.proposal = ''
        self.title = ''
        self.instr = ''
        self.dir = ''
        self.note_title = ''
        self.last_action = 'Init'
        self.last_global_action = 'Init'
        self.line_count = 0
        self.elist = []
        self.rabbit_producer = None

    def close(self):
        self.rabbit_producer.close()


class Handler(BaseHandler):
    ext_desc_conn = \
        'The classic object for specifying all of the ' \
        'connection parameters required to connect to RabbitMQ, ' \
        'ConnectionParameters provides attributes ' \
        'for tweaking every possible connection option: ' \
        'https://pika.readthedocs.io/en/stable/modules/parameters.html#connectionparameters'
    ext_desc_cred = \
        'The credentials classes are used to encapsulate all ' \
        'authentication information for the ConnectionParameters class: ' \
        'https://pika.readthedocs.io/en/stable/modules/credentials.html'
    ext_desc_chann = \
        'A Channel is the primary communication method ' \
        'for interacting with RabbitMQ: ' \
        'https://pika.readthedocs.io/en/stable/modules/channel.html#module-pika.channel'

    parameters = {
        'rabbit_url': Param('RabbitMQ host set in pika connection parameters',
                            type=str,
                            ext_desc=ext_desc_conn),
        'rabbit_port': Param('RabbitMQ port set in pika connection parameters',
                             type=int, default=5672,
                             ext_desc=ext_desc_conn),
        'rabbit_virtual_host': Param(
            'RabbitMQ virtual host set in pika connection parameters',
            type=str,
            ext_desc=ext_desc_conn),
        'rabbit_username': Param('RabbitMQ username from pika credentials',
                                 type=str,
                                 ext_desc=ext_desc_cred),
        'rabbit_password': Param('RabbitMQ password from pika credentials',
                                 type=str,
                                 ext_desc=ext_desc_cred),
        'rabbit_static_queue': Param(
            'RabbitMQ queue name used in given pika channel',
            type=str,
            ext_desc=ext_desc_chann),
    }

    def doInit(self, mode):
        self._out = RabbitWriter()

        self._out.rabbit_producer = RabbitProducer(
            rabbit_url=self.rabbit_url,
            rabbit_port=self.rabbit_port,
            rabbit_virtual_host=self.rabbit_virtual_host,
            rabbit_username=self.rabbit_username,
            rabbit_password=self.rabbit_password,
            rabbit_static_queue=self.rabbit_static_queue)

        self.log.info('workbench_writer: handle init')

    def doShutdown(self):
        self._out.close()
        self.log.info('workbench_writer: handler close')

    def handle_directory(self, time, data):
        BaseHandler.handle_directory(self, time, data)
        self.log.info('workbench_writer: handle directory')
        self._out.last_action = 'Directory'
        self._out.last_global_action = 'Directory'
        # get proposal name here
        self._out.dir, self._out.instr, self._out.proposal = data

    def handle_newexperiment(self, time, data):
        self.log.info('workbench_writer: handle newexperiment')
        self._out.last_action = 'NewExperiment'
        self._out.last_global_action = 'NewExperiment'

        # get proposal name also here if proposal name in handle directory
        # was missing

        self._out.proposal, self._out.title = data

    def handle_setup(self, time, setupnames):
        self.log.info('workbench_writer: handle setup')
        self._out.last_action = 'Setup'
        self._out.last_global_action = 'Setup'

    def handle_entry(self, time, data):
        self.log.info('workbench_writer: handle entry')
        self._out.last_action = 'Entry'
        self._out.last_global_action = 'Entry'

        headers = {
            'proposal': self._out.proposal,
            'subject': 'Comment',
            'new_note': 1,
            'attachment': 0,
            'file': 0,
            'patch_lines': 1,
            'line_count': self._out.line_count,
        }
        self._out.rabbit_producer.produce(headers=headers, message='')

        headers['new_note'] = 0
        headers['patch_lines'] = 0
        headers['line_count'] = 0
        self._out.rabbit_producer.produce(headers=headers, message=str(data))

    def handle_remark(self, time, remark):
        self.log.info('workbench_writer: handle remark')
        self._out.last_action = 'AfterRemark'
        self._out.last_global_action = 'Afterremark'

        headers = {
            'proposal': self._out.proposal,
            'subject': 'Remark %s' % remark,
            'new_note': 1,
            'attachment': 0,
            'file': 0,
            'patch_lines': 1,
            'line_count': self._out.line_count,
        }
        self._out.rabbit_producer.produce(headers=headers, message='')
        remark_content = '<pre style="margin: 0px !important;">%s' % remark
        headers['new_note'] = 0
        headers['patch_lines'] = 0
        headers['line_count'] = 0
        self._out.rabbit_producer.produce(headers=headers,
                                          message=remark_content)

    def handle_scriptend(self, time, script):
        self.log.info('workbench_writer: handle scriptend')

    def handle_sample(self, time, sample):
        self.log.info('workbench_writer: handle sample')
        self._out.last_action = 'Sample'
        self._out.last_global_action = 'Sample'

    def handle_detectors(self, time, dlist):
        self.log.info('workbench_writer: handle detectors')
        self._out.last_action = 'Detectors'
        self._out.last_global_action = 'Detectors'

    def handle_environment(self, time, elist):
        self.log.info('workbench_writer: handle environment')
        self._out.elist = elist
        self._out.last_action = 'Environment'
        self._out.last_global_action = 'Environment'

    def handle_offset(self, time, data):
        self.log.info('workbench_writer: handle offset')
        self._out.last_action = 'Offset'
        self._out.last_global_action = 'Offset'

    def handle_image(self, time, data):
        self.log.info('workbench_writer: handle attachment as image')
        self._out.last_action = 'AfterAttachment'
        self._out.last_global_action = 'Attachment'
        description, fpaths, extensions, names = data  # pylint: disable=unused-variable

        pngs = [(p, n) for (p, n, e) in zip(fpaths, names, extensions)
                if e.lower() == '.png']

        if pngs:
            for png_path, name in pngs:
                with open(png_path, 'rb') as opened_file:
                    basewidth = 1200
                    img = Image.open(opened_file)
                    wpercent = (basewidth / float(img.size[0]))
                    hsize = int((float(img.size[1]) * float(wpercent)))
                    res = img.resize((basewidth, hsize))
                    byteIO = io.BytesIO()
                    res.save(byteIO, format='PNG')
                    data = byteIO.getvalue()
                    self._out.rabbit_producer.handle_attachment(
                        headers={
                            'proposal': self._out.proposal,
                            'subject': name,
                            'new_note': 0,
                            'attachment': 1,
                            'file': 0,
                            'patch_lines': 0,
                            'line_count': 0,
                        }, png_stream=data)

    def handle_message(self, time, message):

        headers = {
            'proposal': self._out.proposal,
            'subject': self._out.last_action,
            'new_note': 0,
            'attachment': 0,
            'file': 0,
            'patch_lines': 1,
            'line_count': self._out.line_count,
        }

        if self._out.last_action == 'scanbegin':
            self._out.rabbit_producer.produce(headers=headers, message='')

        if self._out.last_global_action != 'scanbegin':
            if self._out.last_action != 'message':
                self._out.note_title = self._out.last_action

                headers['new_note'] = 1
                self._out.rabbit_producer.produce(headers=headers, message='')

                # we want to create a new note only if it is not a scanrun
                self._out.line_count = 0

            self.log.info('workbench_writer: handle message')
            self._out.last_action = 'message'
            self._out.line_count += 1

            formatted = formatMessage(message)
            rabbit_formatted = formatMessagePlain(message)
            if not formatted:
                return

            content = '<pre style="margin: 0px !important;">' + formatted

            if not rabbit_formatted:
                return

            headers['new_note'] = 0
            headers['patch_lines'] = 0
            headers['line_count'] = 0
            self._out.rabbit_producer.produce(headers=headers, message=content)

    def handle_scanbegin(self, time, dataset):
        self.log.info('workbench_writer: handle scanbegin')
        self._out.last_action = 'scanbegin'
        self._out.last_global_action = 'scanbegin'

    def handle_scanend(self, time, dataset):
        self.log.info('workbench_writer: handle scanend')
        self._out.last_action = 'AfterScanend'
        self._out.last_global_action = 'scanend'

        xresults_t = np.array(dataset.xresults).transpose()

        env_indices = []
        max_dict = {}
        for env_name in self._out.elist:
            env_indices.append([dataset.xnames.index(env_name), env_name])
        for env_idx in env_indices:
            _max = max(xresults_t[env_idx[0]])

            max_dict[env_idx[1]] = '%s at point: %s' % (
                _max, (xresults_t[env_idx[0]].argmax() + 1))

        scannumber = dataset.counter or -1
        yresults_t = np.array(dataset.yresults).transpose()

        loc_line_count = 0
        scan_end_results = ''

        scan_end_results += '<pre style="margin: 0px !important;">' + \
                            '------NUMBER OF POINTS ------' + '\n'

        scan_end_results += '<pre style="margin: 0px !important;">%d' % len(
            dataset.xresults)

        scan_end_results = scan_end_results + '<br>'
        loc_line_count += 2

        scan_end_results += '<pre style="margin: 0px !important;">' + \
                            '------ENVIRONMENT MAXIMUM------' + '\n'

        loc_line_count += 1
        for k, v in max_dict.items():
            scan_end_results += '<pre style="margin: 0px !important;">' \
                                '%s : %s\n' % (k, v)

            loc_line_count += 1

        scan_end_results += '<br>'
        scan_end_results += '<pre style="margin: 0px !important;">' + \
                            '-------Y-RESULTS MIN/MAX-------' + '\n'

        for i in range(len(yresults_t)):

            scan_end_results += '<pre style="margin: 0px !important;"> %s' \
                                '      begin: %s  end: %s\n' % (
                                    dataset.yvalueinfo[i], yresults_t[i][0],
                                    yresults_t[i][-1])

            loc_line_count += 1
            max_arr = argrelmax(yresults_t[i])[0]
            min_arr = argrelmin(yresults_t[i])[0]

            if len(max_arr) > 0:
                scan_end_results += '<pre style="margin: 0px !important;">' \
                                    '---MAXIMA---\n'
                loc_line_count += 1
            for j in range(len(max_arr)):
                scan_end_results += '<pre style="margin: 0px !important;">' \
                                    'Point: %s Val: %s\n' % (
                                        1 + int(max_arr[j]),
                                        yresults_t[i][max_arr[j]])
                loc_line_count += 1

            if len(min_arr) > 0:
                scan_end_results += '<pre style="margin: 0px !important;">' \
                                    '---MINIMA---\n'
                loc_line_count += 1

            for j in range(len(min_arr)):
                scan_end_results += '<pre style="margin: 0px !important;">' \
                                    'Point: %s Val: %s\n' % (
                                        1 + int(min_arr[j]),
                                        yresults_t[i][min_arr[j]])
                loc_line_count += 1

            scan_end_results += '<pre style="margin: 0px !important;">\n'
            scan_end_results += '<br>'
            loc_line_count += 2

        headers = {
            'proposal': self._out.proposal,
            'subject': 'Scanresults %s Maxima-Minima' % scannumber,
            'new_note': 1,
            'attachment': 0,
            'file': 0,
            'patch_lines': 1,
            'line_count': self._out.line_count,
        }

        self._out.rabbit_producer.produce(headers=headers, message='')

        headers['new_note'] = 0
        headers['patch_lines'] = 0
        headers['line_count'] = 0
        self._out.rabbit_producer.produce(headers=headers,
                                          message=scan_end_results)

        headers['patch_lines'] = 1
        headers['line_count'] = loc_line_count
        self._out.rabbit_producer.produce(headers=headers, message='')

        self._out.line_count = loc_line_count
