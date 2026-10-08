//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "UnitWarnNESlibRLE.h"
#include "UnitMain.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormWarnNESlibRLE *FormWarnNESlibRLE;
//---------------------------------------------------------------------------
__fastcall TFormWarnNESlibRLE::TFormWarnNESlibRLE(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TFormWarnNESlibRLE::FormCreate(TObject *Sender)
{
StaticText1->Caption = AnsiString("This asset is using all 256 tile ID:s.")
	+ "\n\nThe original NESlib decoder can only use up to 255 tiles correctly."
	+ "\n\nA replacement decoder is provided in NEXXT's 'NES programming resources' "
	+ "folder; able to handle all 256 tiles."
	+ "\n\nOld NESlib RLE files are forwards compatible with this decoder."
	+ "\nNew RLE files are backwards compatible so long as they are using 255 or under."

	;
}
//---------------------------------------------------------------------------
void __fastcall TFormWarnNESlibRLE::FormClose(TObject *Sender,
      TCloseAction &Action)
{
	FormMain->CreateReminderConfig();
}
//---------------------------------------------------------------------------
void __fastcall TFormWarnNESlibRLE::FormShow(TObject *Sender)
{
	FormMain->LoadReminderConfig();	
}
//---------------------------------------------------------------------------
