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
//   Tobias Weber <tweber@frm2.tum.de>
//
// *****************************************************************************
/*
 * Cascade Viewer Main Window
 * (Plotter initially based on "spectrogram" qwt sample code)
 */

// Werden Daten vom Server zlib-komprimiert gesendet?
// Dies hat nichts mit der "Pseudokompression" zu tun!
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

#include "globals.h"
#include "tofloader.h"
#include "tofdata.h"
#include "bins.h"
#include "config.h"
#include "client.h"
#include "parse.h"
#include "cascadewidget.h"
#include "logger.h"
#include "helper.h"

#include "ErrorBarPlotCurve.h"
#include "histogram_item.h"
#include "cascadedialogs.h"

#ifdef DATA_COMPRESSED
	#include "decompress.h"
#endif


int main(int, char **);

////////////////////////////// Haupt-Fenster ///////////////////////////////////
class MainWindow : public QMainWindow
{
  Q_OBJECT
	private:
		friend int main(int, char **);

		// Anzahl der Bins für Kalibrationsdialog
		static int NUM_BINS;
		static int SERVER_STATUS_POLL_TIME;
		static int AUTOFETCH_POLL_TIME;

	protected:
		CascadeWidget m_cascadewidget;

		TcpClient m_client;
		QTimer m_statustimer, m_autofetchtimer;

		std::string m_strTitle;
		QLabel *labelZeitkanal, *labelFolie;

		QToolButton *btnLog, *btnAutoFetch;

		QSlider *sliderFolien, *sliderZeitkanaele;

		QStatusBar *statusbar;
		QLabel *pStatusMsg, *pStatusExtCount;

		QAction *actionViewsOverview, *actionViewsSlides,
				*actionViewsPhases, *actionViewsContrasts;

		void Unload()
		{
			m_cascadewidget.SetMode(MODE_SLIDES);
			m_cascadewidget.Unload();
		}

		bool CheckConnected()
		{
			if(!m_client.isconnected())
			{
				QMessageBox::critical(0, "Error", "Not connected to server.",
									  QMessageBox::Ok);
				ServerDisconnect();	// stop timer
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

		void ShowTitleMessage(const char* pcMsg)
		{
			if(pcMsg==0)
				return;

			std::string strMsg = pcMsg;
			strMsg = trim(strMsg);
			if(strMsg=="")
			{
				setWindowTitle(QString(m_strTitle.c_str()).simplified());
				return;
			}

			std::string strNewTitle = m_strTitle;
			strNewTitle += std::string(" - ");
			strNewTitle += strMsg;

			setWindowTitle(QString(strNewTitle.c_str()));
		}

		// iCnts or iClients set to -1 means: do not update respective value
		void SetRightStatus(int iCnts, int iClients=-1)
		{
			static int iLastCnts=-1;
			static int iLastClients=-1;

			bool bUpdateCnts = (iCnts!=-1);
			bool bUpdateClients = (iClients!=-1);

			if((bUpdateCnts && iCnts!=iLastCnts) ||
				(bUpdateClients && iClients!=iLastClients))
			{
				if(bUpdateCnts)
					iLastCnts = iCnts;
				if(bUpdateClients)
					iLastClients = iClients;

				std::ostringstream ostr;
				ostr << "Ext Counts: " << iLastCnts
					 << ", Clients: " << iLastClients;

				pStatusExtCount->setText(ostr.str().c_str());
			}
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
			const TofConfig& conf = GlobalConfig::GetTofConfig();

			sliderFolien->setMaximum(conf.GetFoilCount()-1);
			sliderZeitkanaele->setMaximum(conf.GetImagesPerFoil()-1);
		}

	// Slots
	protected slots:
		/////////// Slot für Tcp-Client ////////////////////////////////////////
		void ServerMessageSlot(const char* pcBuf, int iLen)
		{
			// Antworten müssen mindestens 4 Zeichen lang sein (Kommandostring)
			if(iLen<4) return;

			const TofConfig& conf = GlobalConfig::GetTofConfig();

			////////////////////////////////////////////////////////////////////
			// PAD-Daten vorhanden
			if(!strncmp(pcBuf,"IMAG",4))
			{
				// if global config changed
				bool bForceReinit = false;

	#ifndef DATA_COMPRESSED
				// Abfrage nur für unkomprimierte Daten möglich
				if(iLen-4 != (int)sizeof(int)*conf.GetImageHeight()
											 *conf.GetImageWidth())
				{
					bForceReinit = true;

					// Dimensionen stimmen nicht, neue raten
					if(!GlobalConfig::GuessConfigFromSize(0,(iLen-4)/4,
																		false))
					{
						char pcMsg[256];
						sprintf(pcMsg, "Dimension mismatch in PAD data!\n"
								"Client expected: %d bytes\n"
								"Server sent: %d bytes",
								(int)sizeof(int)*
								conf.GetImageHeight()*
								conf.GetImageWidth(), iLen-4);
						QMessageBox::critical(0, "Cascade - Server", pcMsg,
															QMessageBox::Ok);
						return;
					}
				}
	#endif
				if(bForceReinit)
					m_cascadewidget.ForceReinit();
				void* pvData = m_cascadewidget.NewPad();
	#ifdef DATA_COMPRESSED
				// Komprimierte Daten umkopieren
				int iLenOut = sizeof(int)*conf.IMAGE_HEIGHT*
										  conf.IMAGE_WIDTH;
				if(!zlib_decompress(pcBuf+4, iLen-4, pvData, iLenOut))
				{
					QMessageBox::critical(0, "Cascade - Server",
										  "Error in PAD decompression.",
										  QMessageBox::Ok);
					return;
				}
	#else
				// Unkomprimierte Daten umkopieren
				memcpy(pvData, pcBuf+4, sizeof(int)*
										conf.GetImageHeight()*
										conf.GetImageWidth());
	#endif

				m_cascadewidget.UpdateRange();
				m_cascadewidget.UpdateGraph();

				UpdateLabels(false);
				//ShowMessage("PAD loaded from Server.");
			}
			////////////////////////////////////////////////////////////////////
			// TOF-Daten vorhanden
			else if(!strncmp(pcBuf,"DATA",4))
			{
				// if global config changed
				bool bForceReinit = false;

	#ifndef DATA_COMPRESSED
				int iExpectedSize = conf.GetPseudoCompression()
								? sizeof(int) * conf.GetFoilCount()*
								  conf.GetImagesPerFoil()*
								  conf.GetImageHeight()*
								  conf.GetImageWidth()
								: sizeof(int) * conf.GetImageCount()*
								  conf.GetImageHeight()*
								  conf.GetImageWidth();

				if(iLen-4 != iExpectedSize)
				{
					bForceReinit = true;

					// Dimensionen stimmen nicht, neue raten
					if(!GlobalConfig::GuessConfigFromSize(
								m_cascadewidget.GetTof()->GetCompressionMethod()
													==TOF_COMPRESSION_PSEUDO,
								(iLen-4)/4, true))
					{
						char pcMsg[256];
						sprintf(pcMsg, "Dimension mismatch in TOF data!\n"
									   "Client expected: %d bytes\n"
									   "Server sent: %d bytes",
									   iExpectedSize, iLen-4);
						QMessageBox::critical(0, "Cascade - Server", pcMsg,
												QMessageBox::Ok);
						return;
					}
				}
	#endif
				if(bForceReinit)
					m_cascadewidget.ForceReinit();
				void* pvData = m_cascadewidget.NewTof(/*btnLog->isChecked()*/);

	#ifdef DATA_COMPRESSED
				// Komprimierte Daten umkopieren
				int iLenOut = sizeof(int)*conf.IMAGE_COUNT*
										  conf.IMAGE_HEIGHT*
										  conf.IMAGE_WIDTH;
				if(!zlib_decompress(pcBuf+4, iLen-4, pvData, iLenOut))
				{
					QMessageBox::critical(0, "Cascade - Server",
								"Error in TOF decompression.", QMessageBox::Ok);
					return;
				}
	#else
				// Unkomprimierte Daten umkopieren
				memcpy(pvData, pcBuf+4, iExpectedSize);
	#endif

				//m_cascadewidget.ShowGraph();	// macht viewOverview schon
				//UpdateLabels(false);

				UpdateSliders();
				//ShowMessage("TOF loaded from Server.");
				viewOverview();
				actionViewsOverview->setChecked(true);
			}
			////////////////////////////////////////////////////////////////////
			// Fehler
			else if(!strncmp(pcBuf,"ERR_",4))
			{
				QMessageBox::critical(0, "Cascade - Server", pcBuf+4,
									  QMessageBox::Ok);
			}
			// Status-Update erhalten
			else if(!strncmp(pcBuf,"MSG_",4))
			{
				ArgumentMap args(pcBuf+4);

//---------------------------------------
// TODO: don't display this in status bar
				// stop?
				std::pair<bool, int> pairStop = args.QueryInt("stop",1);
				if(pairStop.first)
					ShowMessage(pairStop.second
									? "Server: Measurement stopped."
									: "Server: Measurement running.");
//---------------------------------------

				// xres?
				std::pair<bool, int> pairXRes =
							args.QueryInt("xres", ServerCfgDlg::GetStatXRes());
				if(pairXRes.first)
				{
					ServerCfgDlg::SetStatXRes(pairXRes.second);

					TofConfig& conf = GlobalConfig::GetTofConfig();
					conf.SetImageWidth(pairXRes.second);
				}

				// yres?
				std::pair<bool, int> pairYRes =
							args.QueryInt("yres", ServerCfgDlg::GetStatYRes());
				if(pairYRes.first)
				{
					ServerCfgDlg::SetStatYRes(pairYRes.second);

					TofConfig& conf = GlobalConfig::GetTofConfig();
					conf.SetImageHeight(pairYRes.second);
				}

				// tres?
				std::pair<bool, int> pairTRes =
							args.QueryInt("tres", ServerCfgDlg::GetStatTRes());
				if(pairTRes.first)
				{
					ServerCfgDlg::SetStatTRes(pairTRes.second);

					TofConfig& conf = GlobalConfig::GetTofConfig();
					conf.SetImageCount(pairTRes.second);
				}

				// measurement time?
				std::pair<bool, double> pairTime = args.QueryDouble("time",
										ServerCfgDlg::GetStatTime());
				if(pairTime.first)
					ServerCfgDlg::SetStatTime(pairTime.second);

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
				std::pair<bool, int> pairComp = args.QueryInt("comp",1);
				if(pairComp.first)
				{
					TofConfig& conf = GlobalConfig::GetTofConfig();

					conf.SetPseudoCompression(pairComp.second);
					ServerCfgDlg::SetStatComp(pairComp.second);
				}

				std::pair<bool, int> pairCnt = args.QueryInt("ext_count",0);
				if(pairCnt.first)
					SetRightStatus(pairCnt.second);

				std::pair<bool, int> pairClients = args.QueryInt("clients",0);
				if(pairClients.first)
					SetRightStatus(-1, pairClients.second);


				// if global config changed, reinit PAD & TOF memory
				if(pairXRes.first || pairYRes.first || pairTRes.first ||
									 pairComp.first)
					m_cascadewidget.ForceReinit();
			}
			else if(!strncmp(pcBuf,"OKAY",4))
			{}
			else
			{
				logger.SetCurLogLevel(LOGLEVEL_ERR);
				logger << "Cascade: Unknown prefix in server response: \""
					   << pcBuf[0]<<pcBuf[1]<<pcBuf[2]<<pcBuf[3]
					   << "\".\n";
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
			sprintf(pcFolie,"Foil (%0d):",m_cascadewidget.GetFoil()+1);
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
			sprintf(pcKanal,"Time Channel (%0d):",
					m_cascadewidget.GetTimechannel()+1);
			labelZeitkanal->setText(pcKanal);
		}

		void SetLog10(bool bLog)
		{
			m_cascadewidget.SetLog10(bLog);
			UpdateLabels(false);
		}

		void SetAutoFetch(bool bAutoFetch)
		{
			if(bAutoFetch)
				m_autofetchtimer.start(AUTOFETCH_POLL_TIME);
			else
				m_autofetchtimer.stop();
		}

		void AutoFetch()
		{
			if(!m_client.isconnected())
			{
				//SetAutoFetch(false);
				//btnAutoFetch->setChecked(false);
				return;
			}
			m_client.sendmsg("CMD_readsram");
		}

		void showCalibration(void)
		{
			if(!m_cascadewidget.IsTofLoaded())
			{
				QMessageBox::critical(0, "Calibration", "No TOF loaded "
										"or not in TOF mode.", QMessageBox::Ok);
				return;
			}

			m_cascadewidget.showCalibrationDlg(NUM_BINS);
		}

		void showGraph(void)
		{
			if(!m_cascadewidget.IsTofLoaded())
			{
				QMessageBox::critical(0, "Graph", "No TOF loaded "
										"or not in TOF mode.", QMessageBox::Ok);
				return;
			}

			m_cascadewidget.showGraphDlg();
		}

		void showSummenDialog(void)
		{
			if(!m_cascadewidget.IsTofLoaded())
			{
				QMessageBox::critical(0, "Sums", "No TOF loaded "
										"or not in TOF mode.", QMessageBox::Ok);
				return;
			}

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

		////////////////////////// Server Menu Items ///////////////////////////
		void ConnectToServer()
		{
			ServerDlg SrvDlg(this);

			// get default settings from config file
			QString strConfigAddress =
						QString(Config::GetSingleton()->QueryString(
						"/cascade_config/server/address",
						"127.0.0.1").c_str()).simplified();

			int iConfigPort = Config::GetSingleton()
						->QueryInt("/cascade_config/server/port", 1234);


			static QString strLastAddress("");
			static int iLastPort = 0;

			// no previous address entered
			if(strLastAddress==QString("") || iLastPort==0)
			{
				SrvDlg.editAddress->setText(strConfigAddress);

				QString strPort;
				strPort.setNum(iConfigPort);
				SrvDlg.editPort->setText(strPort);
			}
			else 								// use previous address
			{
				SrvDlg.editAddress->setText(strLastAddress);

				QString strPort;
				strPort.setNum(iLastPort);
				SrvDlg.editPort->setText(strPort);
			}

			if(SrvDlg.exec() == QDialog::Accepted)
			{
				ServerDisconnect();

				if(!m_client.connecttohost(
						SrvDlg.editAddress->text().toAscii().data(),
						SrvDlg.editPort->text().toInt()))
				{
					char pcBuf[512];
					sprintf(pcBuf, "Could not connect to server\n"
								   "\"%s\"\nat port %d.",
								   SrvDlg.editAddress->text().toAscii().data(),
								   SrvDlg.editPort->text().toInt());
					QMessageBox::critical(0, "Error", pcBuf, QMessageBox::Ok);
					return;
				}

				// show messages
				ShowMessage("Connected to server.");

				std::string strTitleMsg
								= SrvDlg.editAddress->text().toAscii().data();
				strTitleMsg += ":";
				strTitleMsg += SrvDlg.editPort->text().toAscii().data();
				ShowTitleMessage(strTitleMsg.c_str());
				// -------------

				m_statustimer.start(SERVER_STATUS_POLL_TIME);

				strLastAddress = SrvDlg.editAddress->text();
				iLastPort = SrvDlg.editPort->text().toInt();

				// get current config of hardware
				GetServerConfig();
			}
		}

		void ServerDisconnect()
		{
			m_statustimer.stop();
			m_client.disconnect();
			ShowMessage("Disconnected from server.");
			ShowTitleMessage("");
		}

		// enter manual server command
		void ServerCommand()
		{
			if(!CheckConnected()) return;

			CommandDlg commanddlg(this);
			if(commanddlg.exec() == QDialog::Accepted)
			{
				QString strCmd = commanddlg.editCommand->text().simplified();
				if(strCmd != QString(""))
					m_client.sendmsg(strCmd.toAscii().data());
			}
		}

		void ServerStatus()
		{
			if(!CheckConnected()) return;

			m_client.sendmsg("CMD_status_cdr");
			m_client.sendmsg("CMD_status_server");
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

				TofConfig& conf = GlobalConfig::GetTofConfig();
				conf.SetImageWidth(iXRes);
				conf.SetImageHeight(iYRes);
				conf.SetImageCount(iTRes);
				conf.SetPseudoCompression(bComp);

				// reinit PAD & TOF memory
				m_cascadewidget.ForceReinit();

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
				sprintf(pcMsg, "CMD_config_cdr "
							   "time=%f xres=%d yres=%d tres=%d "
							   "mode=%s comp=%d",
							   dTime, iXRes, iYRes, iTRes, pcMode, bComp);
				m_client.sendmsg(pcMsg);
			}
		}
		////////////////////////////////////////////////////////////////////////


		///////////////////////////// File Menu Items /////////////////////////
		void LoadPad()
		{
			m_cascadewidget.NewPad(/*btnLog->isChecked()*/);
			QString strFile = QFileDialog::getOpenFileName(this,
									"Open PAD File","",
									"PAD Files (*.pad *.PAD);;All Files (*)");
			if(strFile!="" &&
				m_cascadewidget.LoadPadFile(strFile.toAscii().data()))
			{
				//m_cascadewidget.UpdateGraph();
				UpdateLabels(false);
				ShowMessage("PAD loaded.");
			}
		}

		void LoadTof()
		{
			m_cascadewidget.NewTof(/*btnLog->isChecked()*/);
			QString strFile = QFileDialog::getOpenFileName(
								this, "Open TOF File","",
								"TOF Files (*.tof *.TOF);;All Files (*)");
			if(strFile!="" &&
			   m_cascadewidget.LoadTofFile(strFile.toAscii().data()))
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
				QString strFile = QFileDialog::getSaveFileName(this,
									"XML Files (*.xml *.XML);;All Files (*)");
				if(strFile=="")
					return;

				TmpImage tmpimg;
				if(m_cascadewidget.IsTofLoaded())	// TOF-Datei offen
					m_cascadewidget.GetTof()->GetOverview(&tmpimg);
				else					// PAD-Datei offen
					tmpimg.ConvertPAD(m_cascadewidget.GetPad());
				tmpimg.WriteXML(strFile.toAscii().data());
			}
		}
		///////////////////////////////////////////////////////////////////


		//////////////////////////ROI /////////////////////////////////////
		void showRoiDlg()
		{
			if(!m_cascadewidget.IsTofLoaded() && !m_cascadewidget.IsPadLoaded())
			{
				QMessageBox::critical(0, "ROI", "No TOF or PAD loaded.",
									  QMessageBox::Ok);
				return;
			}

			m_cascadewidget.showRoiDlg();
		}

		void LoadRoi()
		{
			if(!m_cascadewidget.IsTofLoaded() && !m_cascadewidget.IsPadLoaded())
			{
				QMessageBox::critical(0, "ROI", "No TOF or PAD loaded.",
									  QMessageBox::Ok);
				return;
			}

			QString strFile = QFileDialog::getOpenFileName(this,
									"Open ROI File","",
									"XML Files (*.xml *.XML);;All Files (*)");
			if(strFile!="" && m_cascadewidget.LoadRoi(strFile.toAscii().data()))
			{
				UpdateLabels(false);
				ShowMessage("ROI loaded.");
			}
		}

		void SaveRoi()
		{
			if(!m_cascadewidget.IsTofLoaded() && !m_cascadewidget.IsPadLoaded())
			{
				QMessageBox::critical(0, "ROI", "No TOF or PAD loaded.",
									  QMessageBox::Ok);
				return;
			}

			QString strFile = QFileDialog::getSaveFileName(this,
								"XML Files (*.xml *.XML);;All Files (*)");
			if(strFile=="")
				return;

			if(m_cascadewidget.SaveRoi(strFile.toAscii().data()))
			{
				UpdateLabels(false);
				ShowMessage("ROI saved.");
			}
		}
		///////////////////////////////////////////////////////////////////

		///////////////////////// Help ///////////////////////////////////
		void About()
		{
			QString strAbout = "Cascade Viewer written by Tobias Weber.";
			strAbout += "\n";

			#if defined(__DATE__) && defined(__TIME__)
			strAbout += QString("\n") + QString("Build time: ") +
						QString(__DATE__) + QString(" ") + QString(__TIME__);
			#endif

			#ifdef __VERSION__
			strAbout += QString("\n") + QString("Built with CC version ") +
						QString(__VERSION__);
			#endif
			strAbout += "\n";

			#ifdef QT_VERSION_STR
			strAbout += QString("\n") + QString("Uses Qt version ") +
						QString(QT_VERSION_STR) + QString("\thttp://qt.nokia.com");
			#endif

			#ifdef QWT_VERSION_STR
			strAbout += QString("\n") + QString("Uses Qwt version ") +
						QString(QWT_VERSION_STR) + QString("\thttp://qwt.sf.net");
			#endif

			#ifdef USE_MINUIT
			strAbout += QString("\n") + QString("Uses Minuit 2\t\thttp://root.cern.ch");
			#endif

			#ifdef USE_BOOST
			strAbout += QString("\n") + QString("Uses Boost\t\thttp://www.boost.org");
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

		MainWindow(QWidget *parent=NULL)
			: QMainWindow(parent), m_cascadewidget(this),
			  m_client(this, false), m_statustimer(this), m_autofetchtimer(this),
			  statusbar(NULL)
		{
			m_cascadewidget.SetLog10(true);


			m_strTitle = Config::GetSingleton()->QueryString(
							"/cascade_config/main_window/title",
							"Cascade Viewer");
			setWindowTitle(QString(m_strTitle.c_str()).simplified());


			QWidget *pCentralWidget = new QWidget(this);
			setCentralWidget(pCentralWidget);


			//------------------------------------------------------------------
			//QGroupBox *grouptopright = new QGroupBox(&m_cascadewidget);
			//QGroupBox *groupbottomright = new QGroupBox(&m_cascadewidget);
			QGroupBox *groupbottomleft = new QGroupBox(pCentralWidget);

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
			//------------------------------------------------------------------



			//------------------------------------------------------------------
			QGridLayout *centralgridlayout = new QGridLayout(pCentralWidget);
			centralgridlayout->addWidget(&m_cascadewidget, 0, 0, 1, 1);
			//centralgridlayout->addWidget(grouptopright, 0, 1, 1, 1);
			//centralgridlayout->addWidget(groupbottomright, 1, 1, 1, 1);
			centralgridlayout->addWidget(groupbottomleft, 1, 0, 1, 1);
			//------------------------------------------------------------------



			//------------------------------------------------------------------
			// Menu Items
			// File Menu Items
			QAction *actionLoadPad = new QAction(this);
			actionLoadPad->setText("Load &PAD File...");
			actionLoadPad->setShortcut(QKeySequence(Qt::CTRL + Qt::Key_P));

			QAction *actionLoadTof = new QAction(this);
			actionLoadTof->setText("Load &TOF File...");
			actionLoadTof->setShortcut(QKeySequence(Qt::CTRL + Qt::Key_T));

			QAction *actionWriteXML = new QAction(this);
			actionWriteXML->setText("Write &XML...");

			QAction *actionPrint = new QAction(this);
			actionPrint->setText("P&rint Plot...");

			QAction *actionExit = new QAction(this);
			actionExit->setText("&Exit");


			// Server Menu Items
			QAction *actionConnectServer = new QAction(this);
			actionConnectServer->setText("&Connect to Server...");
			actionConnectServer->setShortcut(
											QKeySequence(Qt::CTRL + Qt::Key_C));

			QAction *actionServerDisconnect = new QAction(this);
			actionServerDisconnect->setText("&Disconnect from Server");

			QAction *actionServerCommand = new QAction(this);
			actionServerCommand->setText("Enter &Manual Command...");

			QAction *actionServerMeasurementStart = new QAction(this);
			actionServerMeasurementStart->setText("&Start Measurement");
			actionServerMeasurementStart->setShortcut(
											QKeySequence(Qt::CTRL + Qt::Key_S));

			QAction *actionServerMeasurementStop = new QAction(this);
			actionServerMeasurementStop->setText("&End Measurement");

			QAction *actionLoadTofServer = new QAction(this);
			actionLoadTofServer->setText("Fetch &Data");
			actionLoadTofServer->setShortcut(
											QKeySequence(Qt::CTRL + Qt::Key_D));

			QAction *actionConfigServer = new QAction(this);
			actionConfigServer->setText("C&onfigure...");

			QAction *actionConfigFromServer = new QAction(this);
			actionConfigFromServer->setText("&Retrieve Configuration");


			// Graph Menu Items
			QAction *actionGraph = new QAction(this);
			actionGraph->setText("&Counts vs. Time Channels...");

			QAction *actionSummen = new QAction(this);
			actionSummen->setText("&Sum Images...");

			QAction *actionCalibration = new QAction(this);
			actionCalibration->setText("C&alibration...");


			// ROI Menu Items
			QAction *actionManageRois = new QAction(this);
			actionManageRois->setText("&Manage ROI...");

			QAction *actionLoadRoi = new QAction(this);
			actionLoadRoi->setText("Load ROI...");

			QAction *actionSaveRoi = new QAction(this);
			actionSaveRoi->setText("Save ROI...");


			// Help Menu Items
			QAction *actionAbout = new QAction(this);
			actionAbout->setText("&About...");

			QAction *actionAboutQt = new QAction(this);
			actionAboutQt->setText("About &Qt...");
			//------------------------------------------------------------------


			//------------------------------------------------------------------
			// Menu Bar
			QMenuBar *menubar = new QMenuBar(this);;

			menubar->setGeometry(QRect(0, 0, 800, 25));
			QMenu *menuFile = new QMenu(menubar);
			menuFile->setTitle("&File");
			menuFile->addAction(actionLoadPad);
			menuFile->addAction(actionLoadTof);
			menuFile->addSeparator();
			menuFile->addAction(actionWriteXML);
			menuFile->addAction(actionPrint);
			menuFile->addSeparator();
			menuFile->addAction(actionExit);
			menubar->addAction(menuFile->menuAction());

			QMenu *menuServer = new QMenu(menubar);
			menuServer->setTitle("&Server");
			menuServer->addAction(actionConnectServer);
			menuServer->addAction(actionServerDisconnect);
			menuServer->addSeparator();
			menuServer->addAction(actionServerCommand);
			menuServer->addSeparator();
			menuServer->addAction(actionConfigFromServer);
			menuServer->addAction(actionConfigServer);
			menuServer->addSeparator();
			menuServer->addAction(actionServerMeasurementStart);
			menuServer->addAction(actionServerMeasurementStop);
			menuServer->addSeparator();
			menuServer->addAction(actionLoadTofServer);
			menubar->addAction(menuServer->menuAction());

			QMenu *menuGraph = new QMenu(menubar);
			menuGraph->setTitle("&Graph");
			menuGraph->addAction(actionCalibration);
			menuGraph->addSeparator();
			menuGraph->addAction(actionGraph);
			menuGraph->addAction(actionSummen);
			menubar->addAction(menuGraph->menuAction());

			QMenu *menuRoi = new QMenu(menubar);
			menuRoi->setTitle("&ROI");
			menuRoi->addAction(actionManageRois);
			menuRoi->addSeparator();
			menuRoi->addAction(actionLoadRoi);
			menuRoi->addAction(actionSaveRoi);
			menubar->addAction(menuRoi->menuAction());

			QMenu *menuHelp = new QMenu(menubar);
			menuHelp->setTitle("&Help");
			menuHelp->addAction(actionAbout);
			menuHelp->addAction(actionAboutQt);
			menubar->addAction(menuHelp->menuAction());

			setMenuBar(menubar);
			//------------------------------------------------------------------


			//------------------------------------------------------------------
			// Toolbar
			QToolBar *toolBar = new QToolBar("Toolbar",this);

			btnLog = new QToolButton(toolBar);
			btnLog->setText("Log10");
			btnLog->setCheckable(true);
			btnLog->setChecked(m_cascadewidget.GetLog10());
			toolBar->addWidget(btnLog);

			btnAutoFetch = new QToolButton(toolBar);
			btnAutoFetch->setText("AutoFetch");
			btnAutoFetch->setCheckable(true);
			btnAutoFetch->setChecked(false);
			toolBar->addWidget(btnAutoFetch);


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
			//------------------------------------------------------------------


			//------------------------------------------------------------------
			// Status Bar
			statusbar = new QStatusBar(this);
			pStatusMsg = new QLabel(this);
			pStatusExtCount = new QLabel(this);
			//pStatusMsg->setFrameStyle(QFrame::Panel|QFrame::Sunken);
			statusbar->addWidget(pStatusMsg,1);
			statusbar->addPermanentWidget(pStatusExtCount,0);
			setStatusBar(statusbar);

			SetRightStatus(0,0);
			//------------------------------------------------------------------


			//------------------------------------------------------------------
			// Connections
			// Toolbar
			connect(btnLog, SIGNAL(toggled(bool)), this,
							SLOT(SetLog10(bool)));
			connect(btnAutoFetch, SIGNAL(toggled(bool)), this,
							SLOT(SetAutoFetch(bool)));
			connect(actionViewsOverview, SIGNAL(triggered()), this,
										 SLOT(viewOverview()));
			connect(actionViewsSlides, SIGNAL(triggered()), this,
									   SLOT(viewSlides()));
			connect(actionViewsPhases, SIGNAL(triggered()), this,
									   SLOT(viewPhases()));
			connect(actionViewsContrasts, SIGNAL(triggered()), this,
									   SLOT(viewContrasts()));

			// Slider
			connect(sliderFolien, SIGNAL(valueChanged(int)), this,
								  SLOT(ChangeFolie(int)));
			connect(sliderZeitkanaele, SIGNAL(valueChanged(int)), this,
								  SLOT(ChangeZeitkanal(int)));

			// File
			connect(actionExit, SIGNAL(triggered()), this,
								SLOT(close()));
			connect(actionLoadPad, SIGNAL(triggered()), this,
								SLOT(LoadPad()));
			connect(actionLoadTof, SIGNAL(triggered()), this,
								   SLOT(LoadTof()));
			connect(actionWriteXML, SIGNAL(triggered()), this,
									SLOT(WriteXML()));
			connect(actionPrint, SIGNAL(triggered()), m_cascadewidget.GetPlot(),
									SLOT(printPlot()));

			// Server
			connect(actionConnectServer, SIGNAL(triggered()), this,
										 SLOT(ConnectToServer()));
			connect(actionServerDisconnect, SIGNAL(triggered()), this,
										 SLOT(ServerDisconnect()));

			connect(actionServerCommand, SIGNAL(triggered()), this,
										 SLOT(ServerCommand()));

			connect(actionLoadTofServer, SIGNAL(triggered()), this,
										 SLOT(LoadTofServer()));
			connect(actionServerMeasurementStart, SIGNAL(triggered()), this,
												SLOT(ServerMeasurementStart()));
			connect(actionServerMeasurementStop, SIGNAL(triggered()), this,
												SLOT(ServerMeasurementStop()));
			connect(actionConfigServer, SIGNAL(triggered()), this,
										SLOT(ServerConfig()));
			connect(actionConfigFromServer, SIGNAL(triggered()), this,
											SLOT(GetServerConfig()));

			// Help
			connect(actionAbout, SIGNAL(triggered()), this,
										 SLOT(About()));
			connect(actionAboutQt, SIGNAL(triggered()), this,
										 SLOT(AboutQt()));

			// Graph
			connect(actionCalibration, SIGNAL(triggered()), this,
									   SLOT(showCalibration()));
			connect(actionGraph, SIGNAL(triggered()), this,
								 SLOT(showGraph()));
			connect(actionSummen, SIGNAL(triggered()), this,
								  SLOT(showSummenDialog()));

			// Timer
			connect(&m_statustimer, SIGNAL(timeout()), this,
									SLOT(ServerStatus()));

			connect(&m_autofetchtimer, SIGNAL(timeout()), this,
									SLOT(AutoFetch()));

			// Server Message
			connect(&m_client, SIGNAL(MessageSignal(const char*, int)), this,
							   SLOT(ServerMessageSlot(const char*, int)));


			// ROI
			connect(actionManageRois, SIGNAL(triggered()), this,
									   SLOT(showRoiDlg()));

			connect(actionSaveRoi, SIGNAL(triggered()), this,
								   SLOT(SaveRoi()));

			connect(actionLoadRoi, SIGNAL(triggered()), this,
								   SLOT(LoadRoi()));

			// Widget
			connect(&m_cascadewidget, SIGNAL(SumDlgSignal(const bool *, int)),
								this, SLOT(FolienSummeSlot(const bool *, int)));
			//------------------------------------------------------------------


			bool bUseAutoFetch = (Config::GetSingleton()->QueryInt(
						"/cascade_config/server/autofetch_use",
						1) !=0 );

			if(bUseAutoFetch)
			{
				btnAutoFetch->setChecked(true);
				SetAutoFetch(true);
			}
		}
};

// Default Values
int MainWindow::NUM_BINS = 100;
int MainWindow::SERVER_STATUS_POLL_TIME = 500;
int MainWindow::AUTOFETCH_POLL_TIME = 250;

int main(int argc, char **argv)
{
	setlocale(LC_ALL, "C");
	QLocale::setDefault(QLocale::English);
	QApplication a(argc, argv);

	// Konfigurationssingleton erzeugen
	const char pcConfigFile[] = "./cascade.xml";
	if(!Config::GetSingleton()->Load(pcConfigFile))
	{
		char pcMsg[512];
		sprintf(pcMsg, "Configuration file \"%s\" could not be found.\n"
					   "Using default configuration.", pcConfigFile);
		QMessageBox::warning(0, "Warning", pcMsg, QMessageBox::Ok);
	}

	// Konfigurationseinstellungen laden
	GlobalConfig::Init();

	int iLogToFile = Config::GetSingleton()->QueryInt(
						"/cascade_config/log/log_to_file", 0);
	if(iLogToFile)
	{
		std::string strLogFile =
			Config::GetSingleton()->QueryString("/cascade_config/log/file",
												"cascade.log");
		logger.Init(strLogFile.c_str());
	}

	int iLogLevel = Config::GetSingleton()->QueryInt(
						"/cascade_config/log/level", LOGLEVEL_INFO);
	GlobalConfig::SetLogLevel(iLogLevel);

	bool bRepeatLogs = Config::GetSingleton()->QueryInt(
						"/cascade_config/log/repeat_duplicate_logs", 1);
	GlobalConfig::SetRepeatLogs(bRepeatLogs);

	int iWinW = Config::GetSingleton()->QueryInt(
						"/cascade_config/main_window/width", WIN_W);
	int iWinH = Config::GetSingleton()->QueryInt(
						"/cascade_config/main_window/height", WIN_H);

	MainWindow::NUM_BINS = Config::GetSingleton()->QueryInt(
						"/cascade_config/graphs/bin_count",
						MainWindow::NUM_BINS);
	MainWindow::SERVER_STATUS_POLL_TIME = Config::GetSingleton()->QueryInt(
						"/cascade_config/server/status_poll_time",
						MainWindow::SERVER_STATUS_POLL_TIME);

	MainWindow::AUTOFETCH_POLL_TIME	= Config::GetSingleton()->QueryInt(
						"/cascade_config/server/autofetch_poll_time",
						MainWindow::AUTOFETCH_POLL_TIME);

	MainWindow mainWindow;
	mainWindow.resize(iWinW, iWinH);
	mainWindow.show();
	int iRet = a.exec();

	// aufräumen
	GlobalConfig::Deinit();
	Config::ClearSingleton();
	return iRet;
}

#ifdef __CASCADE_QT_CLIENT__
	// Qt-Metaobjekte
	#include "cascade.moc"
#endif
