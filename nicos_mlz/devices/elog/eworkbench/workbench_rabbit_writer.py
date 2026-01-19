# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-present by the NICOS contributors (see AUTHORS)
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
import csv
import io
from datetime import datetime
from html import escape
from logging import getLevelName

from PIL import Image

from nicos.core import Param
from nicos.core.params import dictof, none_or, oneof, secret
from nicos.services.elog.handler import Handler as BaseHandler
from nicos.services.elog.utils import formatMessage

from .rabbit_producer import RabbitProducer


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
        'url': Param('RabbitMQ host set in pika connection parameters',
                     type=str, ext_desc=ext_desc_conn),
        'port': Param('RabbitMQ port set in pika connection parameters',
                      type=int, default=5672, ext_desc=ext_desc_conn),
        'virtual_host': Param('RabbitMQ virtual host set in pika '
                              'connection parameters',
                              type=str, ext_desc=ext_desc_conn),
        'username': Param('RabbitMQ username from pika credentials',
                          type=str, ext_desc=ext_desc_cred),
        'password': Param('RabbitMQ password from pika credentials',
                          type=secret, mandatory=True, ext_desc=ext_desc_cred,
                          default='eln_rabbitmq_password'),
        'static_queue': Param('RabbitMQ queue name used in given pika '
                              'channel',
                              type=str, ext_desc=ext_desc_chann),
        'group_mapping': Param('Mapping of events to groups',
                               type=dictof(
                                   oneof('hidden', 'directory', 'newexperiment',
                                         'setup', 'entry', 'remark', 'scriptend',
                                         'scriptbegin', 'sample', 'detectors',
                                         'environment', 'offset', 'attachment',
                                         'image', 'message', 'scanbegin',
                                         'scanend',
                                         ),
                                   none_or(oneof('Setup', 'Sample', 'Scan', ))
                               ),
                               settable=False, userparam=False,
                               default={
                                   'directory': 'Setup',
                                   'newexperiment': 'Setup',
                                   'setup': 'Setup',
                                   'sample': 'Sample',
                                   'detectors': 'Setup',
                                   'environment': 'Setup',
                                   'attachment': None,
                                   'image': None,
                                   'scanbegin': 'Scan',
                                   'scanend': 'Scan',
                               }),
    }

    def doInit(self, mode):
        BaseHandler.doInit(self, mode)
        password = self.password.lookup('RabbitMQ password is required')
        self._rabbit_producer = RabbitProducer(
            url=self.url,
            port=self.port,
            virtual_host=self.virtual_host,
            username=self.username,
            password=password,
            static_queue=self.static_queue)

        self.log.info('workbench_writer: handle init')

    @property
    def _eln_enabled(self):
        return not self._hidden

    def doShutdown(self):
        self._rabbit_producer.close()
        self.log.info('workbench_writer: handler close')

    def handle_hidden(self, time, data):
        BaseHandler.handle_hidden(self, time, data)
        self.log.info('workbench_writer: handle hidden')

        # the switch logic is applied here
        self._hidden = data

        # with restart handle_enable is called before handle directory
        if self._proposal != '':
            headers = self._make_headers(subject='EnableELN',
                                         line_count=1,
                                         timestamp=time,
                                         eln_enabled=True)

            self._rabbit_producer.produce(headers=headers,
                                          message=wb_format
                                          (f'enable eln set to : {self._eln_enabled}'))

    def handle_directory(self, time, data):
        BaseHandler.handle_directory(self, time, data)
        self.log.info('workbench_writer: handle directory')

        if not self._instr:
            self._instr = 'NICOS'

        wb_text = wb_format(
            f'Opened new output files in:   {self._logdir}') + wb_format(
            f'Instrument:   {self._instr}') + wb_format(
            f'Proposal:   {self._proposal}')

        headers = self._make_headers(subject='Directory',
                                     line_count=3,
                                     timestamp=time,
                                     grouping=self.group_mapping.get(
                                         'directory'))

        self._rabbit_producer.produce(headers=headers, message=wb_text)

    def handle_newexperiment(self, time, data):
        BaseHandler.handle_newexperiment(self, time, data)
        self.log.info('workbench_writer: handle newexperiment')

        headers = self._make_headers(subject='NewExperiment',
                                     line_count=3,
                                     timestamp=time,
                                     grouping=self.group_mapping.get(
                                         'newexperiment'))

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(
                                          f'New Experiment: {self._title} <br>'
                                          f'Users: {self._users} <br>'
                                          f'Localcontact: '
                                          f'{self._localcontact}'))

    def handle_setup(self, time, setupnames):
        self.log.info('workbench_writer: handle setup')

        wb_text = wb_format(
            f'Setup Components:  {escape(", ".join(setupnames))}')

        headers = self._make_headers(subject='Setup',
                                     line_count=1,
                                     timestamp=time,
                                     grouping=self.group_mapping.get(
                                         'setup'))

        self._rabbit_producer.produce(headers=headers, message=wb_text)

    def handle_entry(self, time, data):
        self.log.info('workbench_writer: handle entry')

        headers = self._make_headers(subject='Entry',
                                     line_count=1 + escape(data).count('\n')
                                                + data.count('<br>'),
                                     timestamp=time)

        data = data.replace('\n', '<br>')
        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(f'{data}'))

    def handle_remark(self, time, remark):
        self.log.info('workbench_writer: handle remark')

        headers = self._make_headers(subject='Remark',
                                     line_count=1,
                                     timestamp=time)

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(f'{remark}'))

    def handle_scriptend(self, time, script):
        self.log.info('workbench_writer: handle scriptend')

        headers = self._make_headers(subject='Scriptend',
                                     line_count=1,
                                     timestamp=time)

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(f'{escape(script)}'))

    def handle_scriptbegin(self, time, script):
        self.log.info('workbench_writer: handle scriptbegin')

        headers = self._make_headers(subject='Scriptbegin',
                                     line_count=1,
                                     timestamp=time)

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(f'{escape(script)}'))

    def handle_sample(self, time, sample):
        self.log.info('workbench_writer: handle sample')

        headers = self._make_headers(subject='Sample',
                                     line_count=1,
                                     timestamp=time,
                                     grouping=self.group_mapping.get(
                                         'sample'))

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(
                                          f'Sample:   {escape(sample)}'))

    def handle_detectors(self, time, dlist):
        self.log.info('workbench_writer: handle detectors')

        headers = self._make_headers(subject='Detectors',
                                     line_count=1,
                                     timestamp=time,
                                     grouping=self.group_mapping.get(
                                         'detectors'))

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(
                                          f'Detectors:   '
                                          f'{escape(", ".join(dlist))}'))

    def handle_environment(self, time, elist):
        self.log.info('workbench_writer: handle environment')

        headers = self._make_headers(subject='Environment',
                                     line_count=1,
                                     timestamp=time,
                                     grouping=self.group_mapping.get(
                                         'environment'))

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(
                                          f'Environment:   '
                                          f'{escape(", ".join(elist))}'))

    def handle_offset(self, time, data):
        self.log.info('workbench_writer: handle offset')

        dev, old, new = data
        offset_info = escape('Offset of %s changed from %s to %s' %
                             (dev, old, new))

        headers = self._make_headers(subject='Offset',
                                     line_count=1,
                                     timestamp=time)

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_format(f'{offset_info}'))

    def handle_attachment(self, time, data):
        self.log.info('workbench_writer: handle attachment as file')

        description, fpaths, names = data
        for fpath, name in zip(fpaths, names):
            with open(fpath, 'rb') as opened_file:
                data = opened_file.read()
                self._rabbit_producer.handle_file(
                    headers={'proposal': self._proposal,
                             'subject': f'{description} {name}',
                             'note': 0,
                             'loglevel': None,
                             'attachment': 0,
                             'file': 1,
                             'line_count': 0,
                             'img_rows': 0,
                             'eln_enabled': self._eln_enabled,
                             'exp_title': self._title,
                             'users': self._users,
                             'localcontact': self._localcontact,
                             'grouping': self.group_mapping.get('attachment'),
                             'timestamp': wb_timestring_1(time)
                             },
                    file_stream=data)

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
                    self._rabbit_producer.handle_attachment(
                        headers={
                            'proposal': self._proposal,
                            'subject': f'{description} {name}',
                            'note': 0,
                            'loglevel': None,
                            'attachment': 1,
                            'file': 0,
                            'line_count': 0,
                            'img_rows': img_rows,
                            'eln_enabled': self._eln_enabled,
                            'exp_title': self._title,
                            'users': self._users,
                            'localcontact': self._localcontact,
                            'grouping': self.group_mapping.get('image'),
                            'timestamp': wb_timestring_1(time)
                        }, png_stream=finalimg)

    def handle_message(self, time, message):
        formatted = formatMessage(message)
        if not formatted:
            return
        self.log.info('workbench_writer: message')

        headers = self._make_headers(subject=f'{getLevelName(message[2])}',
                                     line_count=1,
                                     loglevel=getLevelName(message[2]),
                                     timestamp=time)

        self._rabbit_producer.produce(headers=headers,
                                      message=formatted)

    def handle_scanbegin(self, time, dataset):
        self.log.info('workbench_writer: handle scanbegin')

        wb_text = wb_format(f'Starting scan:   {dataset.scaninfo}') + wb_format(
            f'Started at:   {datetime(*dataset.started[:6])}')

        headers = self._make_headers(subject='Scanbegin',
                                     line_count=4,
                                     timestamp=time,
                                     grouping=self.group_mapping.get(
                                         'scanbegin'))

        self._rabbit_producer.produce(headers=headers,
                                      message=wb_text)

    def handle_scanend(self, time, dataset):
        self.log.info('workbench_writer: handle scanend')

        scannumber = dataset.counter or -1
        scan_end_results = ''

        scan_end_results += wb_format(
            f'Finished at:   {wb_timestring_2(time)}')
        for file_name in dataset.filepaths:
            scan_end_results += wb_format(f'Filename:   {file_name}')

        # empty lines
        scan_end_results += '<br><br>'

        npoints = len(dataset.xresults)
        dataset_names = []
        dateset_range_vals = []
        csv_data = ''

        if dataset.xresults:
            for i in range(len(dataset.xnames)):
                if i < len(dataset.xnames) - dataset.envvalues:
                    first = dataset.xresults[0][i]
                    last = dataset.xresults[-1][i]
                else:
                    first = min(
                        (dataset.xresults[j][i] for j in range(npoints)),
                        key=lambda x: x or 0)
                    last = max(
                        (dataset.xresults[j][i] for j in range(npoints)),
                        key=lambda x: x or 0)
                dataset_names.append(
                    dataset.xnames[i] + '(' + dataset.xunits[i] + ')')
                if first == last:
                    dateset_range_vals.append(f'{wb_val_format(first)}')
                else:
                    dateset_range_vals.append(
                        f'{wb_val_format(first)} - <br>{wb_val_format(last)}')

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

            csv_data = eln_csv_data(x_names=dataset.xnames,
                                    x_results=dataset.xresults)

        headers = self._make_headers(subject=f'Scanresults {scannumber}',
                                     line_count=15,
                                     timestamp=time,
                                     grouping=self.group_mapping.get(
                                         'scanend'))

        self._rabbit_producer.produce(headers=headers,
                                      message=scan_end_results)

        if csv_data:
            self._rabbit_producer.handle_file(
                headers={'proposal': self._proposal,
                         'subject': f'SCAN_{scannumber}.csv',
                         'note': 0,
                         'loglevel': None,
                         'attachment': 0,
                         'file': 1,
                         'line_count': 0,
                         'img_rows': 0,
                         'eln_enabled': self._eln_enabled,
                         'exp_title': self._title,
                         'users': self._users,
                         'localcontact': self._localcontact,
                         'grouping': None,
                         'timestamp': wb_timestring_1(time)},
                file_stream=csv_data.encode('utf-8'))

    def _make_headers(self,
                      subject,
                      line_count,
                      timestamp,
                      grouping=None,
                      loglevel=None,
                      eln_enabled=None):
        return rb_headers_note(
            proposal=self._proposal,
            title=self._title,
            users=self._users,
            localcontact=self._localcontact,
            eln_enabled=
            self._eln_enabled if eln_enabled is None else eln_enabled,
            subject=subject,
            line_count=line_count,
            timestamp=wb_timestring_1(timestamp),
            grouping=grouping,
            loglevel=loglevel
        )


def wb_val_format(wb_val):
    if isinstance(wb_val, (int, float, complex)):
        return f'{wb_val:.3f}'
    return f'{wb_val}'


def wb_format(wb_line):
    return f'<pre style="margin: 0px !important;">{wb_line}</pre>'


def wb_timestring_1(time):
    return datetime.fromtimestamp(time).strftime('%b %d %Y %H:%M:%S')


def wb_timestring_2(time):
    return datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')


def eln_csv_data(x_names, x_results):
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(x_names)
    for point in x_results:
        cw.writerow(point)
    return si.getvalue()


def rb_headers_note(proposal, subject, line_count, title,
                    users, localcontact,
                    timestamp,
                    eln_enabled=True,
                    grouping=None,
                    loglevel=None):
    return {
        'proposal': proposal,
        'subject': subject,
        'note': 1,
        'loglevel': loglevel,
        'attachment': 0,
        'file': 0,
        'line_count': line_count,
        'img_rows': 0,
        'eln_enabled': eln_enabled,
        'exp_title': title,
        'users': users,
        'localcontact': localcontact,
        'grouping': grouping,
        'timestamp': timestamp
    }
