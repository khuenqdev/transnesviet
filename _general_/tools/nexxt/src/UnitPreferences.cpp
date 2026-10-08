//---------------------------------------------------------------------
#include <vcl.h>
#pragma hdrstop

#include "UnitMain.h"
#include "UnitPreferences.h"
//---------------------------------------------------------------------
#pragma resource "*.dfm"
TFormPreferences *FormPreferences;

extern bool prefStartScale2x;
extern bool prefStartScale3x;
extern bool prefStartScale4x;


extern bool prefStartCol0;
extern bool prefStartCol1;
extern bool prefStartCol2;
extern bool prefStartCol3;

extern bool prefStartSubpal0;
extern bool prefStartSubpal1;
extern bool prefStartSubpal2;
extern bool prefStartSubpal3;

extern bool prefStartGridShow;

extern bool prefStartGrid1;
extern bool prefStartGrid2;
extern bool prefStartGrid4;
extern bool prefStartGrid8;
extern bool prefStartGrid32x30;

extern bool prefStartGridPixelCHR;
extern bool prefStartGridTilesCHR;
extern bool prefStartGridMidpointsCHR;


extern bool prefStartShowBrushes;
extern bool prefStartShowBucket;
extern bool prefStartShowLines;


extern bool prefStartShowCHR;
extern bool prefStartShowMM;

extern bool prefStartShowPaste;
extern bool prefStartShowNavigator;
extern bool prefStartShowBankSelector;
extern bool prefStartShowBankSwapper;
extern bool prefStartShowMetatileEditor;
extern bool prefStartShowColourRose;

extern bool prefStartMsprListID;
extern bool prefStartMsprListLabel;
extern bool prefStartMsprListNTSC;
extern bool prefStartMsprListPAL;
extern bool prefStartMsprListCount;
extern bool prefStartMsprListTag;

extern bool prefStartAntiJagEnabled;

extern bool prefStartPinCHR;
extern bool prefStartPinMM;

extern bool prefStartPinBrushes;
extern bool prefStartPinBucket;
extern bool prefStartPinLines;

extern bool prefStartPinPaste;
extern bool prefStartPinNavigator;
extern bool prefStartPinBankSelector;
extern bool prefStartPinBankSwapper;
extern bool prefStartPinMetatileEditor;
extern bool prefStartPinColourRose;



extern bool bWarnMsprYellow;
extern bool bWarnMsprOrange;
extern bool bWarnMsprRed;
extern bool bWarnMsprCyan;

extern bool bExportPalFilename;
extern bool bExportPalSet;

extern bool bImportCHRWrap;
extern bool bImportCHRCarry;
extern bool bImportCHRSkip;

extern bool bExportVerticalSystemLUT;
extern bool bExportHorizontalSystemLUT;
extern bool bExportDefaultPNG;
extern bool bExportDefaultBMP;
extern bool bExportIncludeNonactiveSupbals;
extern bool bExportIncludeSystemLUT;

extern int iGlobalAlpha;
extern int iRadioOpenSave;
extern int iShowFilepath;
extern bool bSnapToScreen;

extern bool BMPimport_use13;
extern bool BMPimport_usePalOff;
extern int  BMPimport_palOff;
extern bool BMPexport_use13;
extern bool BMPexport_use13_mspr;
extern bool BMPexport_use13_tiles;
extern bool BMPexport_use13_mt;
extern bool BMPexport_use13_subpal;
//extern bool BMPexport_usePalOff;
//extern int  BMPexport_palOff;


//these are initialized when ShowForm is called.
int TMPprefStartScale;
int TMPprefStartCol;
int TMPprefStartSubpal;
bool TMPprefStartGridShow;
bool TMPprefStartGrid1;
bool TMPprefStartGrid2;
bool TMPprefStartGrid4;
bool TMPprefStartGrid8;
bool TMPprefStartGrid32x30;

bool TMPprefStartGridPixelCHR;
bool TMPprefStartGridTilesCHR;
bool TMPprefStartGridMidpointsCHR;

bool TMPprefStartShowCHR;
bool TMPprefStartShowMM;

bool TMPprefStartShowPaste;
bool TMPprefStartShowNavigator;
bool TMPprefStartShowBankSelector;
bool TMPprefStartShowBankSwapper;
bool TMPprefStartShowMetatileEditor;
bool TMPprefStartShowColourRose;

bool TMPprefStartMsprListID;
bool TMPprefStartMsprListLabel;
bool TMPprefStartMsprListNTSC;
bool TMPprefStartMsprListPAL;
bool TMPprefStartMsprListCount;
bool TMPprefStartMsprListTag;

bool TMPprefStartAntiJagEnabled;

bool TMPprefStartShowBrushes;
bool TMPprefStartShowBucket;
bool TMPprefStartShowLines;

bool TMPprefStartPinCHR;
bool TMPprefStartPinMM;

bool TMPprefStartPinBrushes;
bool TMPprefStartPinBucket;
bool TMPprefStartPinLines;
bool TMPprefStartPinPaste;

bool TMPprefStartPinNavigator;
bool TMPprefStartPinBankSelector;
bool TMPprefStartPinBankSwapper;
bool TMPprefStartPinMetatileEditor;
bool TMPprefStartPinColourRose;

extern int flattenCommonBGCol;

//---------------------------------------------------------------------
__fastcall TFormPreferences::TFormPreferences(TComponent* AOwner)
	: TForm(AOwner)
{
}
//---------------------------------------------------------------------
void __fastcall TFormPreferences::GetStartPreferences()
{
	if(TMPprefStartScale==2)	RadioScale2x->Checked=true;

	if(TMPprefStartScale==3)	RadioScale3x->Checked=true;
	if(TMPprefStartScale==4)	RadioScale4x->Checked=true;

	if(TMPprefStartCol==0)		RadioCol0->Checked=true;
	if(TMPprefStartCol==1)		RadioCol1->Checked=true;
	if(TMPprefStartCol==2)		RadioCol2->Checked=true;
	if(TMPprefStartCol==3)		RadioCol3->Checked=true;

	if(TMPprefStartSubpal==0)	RadioSubpal0->Checked=true;
	if(TMPprefStartSubpal==1)	RadioSubpal1->Checked=true;
	if(TMPprefStartSubpal==2)	RadioSubpal2->Checked=true;
	if(TMPprefStartSubpal==3)	RadioSubpal3->Checked=true;

	if(TMPprefStartGridShow)	RadioGridShow->Checked=true;
	else 	                    RadioGridHide->Checked=true;

	CheckGrid1->Checked	= TMPprefStartGrid1;
	CheckGrid2->Checked	= TMPprefStartGrid2;
	CheckGrid4->Checked	= TMPprefStartGrid4;
	CheckGrid8->Checked = TMPprefStartGrid8;

	CheckGrid32x30->Checked = TMPprefStartGrid32x30;

	CheckGridPixelCHR->Checked=TMPprefStartGridPixelCHR;
	CheckGridTilesCHR->Checked=TMPprefStartGridTilesCHR;
	CheckGridMidpointsCHR->Checked=TMPprefStartGridMidpointsCHR;


	CheckPinCHREditor->Checked				=	TMPprefStartPinCHR;
	CheckPinMetaspriteManager->Checked		=	TMPprefStartPinMM;

	CheckPinBrushes->Checked				=	TMPprefStartPinBrushes;
	CheckPinBucket->Checked					=   TMPprefStartPinBucket;
	CheckPinLines->Checked					=   TMPprefStartPinLines;
	CheckPinPaste->Checked					=   TMPprefStartPinPaste;

	CheckPinNavigator->Checked			   =    TMPprefStartPinNavigator;
	CheckPinBankSelector->Checked		   =    TMPprefStartPinBankSelector;
	CheckPinBankSwapper->Checked		   =    TMPprefStartPinBankSwapper;
	CheckPinMetatileEditor->Checked	   	   =    TMPprefStartPinMetatileEditor;
	CheckPinColourRose->Checked		   	   =    TMPprefStartPinColourRose;

	CheckShowCHREditor->Checked				=	TMPprefStartShowCHR;
	CheckShowMetaspriteManager->Checked		=	TMPprefStartShowMM;

	CheckShowBrushes->Checked				=	TMPprefStartShowBrushes;
	CheckShowBucket->Checked				=   TMPprefStartShowBucket;
	CheckShowLines->Checked					=   TMPprefStartShowLines;
	CheckShowPaste->Checked					=   TMPprefStartShowPaste;

	CheckShowPaste->Checked				   =    TMPprefStartShowPaste;

	CheckShowNavigator->Checked			   =    TMPprefStartShowNavigator;
	CheckShowBankSelector->Checked		   =    TMPprefStartShowBankSelector;
	CheckShowBankSwapper->Checked		   =    TMPprefStartShowBankSwapper;
	CheckShowMetatileEditor->Checked	   =    TMPprefStartShowMetatileEditor;
	CheckShowColourRose->Checked		   =    TMPprefStartShowColourRose;


	CheckShowMsprListID->Checked			=   TMPprefStartMsprListID;
	CheckShowMsprListLabel->Checked			=	TMPprefStartMsprListLabel;
	CheckShowMsprListNTSC->Checked			=	TMPprefStartMsprListNTSC;
	CheckShowMsprListPAL->Checked			=	TMPprefStartMsprListPAL;
	CheckShowMsprListCount->Checked			=	TMPprefStartMsprListCount;
	CheckShowMsprListTag->Checked			=	TMPprefStartMsprListTag;

	CheckAntiJagEnabled->Checked	  		=	TMPprefStartAntiJagEnabled;

	if(flattenCommonBGCol	<  0) 	RadioExport16_normal->Checked=true;
	if(flattenCommonBGCol	== 0)   RadioExport16_0->Checked=true;
	if(flattenCommonBGCol	>  0)	RadioExport16_1->Checked=true;
}


void __fastcall TFormPreferences::OKBtnClick(TObject *Sender)
{

	//startup

	prefStartScale2x	=	RadioScale2x->Checked;
	prefStartScale3x	=	RadioScale3x->Checked;
	prefStartScale4x	=	RadioScale4x->Checked;

	prefStartCol0		=	RadioCol0->Checked;
	prefStartCol1		=	RadioCol1->Checked;
	prefStartCol2		=	RadioCol2->Checked;
	prefStartCol3		=	RadioCol3->Checked;

	prefStartSubpal0	=	RadioSubpal0->Checked;
	prefStartSubpal1	=	RadioSubpal1->Checked;
	prefStartSubpal2	=	RadioSubpal2->Checked;
	prefStartSubpal3	=	RadioSubpal3->Checked;

	if(RadioGridHide->Checked) prefStartGridShow=false;
	if(RadioGridShow->Checked) prefStartGridShow=true;

	prefStartGrid1	=	CheckGrid1->Checked;
	prefStartGrid2	=	CheckGrid2->Checked;
	prefStartGrid4	=	CheckGrid4->Checked;
	prefStartGrid8  =	CheckGrid8->Checked;

	prefStartGrid32x30=	CheckGrid32x30->Checked;

	prefStartGridPixelCHR		=	CheckGridPixelCHR->Checked;
	prefStartGridTilesCHR		= CheckGridTilesCHR->Checked;
	prefStartGridMidpointsCHR	= CheckGridMidpointsCHR->Checked;

	prefStartShowCHR	=	CheckShowCHREditor->Checked;
	prefStartShowMM		=	CheckShowMetaspriteManager->Checked;

	prefStartShowBrushes=	CheckShowBrushes->Checked;
	prefStartShowBucket =	CheckShowBucket->Checked;
	prefStartShowLines	=	CheckShowLines->Checked;
	prefStartShowPaste 			=	CheckShowPaste->Checked;

	prefStartShowNavigator 		=	CheckShowNavigator->Checked;
	prefStartShowBankSelector 	=	CheckShowBankSelector->Checked;
	prefStartShowBankSwapper 	=	CheckShowBankSwapper->Checked;
	prefStartShowMetatileEditor =	CheckShowMetatileEditor->Checked;
	prefStartShowColourRose		=	CheckShowColourRose->Checked;


	prefStartMsprListID   	= CheckShowMsprListID->Checked;
	prefStartMsprListLabel  = CheckShowMsprListLabel->Checked;
	prefStartMsprListNTSC   = CheckShowMsprListNTSC->Checked;
	prefStartMsprListPAL    = CheckShowMsprListPAL->Checked;
	prefStartMsprListCount  = CheckShowMsprListCount->Checked;
	prefStartMsprListTag    = CheckShowMsprListTag->Checked;


	prefStartPinCHR				=	CheckPinCHREditor->Checked;
	prefStartPinMM				=	CheckPinMetaspriteManager->Checked;

	prefStartPinBrushes			=	CheckPinBrushes->Checked;
	prefStartPinBucket 			=	CheckPinBucket->Checked;
	prefStartPinLines			=	CheckPinLines->Checked;
	prefStartPinPaste 			=	CheckPinPaste->Checked;

	prefStartPinNavigator 		=	CheckPinNavigator->Checked;
	prefStartPinBankSelector 	=	CheckPinBankSelector->Checked;
	prefStartPinBankSwapper 	=	CheckPinBankSwapper->Checked;
	prefStartPinMetatileEditor  =	CheckPinMetatileEditor->Checked;
	prefStartPinColourRose		=	CheckPinColourRose->Checked;



	prefStartAntiJagEnabled		= CheckAntiJagEnabled->Checked;
	//editor
	FormMain->AutostoreLastUsed->Checked 		= CheckAutostoreLastUsed->Checked;



	FormMain->Applytopen1->Checked		=	CheckBitmaskPen->Checked;
	FormMain->Applytomirror1->Checked	=	CheckBitmaskMirror->Checked;
	FormMain->Applytorotate1->Checked	=	CheckBitmaskRotate->Checked;
	FormMain->Applytonudge1->Checked	=	CheckBitmaskNudge->Checked;
	FormMain->Applytopaste1->Checked	=	CheckBitmaskPaste->Checked;

	FormMain->SafeColours->Checked	=	CheckRules0F->Checked;
	FormMain->SharedBGcol->Checked	=	CheckRulesSharedBG->Checked;

	FormMain->MASCIIneg20h->Checked	=	RadioASCIIneg20->Checked;
	FormMain->MASCIIneg30h->Checked	=	RadioASCIIneg30->Checked;
	FormMain->MASCIIneg40h->Checked	=	RadioASCIIneg40->Checked;

	FormMain->ForceActiveTab1->Checked		=	CheckFindUnusedForce->Checked;
	FormMain->IncludeNametables1->Checked	=	CheckFindUnusedName->Checked;
	FormMain->IncludeMetasprites1->Checked	=	CheckFindUnusedMeta->Checked;

	FormMain->sortonremoval1->Checked		=	CheckRemoveFoundSort->Checked;

	FormMain->IncDecCap1->Checked			=	RadioInkLimitCap->Checked;
	FormMain->IncDecWraparound1->Checked	=	RadioInkLimitWrap->Checked;

	FormMain->IncDecPerclick1->Checked		=	RadioInkBehaviourClick->Checked;
	FormMain->OverDistance1->Checked		=	RadioInkBehaviourDistance->Checked;

	FormMain->IncDecFlow1->Checked		=	RadioInkFlowQuickest->Checked;
	FormMain->IncDecFlow2->Checked		=	RadioInkFlowQuick->Checked;
	FormMain->IncDecFlow3->Checked		=	RadioInkFlowMedium->Checked;
	FormMain->IncDecFlow4->Checked		=	RadioInkFlowSlow->Checked;
	FormMain->IncDecFlow5->Checked		=	RadioInkFlowSlowest->Checked;


	//import
	FormMain->MImportBestOffsets->Checked	=	CheckBMPBestOffsets->Checked;
	FormMain->MImportLossy->Checked			=	CheckBMPLossy->Checked;
	FormMain->MImportThreshold->Checked		=	CheckBMPThres->Checked;
	FormMain->MImportNoColorData->Checked	=	CheckBMPNoColour->Checked;
	BMPimport_use13				=	CheckBMPExpect13->Checked;
	BMPimport_usePalOff			=	CheckBMPLUToffset->Checked;
	BMPimport_palOff			=	UpDownLUToff->Position;
	

	bImportCHRWrap 		= RadioImportCHRWrap->Checked;
	bImportCHRCarry 	= RadioImportCHRCarry->Checked;
	bImportCHRSkip		= RadioImportCHRSkip->Checked;


	//text export
	FormMain->Noterminator1->Checked		=	RadioNoHeader->Checked;
	FormMain->Spritecountheader1->Checked	=	RadioSpriteCount->Checked;
	FormMain->Nflagterminator1->Checked		=	RadioNflag->Checked;
	FormMain->FFterminator1->Checked		=	RadioFFTerminator->Checked;
	FormMain->Single00terminator1->Checked	=	RadioSingle00->Checked;
	FormMain->Double00terminator1->Checked	=	RadioDouble00->Checked;

	FormMain->AskMetaName1->Checked			=	CheckAskSprName->Checked;
	FormMain->AskBankName1->Checked			=	CheckAskBankName->Checked;

	FormMain->byte1->Checked				=	RadioAsmByte->Checked;
	FormMain->db1->Checked					=	RadioAsmDb->Checked;

	FormMain->SignCa65->Checked				=   RadioAsmCaSign->Checked;
	FormMain->SignOther->Checked			=	RadioAsmOtherSign->Checked;

	FormMain->MSaveIncName->Checked			=	CheckIncludeNames->Checked;
	FormMain->MSaveIncAttr->Checked			=	CheckIncludeAttributes->Checked;
	FormMain->MSaveRLE->Checked				=	CheckRLECompress->Checked;

	FormMain->ForAnimationBanks1->Checked 	=   CheckForMsprBanks->Checked;
	FormMain->ForAnimationSingles1->Checked	=   CheckForMsprSingles->Checked;

	bExportPalFilename 						= 	CheckExportPalFilename->Checked;
	bExportPalSet							= 	CheckExportPalSet->Checked;





	FormMain->FormatAnimAsTable1->Checked				= RadioAnimAsTable->Checked;
	FormMain->FormatAnimAsFooter1->Checked 				= RadioAnimAsFooter->Checked;

	FormMain->includeNTSCanimationdata1->Checked		= CheckIncludeNTSC->Checked;
	FormMain->includePALanimationdata1->Checked			= CheckIncludePAL->Checked;

	FormMain->N2bit6bit->Checked				=  Radio6bit->Checked;
	FormMain->N1byte1byte->Checked				= Radio8bit->Checked;
	FormMain->N2bit14bit->Checked 				= Radio14bit->Checked;

	bExportVerticalSystemLUT 			= RadioExportVerticalSystemLUT->Checked;
	bExportHorizontalSystemLUT			= RadioExportHorizontalSystemLUT->Checked;
	bExportDefaultPNG					= RadioExportDefaultPNG->Checked;
	bExportDefaultBMP					= RadioExportDefaultBMP->Checked;
	bExportIncludeNonactiveSupbals		= CheckExportIncludeNonactiveSupbals->Checked;
	bExportIncludeSystemLUT				= CheckExportIncludeSystemLUT->Checked;

	BMPexport_use13				=   CheckExport13Col->Checked;
	BMPexport_use13_mspr 		=   CheckExport13ColSpr->Checked;
	BMPexport_use13_tiles 		=   CheckExport13ColTiles->Checked;
	BMPexport_use13_mt 			=   CheckExport13ColMTiles->Checked;
	BMPexport_use13_subpal		=   CheckExport13ColSubpals->Checked;

	//BMPexport_usePalOff		=   CheckExpBeginLUT->Checked;
	//BMPexport_palOff         =   UpDownLUToff->Position;
	if(RadioExport16_normal->Checked) flattenCommonBGCol=-1;
	if(RadioExport16_0->Checked)	  flattenCommonBGCol=0;
	if(RadioExport16_1->Checked)	  flattenCommonBGCol=1;


	//grids & guides
	bWarnMsprYellow							=	CheckMsprYellow->Checked;
	bWarnMsprOrange 						= 	CheckMsprOrange->Checked;
	bWarnMsprRed							=	CheckMsprRed->Checked;
	bWarnMsprCyan							=   CheckMsprCyan->Checked;


	FormMain->AlwaysCanvas1->Checked		=	RadioMainScrAlways->Checked;
	FormMain->MouseCanvas1->Checked			=	RadioMainScrMouse->Checked;
	FormMain->MouseButtonCanvas1->Checked	=	RadioMainScrMB->Checked;
	FormMain->ButtonCanvas1->Checked		=	RadioMainScrButton->Checked;
	FormMain->NeverCanvas1->Checked			=	RadioMainScrNever->Checked;

	FormMain->AlwaysNavigator1->Checked		=	RadioNavScrAlways->Checked;
	FormMain->MouseNavigator1->Checked		=	RadioNavScrMouse->Checked;
	FormMain->MouseButtonNavigator1->Checked=	RadioNavScrMB->Checked;
	FormMain->ButtonNavigator1->Checked		=	RadioNavScrButton->Checked;
	FormMain->NeverNavigator1->Checked		=	RadioNavScrNever->Checked;

	FormMain->AutoViewDragMode1->Checked	=	CheckAutoshowDrag->Checked;



	//workspace
	FormMain->Sprlistl1->Checked	=	RadioSprlistLeft->Checked;
	FormMain->Sprlistc1->Checked	=	RadioSprlistCenter->Checked;
	FormMain->CHReditortoolbartop->Checked		  =	RadioToolTop->Checked;
	FormMain->CHReditortoolbarbottom->Checked	  =	RadioToolBottom->Checked;

	FormMain->SidebarLeft1->Checked	=	RadioSidebarLeft->Checked;
	FormMain->SidebarRight1->Checked	=	RadioSidebarRight->Checked;


	iGlobalAlpha							=	TrackBarAlpha->Position;

	bSnapToScreen							=	CheckFormToMonitor->Checked;

	if(RadioOpenSave1->Checked) iRadioOpenSave=1;
	if(RadioOpenSave2->Checked) iRadioOpenSave=2;
	if(RadioOpenSave3->Checked)	iRadioOpenSave=3;

	if(RadioFilename->Checked)	iShowFilepath=1;
	if(RadioFilenameFolder->Checked)iShowFilepath=2;
	if(RadioFullPath->Checked)	iShowFilepath=3;


	//------
	FormMain->SaveConfig();
	FormMain->LoadConfig(); //apply
}
//---------------------------------------------------------------------------

void __fastcall TFormPreferences::FormShow(TObject *Sender)
{
	//startup

	if(prefStartScale2x) 	 	TMPprefStartScale = 2;
	else if(prefStartScale3x)	TMPprefStartScale = 3;
	else if(prefStartScale4x)	TMPprefStartScale = 4;
	else						TMPprefStartScale = 2;

	if(prefStartCol0) 	 		TMPprefStartCol = 0;
	else if(prefStartCol1)		TMPprefStartCol = 1;
	else if(prefStartCol2)		TMPprefStartCol = 2;
	else if(prefStartCol3)		TMPprefStartCol = 3;
	else 						TMPprefStartCol = 3;

	if(prefStartSubpal0) 	 	TMPprefStartSubpal = 0;
	else if(prefStartSubpal1)	TMPprefStartSubpal = 1;
	else if(prefStartSubpal2)	TMPprefStartSubpal = 2;
	else if(prefStartSubpal3)	TMPprefStartSubpal = 3;
	else 						TMPprefStartSubpal = 0;

	TMPprefStartGridShow	=	prefStartGridShow;
	TMPprefStartGrid1		=	prefStartGrid1;
	TMPprefStartGrid2		=	prefStartGrid2;
	TMPprefStartGrid4		=	prefStartGrid4;
	TMPprefStartGrid8		=	prefStartGrid8;

	TMPprefStartGrid32x30   =	prefStartGrid32x30;
	TMPprefStartGridPixelCHR=	prefStartGridPixelCHR;

	TMPprefStartShowCHR		=	prefStartShowCHR;
	TMPprefStartShowMM		=	prefStartShowMM;

	TMPprefStartShowBrushes =   prefStartShowBrushes;
	TMPprefStartShowBucket  =   prefStartShowBucket;
	TMPprefStartShowLines   =   prefStartShowLines;
	TMPprefStartShowPaste			=	prefStartShowPaste;

	TMPprefStartShowNavigator		=	prefStartShowNavigator;
	TMPprefStartShowBankSelector	=	prefStartShowBankSelector;
	TMPprefStartShowBankSwapper		=	prefStartShowBankSwapper;
	TMPprefStartShowMetatileEditor	=	prefStartShowMetatileEditor;
	TMPprefStartShowColourRose		=	prefStartShowColourRose;

	TMPprefStartMsprListID=prefStartMsprListID;
	TMPprefStartMsprListLabel=prefStartMsprListLabel;
	TMPprefStartMsprListNTSC=prefStartMsprListNTSC;
	TMPprefStartMsprListPAL=prefStartMsprListPAL;
	TMPprefStartMsprListCount=prefStartMsprListCount;
	TMPprefStartMsprListTag=prefStartMsprListTag;

	TMPprefStartPinCHR		=	prefStartPinCHR;
	TMPprefStartPinMM		=	prefStartPinMM;

	TMPprefStartPinBrushes =   prefStartPinBrushes;
	TMPprefStartPinBucket  =   prefStartPinBucket;
	TMPprefStartPinLines   =   prefStartPinLines;
	TMPprefStartPinPaste			=	prefStartPinPaste;

	TMPprefStartPinNavigator		=	prefStartPinNavigator;
	TMPprefStartPinBankSelector		=	prefStartPinBankSelector;
	TMPprefStartPinBankSwapper		=	prefStartPinBankSwapper;
	TMPprefStartPinMetatileEditor	=	prefStartPinMetatileEditor;
	TMPprefStartPinColourRose		=	prefStartPinColourRose;


	TMPprefStartAntiJagEnabled=prefStartAntiJagEnabled;
	GetStartPreferences();

	//editor

	CheckAutostoreLastUsed->Checked =  FormMain->AutostoreLastUsed->Checked;


	CheckBitmaskPen->Checked		=	FormMain->Applytopen1->Checked;
	CheckBitmaskMirror->Checked		=	FormMain->Applytomirror1->Checked;
	CheckBitmaskRotate->Checked		=	FormMain->Applytorotate1->Checked;
	CheckBitmaskNudge->Checked		=	FormMain->Applytonudge1->Checked;
	CheckBitmaskPaste->Checked		=	FormMain->Applytopaste1->Checked;

	CheckRules0F->Checked			=	FormMain->SafeColours->Checked;
	CheckRulesSharedBG->Checked		=	FormMain->SharedBGcol->Checked;

	RadioASCIIneg20->Checked		=	FormMain->MASCIIneg20h->Checked;
	RadioASCIIneg30->Checked		=	FormMain->MASCIIneg30h->Checked;
	RadioASCIIneg40->Checked		=	FormMain->MASCIIneg40h->Checked;

	CheckFindUnusedForce->Checked	=	FormMain->ForceActiveTab1->Checked;
	CheckFindUnusedName->Checked	=	FormMain->IncludeNametables1->Checked;
	CheckFindUnusedMeta->Checked	=	FormMain->IncludeMetasprites1->Checked;

	CheckRemoveFoundSort->Checked	=	FormMain->sortonremoval1->Checked;

	RadioInkLimitCap->Checked		=	FormMain->IncDecCap1->Checked;
	RadioInkLimitWrap->Checked		=	FormMain->IncDecWraparound1->Checked;

	RadioInkBehaviourClick->Checked	=	FormMain->IncDecPerclick1->Checked;
	RadioInkBehaviourDistance->Checked=	FormMain->OverDistance1->Checked;

	RadioInkFlowQuickest->Checked	=	FormMain->IncDecFlow1->Checked;
	RadioInkFlowQuick->Checked		=	FormMain->IncDecFlow2->Checked;
	RadioInkFlowMedium->Checked		=	FormMain->IncDecFlow3->Checked;
	RadioInkFlowSlow->Checked		=	FormMain->IncDecFlow4->Checked;
	RadioInkFlowSlowest->Checked	=	FormMain->IncDecFlow5->Checked;


	//import
	CheckBMPBestOffsets->Checked	=	FormMain->MImportBestOffsets->Checked;
	CheckBMPLossy->Checked			=	FormMain->MImportLossy->Checked;
	CheckBMPThres->Checked			=	FormMain->MImportThreshold->Checked;
	CheckBMPNoColour->Checked		=	FormMain->MImportNoColorData->Checked;

	CheckBMPExpect13->Checked		=	BMPimport_use13;
	CheckBMPLUToffset->Checked		=	BMPimport_usePalOff;
	UpDownLUToff->Position			=	BMPimport_palOff;

	RadioImportCHRWrap->Checked     = bImportCHRWrap;
	RadioImportCHRCarry->Checked    = bImportCHRCarry;
	RadioImportCHRSkip->Checked     = bImportCHRSkip;



	//text export
	RadioNoHeader->Checked 		=	FormMain->Noterminator1->Checked;
	RadioSpriteCount->Checked	=	FormMain->Spritecountheader1->Checked;
	RadioNflag->Checked			=	FormMain->Nflagterminator1->Checked;
	RadioFFTerminator->Checked	=	FormMain->FFterminator1->Checked;
	RadioSingle00->Checked		=	FormMain->Single00terminator1->Checked;
	RadioDouble00->Checked		=	FormMain->Double00terminator1->Checked;

	CheckAskSprName->Checked	=	FormMain->AskMetaName1->Checked;
	CheckAskBankName->Checked	=	FormMain->AskBankName1->Checked;

	RadioAsmByte->Checked		=   FormMain->byte1->Checked;
	RadioAsmDb->Checked			=	FormMain->db1->Checked;

	RadioAsmCaSign->Checked 	  =   FormMain->SignCa65->Checked;
	RadioAsmOtherSign->Checked	  =   FormMain->SignOther->Checked;


	CheckIncludeNames->Checked			=	FormMain->MSaveIncName->Checked;
	CheckIncludeAttributes->Checked		=	FormMain->MSaveIncAttr->Checked;
	CheckRLECompress->Checked		   	=	FormMain->MSaveRLE->Checked;



	CheckExportPalFilename->Checked	= bExportPalFilename;
	CheckExportPalSet->Checked		= bExportPalSet;

	RadioAnimAsTable->Checked				= FormMain->FormatAnimAsTable1->Checked;
	RadioAnimAsFooter->Checked				= FormMain->FormatAnimAsFooter1->Checked;

	CheckIncludeNTSC->Checked			= FormMain->includeNTSCanimationdata1->Checked;
	CheckIncludePAL->Checked			= FormMain->includePALanimationdata1->Checked;
	CheckForMsprBanks->Checked          = FormMain->ForAnimationBanks1->Checked;
	CheckForMsprSingles->Checked        = FormMain->ForAnimationSingles1->Checked;

	Radio6bit->Checked					= FormMain->N2bit6bit->Checked;
	Radio8bit->Checked					= FormMain->N1byte1byte->Checked;
	Radio14bit->Checked					= FormMain->N2bit14bit->Checked;

	//export
	RadioExportVerticalSystemLUT->Checked			=  bExportVerticalSystemLUT;
	RadioExportHorizontalSystemLUT->Checked			=  bExportHorizontalSystemLUT;
	RadioExportDefaultPNG->Checked					=  bExportDefaultPNG;
	RadioExportDefaultBMP->Checked					=  bExportDefaultBMP;
	CheckExportIncludeNonactiveSupbals->Checked		=  bExportIncludeNonactiveSupbals;
	CheckExportIncludeSystemLUT->Checked				=  bExportIncludeSystemLUT;

	CheckExport13Col->Checked			=	BMPexport_use13;
	CheckExport13ColSpr->Checked		=	BMPexport_use13_mspr;
	CheckExport13ColTiles->Checked		=	BMPexport_use13_tiles;
	CheckExport13ColMTiles->Checked	 	=	BMPexport_use13_mt;
	CheckExport13ColSubpals->Checked	=	BMPexport_use13_subpal;
	//CheckExpBeginLUT->Checked		=	BMPexport_usePalOff;
	//UpDownLUToff->Position			=	BMPexport_palOff;

	//grids & guides
	CheckMsprYellow->Checked			= bWarnMsprYellow;
	CheckMsprOrange->Checked            = bWarnMsprOrange;
	CheckMsprRed->Checked               = bWarnMsprRed;
	CheckMsprCyan->Checked				= bWarnMsprCyan;

	RadioMainScrAlways->Checked          = FormMain->AlwaysCanvas1->Checked;
	RadioMainScrMouse->Checked           = FormMain->MouseCanvas1->Checked;
	RadioMainScrMB->Checked              = FormMain->MouseButtonCanvas1->Checked;
	RadioMainScrButton->Checked          = FormMain->ButtonCanvas1->Checked;
	RadioMainScrNever->Checked           = FormMain->NeverCanvas1->Checked;

	RadioNavScrAlways->Checked         = FormMain->AlwaysNavigator1->Checked;
	RadioNavScrMouse->Checked          = FormMain->MouseNavigator1->Checked;
	RadioNavScrMB->Checked             = FormMain->MouseButtonNavigator1->Checked;
	RadioNavScrButton->Checked         = FormMain->ButtonNavigator1->Checked;
	RadioNavScrNever->Checked          = FormMain->NeverNavigator1->Checked;

	CheckAutoshowDrag->Checked			= FormMain->AutoViewDragMode1->Checked;

	//Workspace
	RadioSprlistLeft->Checked		=	FormMain->Sprlistl1->Checked;
	RadioSprlistCenter->Checked		=	FormMain->Sprlistc1->Checked;
	RadioToolTop->Checked			=	FormMain->CHReditortoolbartop->Checked;
	RadioToolBottom->Checked		=	FormMain->CHReditortoolbarbottom->Checked;
	RadioSidebarLeft->Checked		=   FormMain->SidebarLeft1->Checked;
	RadioSidebarRight->Checked		=	FormMain->SidebarRight1->Checked;

	TrackBarAlpha->Position			= iGlobalAlpha;
	CheckFormToMonitor->Checked		= bSnapToScreen;

	RadioOpenSave1->Checked		  	= iRadioOpenSave<=1?true:false;
	RadioOpenSave2->Checked         = iRadioOpenSave==2?true:false;
	RadioOpenSave3->Checked         = iRadioOpenSave>=3?true:false;

	RadioFilename->Checked			= iShowFilepath=1?true:false;
	RadioFilenameFolder->Checked		= iShowFilepath=2?true:false;
	RadioFullPath->Checked			= iShowFilepath=3?true:false;

}
//---------------------------------------------------------------------------

void __fastcall TFormPreferences::HelpBtnClick(TObject *Sender)
{
	TMPprefStartScale=2;
	TMPprefStartCol=3;
	TMPprefStartSubpal=0;

	TMPprefStartGridShow=false;
	TMPprefStartGrid1=false;
	TMPprefStartGrid2=true;
	TMPprefStartGrid4=false;
	TMPprefStartGrid8=false;
	TMPprefStartGrid32x30=false;
	TMPprefStartGridPixelCHR=true;
	TMPprefStartGridTilesCHR=true;
	TMPprefStartGridMidpointsCHR=true;

	TMPprefStartShowCHR=false;
	TMPprefStartShowMM=false;

	TMPprefStartShowPaste			=false;

	TMPprefStartShowNavigator		=false;
	TMPprefStartShowBankSelector	=false;
	TMPprefStartShowBankSwapper		=false;
	TMPprefStartShowMetatileEditor	=false;
	TMPprefStartShowColourRose		=false;

	TMPprefStartAntiJagEnabled=true;

	TMPprefStartPinCHR=true;
	TMPprefStartPinMM=true;

	TMPprefStartPinBrushes=true;
	TMPprefStartPinBucket=true;
	TMPprefStartPinLines=true;
	TMPprefStartPinPaste=true;

	TMPprefStartPinNavigator=false;
	TMPprefStartPinBankSelector=false;
	TMPprefStartPinBankSwapper=false;
	TMPprefStartPinMetatileEditor=false;
	TMPprefStartPinColourRose=false;




	GetStartPreferences();

	//editor
	CheckAutostoreLastUsed->Checked	=	false;



	CheckBitmaskPen->Checked		=	true;
	CheckBitmaskMirror->Checked		=	true;
	CheckBitmaskRotate->Checked		=	true;
	CheckBitmaskNudge->Checked		=	true;
	CheckBitmaskPaste->Checked		=	true;

	CheckRules0F->Checked			=	true;
	CheckRulesSharedBG->Checked		=	true;

	RadioASCIIneg20->Checked		=	true;
	RadioASCIIneg30->Checked		=	false;
	RadioASCIIneg40->Checked		=	false;

	CheckFindUnusedForce->Checked	=	false;
	CheckFindUnusedName->Checked	=	true;
	CheckFindUnusedMeta->Checked	=	true;

	CheckRemoveFoundSort->Checked	=	false;

	RadioInkLimitCap->Checked		=	true;
	RadioInkLimitWrap->Checked		=	false;

	RadioInkBehaviourClick->Checked	=	true;
	RadioInkBehaviourDistance->Checked=	false;

	RadioInkFlowQuickest->Checked	=	false;
	RadioInkFlowQuick->Checked		=	false;
	RadioInkFlowMedium->Checked		=	false;
	RadioInkFlowSlow->Checked		=	true;
	RadioInkFlowSlowest->Checked	=	false;


	//import
	CheckBMPBestOffsets->Checked	=	false;
	CheckBMPLossy->Checked			=	false;
	CheckBMPThres->Checked			=	false;
	CheckBMPNoColour->Checked		=	false;
    CheckBMPExpect13->Checked		=	false;

	RadioImportCHRWrap->Checked     = true;
	RadioImportCHRCarry->Checked    = false;
	RadioImportCHRSkip->Checked     = false;


	//text export
	RadioNoHeader->Checked 		=	false;
	RadioSpriteCount->Checked	=	false;
	RadioNflag->Checked			=	true;
	RadioFFTerminator->Checked	=	false;
	RadioSingle00->Checked		=	false;
	RadioDouble00->Checked		=	false;

	CheckExportPalFilename->Checked = true;
	CheckExportPalSet->Checked	= true;

	CheckAskSprName->Checked	=	false;
	CheckAskBankName->Checked	=	true;

	RadioAsmByte->Checked		=   true;
	RadioAsmDb->Checked			=	false;

	RadioAsmCaSign->Checked		=	true;
	RadioAsmOtherSign->Checked	=	false;

	CheckIncludeNames->Checked			=	true;
	CheckIncludeAttributes->Checked		=	true;
	CheckRLECompress->Checked	   		=	false;

	CheckForMsprBanks->Checked  					= true;
	CheckForMsprSingles->Checked                 = false;

	RadioAnimAsTable->Checked				= true;
	CheckIncludeNTSC->Checked			= true;
	CheckIncludePAL->Checked			= false;

	Radio6bit->Checked					= true;
	Radio8bit->Checked					= false;
	Radio14bit->Checked					= false;

    //img export
	RadioExportVerticalSystemLUT->Checked 		= true;
	RadioExportDefaultPNG->Checked 				= true;

	CheckExportIncludeNonactiveSupbals->Checked = false;
	CheckExportIncludeSystemLUT->Checked 		= true;
	CheckExport13Col->Checked			=	false;
	CheckExport13ColSpr->Checked		=	false;
	CheckExport13ColTiles->Checked		=	false;
	CheckExport13ColMTiles->Checked		= 	false;
    CheckExport13ColSubpals->Checked	=   false;
	//CheckExpBeginLUT->Checked		=	false;
	//UpDownLUToff->Position			=	1;
	flattenCommonBGCol=-1;
	RadioExport16_normal->Checked = true;

	//grids & guidelines
	CheckMsprYellow->Checked			= true;
	CheckMsprOrange->Checked            = false;
	CheckMsprRed->Checked               = true;
	CheckMsprCyan->Checked				= false;

	RadioNavScrAlways->Checked          = false;
	RadioNavScrMouse->Checked           = false;
	RadioNavScrMB->Checked              = true;
	RadioNavScrButton->Checked          = false;
	RadioNavScrNever->Checked           = false;

	RadioMainScrAlways->Checked         = false;
	RadioMainScrMouse->Checked          = false;
	RadioMainScrMB->Checked             = false;
	RadioMainScrButton->Checked         = true;
	RadioMainScrNever->Checked          = false;

	CheckAutoshowDrag->Checked			= true;


	//Workspace
	RadioSprlistLeft->Checked		=	true;
	RadioSprlistCenter->Checked		=	false;

	RadioToolTop->Checked			=	false;
	RadioToolBottom->Checked		=	true;

	RadioSidebarLeft->Checked		=   false;
	RadioSidebarRight->Checked		=	true;

	TrackBarAlpha->Position		= FAC_ALPHA;

	CheckFormToMonitor->Checked	= false;

	RadioOpenSave1->Checked		  		= true;
	RadioOpenSave2->Checked             = false;
	RadioOpenSave3->Checked             = false;

}
//---------------------------------------------------------------------------




