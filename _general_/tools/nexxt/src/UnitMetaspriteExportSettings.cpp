//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "UnitMetaspriteExportSettings.h"
#include "UnitMain.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormMetaspriteExportSettings *FormMetaspriteExportSettings;

extern unsigned int OAMtextOrder[4];
extern int OAMtextWarnLoX;
extern int OAMtextWarnLoY;
extern int OAMtextWarnHiX;
extern int OAMtextWarnHiY;
extern int OAMtextOffsetX;
extern int OAMtextOffsetY;

extern bool bOAMtextEnableOffset;
extern bool bOAMtextEnableCustomOrder;
extern bool bOAMtextEnableWarning;
extern bool bOAMtextJustWarning;

unsigned int iYXTAbtnID=0;
//---------------------------------------------------------------------------
__fastcall TFormMetaspriteExportSettings::TFormMetaspriteExportSettings(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::BtnThisSessionClick(
      TObject *Sender)
{
	UpDownOffsetX->Position=0;
	UpDownOffsetY->Position=0;
	OAMtextOffsetX	=UpDownOffsetX->Position;
	OAMtextOffsetY	=UpDownOffsetY->Position;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::Btn32x30Click(
	  TObject *Sender)
{
   UpDownOffsetX->Position=64;
   UpDownOffsetY->Position=64;
   OAMtextOffsetX	=UpDownOffsetX->Position;
   OAMtextOffsetY	=UpDownOffsetY->Position;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::SpeedButton1Click(
	  TObject *Sender)
{
	UpDownOffsetX->Position=128;
	UpDownOffsetY->Position=128;
	OAMtextOffsetX	=UpDownOffsetX->Position;
	OAMtextOffsetY	=UpDownOffsetY->Position;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::SpeedButton19Click(
      TObject *Sender)
{
	UpDownWarnLoX->Position=-64;
	UpDownWarnLoY->Position=-64;
	UpDownWarnHiX->Position=63;
	UpDownWarnHiY->Position=63;
	OAMtextWarnLoX	=UpDownWarnLoX->Position;
	OAMtextWarnLoY	=UpDownWarnLoY->Position;
	OAMtextWarnHiX	=UpDownWarnHiX->Position;
	OAMtextWarnHiY	=UpDownWarnHiY->Position;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::SpeedButton20Click(
	  TObject *Sender)
{
	UpDownWarnLoX->Position=-127;
	UpDownWarnLoY->Position=-127;
	UpDownWarnHiX->Position=127;
	UpDownWarnHiY->Position=127;
	OAMtextWarnLoX	=UpDownWarnLoX->Position;
	OAMtextWarnLoY	=UpDownWarnLoY->Position;
	OAMtextWarnHiX	=UpDownWarnHiX->Position;
	OAMtextWarnHiY	=UpDownWarnHiY->Position;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::SpeedButton21Click(
	  TObject *Sender)
{
	UpDownWarnLoX->Position=-128;
	UpDownWarnLoY->Position=-128;
	UpDownWarnHiX->Position=127;
	UpDownWarnHiY->Position=127;
	OAMtextWarnLoX	=UpDownWarnLoX->Position;
	OAMtextWarnLoY	=UpDownWarnLoY->Position;
	OAMtextWarnHiX	=UpDownWarnHiX->Position;
	OAMtextWarnHiY	=UpDownWarnHiY->Position;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::SpeedButton22Click(
	  TObject *Sender)
{
	UpDownWarnLoX->Position=0;
	UpDownWarnLoY->Position=0;
	UpDownWarnHiX->Position=254;
	UpDownWarnHiY->Position=254;
	OAMtextWarnLoX	=UpDownWarnLoX->Position;
	OAMtextWarnLoY	=UpDownWarnLoY->Position;
	OAMtextWarnHiX	=UpDownWarnHiX->Position;
	OAMtextWarnHiY	=UpDownWarnHiY->Position;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::SpeedButton23Click(
	  TObject *Sender)
{
	UpDownWarnLoX->Position=0;
	UpDownWarnLoY->Position=0;
	UpDownWarnHiX->Position=255;
	UpDownWarnHiY->Position=255;
	OAMtextWarnLoX	=UpDownWarnLoX->Position;
	OAMtextWarnLoY	=UpDownWarnLoY->Position;
	OAMtextWarnHiX	=UpDownWarnHiX->Position;
	OAMtextWarnHiY	=UpDownWarnHiY->Position;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::UpdateUI(void)
{

	//extern unsigned int OAMtextOrder[4];
	UpDownWarnLoX->Position	=OAMtextWarnLoX;
	UpDownWarnLoY->Position	=OAMtextWarnLoY;
	UpDownWarnHiX->Position	=OAMtextWarnHiX;
	UpDownWarnHiY->Position	=OAMtextWarnHiY;

	UpDownOffsetX->Position	=OAMtextOffsetX;
	UpDownOffsetY->Position	=OAMtextOffsetY;

	CheckOffset->Checked	=bOAMtextEnableOffset;
	CheckOffset->Checked	=bOAMtextEnableCustomOrder;
	CheckWarn->Checked		=bOAMtextEnableWarning;
	CheckJustWarn->Checked	=bOAMtextJustWarning;
    UpdateOrderButtons();

}

void __fastcall TFormMetaspriteExportSettings::UpdateVars(void)
{

	//extern unsigned int OAMtextOrder[4];
	OAMtextWarnLoX	=UpDownWarnLoX->Position;
	OAMtextWarnLoY	=UpDownWarnLoY->Position;
	OAMtextWarnHiX	=UpDownWarnHiX->Position;
	OAMtextWarnHiY	=UpDownWarnHiY->Position;

	OAMtextOffsetX	=UpDownOffsetX->Position;
	OAMtextOffsetY	=UpDownOffsetY->Position;

	bOAMtextEnableOffset		=CheckOffset->Checked;
	bOAMtextEnableCustomOrder	=CheckCustomOrder->Checked;
	bOAMtextEnableWarning		=CheckWarn->Checked;
	bOAMtextJustWarning			=CheckJustWarn->Checked;


}
void __fastcall TFormMetaspriteExportSettings::FormShow(TObject *Sender)
{
	UpdateUI();	
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::FormClose(TObject *Sender,
      TCloseAction &Action)
{
	UpdateVars();
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::FormDeactivate(
      TObject *Sender)
{
	UpdateVars();
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::BtnNegateXClick(
      TObject *Sender)
{

	 OAMtextOffsetX				=  UpDownOffsetX->Position;
	 OAMtextOffsetX				= -OAMtextOffsetX;
	 UpDownOffsetX->Position	=  OAMtextOffsetX;


}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::BtnNegateYClick(
      TObject *Sender)
{
	 OAMtextOffsetY				=  UpDownOffsetY->Position;
	 OAMtextOffsetY				= -OAMtextOffsetY;
	 UpDownOffsetY->Position	=  OAMtextOffsetY;
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::SpeedButton12Click(
	  TObject *Sender)
{
	OAMtextOrder[0]=0; //x
	OAMtextOrder[1]=1; //y
	OAMtextOrder[2]=2; //tile id
	OAMtextOrder[3]=3; //attribute
	UpdateOrderButtons();
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::UpdateOrderButtons(void)
{
	AnsiString str[4]={"X","Y","ID","Attr"};
	btnOAM0->Caption=str[OAMtextOrder[0]];
	btnOAM1->Caption=str[OAMtextOrder[1]];
	btnOAM2->Caption=str[OAMtextOrder[2]];
	btnOAM3->Caption=str[OAMtextOrder[3]];
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::SpeedButton13Click(
	  TObject *Sender)
{
	OAMtextOrder[0]=1; //y
	OAMtextOrder[1]=2; //tile
	OAMtextOrder[2]=3; //attr
	OAMtextOrder[3]=0; //x
	UpdateOrderButtons();
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::SpeedButton16Click(
      TObject *Sender)
{
	OAMtextOrder[0]=1; //y
	OAMtextOrder[1]=0; //x
	OAMtextOrder[2]=2; //tile id
	OAMtextOrder[3]=3; //attribute
	UpdateOrderButtons();
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::EditOffsetXExit(
      TObject *Sender)
{
	int n;

	if(!TryStrToInt(EditOffsetX->Text,n)) n=0;
	if(n<UpDownOffsetX->Min) n=UpDownOffsetX->Min;

	if(n>UpDownOffsetX->Max) n=n>UpDownOffsetX->Max;

	UpDownOffsetX->Position=n;
	OAMtextOffsetX = n;
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::EditOffsetYExit(
      TObject *Sender)
{
     int n;

	if(!TryStrToInt(EditOffsetY->Text,n)) n=0;
	if(n<UpDownOffsetY->Min) n=UpDownOffsetY->Min;

	if(n>UpDownOffsetY->Max) n=n>UpDownOffsetY->Max;

	UpDownOffsetY->Position=n;
	OAMtextOffsetY = n;
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::EditWarnLoXExit(
      TObject *Sender)
{
	int n;

	if(!TryStrToInt(EditWarnLoX->Text,n)) n=0;
	if(n<UpDownWarnLoX->Min) n=UpDownWarnLoX->Min;

	if(n>UpDownWarnLoX->Max) n=n>UpDownWarnLoX->Max;

	UpDownWarnLoX->Position=n;
	OAMtextWarnLoX = n;
}
//---------------------------------------------------------------------------


void __fastcall TFormMetaspriteExportSettings::EditWarnHiXExit(
      TObject *Sender)
{
    int n;

	if(!TryStrToInt(EditWarnHiX->Text,n)) n=0;
	if(n<UpDownWarnHiX->Min) n=UpDownWarnHiX->Min;

	if(n>UpDownWarnHiX->Max) n=n>UpDownWarnHiX->Max;

	UpDownWarnHiX->Position=n;
	OAMtextWarnHiX = n;
}
//---------------------------------------------------------------------------


void __fastcall TFormMetaspriteExportSettings::EditWarnLoYExit(
      TObject *Sender)
{
	 int n;

	if(!TryStrToInt(EditWarnLoY->Text,n)) n=0;
	if(n<UpDownWarnLoY->Min) n=UpDownWarnLoY->Min;

	if(n>UpDownWarnLoY->Max) n=n>UpDownWarnLoY->Max;

	UpDownWarnLoY->Position=n;
	OAMtextWarnLoY = n;
}
//---------------------------------------------------------------------------


void __fastcall TFormMetaspriteExportSettings::EditWarnHiYExit(
      TObject *Sender)
{
     int n;

	if(!TryStrToInt(EditWarnHiY->Text,n)) n=0;
	if(n<UpDownWarnHiY->Min) n=UpDownWarnHiY->Min;

	if(n>UpDownWarnHiY->Max) n=n>UpDownWarnHiY->Max;

	UpDownWarnHiY->Position=n;
	OAMtextWarnHiY = n;
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::EditOffsetXKeyPress(
      TObject *Sender, char &Key)
{
	//allow sign on first character
	if(Key == '-')
	{
		int pos = ((TEdit*)Sender)->SelStart;

		if(pos == 0 && ((TEdit*)Sender)->Text.Pos("-") == 0) return;

		Key = 0;
		return;
	}
	//the usual filter
	else if(!((Key>='0'&&Key<='9')||Key==VK_BACK||Key==VK_DELETE)) Key = 0;
}
//---------------------------------------------------------------------------
void __fastcall TFormMetaspriteExportSettings::EditOffsetXClick(
      TObject *Sender)
{
	((TEdit*)Sender)->SelectAll();
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::CheckOffsetClick(
      TObject *Sender)
{
	UpdateVars();
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::btnOAM0Click(
      TObject *Sender)
{
	iYXTAbtnID=((TSpeedButton*)Sender)->Tag;

	for (int i = 0; i < PopupMenu1->Items->Count; i++) {
		TMenuItem *item = PopupMenu1->Items->Items[i];
		if (item->Tag == (signed)OAMtextOrder[iYXTAbtnID]) {
			item->Checked = true;
			break;
		}
	}
	TPoint p = Mouse->CursorPos;
		int x= p.x;
		int y= p.y;
	PopupMenu1->Popup(x,y);
}
//---------------------------------------------------------------------------

void __fastcall TFormMetaspriteExportSettings::X1Click(TObject *Sender)
{
	int tag =  ((TMenuItem*)Sender)->Tag;
	OAMtextOrder[iYXTAbtnID]=tag;
	UpdateOrderButtons();
}
//---------------------------------------------------------------------------

