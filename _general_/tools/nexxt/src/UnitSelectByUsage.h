//---------------------------------------------------------------------------

#ifndef UnitSelectByUsageH
#define UnitSelectByUsageH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <Buttons.hpp>
#include <ComCtrls.hpp>
//---------------------------------------------------------------------------
class TFormSelectByUsage : public TForm
{
__published:	// IDE-managed Components
	TTrackBar *TrackBar1;
	TCheckBox *CheckBox1;
	TSpeedButton *SpeedButton1;
	TLabel *Label1;
	TLabel *Label2;
	void __fastcall TrackBar1Change(TObject *Sender);
	void __fastcall SpeedButton1Click(TObject *Sender);
	void __fastcall FormCreate(TObject *Sender);
	void __fastcall FormShow(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TFormSelectByUsage(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TFormSelectByUsage *FormSelectByUsage;
//---------------------------------------------------------------------------
#endif
