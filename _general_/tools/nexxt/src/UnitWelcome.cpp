//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop

#include "UnitWelcome.h"
#include "UnitMain.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormWelcome *FormWelcome;
//---------------------------------------------------------------------------
__fastcall TFormWelcome::TFormWelcome(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
void __fastcall TFormWelcome::Button1Click(TObject *Sender)
{
	ShellExecute(NULL, "open", "https://ko-fi.com/frankengraphics", "", NULL, SW_RESTORE);
	
}
//---------------------------------------------------------------------------
void __fastcall TFormWelcome::Button2Click(TObject *Sender)
{
	ShellExecute(NULL, "open", "https://www.patreon.com/frankengraphics", "", NULL, SW_RESTORE);	
}
//---------------------------------------------------------------------------
void __fastcall TFormWelcome::FormCreate(TObject *Sender)
{
	StaticText2->Caption = AnsiString("")
	+ "2.8.0:"
	+ "\n- New feature: Metasprites can explicitly reference the 4 tilset views, per frame."
	+ "\n-Bugfix: duration insertion behaviour when inserting/duplicating a metasprite frame fixed."
	+ "\n"

	+ "\n 2.7.7:"


	+ "\n- New minor feature: Highlight used colours in ALL subpalettes on system palette (shift+ctrl-hover)"
	+ "\n"
	+ "\n- New minor feature: 'Open Session' now also accepts all kinds of other assets,"
	+ "reducing unnecessary warning messages. Various file extensions have been added to the session open dialog."
	+ "\n"
	+ "\n-Bugfix: 'highlight used colours' now behaves more predictably/intuitively."
	+ "\n"
	;

	StaticText3->Caption = AnsiString("")
	+ "- Preparations for the big next (v4.x) development cycle"
	+ "\n- 3.x is coming to an end. Maintenance updates and small features that don't interfere with 4.x groundwork may happen before the 4.x stretch is ready to launch."
	;

	StaticText1->Caption = AnsiString("Thanks for using NEXXT! It's free && open source.")
	+ "\nHowever, it takes lots of time to develop,"
	+ " so it takes time off my job schedule to keep it improving."
	+ "\n\nIf possible, consider donating on ko-fi or subscribing to my patreon to help."
	+ " Thanks!  /FrankenGraphics"
	;

	StaticText4->Caption = AnsiString("")
	;
}
//---------------------------------------------------------------------------


void __fastcall TFormWelcome::FormClose(TObject *Sender,
      TCloseAction &Action)
{
	FormMain->CreateWelcomeConfig();
}
//---------------------------------------------------------------------------

void __fastcall TFormWelcome::Button3Click(TObject *Sender)
{
	FormWelcome->Close();	
}
//---------------------------------------------------------------------------

