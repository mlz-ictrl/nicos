// *****************************************************************************
// Module:
//   $Id$
//
// Author:
//   Tobias Weber <tobias.weber@frm2.tum.de>
//   Georg Brandl <georg.brandl@frm2.tum.de>
//
// NICOS-NG, the Networked Instrument Control System of the FRM-II
// Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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
// *****************************************************************************

#include <assert.h>
#include <locale.h>

#include <QApplication>
#include <QCheckBox>
#include <QLabel>
#include <QLayout>
#include <QLocale>
#include <QMainWindow>
#include <QPushButton>
#include <QSlider>

#include <fitsio.h>

#include "lw_app.h"
#include "lw_data.h"
#include "lw_widget.h"


LWData *data_from_fits(const char *filename)
{
    fitsfile *fptr;
    int status = 0;
    int bitpix, naxis, anynul, hdutype;
    long naxes[3], total_pixel, x, y;
    float nullval = 0.;
    float *tmpar;
    data_t *data;

    fits_open_file(&fptr, filename, READONLY, &status);
    fits_get_img_param(fptr, 3, &bitpix, &naxis, naxes, &status);
    fits_get_hdu_type(fptr, &hdutype, &status);
    assert(hdutype == IMAGE_HDU);
    assert(naxis == 3);

    total_pixel = naxes[0] * naxes[1];
    tmpar = new float[total_pixel];
    data = new data_t[total_pixel];

    fits_read_img(fptr, TFLOAT, 1, total_pixel, &nullval,
                  tmpar, &anynul, &status);
    fits_close_file(fptr, &status);

    for (y = 0; y < naxes[1]; y++)
        for (x = 0; x < naxes[0]; x++)
            data[x + y*naxes[0]] = (data_t)tmpar[x + y*naxes[0]];
    LWData *ret = new LWData(naxes[0], naxes[1], 1, (const char *)data);
    delete tmpar;
    return ret;
}


int main(int argc, char **argv)
{
    setlocale(LC_ALL, "C");
    QLocale::setDefault(QLocale::English);
    QApplication app(argc, argv);

    QMainWindow mainWindow;
    QFrame frame;
    QHBoxLayout layout1;
    frame.setLayout(&layout1);

    LWWidget widget(&frame);
    widget.setData(data_from_fits("test1.fits"));
    layout1.addWidget(&widget);

    QVBoxLayout layout2;
    QLabel lbl1("min", &frame);
    layout2.addWidget(&lbl1);
    QSlider sl1(&frame);
    sl1.setRange(widget.data()->min(), widget.data()->max());
    QObject::connect(&sl1, SIGNAL(valueChanged(int)),
                     &widget, SLOT(setCustomRangeMin(int)));
    layout2.addWidget(&sl1);
    layout1.addLayout(&layout2);

    QVBoxLayout layout3;
    QLabel lbl2("max", &frame);
    layout3.addWidget(&lbl2);
    QSlider sl2(&frame);
    sl2.setRange(widget.data()->min(), widget.data()->max());
    sl2.setValue(sl2.maximum());
    QObject::connect(&sl2, SIGNAL(valueChanged(int)),
                     &widget, SLOT(setCustomRangeMax(int)));
    layout3.addWidget(&sl2);
    layout1.addLayout(&layout3);

    QVBoxLayout layout4;
    QCheckBox chk1("logscale", &frame);
    layout4.addWidget(&chk1);
    QObject::connect(&chk1, SIGNAL(toggled(bool)),
                     &widget, SLOT(setLog10(bool)));
    QCheckBox chk2("gray", &frame);
    layout4.addWidget(&chk2);
    QObject::connect(&chk2, SIGNAL(toggled(bool)),
                     &widget, SLOT(setColormapGray(bool)));
    QCheckBox chk3("cyclic", &frame);
    layout4.addWidget(&chk3);
    QObject::connect(&chk3, SIGNAL(toggled(bool)),
                     &widget, SLOT(setColormapCyclic(bool)));
    QPushButton btn("reload", &frame);
    layout4.addWidget(&btn);
    QObject::connect(&btn, SIGNAL(released()),
                     &widget, SLOT(reload()));

    layout1.addLayout(&layout4);

    mainWindow.setCentralWidget(&frame);
    mainWindow.resize(900, 750);
    mainWindow.show();
    int ret = app.exec();

    return ret;
}
