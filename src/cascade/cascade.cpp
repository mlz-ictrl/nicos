// *****************************************************************************
// Module:
//   $Id$
//
// Author:
//   Tobias Weber <tweber@frm2.tum.de>
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
// Cascade-Hauptfenster

// Werden Daten vom Server komprimiert gesendet?
//#define DATA_COMPRESSED

#define WIN_W 900
#define WIN_H 675


#include <iostream>
#include <stdlib.h>
#include <limits>
#include <string.h>

#include <qapplication.h>
#include <qmainwindow.h>
#include <qtoolbar.h>
#include <qtoolbutton.h>
#include <qprinter.h>
#include <qprintdialog.h>
#include <qpen.h>
#include <QtCore/QVariant>
#include <QtCore/QTimer>
#include <QtGui/QGridLayout>
#include <QtGui/QMenu>
#include <QtGui/QMenuBar>
#include <QtGui/QStatusBar>
#include <QtGui/QGroupBox>
#include <QtGui/QFileDialog>
#include <QtGui/QSlider>
#include <QtGui/QLabel>
#include <QtGui/QPainter>
#include <QDialog>
#include <QLine>
#include <QMessageBox>

#include "tofloader.h"
#include "tofdata.h"
#include "bins.h"
#include "config.h"
#include "client.h"
#include "parse.h"
#include "cascadewidget.h"
#include "logger.h"

#include "ErrorBarPlotCurve.h"
#include "histogram_item.h"
#include "cascadedialogs.h"

#ifdef DATA_COMPRESSED
	#include "decompress.h"
#endif


int main(int, char **);

////////////////////////////// Haupt-Fenster ///////////////////////////////////////
class MainWindow : public QMainWindow
{
  Q_OBJECT
	private:
		friend int main(int, char **);
		static int NUM_BINS;			// Anzahl der Bins für Kalibrationsdialog
		static int SERVER_STATUS_POLL_TIME;
		
	protected:
		CascadeWidget m_cascadewidget;
		
		QLabel *labelZeitkanal, *labelFolie;
		QToolButton *btnLog;
		QSlider *sliderFolien, *sliderZeitkanaele;
		QStatusBar *statusbar;
		QLabel *pStatusMsg;
		QAction *actionViewsOverview, *actionViewsSlides, *actionViewsPhases, *actionViewsContrasts;
		
		TcpClient m_client;
		QTimer m_statustimer;	
		
		void Unload()
		{
			m_cascadewidget.SetMode(MODE_SLIDES);
			m_cascadewidget.Unload();
		}
			
		bool CheckConnected()
		{
			if(!m_client.isconnected())
			{
				QMessageBox::critical(0, "Error", "Not connected to server.", QMessageBox::Ok);
				return false;
			}
			return true;
		}

		void ShowMessage(const char* pcMsg, bool bTemp=false)
		{
			if(!statusbar) return;
		
			if(bTemp)
				statusbar->showMessage(pcMsg);
			else
				pStatusMsg->setText(pcMsg);
		}
		
		void UpdateLabels(bool bUpdateWidgetLabels=true)
		{
			if(bUpdateWidgetLabels)
				m_cascadewidget.UpdateLabels();
			
			if(m_cascadewidget.IsTofLoaded())
			{
				sliderFolien->setEnabled(true);
				labelFolie->setEnabled(true);
				
				switch(m_cascadewidget.GetMode())
				{
					case MODE_SLIDES:
					case MODE_SUMS:
						sliderZeitkanaele->setEnabled(true);
						labelZeitkanal->setEnabled(true);
						break;

					case MODE_PHASES:
					case MODE_PHASESUMS:
						sliderZeitkanaele->setEnabled(false);
						labelZeitkanal->setEnabled(false);
						break;

					case MODE_CONTRASTS:
					case MODE_CONTRASTSUMS:
						sliderZeitkanaele->setEnabled(false);
						labelZeitkanal->setEnabled(false);
						break;
				}

				// Statuszeile aktualisieren
				switch(m_cascadewidget.GetMode())
				{
					case MODE_SLIDES:
						ShowMessage("Showing Foils.");
						break;
					case MODE_SUMS:
						ShowMessage("Showing Sums.");
						break;

					case MODE_PHASES:
						ShowMessage("Showing Phases.");
						break;
					case MODE_PHASESUMS:
						ShowMessage("Showing Phase Sums.");
						break;

					case MODE_CONTRASTS:
						ShowMessage("Showing Contrasts.");
						break;
					case MODE_CONTRASTSUMS:
						ShowMessage("Showing Contrast Sums.");
						break;
				}
			}
			else if(m_cascadewidget.IsPadLoaded())
			{
				sliderFolien->setEnabled(false);
				labelFolie->setEnabled(false);
				sliderZeitkanaele->setEnabled(false);
				labelZeitkanal->setEnabled(false);
				ShowMessage("Showing PAD.");
			}
		}
		
		void UpdateSliders()
		{
			sliderFolien->setMaximum(Config_TofLoader::GetFoilCount()-1);
			sliderZeitkanaele->setMaximum(Config_TofLoader::GetImagesPerFoil()-1);
		}

	// Slots
	protected slots:
		/////////// Slot für Tcp-Client /////////////////////////////
		void ServerMessageSlot(const char* pcBuf, int iLen)
		{
			// Antworten müssen mindestens 4 Zeichen lang sein (Kommandostring)
			if(iLen<4) return;
			
			//////////////////////////////////////////////////////////////////////////////////////////
			// PAD-Daten vorhanden
			if(!strncmp(pcBuf,"IMAG",4))
			{
	#ifndef DATA_COMPRESSED
				// Abfrage nur für unkomprimierte Daten möglich
				if(iLen-4 != sizeof(int)*Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth())
				{
					// Dimensionen stimmen nicht, neue raten
					if(!Config_TofLoader::GuessConfigFromSize(0,(iLen-4)/4, false))
					{
						char pcMsg[256];
						sprintf(pcMsg, "Dimension mismatch in PAD data!\nClient expected: %d bytes\nServer sent: %d bytes", sizeof(int)*Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth(), iLen-4);
						QMessageBox::critical(0, "Cascade - Server", pcMsg, QMessageBox::Ok);
						return;
					}
				}
	#endif			

				void* pvData = m_cascadewidget.NewPad(/*btnLog->isChecked()*/);
	#ifdef DATA_COMPRESSED
				// Komprimierte Daten umkopieren
				int iLenOut = sizeof(int)*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH;
				if(!zlib_decompress(pcBuf+4, iLen-4, pvData, iLenOut))
				{
					QMessageBox::critical(0, "Cascade - Server", "Error in PAD decompression.", QMessageBox::Ok);
					return;
				}
	#else
				// Unkomprimierte Daten umkopieren
				memcpy(pvData, pcBuf+4, sizeof(int)*Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth());
	#endif			

				m_cascadewidget.UpdateRange();
				m_cascadewidget.UpdateGraph();

				UpdateLabels(false);
				ShowMessage("PAD loaded from Server.");
			}
			//////////////////////////////////////////////////////////////////////////////////////////
			// TOF-Daten vorhanden
			else if(!strncmp(pcBuf,"DATA",4))
			{
	#ifndef DATA_COMPRESSED
				int iExpectedSize = Config_TofLoader::GetPseudoCompression() 
								? sizeof(int)*Config_TofLoader::GetFoilCount()*Config_TofLoader::GetImagesPerFoil()*Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth()
								: sizeof(int)*Config_TofLoader::GetImageCount()*Config_TofLoader::GetImageHeight()*Config_TofLoader::GetImageWidth();	
	
				if(iLen-4 != iExpectedSize)
				{
					// Dimensionen stimmen nicht, neue raten
					if(!Config_TofLoader::GuessConfigFromSize(m_cascadewidget.GetTof()->GetCompressionMethod()==TOF_COMPRESSION_PSEUDO, (iLen-4)/4, true))
					{
						char pcMsg[256];
						sprintf(pcMsg, "Dimension mismatch in TOF data!\nClient expected: %d bytes\nServer sent: %d bytes", iExpectedSize, iLen-4);
						QMessageBox::critical(0, "Cascade - Server", pcMsg, QMessageBox::Ok);
						return;
					}
				}
	#endif
				void* pvData = m_cascadewidget.NewTof(/*btnLog->isChecked()*/);
				
	#ifdef DATA_COMPRESSED
				// Komprimierte Daten umkopieren
				int iLenOut = sizeof(int)*Config_TofLoader::IMAGE_COUNT*Config_TofLoader::IMAGE_HEIGHT*Config_TofLoader::IMAGE_WIDTH;
				if(!zlib_decompress(pcBuf+4, iLen-4, pvData, iLenOut))
				{
					QMessageBox::critical(0, "Cascade - Server", "Error in TOF decompression.", QMessageBox::Ok);
					return;
				}
	#else
				// Unkomprimierte Daten umkopieren
				memcpy(pvData, pcBuf+4, iExpectedSize);
	#endif

				//m_cascadewidget.ShowGraph();	// macht viewOverview schon
				//UpdateLabels(false);

				UpdateSliders();
				ShowMessage("TOF loaded from Server.");
				viewOverview();
				actionViewsOverview->setChecked(true);
			}
			//////////////////////////////////////////////////////////////////////////////////////////
			// Fehler
			else if(!strncmp(pcBuf,"ERR_",4))
			{
				QMessageBox::critical(0, "Cascade - Server", pcBuf+4, QMessageBox::Ok);
			}
			// Status-Update erhalten
			else if(!strncmp(pcBuf,"MSG_",4))
			{
				ArgumentMap args(pcBuf+4);
				
				// stop?
				bool bHasStop;
				bool bMessungFertig = (bool)args.QueryInt("stop",1,&bHasStop);
				if(bHasStop) 
					ShowMessage(bMessungFertig?"Server: Measurement stopped.":"Server: Measurement running.");
				
				// xres?
				bool bHasX;
				int iXRes = args.QueryInt("xres", ServerCfgDlg::GetStatXRes(), &bHasX);
				if(bHasX)
				{
					ServerCfgDlg::SetStatXRes(iXRes);
					Config_TofLoader::SetImageWidth(iXRes);
				}
				
				// yres?
				bool bHasY;
				int iYRes = args.QueryInt("yres", ServerCfgDlg::GetStatYRes(), &bHasY);
				if(bHasY)
				{
					ServerCfgDlg::SetStatYRes(iYRes);
					Config_TofLoader::SetImageWidth(iYRes);
				}
				
				// tres?
				bool bHasT;
				int iTRes = args.QueryInt("tres", ServerCfgDlg::GetStatTRes(), &bHasT);
				if(bHasT)
				{
					ServerCfgDlg::SetStatTRes(iTRes);
					Config_TofLoader::SetImageCount(iTRes);
				}
				
				// measurement time?
				bool bHasTime;
				double dTime = args.QueryDouble("time", ServerCfgDlg::GetStatTime(), &bHasTime);
				if(bHasTime)
					ServerCfgDlg::SetStatTime(dTime);
				
				// mode?
				const char* pcMode = args.QueryString("mode");
				if(pcMode)
				{
					if(strcasecmp(pcMode, "tof")==0)
						ServerCfgDlg::SetStatMode(MODE_TOF);
					else if(strcasecmp(pcMode, "image")==0)
						ServerCfgDlg::SetStatMode(MODE_PAD);
				}
				
				// pseudo-compression?
				bool bHasComp=0;
				bool bComp = (bool)args.QueryInt("comp",1,&bHasComp);
				if(bHasComp)
				{
					Config_TofLoader::SetPseudoCompression(bComp);
					ServerCfgDlg::SetStatComp(bComp);
				}
			}
			else if(!strncmp(pcBuf,"OKAY",4))
			{}
			else
			{
				logger.SetCurLogLevel(LOGLEVEL_ERR);
				logger << "Cascade: Unknown prefix in server response: \"" <<pcBuf[0]<<pcBuf[1]<<pcBuf[2]<<pcBuf[3] << "\".\n";
			}
		}

		// Slot vom Summen-Dialog
		void FolienSummeSlot(const bool *pbKanaele, int iMode)
		{
			switch(iMode)
			{
				case MODE_SLIDES:
				case MODE_SUMS:
					actionViewsSlides->setChecked(true);
					break;

				case MODE_PHASES:
				case MODE_PHASESUMS:
					actionViewsPhases->setChecked(true);
					break;

				case MODE_CONTRASTS:
				case MODE_CONTRASTSUMS:
					actionViewsContrasts->setChecked(true);
					break;
			}
			UpdateLabels(false);
		}

		// Callback vom Folien-Slider
		void ChangeFolie(int iVal)
		{
			if(!m_cascadewidget.IsTofLoaded()) return;
			
			switch(m_cascadewidget.GetMode()) 
			{
				case MODE_SUMS:
					actionViewsSlides->setChecked(true);
					m_cascadewidget.SetMode(MODE_SLIDES);
					break;
				case MODE_PHASESUMS:
					actionViewsPhases->setChecked(true);
					m_cascadewidget.SetMode(MODE_PHASES);
					break;
				case MODE_CONTRASTSUMS:
					actionViewsContrasts->setChecked(true);
					m_cascadewidget.SetMode(MODE_CONTRASTS);
					break;
			}
			
			m_cascadewidget.SetFoil(iVal);
			m_cascadewidget.UpdateGraph();
			UpdateLabels(false);

			char pcFolie[128];
			sprintf(pcFolie,"Foil (%0.2d):",m_cascadewidget.GetFoil()+1);
			labelFolie->setText(pcFolie);
		}
		
		// Callback vom Kanal-Slider
		void ChangeZeitkanal(int iVal)
		{
			if(!m_cascadewidget.IsTofLoaded()) return;
			
			switch(m_cascadewidget.GetMode())
			{
				case MODE_SUMS:
					actionViewsSlides->setChecked(true);
					m_cascadewidget.SetMode(MODE_SLIDES);
					break;
				case MODE_PHASESUMS:
					actionViewsPhases->setChecked(true);
					m_cascadewidget.SetMode(MODE_PHASES);
					break;
				case MODE_CONTRASTSUMS:
					actionViewsContrasts->setChecked(true);
					m_cascadewidget.SetMode(MODE_CONTRASTS);
					break;
			}
			
			m_cascadewidget.SetTimechannel(iVal);
			m_cascadewidget.UpdateGraph();
			UpdateLabels(false);

			char pcKanal[128];
			sprintf(pcKanal,"Time Channel (%0.2d):",m_cascadewidget.GetTimechannel()+1);
			labelZeitkanal->setText(pcKanal);
		}
		
		void SetLog10(bool bLog)
		{	
			m_cascadewidget.SetLog10(bLog);
			UpdateLabels(false);
		}
		
		void showCalibration(void)
		{
			m_cascadewidget.showCalibrationDlg(NUM_BINS);
		}
		
		void showGraph(void)
		{
			m_cascadewidget.showGraphDlg();
		}
			
		void showSummenDialog(void)
		{
			m_cascadewidget.showSumDlg();
		}
		
		void viewOverview()
		{
			m_cascadewidget.viewOverview();
			UpdateLabels(false);
		}
		
		void viewSlides()
		{
			m_cascadewidget.viewSlides();
			UpdateLabels(false);
		}
		
		void viewPhases()
		{
			m_cascadewidget.viewPhases();
			UpdateLabels(false);
		}

		void viewContrasts()
		{
			m_cascadewidget.viewContrasts();
			UpdateLabels(false);
		}
		
		////////////////////////// Server-Menüpunkte /////////////////////////////////////
		void ConnectToServer()
		{
			m_statustimer.stop();
			ServerDlg SrvDlg(this);
			
			char pcBuf[512];
			Config::GetSingleton()->QueryString("/cascade_config/server/address", pcBuf, "127.0.0.1");
			SrvDlg.editAddress->setText(QString(pcBuf).simplified());
			
			int iPort = Config::GetSingleton()->QueryInt("/cascade_config/server/port", 1234);
			QString strPort; strPort.setNum(iPort);
			SrvDlg.editPort->setText(strPort);
			
			if(SrvDlg.exec()==QDialog::Accepted)
			{
				if(!m_client.connecttohost(SrvDlg.editAddress->text().toAscii().data(), SrvDlg.editPort->text().toInt()))
				{
					sprintf(pcBuf, "Could not connect to server\n\"%s\"\nat port %d.", SrvDlg.editAddress->text().toAscii().data(), SrvDlg.editPort->text().toInt());
					QMessageBox::critical(0, "Error", pcBuf, QMessageBox::Ok);
					return;
				}
				ShowMessage("Connected to server.");
				m_statustimer.start(SERVER_STATUS_POLL_TIME);
				
				// get current config of hardware
				GetServerConfig();
			}
		}
		
		void ServerDisconnect()
		{
			m_statustimer.stop();
			m_client.disconnect();
			ShowMessage("Disconnected from server.");
		}
		
		void ServerStatus()
		{
			if(!CheckConnected()) return;
			m_client.sendmsg("CMD_status_cdr");
		}
		
		void ServerMeasurementStart()
		{
			if(!CheckConnected()) return;
			m_client.sendmsg("CMD_start");
		}
		
		void ServerMeasurementStop()
		{
			if(!CheckConnected()) return;
			m_client.sendmsg("CMD_stop");
		}	

		void LoadTofServer()
		{
			if(!CheckConnected()) return;
			m_client.sendmsg("CMD_readsram");
		}
		
		void GetServerConfig()
		{
			if(!CheckConnected()) return;
			m_client.sendmsg("CMD_getconfig_cdr");
		}
		
		void ServerConfig()
		{
			if(!CheckConnected()) return;
			ServerCfgDlg srvcfgdlg(this);
			
			if(srvcfgdlg.exec()==QDialog::Accepted)
			{
				double dTime = srvcfgdlg.GetMeasTime();
				unsigned int iXRes = srvcfgdlg.GetXRes(); 
				unsigned int iYRes = srvcfgdlg.GetYRes();
				unsigned int iTRes = srvcfgdlg.GetTRes();
				bool bComp = srvcfgdlg.GetPseudoComp();
				
				Config_TofLoader::SetImageWidth(iXRes);
				Config_TofLoader::SetImageHeight(iYRes);
				Config_TofLoader::SetImageCount(iTRes);
				Config_TofLoader::SetPseudoCompression(bComp);
				
				const char* pcMode = "";
				switch(srvcfgdlg.GetMode())
				{
					case MODE_PAD:
						pcMode = "image";
						break;
					case MODE_TOF:
						pcMode = "tof";
						break;
				}
				char pcMsg[256];
				sprintf(pcMsg, "CMD_config_cdr time=%f xres=%d yres=%d tres=%d mode=%s comp=%d", dTime, iXRes, iYRes, iTRes, pcMode, bComp);
				m_client.sendmsg(pcMsg);
			}
		}
		//////////////////////////////////////////////////////////////////////////////


		///////////////////////////// Datei-Menüpunkte ///////////////////////////////
		void LoadPad()
		{
			m_cascadewidget.NewPad(/*btnLog->isChecked()*/);
			QString strFile = QFileDialog::getOpenFileName(this, "Open PAD File","","PAD File (*.pad *.PAD);;All files (*)");
			if(strFile!="" && m_cascadewidget.LoadPadFile(strFile.toAscii().data()))
			{
				//m_cascadewidget.UpdateGraph();
				UpdateLabels(false);
				ShowMessage("PAD loaded.");
			}
		}

		void LoadTof()
		{
			m_cascadewidget.NewTof(/*btnLog->isChecked()*/);
			QString strFile = QFileDialog::getOpenFileName(this, "Open TOF File","","TOF File (*.tof *.TOF);;All files (*)");
			if(strFile!="" && m_cascadewidget.LoadTofFile(strFile.toAscii().data()))
			{
				//m_cascadewidget.UpdateGraph();	// macht viewOverview schon
				UpdateLabels(false);
				UpdateSliders();
				ShowMessage("TOF loaded.");

				//viewOverview();
				actionViewsOverview->setChecked(true);
			}
		}
		
		void WriteXML(void)
		{
			if(m_cascadewidget.IsTofLoaded() || m_cascadewidget.IsPadLoaded())
			{
				QString strFile = QFileDialog::getSaveFileName(this, "Save XML File","","XML Files (*.xml)");
				TmpImage tmpimg;
				if(m_cascadewidget.IsTofLoaded())	// TOF-Datei offen
					m_cascadewidget.GetTof()->GetOverview(&tmpimg);
				else					// PAD-Datei offen
					tmpimg.ConvertPAD(m_cascadewidget.GetPad());
				tmpimg.WriteXML(strFile.toAscii().data());
			}
		}
		///////////////////////////////////////////////////////////////////
		
		
		///////////////////////// Hilfe ///////////////////////////////////
		void About() 
		{ 
			QString strAbout = "Cascade Qt Client written by Tobias Weber.";
			strAbout += "\n";
			
			#ifdef __TIMESTAMP__
			strAbout += QString("\n") + QString("Build time: ") + QString(__TIMESTAMP__);
			#endif
			
			#ifdef __VERSION__
			strAbout += QString("\n") + QString("Built with CC version ") + QString(__VERSION__);
			#endif
			strAbout += "\n";

			#ifdef QT_VERSION_STR
			strAbout += QString("\n") + QString("Linked to Qt version ") + QString(QT_VERSION_STR);
			#endif
			
			#ifdef QWT_VERSION_STR
			strAbout += QString("\n") + QString("Linked to Qwt version ") + QString(QWT_VERSION_STR);
			#endif
			
			QMessageBox::about(this, "About", strAbout); 
		}
		void AboutQt() { QMessageBox::aboutQt(this); }
		///////////////////////////////////////////////////////////////////

	public:
		virtual ~MainWindow()
		{
			Unload();
		}
		
		MainWindow(QWidget *parent=NULL) : QMainWindow(parent), m_cascadewidget(this), m_client(this, false), statusbar(NULL), m_statustimer(this)
		{
			m_cascadewidget.SetLog10(true);
			
			char pcBuf[256];
			Config::GetSingleton()->QueryString("/cascade_config/main_window/title", pcBuf, "Cascade");
			setWindowTitle(QString(pcBuf).simplified());

			QWidget *pCentralWidget = new QWidget(this);
			setCentralWidget(pCentralWidget);
			
			// Gruppen
			//QGroupBox *grouptopright = new QGroupBox(&m_cascadewidget);
			//QGroupBox *groupbottomright = new QGroupBox(&m_cascadewidget);
			QGroupBox *groupbottomleft = new QGroupBox(pCentralWidget);
			
			QGridLayout *centralgridlayout = new QGridLayout(pCentralWidget);
			centralgridlayout->addWidget(&m_cascadewidget, 0, 0, 1, 1);
			//centralgridlayout->addWidget(grouptopright, 0, 1, 1, 1);
			//centralgridlayout->addWidget(groupbottomright, 1, 1, 1, 1);
			centralgridlayout->addWidget(groupbottomleft, 1, 0, 1, 1);
			
			
			// Gruppe links unten
			QGridLayout *pLayoutBL = new QGridLayout(groupbottomleft);
					
			labelFolie = new QLabel(groupbottomleft);
			pLayoutBL->addWidget(labelFolie, 0, 0, 1, 1);
			
			sliderFolien = new QSlider(groupbottomleft);
			sliderFolien->setOrientation(Qt::Horizontal);
			sliderFolien->setMinimum(0);
			sliderFolien->setValue(0);
			labelFolie->setText("Foil:");
			//ChangeFolie(0);
			pLayoutBL->addWidget(sliderFolien, 0, 1, 1, 1);
			
			labelZeitkanal = new QLabel(groupbottomleft);
			pLayoutBL->addWidget(labelZeitkanal, 1, 0, 1, 1);
			
			sliderZeitkanaele = new QSlider(groupbottomleft);
			sliderZeitkanaele->setOrientation(Qt::Horizontal);
			sliderZeitkanaele->setMinimum(0);
			
			sliderZeitkanaele->setValue(0);
			labelZeitkanal->setText("Time Channel:");
			//ChangeZeitkanal(0);
			UpdateSliders();
			
			pLayoutBL->addWidget(sliderZeitkanaele, 1, 1, 1, 1);
			
			
			// Datei-Menüpunkte
			QAction *actionLoadPad = new QAction(this);
			actionLoadPad->setText("Load PAD File...");
			QAction *actionLoadTof = new QAction(this);
			actionLoadTof->setText("Load TOF File...");
			QAction *actionWriteXML = new QAction(this);
			actionWriteXML->setText("Write XML...");
			QAction *actionPrint = new QAction(this);
			actionPrint->setText("Print Plot...");
			QAction *actionExit = new QAction(this);
			actionExit->setText("Exit");		
			
			// Server-Menüpunkte
			QAction *actionConnectServer = new QAction(this);
			actionConnectServer->setText("Connect to Server...");
			QAction *actionServerDisconnect = new QAction(this);
			actionServerDisconnect->setText("Disconnect from Server");
			QAction *actionServerMeasurementStart = new QAction(this);
			actionServerMeasurementStart->setText("Start Measurement");
			QAction *actionServerMeasurementStop = new QAction(this);
			actionServerMeasurementStop->setText("Stop Measurement");
			QAction *actionLoadTofServer = new QAction(this);
			actionLoadTofServer->setText("Get Data");
			QAction *actionConfigServer = new QAction(this);
			actionConfigServer->setText("Configure...");
			QAction *actionConfigFromServer = new QAction(this);
			actionConfigFromServer->setText("Retrieve Configuration");
					
			// Graph-Menüpunkte
			QAction *actionGraph = new QAction(this);
			actionGraph->setText("Time Channels...");
			QAction *actionSummen = new QAction(this);
			actionSummen->setText("Sum Images...");
			QAction *actionCalibration = new QAction(this);
			actionCalibration->setText("Calibration...");
			
			
			// Hilfe-Menüpunkte
			QAction *actionAbout = new QAction(this);
			actionAbout->setText("About...");
			QAction *actionAboutQt = new QAction(this);
			actionAboutQt->setText("About Qt...");			
			
			
			// Menüleiste
			QMenuBar *menubar = new QMenuBar(this);;

			menubar->setGeometry(QRect(0, 0, 800, 25));
			QMenu *menuFile = new QMenu(menubar);
			menuFile->setTitle("File");
			menubar->addAction(menuFile->menuAction());
			menuFile->addAction(actionLoadPad);
			menuFile->addAction(actionLoadTof);
			menuFile->addSeparator();
			menuFile->addAction(actionWriteXML);
			menuFile->addAction(actionPrint);
			menuFile->addSeparator();
			menuFile->addAction(actionExit);

			QMenu *menuServer = new QMenu(menubar);
			menuServer->setTitle("Server");
			menubar->addAction(menuServer->menuAction());
			menuServer->addAction(actionConnectServer);
			menuServer->addAction(actionServerDisconnect);
			menuServer->addSeparator();
			menuServer->addAction(actionConfigFromServer);
			menuServer->addAction(actionConfigServer);
			menuServer->addSeparator();
			menuServer->addAction(actionServerMeasurementStart);
			menuServer->addAction(actionServerMeasurementStop);
			menuServer->addSeparator();
			menuServer->addAction(actionLoadTofServer);

			QMenu *menuGraph = new QMenu(menubar);
			menuGraph->setTitle("Graph");
			menubar->addAction(menuGraph->menuAction());
			menuGraph->addAction(actionCalibration);
			menuGraph->addSeparator();
			menuGraph->addAction(actionGraph);
			menuGraph->addAction(actionSummen);
			
			QMenu *menuHelp = new QMenu(menubar);
			menuHelp->setTitle("Help");
			menubar->addAction(menuHelp->menuAction());
			menuHelp->addAction(actionAbout);
			menuHelp->addAction(actionAboutQt);

			setMenuBar(menubar);

			
			// Toolbar
			QToolBar *toolBar = new QToolBar(this);
			
			btnLog = new QToolButton(toolBar);
			btnLog->setText("Log10");
			btnLog->setCheckable(true);
			btnLog->setChecked(m_cascadewidget.GetLog10());
			toolBar->addWidget(btnLog);
			
			QMenu *pMenuViews = new QMenu;
			
			actionViewsOverview = new QAction(this);
			actionViewsOverview->setText("Overview");
			actionViewsOverview->setCheckable(true);
			pMenuViews->addAction(actionViewsOverview);
			
			actionViewsSlides = new QAction(this);;
			actionViewsSlides->setText("Slides");
			actionViewsSlides->setCheckable(true);
			pMenuViews->addAction(actionViewsSlides);
			pMenuViews->addSeparator();
			
			actionViewsPhases = new QAction(this);;
			actionViewsPhases->setText("Phases");
			actionViewsPhases->setCheckable(true);
			pMenuViews->addAction(actionViewsPhases);
			
			actionViewsContrasts = new QAction(this);;
			actionViewsContrasts->setText("Contrasts");
			actionViewsContrasts->setCheckable(true);
			pMenuViews->addAction(actionViewsContrasts);
			
			QActionGroup *pActionGroupViews = new QActionGroup(this);
			pActionGroupViews->addAction(actionViewsOverview);
			pActionGroupViews->addAction(actionViewsSlides);
			pActionGroupViews->addAction(actionViewsPhases);
			pActionGroupViews->addAction(actionViewsContrasts);
			actionViewsOverview->setChecked(true);
			
			QToolButton *btnView = new QToolButton(toolBar);
			btnView->setText("Views");
			btnView->setCheckable(false);
			btnView->setPopupMode(QToolButton::InstantPopup);
			btnView->setMenu(pMenuViews);
			toolBar->addWidget(btnView);
			
			addToolBar(toolBar);
			
			
			// Statusleiste
			statusbar = new QStatusBar(this);
			pStatusMsg = new QLabel(this);
			//pStatusMsg->setFrameStyle(QFrame::Panel|QFrame::Sunken);
			statusbar->addWidget(pStatusMsg,1);
			setStatusBar(statusbar);
			
			// Verbindungen
			// Toolbar
			connect(btnLog, SIGNAL(toggled(bool)), this, SLOT(SetLog10(bool)));
			connect(actionViewsOverview, SIGNAL(triggered()), this, SLOT(viewOverview()));
			connect(actionViewsSlides, SIGNAL(triggered()), this, SLOT(viewSlides()));
			connect(actionViewsPhases, SIGNAL(triggered()), this, SLOT(viewPhases()));
			connect(actionViewsContrasts, SIGNAL(triggered()), this, SLOT(viewContrasts()));
			
			// Slider
			connect(sliderFolien, SIGNAL(valueChanged(int)), this, SLOT(ChangeFolie(int)));
			connect(sliderZeitkanaele, SIGNAL(valueChanged(int)), this, SLOT(ChangeZeitkanal(int)));		
			
			// Datei
			connect(actionExit, SIGNAL(triggered()), this, SLOT(close()));
			connect(actionLoadPad, SIGNAL(triggered()), this, SLOT(LoadPad()));
			connect(actionLoadTof, SIGNAL(triggered()), this, SLOT(LoadTof()));
			connect(actionWriteXML, SIGNAL(triggered()), this, SLOT(WriteXML()));
			connect(actionPrint, SIGNAL(triggered()), m_cascadewidget.GetPlot(), SLOT(printPlot()));		
			
			// Server
			connect(actionConnectServer, SIGNAL(triggered()), this, SLOT(ConnectToServer()));
			connect(actionServerDisconnect, SIGNAL(triggered()), this, SLOT(ServerDisconnect()));
			
			connect(actionLoadTofServer, SIGNAL(triggered()), this, SLOT(LoadTofServer()));
			connect(actionServerMeasurementStart, SIGNAL(triggered()), this, SLOT(ServerMeasurementStart()));
			connect(actionServerMeasurementStop, SIGNAL(triggered()), this, SLOT(ServerMeasurementStop()));
			connect(actionConfigServer, SIGNAL(triggered()), this, SLOT(ServerConfig()));
			connect(actionConfigFromServer, SIGNAL(triggered()), this, SLOT(GetServerConfig()));
			
			// Hilfe
			connect(actionAbout, SIGNAL(triggered()), this, SLOT(About()));
			connect(actionAboutQt, SIGNAL(triggered()), this, SLOT(AboutQt()));
			
			// Graph
			connect(actionCalibration, SIGNAL(triggered()), this, SLOT(showCalibration()));
			connect(actionGraph, SIGNAL(triggered()), this, SLOT(showGraph()));
			connect(actionSummen, SIGNAL(triggered()), this, SLOT(showSummenDialog()));
			
			connect(&m_statustimer, SIGNAL(timeout()), this, SLOT(ServerStatus()));
			
			connect(&m_client, SIGNAL(MessageSignal(const char*, int)), this, SLOT(ServerMessageSlot(const char*, int)));

			// Widget
			connect(&m_cascadewidget, SIGNAL(SumDlgSignal(const bool *, int)), this, SLOT(FolienSummeSlot(const bool *, int)));
		}
};

// Default-Werte
int MainWindow::NUM_BINS = 100;
int MainWindow::SERVER_STATUS_POLL_TIME = 1000;

int main(int argc, char **argv)
{
	QApplication a(argc, argv);
	setlocale(LC_ALL, "C");
	QLocale::setDefault(QLocale::English);
	
	// Konfigurationssingleton erzeugen
	const char pcConfigFile[] = "./cascade.xml";
	if(!Config::GetSingleton()->Load(pcConfigFile))
	{
		char pcMsg[512];
		sprintf(pcMsg, "Configuration file \"%s\" could not be found.\nUsing default configuration.",pcConfigFile);
		QMessageBox::warning(0, "Warning", pcMsg, QMessageBox::Ok);
	}
	
	// Konfigurationseinstellungen laden
	Config_TofLoader::Init();
	
	int iLogToFile = Config::GetSingleton()->QueryInt("/cascade_config/log/log_to_file", 0);
	if(iLogToFile)
	{
		char pcLogFile[256];
		Config::GetSingleton()->QueryString("/cascade_config/log/file", pcLogFile, "cascade.log");
		logger.Init(pcLogFile);
	}
	
	int iLogLevel = Config::GetSingleton()->QueryInt("/cascade_config/log/level", LOGLEVEL_INFO);
	Config_TofLoader::SetLogLevel(iLogLevel);
	
	int iWinW = Config::GetSingleton()->QueryInt("/cascade_config/main_window/width", WIN_W);
	int iWinH = Config::GetSingleton()->QueryInt("/cascade_config/main_window/height", WIN_H);
	
	MainWindow::NUM_BINS = Config::GetSingleton()->QueryInt("/cascade_config/graphs/bin_count", MainWindow::NUM_BINS);
	MainWindow::SERVER_STATUS_POLL_TIME = Config::GetSingleton()->QueryInt("/cascade_config/server/status_poll_time", MainWindow::SERVER_STATUS_POLL_TIME);
	
	
	MainWindow mainWindow;
	mainWindow.resize(iWinW, iWinH);
	mainWindow.show();
	int iRet = a.exec();
	
	
	// aufräumen
	Config_TofLoader::Deinit();
	Config::ClearSingleton();
	return iRet;
}

#ifdef __CASCADE_QT_CLIENT__
	// Qt-Metaobjekte
	#include "cascade.moc"
#endif
