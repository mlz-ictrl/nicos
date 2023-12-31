# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2024 by the NICOS contributors (see AUTHORS)
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
from PIL import Image
from html import escape
from logging import ERROR
from datetime import datetime

from nicos.core import Param
from nicos.services.elog.handler import Handler as BaseHandler
from nicos.services.elog.utils import formatMessage

from nicos.services.elog.handler.eworkbench.rabbit_producer import \
    RabbitProducer


class RabbitWriter:
    def __init__(self):
        self.proposal = ''
        self.instr = ''
        self.logdir = ''
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

        # get proposal here
        self._out.logdir, self._out.instr, self._out.proposal = data
        if not self._out.instr:
            self._out.instr = 'NICOS'

        wb_text = wb_format(
            f'Opened new output files in:   {self._out.logdir}') + wb_format(
            f'Instrument:   {self._out.instr}') + wb_format(
            f'Proposal:   {self._out.proposal}')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Directory  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=3)

        self._out.rabbit_producer.produce(headers=headers, message=wb_text)

    def handle_newexperiment(self, time, data):
        self.log.info('workbench_writer: handle newexperiment')

        # get proposal here if proposal name in handle directory was missing
        self._out.proposal, title = data

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject='NewExperiment  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(
                                              f'New Experiment is: {title}'))

    def handle_setup(self, time, setupnames):
        self.log.info('workbench_writer: handle setup')

        wb_text = wb_format(
            f'Setup Components:  {escape(", ".join(setupnames))}')
        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Setup  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers, message=wb_text)

    def handle_entry(self, time, data):
        self.log.info('workbench_writer: handle entry')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Entry  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(f'{escape(data)}'))

    def handle_remark(self, time, remark):
        self.log.info('workbench_writer: handle remark')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Remark  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(f'{remark}'))

    def handle_scriptend(self, time, script):
        self.log.info('workbench_writer: handle scriptend')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Scriptend  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(
                                              f'{escape(script)}'))

    def handle_scriptbegin(self, time, script):
        self.log.info('workbench_writer: handle scriptbegin')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Scriptbegin  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(
                                              f'{escape(script)}'))

    def handle_sample(self, time, sample):
        self.log.info('workbench_writer: handle sample')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Sample  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(
                                              f'Sample:   {escape(sample)}'))

    def handle_detectors(self, time, dlist):
        self.log.info('workbench_writer: handle detectors')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Detectors  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(
                                              f'Detectors:   '
                                              f'{escape(", ".join(dlist))}'))

    def handle_environment(self, time, elist):
        self.log.info('workbench_writer: handle environment')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Environment  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(
                                              f'Environment:   '
                                              f'{escape(", ".join(elist))}'))

    def handle_offset(self, time, data):
        self.log.info('workbench_writer: handle offset')

        dev, old, new = data
        offset_info = escape('Offset of %s changed from %s to %s' %
                             (dev, old, new))

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Offset  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=1)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_format(f'{offset_info}'))

    def handle_attachment(self, time, data):
        self.log.info('workbench_writer: handle attachment as file')

        description, fpaths, names = data
        for fpath, name in zip(fpaths, names):
            with open(fpath, 'rb') as opened_file:
                data = opened_file.read()
                self._out.rabbit_producer.handle_file(
                    headers={'proposal': self._out.proposal,
                             'subject': f'{self._out.proposal}  '
                                        f'{description} {name}  '
                                        f'{wb_timestring_1(time)}',
                             'note': 0,
                             'attachment': 0,
                             'file': 1,
                             'line_count': 0,
                             'img_rows': 0}, file_stream=data)

    def handle_image(self, time, data):
        self.log.info('workbench_writer: handle attachment as image')

        description, fpaths, extensions, names = data

        pngs = [(p, n) for (p, n, e) in zip(fpaths, names, extensions)
                if e.lower() == '.png']
        svgs = [(p, n) for (p, n, e) in zip(fpaths, names, extensions) if
                e.lower() == '.svg']
        if svgs:
            svg_fpaths, svg_names = zip(*svgs)
            self.handle_attachment(time, [description, svg_fpaths, svg_names])

        if pngs:
            for png_path, name in pngs:
                with open(png_path, 'rb') as opened_file:
                    basewidth = 1200
                    baseheight = 900
                    img = Image.open(opened_file)
                    wpercent = (basewidth / float(img.size[0]))
                    hsize = int((float(img.size[1]) * float(wpercent)))
                    if hsize > baseheight:
                        hpercent = (baseheight / hsize)
                        basewidth = int(basewidth * float(hpercent))
                        hsize = baseheight
                    res = img.resize((basewidth, hsize))
                    img_rows = int(hsize / 32) + 1
                    byteIO = io.BytesIO()
                    res.save(byteIO, format='PNG')
                    finalimg = byteIO.getvalue()
                    self._out.rabbit_producer.handle_attachment(
                        headers={
                            'proposal': self._out.proposal,
                            'subject': f'{self._out.proposal}  '
                                       f'{description} {name}  '
                                       f'{wb_timestring_1(time)}',
                            'note': 0,
                            'attachment': 1,
                            'file': 0,
                            'line_count': 0,
                            'img_rows': img_rows
                        }, png_stream=finalimg)

    def handle_message(self, time, message):
        formatted = formatMessage(message)
        if not formatted:
            return
        if message[2] == ERROR:
            self.log.info('workbench_writer: handle error message')
            headers = rb_headers_note(proposal=self._out.proposal,
                                      subject=f'ERROR   '
                                              f'{wb_timestring_1(time)}',
                                      line_count=1)

            self._out.rabbit_producer.produce(headers=headers,
                                              message=wb_format(f'{formatted}'))

        return

    def handle_scanbegin(self, time, dataset):
        self.log.info('workbench_writer: handle scanbegin')

        wb_text = wb_format(f'Starting scan:   {dataset.info}') + \
                  wb_format(f'Started at:   '
                            f'{wb_timestring_2(dataset.started)}')

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Scanbegin  '
                                          f'{wb_timestring_1(time)}',
                                  line_count=4)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=wb_text)

    def handle_scanend(self, time, dataset):
        self.log.info('workbench_writer: handle scanend')

        scannumber = dataset.counter or -1
        scan_end_results = ''

        scan_end_results += wb_format(f'Starting scan:   {dataset.scaninfo}')
        scan_end_results += wb_format(
            f'Started  at:   {datetime(*dataset.started[:6])}')
        scan_end_results += wb_format(
            f'Finished at:   '
            f'{wb_timestring_2(time)}')
        for file_name in dataset.filepaths:
            scan_end_results += wb_format(f'Filename:   {file_name}')

        # empty lines
        scan_end_results += '<br><br>'

        npoints = len(dataset.xresults)
        dataset_names = []
        dateset_range_vals = []

        if dataset.xresults:
            for i in range(len(dataset.xnames)):
                if i < len(dataset.xnames) - dataset.envvalues:
                    first = dataset.xresults[0][i]
                    last = dataset.xresults[-1][i]
                else:
                    first = min(
                        (dataset.xresults[j][i] for j in range(npoints)),
                        key=lambda x: x or 0)
                    last = max((dataset.xresults[j][i] for j in range(npoints)),
                               key=lambda x: x or 0)
                dataset_names.append(
                    dataset.xnames[i] + '(' + dataset.xunits[i] + ')')
                if first == last:
                    dateset_range_vals.append(f'{first:.3f}')
                else:
                    dateset_range_vals.append(f'{first:.3f} - <br>{last:.3f}')

            cell_width = '%s' % (round(100 / (len(dataset_names) + 2), 3))
            scan_end_results += '<table style="border-collapse: collapse; ' \
                                'width: 90%; height: 100px;" border="1"> <tbody>'
            scan_end_results += '<tr>'
            scan_end_results += f'<td style="width: {cell_width} ;">' \
                                f'{wb_format("SCAN")}</td>'
            scan_end_results += f'<td style="width: {cell_width} ;">' \
                                f'{wb_format("POINTS")}</td></td>'
            for i in range(len(dataset_names)):
                scan_end_results += f'<td style="width: {cell_width} ;">' \
                                    f'{wb_format(dataset_names[i])}</td>'
            scan_end_results += '</tr>'
            scan_end_results += '<tr>'
            scan_end_results += f'<td style="width: {cell_width} ;">' \
                                f'{wb_format(scannumber)}</td>'
            scan_end_results += f'<td style="width: {cell_width} ;">' \
                                f'{wb_format(npoints)}</td>'

            for i in range(len(dateset_range_vals)):
                scan_end_results += f'<td style="width: {cell_width} ;">' \
                                    f'{wb_format(dateset_range_vals[i])}</td>'

            scan_end_results += '</tr>'
            scan_end_results += '</tbody></table>'

        headers = rb_headers_note(proposal=self._out.proposal,
                                  subject=f'Scanresults {scannumber}   '
                                          f'{wb_timestring_1(time)}',
                                  line_count=15)

        self._out.rabbit_producer.produce(headers=headers,
                                          message=scan_end_results)


def wb_format(wb_line):
    return f'<pre style="margin: 0px !important;">{wb_line}</pre>'


def wb_timestring_1(time):
    return datetime.fromtimestamp(time).strftime("%b %d %Y %H:%M:%S")


def wb_timestring_2(time):
    return datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")


def rb_headers_note(proposal, subject, line_count):
    return {
        'proposal': proposal,
        'subject': subject,
        'note': 1,
        'attachment': 0,
        'file': 0,
        'line_count': line_count,
        'img_rows': 0
    }
