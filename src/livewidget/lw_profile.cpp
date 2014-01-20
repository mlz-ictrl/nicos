// *****************************************************************************
// NICOS, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
//
// This program is free software; you can redistribute it and/or modify it under
// the terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
// details.
//
// You should have received a copy of the GNU General Public License along with
// this program; if not, write to the Free Software Foundation, Inc.,
// 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
// Module authors:
//   Georg Brandl <georg.brandl@frm2.tum.de>
//
// *****************************************************************************

#include <iostream>
#include <stdio.h>

#include "lw_controls.h"


static double *integrate_x(LWData *data)
{
    int h = data->height();
    double *dest = new double[h*data->width()];
    for (int x = 0; x < data->width(); x++) {
        for (int y = 0; y < h; y++)
            dest[h*x+y] = data->value(x, y);
    }
    return dest;
}

static double *integrate_y(LWData *data)
{
    int w = data->width();
    double *dest = new double[w*data->height()];
    for (int y = 0; y < data->height(); y++) {
        for (int x = 0; x < w; x++)
            dest[w*y+x] = data->value(x, y);
    }
    return dest;
}

/* Uses the "rotation by area mapping" as implemented by leptonica.com */

static double *straightenLine(LWData *data, int x1, int y1, int x2, int y2,
                              int lw, int *npixels)
{
    if (x1 == 0 && x2 == data->width() && lw == data->height()) {
        *npixels = data->width();
        return integrate_y(data);
    }
    if (y1 == 0 && y2 == data->height() && lw == data->width()) {
        *npixels = data->height();
        return integrate_x(data);
    }

    double angle = - atan2(y2 - y1, x2 - x1);
    double len = sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2));
    int width = *npixels = (int)(len + 0.5);
    int height = lw;
    double *dest = new double[width * height];
    data_t xpm, ypm, xp, yp, xf, yf;
    data_t v00, v01, v10, v11;

    double sina = 16. * sin(angle);
    double cosa = 16. * cos(angle);

    double xstart = 16. * x1 - lw/2. * sina;
    double ystart = 16. * y1 - lw/2. * cosa;

    for (int x = 0; x < width; x++) {
        for (int y = 0; y < height; y++) {
            xpm = (data_t)(xstart + x * cosa + y * sina);
            ypm = (data_t)(ystart + y * cosa - x * sina);
            xp = xpm >> 4;
            yp = ypm >> 4;
            xf = xpm & 0xF;
            yf = ypm & 0xF;

            // area weighting
            v00 = (16 - xf) * (16 - yf) * (long)data->value(xp, yp);
            v10 = xf * (16 - yf) * (long)data->value(xp + 1, yp);
            v01 = (16 - xf) * yf * (long)data->value(xp, yp + 1);
            v11 = xf * yf * (long)data->value(xp + 1, yp + 1);
            dest[y * width + x] = (v00 + v01 + v10 + v11 + 128) / 256;
        }
    }
    return dest;
}


LWProfileWindow::LWProfileWindow(QWidget *parent, LWWidget *widget) :
    QMainWindow(parent), m_data_x(0), m_data_y(0)
{
    m_widget = widget;
    m_plot = new QwtPlot(this);
    m_curve = new QwtPlotCurve();
    m_curve->setRenderHint(QwtPlotCurve::RenderAntialiased);
    m_curve->attach(m_plot);
    m_zoomer = new QwtPlotZoomer(m_plot->canvas());
    m_zoomer->setMousePattern(QwtPlotZoomer::MouseSelect3, Qt::NoButton);
    m_picker = new QwtPlotPicker(m_plot->canvas());
    m_picker->setSelectionFlags(QwtPicker::PointSelection |
                                QwtPicker::ClickSelection);
    m_picker->setMousePattern(QwtPicker::MouseSelect1, Qt::MidButton);
    QObject::connect(m_picker, SIGNAL(selected(const QwtDoublePoint &)),
                     this, SLOT(pickerSelected(const QwtDoublePoint &)));
    setCentralWidget(m_plot);
    setContentsMargins(5, 5, 5, 5);
    QFont plotfont(font());
    plotfont.setPointSize(plotfont.pointSize() * 0.7);
    m_plot->setAxisFont(QwtPlot::xBottom, plotfont);
    m_plot->setAxisFont(QwtPlot::yLeft, plotfont);
    m_plot->setCanvasBackground(Qt::white);
    resize(800, 200);
}

LWProfileWindow::~LWProfileWindow()
{
}

void LWProfileWindow::update(LWData *data, double *px, double *py,
                             int w, int b, int type)
{
    if (m_data_x) {
        delete[] m_data_x;
        m_data_x = 0;
        delete[] m_data_y;
        m_data_y = 0;
    }
    int len;
    double *straight = straightenLine(data, px[0], py[0], px[1], py[1], w, &len);
    int nbins = len / b;
    m_data_x = new double[nbins];
    m_data_y = new double[nbins];
    for (int i = 0; i < nbins; i++) {
        m_data_x[i] = i*b;
        m_data_y[i] = 0;
        for (int j = 0; j < w; j++)
            for (int k = 0; k < b; k++)
                m_data_y[i] += straight[len*j + (i*b + k)];
    }
    delete[] straight;
    m_type = type;
    m_curve->setData(QwtCPointerData(m_data_x, m_data_y, nbins));
    m_plot->setAxisAutoScale(QwtPlot::xBottom);
    m_plot->setAxisAutoScale(QwtPlot::yLeft);
    m_zoomer->setZoomBase(true);
    emit m_widget->profileUpdate(m_type, nbins, m_data_x, m_data_y);
}

void LWProfileWindow::pickerSelected(const QwtDoublePoint &point)
{
    emit m_widget->profilePointPicked(m_type, point.x(), point.y());
}
