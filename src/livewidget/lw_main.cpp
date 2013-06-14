// *****************************************************************************
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
// Module authors:
//   Georg Brandl <georg.brandl@frm2.tum.de>
//   Philipp Schmakat <philipp.schmakat@frm2.tum.de>
//
// *****************************************************************************

// Demo application, currently for testing purposes only.

#include <QApplication>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "lw_widget.h"

int main(int argc, char *argv[])
{
     QApplication app(argc, argv);
     QMainWindow mainWin;

     LWWidget widget(&mainWin);
     LWData *raw_data;

     if (argc == 1)
         raw_data = new LWData("data/raw/hd_000.000.fits", TYPE_FITS);
     else
         raw_data = new LWData(argv[1], TYPE_FITS);

     widget.setData(raw_data);
     widget.setControls((LWCtrl)(ShowGrid | Logscale | Grayscale | Filelist |
                                 Normalize | Darkfield | Despeckle | //ImageOperations |
                                 CreateProfile | Histogram | MinimumMaximum));
     widget.setKeepAspect(true);
     widget.setStandardColorMap(true,false);

     mainWin.setCentralWidget(&widget);
     mainWin.setMinimumHeight(800);
     mainWin.setMinimumWidth(1400);
     mainWin.show();

     return app.exec();
}
