//---------------------------------------------------------------------------

#ifndef UnitWelcomeH
#define UnitWelcomeH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ComCtrls.hpp>
//---------------------------------------------------------------------------
class TFormWelcome : public TForm
{
__published:	// IDE-managed Components
	TGroupBox *GroupBox1;
	TStaticText *StaticText1;
	TRadioButton *RadioButton1;
	TRadioButton *RadioButton2;
	TLabel *Label2;
	TGroupBox *GroupBox2;
	TStaticText *StaticText2;
	TGroupBox *GroupBox3;
	TStaticText *StaticText3;
	TButton *Button1;
	TButton *Button2;
	TButton *Button3;
	TStaticText *StaticText4;
	void __fastcall Button1Click(TObject *Sender);
	void __fastcall Button2Click(TObject *Sender);
	void __fastcall FormCreate(TObject *Sender);
	void __fastcall FormClose(TObject *Sender, TCloseAction &Action);
	void __fastcall Button3Click(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TFormWelcome(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TFormWelcome *FormWelcome;
//---------------------------------------------------------------------------
#endif
