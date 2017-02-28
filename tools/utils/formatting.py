#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""
Utility script for reformatting NICOS setup files via yapf
(https://github.com/google/yapf).
"""
import re
import yapf

# Style specification for yapf
STYLE_CONFIG = '''{
ALIGN_CLOSING_BRACKET_WITH_VISUAL_INDENT : True,
ALLOW_MULTILINE_LAMBDAS : True,
BLANK_LINE_BEFORE_NESTED_CLASS_OR_DEF : False,
COALESCE_BRACKETS : True,
COLUMN_LIMIT : 80,
CONTINUATION_INDENT_WIDTH : 4,
DEDENT_CLOSING_BRACKETS : True,
INDENT_DICTIONARY_VALUE : True,
JOIN_MULTIPLE_LINES : False,
SPACES_AROUND_POWER_OPERATOR = True,
SPACES_AROUND_DEFAULT_OR_NAMED_ASSIGN = True,
SPACES_BEFORE_COMMENT : 2,
SPACE_BETWEEN_ENDING_COMMA_AND_CLOSING_BRACKET : False;
SPLIT_ARGUMENTS_WHEN_COMMA_TERMINATED : True,
SPLIT_BEFORE_BITWISE_OPERATOR : True,
SPLIT_BEFORE_FIRST_ARGUMENT : False,
SPLIT_BEFORE_LOGICAL_OPERATOR : True,
SPLIT_BEFORE_NAMED_ASSIGNS : True,
USE_TABS : False,
}'''

def format_setup_text(origin):
    result = yapf.yapf_api.FormatCode(origin, style_config=STYLE_CONFIG)[0]

    # custom replacement for device class on device line
    result = re.sub(r'(device\()\n\s*', '\\1', result)

    # strip the result (in case of unnecessary newlines at the end)
    result = result.strip() + '\n'

    return result
