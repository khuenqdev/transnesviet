//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "UnitSelectByUsage.h"
#include "UnitMain.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormSelectByUsage *FormSelectByUsage;

extern int chrSelected[256];
extern int tileActive;
//---------------------------------------------------------------------------
__fastcall TFormSelectByUsage::TFormSelectByUsage(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TFormSelectByUsage::TrackBar1Change(TObject *Sender)
{
	int thres=TrackBar1->Position;
	Label2->Caption=IntToStr(thres);
	bool bContents = CheckBox1->Checked;
	FormMain->FindDoublesUnused(true,bContents,thres);

}
//---------------------------------------------------------------------------
void __fastcall TFormSelectByUsage::SpeedButton1Click(TObject *Sender)
{
	for(int i=0;i<256;++i) chrSelected[i]=0;
	FormMain->SelectTile(tileActive);
	FormMain->UpdateAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormSelectByUsage::FormCreate(TObject *Sender)
{
	int thres=TrackBar1->Position;
	Label2->Caption=IntToStr(thres);
		
}
//---------------------------------------------------------------------------
void __fastcall TFormSelectByUsage::FormShow(TObject *Sender)
{
	int thres=TrackBar1->Position;
	Label2->Caption=IntToStr(thres);
		
}
//---------------------------------------------------------------------------
