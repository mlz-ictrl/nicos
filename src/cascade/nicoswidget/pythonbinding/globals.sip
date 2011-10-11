//
// global configuration of TOF file layout
//
class Config_TofLoader
{
%TypeHeaderCode
#include "../../globals.h"
%End
	public:
		static int GetFoilCount();
		static int GetImagesPerFoil();
		static int GetImageWidth();
		static int GetImageHeight();
		static int GetImageCount();
		static int GetFoilBegin(int iFoil);
		static bool GetPseudoCompression();


		static void SetFoilCount(int iNumFoils);			// number of foils in TOF (e.g. 4)
		static void SetImagesPerFoil(int iNumImagesPerFoil);// number of time channels per foil (e.g. 16)
		static void SetImageWidth(int iImgWidth);			// x_res (e.g. 128)
		static void SetImageHeight(int iImgHeight);			// y_res (e.g. 128)
		static void SetImageCount(int iImgCount);			// total number of images in TOF == t_res (e.g. 128)
		static void SetFoilBegin(int iFoil, int iOffs);		// index of first time channel for each foil (e.g. 0,0;  1, 16;  2, 32;  3, 48)

															// false: all images specified in t_res are sent by server, including padding ones;
		static void SetPseudoCompression(bool bSet);		//        counts in first time are split between first and last channels
															// true: the opposite of both points

		static void SetLogLevel(int iLevel);			// Log Level: 0: log nothing,
														//            1: log errors,
														//            2: log errors & warnings,
														//            3: log errors & warnings & infos

		static void SetRepeatLogs(bool bRepeat);		// Repeat duplicate logs?

		static void SetMinuitMaxFnc(unsigned int uiMaxFcn);
		static void SetMinuitTolerance(double dTolerance);
		static void SetMinuitAlgo(int iAlgo);
		static void SetMinuitStrategy(unsigned int iStrategy);
};
