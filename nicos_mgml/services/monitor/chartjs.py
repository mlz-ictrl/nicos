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
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

import json
import random
import struct


def construct_color(val, opacity):
    if 'rgba' in val:
        return val
    if '#' in val:
        val = struct.unpack('BBB', val.decode('hex'))
    val = val + (opacity,)
    return 'rgba' + str(val)


DEFAULT_BLUE = {
                'fill_color': 'rgba(151,187,205,0.2)',
                'stroke_color': 'rgba(151,187,205,1)',
                'point_color': 'rgba(151,187,205,1)',
                'point_stroke_color': '#fff',
                'point_highlight_fill_color': '#fff',
                'point_highlight_stroke_color': 'rgba(151,187,205,1)',
            }
DEFAULT_GREEN = {
                'fill_color': 'rgba(0,255,0,0.2)',
                'stroke_color': 'rgba(39, 174, 96,.4)',
                'point_color': 'rgba(39, 174, 96,1)',
                'point_stroke_color': '#fff',
                'point_highlight_fill_color': '#fff',
                'point_highlight_stroke_color': 'rgba(39, 174, 96,1)',
            }
DEFAULT_RED = {
                'fill_color': 'rgba(255,0,0,0.2)',
                'stroke_color': 'rgba(192, 57, 43,.4)',
                'point_color': 'rgba(192, 57, 43,1)',
                'point_stroke_color': '#fff',
                'point_highlight_fill_color': '#fff',
                'point_highlight_stroke_color': 'rgba(192, 57, 43,1)',
            }
DEFAULT_BLACK = {
                'fill_color': 'rgba(O,0,0,0.2)',
                'stroke_color': 'rgba(0, 0, 0,.4)',
                'point_color': 'rgba(0, 0, 0,1)',
                'point_stroke_color': '#fff',
                'point_highlight_fill_color': '#fff',
                'point_highlight_stroke_color': 'rgba(0, 0, 0,1)',
            }


class ScatterChart():

    def __init__(self, width=450, height=340, params={}):
        self.embed = f'<div class="chart-area"><canvas id="myChart" height="{height}"></canvas></div><script>'
        self.type = 'Scatter'
        self.struct = 'points'
        self.secondaxis = False

        self.x = {}
        self.y = {}
        self.params = {'datasetFill': False, 'animation': True, 'pointDot': False}
        self.params.update(params)

    def set_color(self, dimension, color_scheme):
        self.y[dimension].update(color_scheme)
        return dimension

    def add_line(self, name, lst, options={}):
        self.y[name] = {'values': lst, 'name': name}
        self.set_color(name, DEFAULT_RED)

        for key in options.keys():
            if 'color' in key and type(options[key]) == dict:
                options[key] = construct_color(options[key].get('color', (0, 0, 0)), options[key].get('opacity', 1))
        self.y[name].update(options)

    def update_line(self, name, key, value):
        self.y.get(name, {})[key] = value

    def build_chart(self):
        data  = {'labels': self.x, 'datasets': []}
        for dimension in reversed(self.y.keys()):
            line = {
                'label': str(self.y[dimension].get('name')),
                'backgroundColor': self.y[dimension].get('fill_color'),
                'borderColor': self.y[dimension].get('stroke_color'),
                'pointBackgroundColor': self.y[dimension].get('point_color',),
                'pointBorderColor': self.y[dimension].get('point_stroke_color'),
                # TODO: doubled entry
                'pointHoverBackgroundColor': self.y[dimension].get('point_highlight_fill_color'),
                # 'pointHoverBackgroundColor': self.y[dimension].get('point_highlight_stroke_color'),
                'data': self.y[dimension].get('values', []),
                'stacked': self.y[dimension].get('stacked', 'false'),
                'yAxisID': self.y[dimension].get('yAxisID', 'y'),
                'showLine': 'true',
            }
            data['datasets'].append(line)
        js_data = json.dumps(data)
        var = 'var chartdata = %s' % js_data
        chart = self.embed + '\n' + var
        # optional second axis
        secondaxisconfig = ''
        if self.secondaxis:
            secondaxisconfig = """
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        grid: {
                            drawOnChartArea: false, // only want the grid lines for one axis to show up
                        },
                    },"""
        chart += '\n' + f"""
        const config = {{
            type: 'scatter',
            data: chartdata,
            options: {{
                maintainAspectRatio: false,
                parsing: false,
                layout: {{
                    padding: {{
                        left: 10,
                        right: 25,
                        top: 25,
                        bottom: 0
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'time',
                    }},{secondaxisconfig}
                }},
            }}
        }};
        const myScatterChart = new Chart(
            document.getElementById('myChart'),
            config
        );"""
        # chart = chart + "\n" + "var myLineChart = new Chart(ctx).%s(data, %s ); \n " % ( self.type ,str(json.dumps(self.params)))
        token = random.randint(1, 10000)
        chart = chart + '</script>'
        return chart.replace('myScatterChart', 'myScatterChart%d' % token).replace('config', 'config%d' % token).replace('myChart', 'myChart%d' % token).replace('chartdata', 'chartdata%d' % token)

    def build_html(self):
        html = '<html>\n<head>\n<title>Chart</title>\n<script src= "http://www.chartjs.org/assets/Chart.js"></script> \n</head>\n<body>\n %s' % self.build_chart()
        html = html + '\n</body></html>'
        return html
