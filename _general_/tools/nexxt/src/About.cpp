//---------------------------------------------------------------------
#include <vcl.h>
#pragma hdrstop

#include "About.h"
#include "UnitMain.h"
//--------------------------------------------------------------------- 
#pragma resource "*.dfm"
TAboutBox *AboutBox;
//--------------------------------------------------------------------- 
__fastcall TAboutBox::TAboutBox(TComponent* AOwner)
	: TForm(AOwner)
{
}
//---------------------------------------------------------------------
void __fastcall TAboutBox::FormShow(TObject *Sender)
{
	ProductName->Caption=Application->Title;
	StaticText1->Caption=(AnsiString)
	"Build date: September 17th, 2026.\n\nDeveloped by FrankenGraphics."
	+"\nBased on NESST; developed by Shiru."
	+"\n\nThis software is Public Domain, excluding FreeImage library whose licence is included in the source."
	+"\n\nThanks to contributors Antoine Gohin (Broke Studio), jroweboy,\nand the NESdev community."
	+"\n\nSpecial thanks to Shiru, and to my patreon supporters,"
	+" for without this work would not have come this far: "

	+"\n\n Amina, Antoni Aloy Torrens, an insignifant speck of dust, André Luís Baptista da Silva, "
	+"Ben Smith, BIG EVIL CORPORATION, Broke Studio, "
	+"Colin Kingfisher, Colin Reed, Cornel, "
	+"Deadeye, Howie Day, "
	+"Eric DeSantis, Frank Provo, "
	+"Jacob Speicher, JayBee, Jo, Joe's Computer Museum, "
	+"Johanna, Jone, Justin Orenich, Kacper Woźniak, Kalle Siukola, "
	+"Marc Moore, Margaret McNulty-Beldyk, "
	+"Matthew Klundt, Matt Roszak, Martin Donlon, Max Meiners, Maxim Sergeevich, "
	+"Michael Thompson, michael_emh, "
	+"Nicholas Berthiaume, NovaSquirrel, "
	+"Pete Spicer, "

	+"Raftronaut, Ratttz, ReJ aka Renaldas Zioma, RetroNES Software, RT, Rusty Gerard, "

	+"Sarah Lynne, Sean Robinson, "
	+"Stupidcidal, W-, zeta0134, zzox."
	;
	StaticText1->Width=300;
	StaticText1->Height=470;
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::OKButtonClick(TObject *Sender)
{
	Close();
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::btnItchClick(TObject *Sender)
{
	ShellExecute(NULL, "open", "https://frankengraphics.itch.io/nexxt", "", NULL, SW_RESTORE);
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::btnCommunityClick(TObject *Sender)
{
  ShellExecute(NULL, "open", "https://frankengraphics.itch.io/nexxt/community", "", NULL, SW_RESTORE);
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::btnShiruClick(TObject *Sender)
{
ShellExecute(NULL, "open", "https://shiru.untergrund.net/index.shtml", "", NULL, SW_RESTORE);
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::btnBskyClick(TObject *Sender)
{
	ShellExecute(NULL, "open", "https://bsky.app/profile/frankengraphics.bsky.social", "", NULL, SW_RESTORE);
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::btnPatreonClick(TObject *Sender)
{
	ShellExecute(NULL, "open", "https://www.patreon.com/frankengraphics", "", NULL, SW_RESTORE);
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::btnMastoClick(TObject *Sender)
{
	ShellExecute(NULL, "open", "https://mastodon.art/@FrankenGraphics", "", NULL, SW_RESTORE);
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::btnXClick(TObject *Sender)
{
	ShellExecute(NULL, "open", "https://twitter.com/FrankenGraphics", "", NULL, SW_RESTORE);
}
//---------------------------------------------------------------------------

void __fastcall TAboutBox::Button1Click(TObject *Sender)
{
	ShellExecute(NULL, "open", "https://ko-fi.com/frankengraphics", "", NULL, SW_RESTORE);
}
//---------------------------------------------------------------------------

