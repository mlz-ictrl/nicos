#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2016 by the NICOS contributors (see AUTHORS)
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

"""Utilities for sending E-Mails."""

from os import path

# do not call this file email.py !

from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate

import smtplib

from nicos.pycompat import string_types
from nicos.core.params import mailaddress


def sendMail(mailserver, receiverlist, mailsender, topic, body,
             attach_files=(), debuglevel=0):
    """Sends an email to a list of receivers with given topic and content via
    the given server.

    Returns True if succesful and list of error-messages else

    mailserver is a working E-Mailserver accepting mail from us,
    receiverlist is a not empty list of valid E-Mail adresses or a string with
    comma-separated E-Mail adresses
    sender is a valid E-Mail-address,
    topic and body are strings and the list of attach_files may be empty
    if attach_files is not empty, it must contain names of existing files!
    """
    # try to check parameters
    errors = []
    if isinstance(receiverlist, string_types):
        receiverlist = receiverlist.replace(',', ' ').split()
    try:
        mailaddress(mailsender)
    except ValueError as e:
        errors.append('Mailsender: %s' % e)
    for a in receiverlist:
        try:
            mailaddress(a)
        except ValueError as e:
            errors.append('Receiver: %s' % e)
    for fn in attach_files:
        if not path.exists(fn):
            errors.append('Attachment %r does not exist, please check config!' % fn)
        elif not path.isfile(fn):
            errors.append('Attachment %r is not a file, please check config!' % fn)
    if errors:
        return ['No mail sent because of invalid parameters'] + errors

    # construct msg according to
    # http://docs.python.org/library/email-examples.html#email-examples
    receivers = ', '.join(receiverlist)
    msg = MIMEMultipart()
    msg['Subject'] = topic
    msg['From'] = mailsender
    msg['To'] = receivers
    msg['Date'] = formatdate()
    # Set Return-Path so that it isn't set (generally incorrectly) for us.
    msg['Return-Path'] = mailsender
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # now attach the files
    for fn in attach_files:
        with open(fn, 'rb') as fp:
            filedata = fp.read()

        attachment = MIMEApplication(filedata, 'x-zip')  # This may need adjustments!
        attachment['Content-Disposition'] = 'ATTACHMENT; filename="%s"' % \
            path.basename(fn)
        msg.attach(attachment)

    # now comes the final part: send the mail
    mailer = None
    try:
        mailer = smtplib.SMTP(mailserver)
        if debuglevel == 'debug':
            mailer.set_debuglevel(debuglevel)
        mailer.sendmail(mailsender, receiverlist + [mailsender], msg.as_string())
    except Exception as e:
        return [str(e)]
    finally:
        if mailer:
            mailer.quit()
