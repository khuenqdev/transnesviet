//---------------------------------------------------------------------------

#ifndef UnitExportNESMakerImageH
#define UnitExportNESMakerImageH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
//---------------------------------------------------------------------------
class TFormExportNESMakerImage : public TForm
{
__published:	// IDE-managed Components
	TGroupBox *GroupBox1;
	TRadioButton *RadioFull;
	TRadioButton *RadioUpper;
	TRadioButton *RadioLower;
	TRadioButton *RadioSelection;
	TRadioButton *Radio1st;
	TRadioButton *Radio2nd;
	TRadioButton *Radio3rd;
	TRadioButton *Radio4th;
	TButton *Button1;
	TButton *Button2;
	void __fastcall FormShow(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TFormExportNESMakerImage(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TFormExportNESMakerImage *FormExportNESMakerImage;
//---------------------------------------------------------------------------
#endif
