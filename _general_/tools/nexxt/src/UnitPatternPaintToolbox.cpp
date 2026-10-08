//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "UnitPatternPaintToolbox.h"
#include "UnitMain.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormPatternPaint *FormPatternPaint;
//---------------------------------------------------------------------------
__fastcall TFormPatternPaint::TFormPatternPaint(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TFormPatternPaint::btn0MouseEnter(TObject *Sender)
{
	FormMain->LabelStats->Caption="Toggles whether colour 0 from the source pattern is used or ignored.";
}
//---------------------------------------------------------------------------

void __fastcall TFormPatternPaint::btn1MouseEnter(TObject *Sender)
{
	FormMain->LabelStats->Caption="Toggles whether colour 1 from the source pattern is used or ignored.";
}
//---------------------------------------------------------------------------

void __fastcall TFormPatternPaint::btn2MouseEnter(TObject *Sender)
{
	FormMain->LabelStats->Caption="Toggles whether colour 2 from the source pattern is used or ignored.";
}
//---------------------------------------------------------------------------

void __fastcall TFormPatternPaint::btn3MouseEnter(TObject *Sender)
{
	FormMain->LabelStats->Caption="Toggles whether colour 3 from the source pattern is used or ignored.";
}
//---------------------------------------------------------------------------

void __fastcall TFormPatternPaint::btnMaskModeMouseEnter(TObject *Sender)
{
   FormMain->LabelStats->Caption="In mask mode, the pattern acts as a mask for your normal pen colour.\nTo make use of this mode, at least 1 colour button should be toggled OFF.";
}
//---------------------------------------------------------------------------

void __fastcall TFormPatternPaint::btnPenMouseEnter(TObject *Sender)
{
   FormMain->LabelStats->Caption="Toggles whether Pattern Paint applies to Pen when on.";
}
//---------------------------------------------------------------------------

void __fastcall TFormPatternPaint::btnBrushMouseEnter(TObject *Sender)
{
   FormMain->LabelStats->Caption="Toggles whether Pattern Paint applies to Brush [B] when on.";
}
//---------------------------------------------------------------------------

void __fastcall TFormPatternPaint::btnBucketMouseEnter(TObject *Sender)
{
  FormMain->LabelStats->Caption="Toggles whether Pattern Paint applies to Bucket [Ctrl] when on.";
}
//---------------------------------------------------------------------------

void __fastcall TFormPatternPaint::btnLineMouseEnter(TObject *Sender)
{
  FormMain->LabelStats->Caption="Toggles whether Pattern Paint applies to Line [N] or [Alt] when on.";
}
//---------------------------------------------------------------------------

