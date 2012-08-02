/*
 * configuration of PAD class
 */
class PadConfig
{
%TypeHeaderCode
#include "../../globals.h"
%End

	public:
		PadConfig();
		PadConfig(const PadConfig& conf);

		//----------------------------------------------------------------------
		// getter
		int GetImageWidth() const;
		int GetImageHeight() const;

		//----------------------------------------------------------------------
		// setter
		void SetImageWidth(int iImgWidth);
		void SetImageHeight(int iImgHeight);
};


/*
 * configuration of TOF class
 */
class TofConfig : PadConfig
{
%TypeHeaderCode
#include "../../globals.h"
%End

	public:
		TofConfig();
		TofConfig(const TofConfig& conf);

		//----------------------------------------------------------------------
		// getter
		int GetFoilCount() const;
		int GetImagesPerFoil() const;
		int GetImageCount() const;
		int GetFoilBegin(int iFoil) const;
		bool GetPseudoCompression() const;
		bool GetSumFirstAndLast() const;
		double GetNumOscillations() const;		

		//----------------------------------------------------------------------
		// setter

		// number of foils in TOF (e.g. 4)
		void SetFoilCount(int iNumFoils);

		// number of time channels per foil (e.g. 16)
		void SetImagesPerFoil(int iNumImagesPerFoil);

		// total number of images in TOF == t_res (e.g. 128)
		void SetImageCount(int iImgCount);

		// index of first time channel for each foil (e.g. 0,0;  1, 16;  2, 32;  3, 48)
		void SetFoilBegin(int iFoil, int iOffs);

		// false: all images specified in t_res are sent by server, including padding ones;
		//        counts in first time are split between first and last channels
		// true: the opposite of both points
		void SetPseudoCompression(bool bSet);

		void SetSumFirstAndLast(bool bSet);

		// for frequency of MIEZE sine fit
		void SetNumOscillations(double dVal);		
};


/*
 * global, static configuration class
 * used to configure layout of TOF & PAD formats etc. before first use of
 * these classes
 */
class GlobalConfig
{
%TypeHeaderCode
#include "../../globals.h"
%End

	public:
		static TofConfig& GetTofConfig();

		// Log Level: 0: log nothing,
		//            1: log errors,
		//            2: log errors & warnings,
		//            3: log errors & warnings & infos
		static void SetLogLevel(int iLevel);

		// Repeat duplicate logs?
		static void SetRepeatLogs(bool bRepeat);
};
