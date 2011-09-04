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

#include <locale.h>

#include <QApplication>
#include <QLayout>
#include <QLocale>
#include <QMainWindow>

#include "lw_app.h"
#include "lw_data.h"
#include "lw_widget.h"


int main(int argc, char **argv)
{
    setlocale(LC_ALL, "C");
    QLocale::setDefault(QLocale::English);
    QApplication app(argc, argv);

    QMainWindow mainWindow;
    LWWidget widget(&mainWindow);

    data_t *tmp = new data_t[256];
    for (int y = 0; y < 16; y++) {
      for (int x = 0; x < 16; x++) {
        tmp[y*16 + x] = y*(16 - x);
      }
    }
    
    widget.setData(new LWData(16, 16, 1, tmp));
    widget.setLog10(0);

    mainWindow.setCentralWidget(&widget);   
    mainWindow.resize(900, 750);
    mainWindow.show();
    int ret = app.exec();

    return ret;
}
