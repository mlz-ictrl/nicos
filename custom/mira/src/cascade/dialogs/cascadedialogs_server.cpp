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
//   Tobias Weber <tweber@frm2.tum.de>
//
// *****************************************************************************
// Cascade sub dialogs


// ************************* Server Command Dialog ********************
CommandDlg::CommandDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
}

CommandDlg::~CommandDlg()
{}
// ********************************************************************



// ************************* Server-Dialog *************************************
ServerDlg::ServerDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
}

ServerDlg::~ServerDlg()
{}

ServerCfgDlg::ServerCfgDlg(QWidget *pParent) : QDialog(pParent)
{
	setupUi(this);
	QString str;

	str.setNum(s_dLastTime);
	editMeasTime->setText(str);

	str.setNum(s_iXRes);
	editxres->setText(str);

	str.setNum(s_iYRes);
	edityres->setText(str);

	str.setNum(s_iTRes);
	edittres->setText(str);

	checkBoxPseudoComp->setChecked(s_bUsePseudoComp);

	if(s_iMode==MODE_PAD)
	{
		radioButtonPad->setChecked(1);
		radioButtonTof->setChecked(0);
		toggledmode(0);
	}
	else if(s_iMode==MODE_TOF)
	{
		radioButtonTof->setChecked(1);
		radioButtonPad->setChecked(0);
		toggledmode(1);
	}
	connect(radioButtonTof, SIGNAL(toggled(bool)), this,
							SLOT(toggledmode(bool)));

	setFixedSize(width(),height());
}

ServerCfgDlg::~ServerCfgDlg()
{}

void ServerCfgDlg::toggledmode(bool bChecked)
{
	if(radioButtonTof->isChecked())
	{
		edittres->setEnabled(1);
	}
	else if(radioButtonPad->isChecked())
	{
		edittres->setEnabled(0);
	}
}

double ServerCfgDlg::GetMeasTime()
{
	s_dLastTime = editMeasTime->text().toDouble();
	return s_dLastTime;
}

unsigned int ServerCfgDlg::GetXRes()
{
	s_iXRes = editxres->text().toInt();
	return s_iXRes;
}

unsigned int ServerCfgDlg::GetYRes()
{
	s_iYRes = edityres->text().toInt();
	return s_iYRes;
}

unsigned int ServerCfgDlg::GetTRes()
{
	if(radioButtonPad->isChecked())
		return 1;

	s_iTRes = edittres->text().toInt();
	return s_iTRes;
}

int ServerCfgDlg::GetMode()
{
	if(radioButtonPad->isChecked())
		s_iMode = MODE_PAD;
	else if(radioButtonTof->isChecked())
		s_iMode = MODE_TOF;
	return s_iMode;
}

bool ServerCfgDlg::GetPseudoComp()
{
	s_bUsePseudoComp = checkBoxPseudoComp->isChecked();
	return s_bUsePseudoComp;
}


void ServerCfgDlg::SetStatXRes(int iXRes) { s_iXRes = iXRes; }
void ServerCfgDlg::SetStatYRes(int iYRes) { s_iYRes = iYRes; }
void ServerCfgDlg::SetStatTRes(int iTRes) { s_iTRes = iTRes; }
void ServerCfgDlg::SetStatMode(int iMode) { s_iMode = iMode; }
void ServerCfgDlg::SetStatTime(double dTime) { s_dLastTime = dTime; }
void ServerCfgDlg::SetStatComp(bool bComp) { s_bUsePseudoComp = bComp; }

int ServerCfgDlg::GetStatXRes() { return s_iXRes; }
int ServerCfgDlg::GetStatYRes() { return s_iYRes; }
int ServerCfgDlg::GetStatTRes() { return s_iTRes; }
int ServerCfgDlg::GetStatMode()  { return s_iMode; }
double ServerCfgDlg::GetStatTime() { return s_dLastTime; }
bool ServerCfgDlg::GetStatComp() { return s_bUsePseudoComp; }


double ServerCfgDlg::s_dLastTime = 10.0;
unsigned int ServerCfgDlg::s_iXRes = 128;
unsigned int ServerCfgDlg::s_iYRes = 128;
unsigned int ServerCfgDlg::s_iTRes = 128;
int ServerCfgDlg::s_iMode = 1;
bool ServerCfgDlg::s_bUsePseudoComp = 0;
// *****************************************************************************
