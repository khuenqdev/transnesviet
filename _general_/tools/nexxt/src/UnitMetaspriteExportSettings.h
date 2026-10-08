//---------------------------------------------------------------------------

#ifndef UnitMetaspriteExportSettingsH
#define UnitMetaspriteExportSettingsH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <Buttons.hpp>
#include <ComCtrls.hpp>
#include <Menus.hpp>
//---------------------------------------------------------------------------
class TFormMetaspriteExportSettings : public TForm
{
__published:	// IDE-managed Components
	TGroupBox *GroupBox1;
	TSpeedButton *BtnThisSession;
	TSpeedButton *Btn32x30;
	TSpeedButton *SpeedButton1;
	TSpeedButton *BtnIncX;
	TSpeedButton *BtnIncY;
	TUpDown *UpDownOffsetY;
	TEdit *EditOffsetY;
	TSpeedButton *BtnDecY;
	TSpeedButton *BtnDecX;
	TEdit *EditOffsetX;
	TUpDown *UpDownOffsetX;
	TCheckBox *CheckOffset;
	TGroupBox *GroupBox2;
	TSpeedButton *SpeedButton5;
	TSpeedButton *SpeedButton6;
	TSpeedButton *SpeedButton7;
	TSpeedButton *SpeedButton8;
	TUpDown *UpDownWarnHiX;
	TEdit *EditWarnHiX;
	TEdit *EditWarnLoX;
	TUpDown *UpDownWarnLoX;
	TCheckBox *CheckWarn;
	TLabel *Label1;
	TSpeedButton *SpeedButton2;
	TLabel *Label2;
	TSpeedButton *SpeedButton3;
	TEdit *EditWarnLoY;
	TUpDown *UpDownWarnLoY;
	TEdit *EditWarnHiY;
	TUpDown *UpDownWarnHiY;
	TSpeedButton *SpeedButton9;
	TSpeedButton *SpeedButton10;
	TCheckBox *CheckJustWarn;
	TGroupBox *GroupBox3;
	TSpeedButton *btnOAM0;
	TSpeedButton *btnOAM1;
	TSpeedButton *btnOAM2;
	TSpeedButton *btnOAM3;
	TCheckBox *CheckCustomOrder;
	TSpeedButton *SpeedButton12;
	TLabel *Label3;
	TLabel *Label4;
	TLabel *Label5;
	TLabel *Label6;
	TSpeedButton *SpeedButton13;
	TSpeedButton *BtnNegateY;
	TSpeedButton *BtnNegateX;
	TSpeedButton *SpeedButton19;
	TSpeedButton *SpeedButton20;
	TSpeedButton *SpeedButton21;
	TSpeedButton *SpeedButton22;
	TSpeedButton *SpeedButton23;
	TPopupMenu *PopupMenu1;
	TMenuItem *X1;
	TMenuItem *Y1;
	TMenuItem *ID1;
	TMenuItem *Attributes1;
	TSpeedButton *SpeedButton16;
	void __fastcall BtnThisSessionClick(TObject *Sender);
	void __fastcall Btn32x30Click(TObject *Sender);
	void __fastcall SpeedButton1Click(TObject *Sender);
	void __fastcall SpeedButton19Click(TObject *Sender);
	void __fastcall SpeedButton20Click(TObject *Sender);
	void __fastcall SpeedButton21Click(TObject *Sender);
	void __fastcall SpeedButton22Click(TObject *Sender);
	void __fastcall SpeedButton23Click(TObject *Sender);
	void __fastcall UpdateUI(void);
	void __fastcall UpdateVars(void);
	void __fastcall UpdateOrderButtons(void);
	void __fastcall FormShow(TObject *Sender);
	void __fastcall FormClose(TObject *Sender, TCloseAction &Action);
	void __fastcall FormDeactivate(TObject *Sender);
	void __fastcall BtnNegateXClick(TObject *Sender);
	void __fastcall BtnNegateYClick(TObject *Sender);
	void __fastcall SpeedButton12Click(TObject *Sender);
	void __fastcall SpeedButton13Click(TObject *Sender);
	void __fastcall SpeedButton16Click(TObject *Sender);
	void __fastcall EditOffsetXExit(TObject *Sender);
	void __fastcall EditOffsetYExit(TObject *Sender);
	void __fastcall EditWarnLoXExit(TObject *Sender);
	void __fastcall EditWarnHiXExit(TObject *Sender);
	void __fastcall EditWarnLoYExit(TObject *Sender);
	void __fastcall EditWarnHiYExit(TObject *Sender);
	void __fastcall EditOffsetXKeyPress(TObject *Sender, char &Key);
	void __fastcall EditOffsetXClick(TObject *Sender);
	void __fastcall CheckOffsetClick(TObject *Sender);
	void __fastcall btnOAM0Click(TObject *Sender);
	void __fastcall X1Click(TObject *Sender);

private:	// User declarations
public:		// User declarations
	__fastcall TFormMetaspriteExportSettings(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TFormMetaspriteExportSettings *FormMetaspriteExportSettings;
//---------------------------------------------------------------------------
#endif
