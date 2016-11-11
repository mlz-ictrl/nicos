#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

from nicos import session
from nicos.core.data import DataSink, DataSinkHandler


class DiObHandler(DataSinkHandler):
    def end(self):
        exp = session.experiment
        try:
            last_img = self.dataset.filepaths[0]
        except IndexError:
            return

        if exp.curimgtype == 'openbeam':
            self.log.info('last open beam image is %r', last_img)
            exp._setROParam('lastopenbeamimage', last_img)
        elif exp.curimgtype == 'dark':
            self.log.info('last dark image is %r', last_img)
            exp._setROParam('lastdarkimage', last_img)


class DiObSink(DataSink):
    # Nop sink
    handlerclass = DiObHandler
