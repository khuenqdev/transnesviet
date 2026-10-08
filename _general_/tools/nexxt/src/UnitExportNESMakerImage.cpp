//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "UnitExportNESMakerImage.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormExportNESMakerImage *FormExportNESMakerImage;
extern bool chrSelectRect;
//---------------------------------------------------------------------------
__fastcall TFormExportNESMakerImage::TFormExportNESMakerImage(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TFormExportNESMakerImage::FormShow(TObject *Sender)
{
	if(!chrSelectRect){
        RadioUpper->Checked=true;
		RadioSelection->Enabled=false;
	}
}
//---------------------------------------------------------------------------
