//---------------------------------------------------------------------------

#ifndef UnitSetSizeH
#define UnitSetSizeH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ComCtrls.hpp>
#include <Buttons.hpp>
//---------------------------------------------------------------------------
class TFormSetSize : public TForm
{
__published:	// IDE-managed Components
	TGroupBox *GroupBox1;
	TButton *ButtonCancel;
	TButton *ButtonOK;
	TEdit *EditWidth;
	TEdit *EditHeight;
	TUpDown *UpDownWidth;
	TUpDown *UpDownHeight;
	TCheckBox *CheckBoxClear;
	TCheckBox *CheckNullTile;
	TSpeedButton *BtnWdtInc;
	TSpeedButton *BtnHgtInc;
	TSpeedButton *BtnWdtDec;
	TSpeedButton *BtnHgtDec;
	TSpeedButton *Btn32x30;
	TSpeedButton *BtnThisSession;
	TSpeedButton *SpeedButton1;
	TRadioButton *Radio1;
	TRadioButton *Radio2;
	TLabel *Label1;
	TGroupBox *GroupBox2;
	TSpeedButton *btnTL;
	TSpeedButton *btnTC;
	TSpeedButton *btnTR;
	TSpeedButton *btnCL;
	TSpeedButton *btnCC;
	TSpeedButton *btnCR;
	TSpeedButton *btnBL;
	TSpeedButton *btnBC;
	TSpeedButton *btnBR;
	void __fastcall ButtonOKClick(TObject *Sender);
	void __fastcall ButtonCancelClick(TObject *Sender);
	void __fastcall FormShow(TObject *Sender);
	void __fastcall EditWidthKeyPress(TObject *Sender, char &Key);
	void __fastcall EditWidthExit(TObject *Sender);
	void __fastcall EditWidthClick(TObject *Sender);
	void __fastcall EditHeightExit(TObject *Sender);
	void __fastcall BtnWdtIncClick(TObject *Sender);
	void __fastcall BtnWdtDecClick(TObject *Sender);
	void __fastcall BtnHgtIncClick(TObject *Sender);
	void __fastcall BtnHgtDecClick(TObject *Sender);
	void __fastcall BtnThisSessionClick(TObject *Sender);
	void __fastcall Btn32x30Click(TObject *Sender);
	void __fastcall SpeedButton1Click(TObject *Sender);
	void __fastcall UpDownWidthClick(TObject *Sender, TUDBtnType Button);
	void __fastcall UpDownHeightClick(TObject *Sender, TUDBtnType Button);
	void __fastcall Radio1Click(TObject *Sender);
	void __fastcall Radio2Click(TObject *Sender);
private:	// User declarations

public:		// User declarations
	__fastcall TFormSetSize(TComponent* Owner);
	void __fastcall UpdateXYReadout(void);
	int NewWidth;
	int NewHeight;
	bool Confirm;
};
//---------------------------------------------------------------------------
extern PACKAGE TFormSetSize *FormSetSize;
//---------------------------------------------------------------------------
#endif
