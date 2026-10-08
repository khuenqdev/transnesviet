//---------------------------------------------------------------------------

#ifndef UnitFaderH
#define UnitFaderH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <ComCtrls.hpp>
#include <ExtCtrls.hpp>
#include <Buttons.hpp>
#include <Menus.hpp>
//---------------------------------------------------------------------------
class TFormFader : public TForm
{
__published:	// IDE-managed Components
	TPaintBox *PaintBoxFader;
	TPaintBox *PaintBoxSys;
	TPaintBox *PaintBoxSubpal;
	TGroupBox *GroupBox1;
	TCheckBox *CheckBox1;
	TCheckBox *CheckBox2;
	TCheckBox *CheckBox3;
	TCheckBox *CheckBox4;
	TCheckBox *CheckBox5;
	TGroupBox *GroupBox2;
	TTrackBar *TrackBarMain;
	TGroupBox *GroupBox3;
	TSpeedButton *SpeedButton1;
	TSpeedButton *SpeedButton2;
	TSpeedButton *SpeedButton3;
	TSpeedButton *SpeedButton4;
	TSpeedButton *SpeedButton5;
	TGroupBox *GroupBox4;
	TCheckBox *ChkG;
	TCheckBox *ChkR;
	TCheckBox *ChkB;
	TCheckBox *CheckBox9;
	TCheckBox *ChkM;
	TGroupBox *GroupBox5;
	TRadioButton *Radio00;
	TRadioButton *Radio40;
	TRadioButton *Radio80;
	TRadioButton *RadioC0;
	TSpeedButton *SpeedButton6;
	TLabel *Label1;
	TEdit *Edit1;
	TUpDown *UpDown1;
	TLabel *Label2;
	TLabel *Label3;
	TGroupBox *GroupBox6;
	TSpeedButton *SpeedButton8;
	TSpeedButton *SpeedButton9;
	TSpeedButton *SpeedButton10;
	TPopupMenu *PopupMenuPresets;
	TMenuItem *Narrowdown1;
	TMenuItem *Narrowtocold1;
	TMenuItem *Narrowtohot1;
	TMenuItem *Narrowtomossy1;
	TMenuItem *Sunburn61;
	TMenuItem *Subtlefadetoblacks1;
	TMenuItem *Pronouncedfadetoblacks1;
	TMenuItem *urnoffthelights1;
	TSpeedButton *SpeedButton7;
	TPopupMenu *PopupMenuSave;
	TMenuItem *binary1;
	TPopupMenu *PopupMenuAB;
	TMenuItem *copyAtoB1;
	TMenuItem *copyBtoA1;
	TMenuItem *swapAB1;
	TMenuItem *currentchannelonly1;
	TMenuItem *alllchannels1;
	TMenuItem *copyAtoB2;
	TMenuItem *copyBtoA2;
	TMenuItem *swapAB2;
	TPopupMenu *PopupMenuChannel;
	TMenuItem *copythischannel1;
	TMenuItem *pastetothischannel1;
	TMenuItem *clonethischanneltoallsubpalchannels1;
	void __fastcall FormShow(TObject *Sender);
	void __fastcall PaintBoxSysPaint(TObject *Sender);
	void __fastcall PaintBoxFaderPaint(TObject *Sender);
	void __fastcall PaintBoxSubpalPaint(TObject *Sender);
	void __fastcall FormCreate(TObject *Sender);
	void __fastcall Radio00Click(TObject *Sender);
	void __fastcall TrackBarMainChange(TObject *Sender);
	void __fastcall ChkBClick(TObject *Sender);
	void __fastcall ChkGClick(TObject *Sender);
	void __fastcall ChkRClick(TObject *Sender);
	void __fastcall ChkMClick(TObject *Sender);
	void __fastcall UpDown1Click(TObject *Sender, TUDBtnType Button);
	void __fastcall CheckBox1Click(TObject *Sender);
	void __fastcall SpeedButton8Click(TObject *Sender);
	void __fastcall SpeedButton10Click(TObject *Sender);
	void __fastcall SpeedButton6MouseDown(TObject *Sender,
          TMouseButton Button, TShiftState Shift, int X, int Y);
	void __fastcall SpeedButton1MouseDown(TObject *Sender,
          TMouseButton Button, TShiftState Shift, int X, int Y);
private:	// User declarations
public:		// User declarations
	__fastcall TFormFader(TComponent* Owner);
	void __fastcall DrawAll(void);
	void __fastcall SetIDPageRadio(void);
    void __fastcall SetIDPageVar(void);
	void __fastcall GenerateTable(void);
	void __fastcall DrawColSys(int x,int y,int w, int h,int c,bool sel);
	void __fastcall DrawColFader(int x,int y,int w, int h,int c,bool sel);
	void __fastcall DrawColSubpal(int x,int y,int w, int h,int c,bool sel);
	void __fastcall DrawSubpal(int x,int y,int pal, bool fader);
	void __fastcall DrawFaderCanvas(void);
	void __fastcall DrawSystemPalette(void);
	void __fastcall DrawSubPalette(void);

};
//---------------------------------------------------------------------------
extern PACKAGE TFormFader *FormFader;
//---------------------------------------------------------------------------
#endif
