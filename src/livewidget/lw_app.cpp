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
#include <QLayout>
#include <QLocale>
#include <QMainWindow>

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
    LWData *ret = new LWData(naxes[0], naxes[1], 1, data);
    delete tmpar;
    return ret;
}
    
    
int main(int argc, char **argv)
{
    setlocale(LC_ALL, "C");
    QLocale::setDefault(QLocale::English);
    QApplication app(argc, argv);

    QMainWindow mainWindow;
    LWWidget widget(&mainWindow);

    widget.setData(data_from_fits("test1.fits"));

    mainWindow.setCentralWidget(&widget);   
    mainWindow.resize(900, 750);
    mainWindow.show();
    int ret = app.exec();

    return ret;
}
