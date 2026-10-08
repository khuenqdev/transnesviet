//---------------------------------------------------------------------------

#ifndef UnitWarnNESlibRLEH
#define UnitWarnNESlibRLEH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
//---------------------------------------------------------------------------
class TFormWarnNESlibRLE : public TForm
{
__published:	// IDE-managed Components
	TButton *Button1;
	TCheckBox *CheckBox1;
	TStaticText *StaticText1;
	void __fastcall FormCreate(TObject *Sender);
	void __fastcall FormClose(TObject *Sender, TCloseAction &Action);
	void __fastcall FormShow(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TFormWarnNESlibRLE(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TFormWarnNESlibRLE *FormWarnNESlibRLE;
//---------------------------------------------------------------------------
#endif
