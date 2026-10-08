//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "UnitAccessibilityTestFilters.h"
#include "UnitMain.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormAccessibility *FormAccessibility;
extern int iAccessibility_ctmi;
extern void palette_calc(bool);
//---------------------------------------------------------------------------
__fastcall TFormAccessibility::TFormAccessibility(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TFormAccessibility::SpeedButton1Click(TObject *Sender)
{
	if(SpeedButton1->Down) iAccessibility_ctmi= 2;
	else  iAccessibility_ctmi= 0;
	palette_calc(false);
	FormMain->UpdateAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormAccessibility::SpeedButton2Click(TObject *Sender)
{
   if(SpeedButton2->Down) iAccessibility_ctmi= 1;
	else  iAccessibility_ctmi= 0;
	palette_calc(false);
	FormMain->UpdateAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormAccessibility::SpeedButton3Click(TObject *Sender)
{
	if(SpeedButton3->Down) iAccessibility_ctmi= 4;
	else  iAccessibility_ctmi= 0;
	palette_calc(false);
	FormMain->UpdateAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormAccessibility::SpeedButton4Click(TObject *Sender)
{
	if(SpeedButton4->Down) iAccessibility_ctmi= 3;
	else  iAccessibility_ctmi= 0;
	palette_calc(false);
	FormMain->UpdateAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormAccessibility::SpeedButton5Click(TObject *Sender)
{
	if(SpeedButton5->Down) iAccessibility_ctmi= 5;
	else  iAccessibility_ctmi= 0;
	palette_calc(false);
	FormMain->UpdateAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormAccessibility::SpeedButton6Click(TObject *Sender)
{
	if(SpeedButton6->Down) iAccessibility_ctmi= 6;
	else  iAccessibility_ctmi= 0;
	palette_calc(false);
	FormMain->UpdateAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormAccessibility::SpeedButton7Click(TObject *Sender)
{
	if(SpeedButton7->Down) iAccessibility_ctmi= 7;
	else  iAccessibility_ctmi= 0;
	palette_calc(false);
	FormMain->UpdateAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormAccessibility::SpeedButton1MouseEnter(TObject *Sender)
{
		FormMain->LabelStats->Caption="Filters designed to help find contrasting issues and distractive elements related to colour perception.\nNote that they aren't accurate in their portrayal of colourblindess,\nbut are rather there to give indication of potential accessibility issues.";	
}
//---------------------------------------------------------------------------
