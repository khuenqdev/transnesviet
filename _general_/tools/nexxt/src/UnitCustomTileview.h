//---------------------------------------------------------------------------

#ifndef UnitCustomTileviewH
#define UnitCustomTileviewH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <Buttons.hpp>
#include <ExtCtrls.hpp>
#include <Dialogs.hpp>
#include <Menus.hpp>
//---------------------------------------------------------------------------
class TFormCustomTileview : public TForm
{
__published:	// IDE-managed Components
	TImage *ImageTileview;
	TSpeedButton *SpeedButton1;
	TSpeedButton *SpeedButton2;
	TSpeedButton *SpeedButton3;
	TGroupBox *GroupBox1;
	TRadioButton *RadioPatterns;
	TRadioButton *RadioIDs;
	TOpenDialog *OpenDialog1;
	TSaveDialog *SaveDialog1;
	TCheckBox *CheckBox1;
	TPopupMenu *PopupMenu1;
	TMenuItem *Normal1;
	TMenuItem *NES8x16mode1;
	TMenuItem *byfrequency1;
	TMenuItem *bydensity1;
	TMenuItem *bydetail1;
	TMenuItem *byedgecontent1;
	TMenuItem *byselectedcolour1;
	TMenuItem *N4x12x21;
	TMenuItem *N4x12x2topdown1;
	TMenuItem *N16x14x41;
	TMenuItem *N1;
	TMenuItem *N2;
	void __fastcall UpdateUI(bool doTiles);
	bool __fastcall OpenCharmap(AnsiString name);
	void __fastcall SpeedButton1Click(TObject *Sender);
	void __fastcall FormShow(TObject *Sender);
	void __fastcall FormCreate(TObject *Sender);
	void __fastcall RadioPatternsClick(TObject *Sender);
	void __fastcall ImageTileviewMouseMove(TObject *Sender, TShiftState Shift,
          int X, int Y);
	void __fastcall ImageTileviewMouseLeave(TObject *Sender);
	void __fastcall ImageTileviewMouseDown(TObject *Sender,
          TMouseButton Button, TShiftState Shift, int X, int Y);
	void __fastcall ImageTileviewDragDrop(TObject *Sender, TObject *Source,
          int X, int Y);
	void __fastcall ImageTileviewDragOver(TObject *Sender, TObject *Source,
          int X, int Y, TDragState State, bool &Accept);
	void __fastcall ImageTileviewEndDrag(TObject *Sender, TObject *Target,
          int X, int Y);
	void __fastcall SpeedButton3Click(TObject *Sender);
	void __fastcall Normal1Click(TObject *Sender);
	void __fastcall ResetViewContents(int tag);
	void __fastcall SaveCharmap(int offset, int size);
	void __fastcall SpeedButton2Click(TObject *Sender);
	void __fastcall SpeedButton1MouseEnter(TObject *Sender);
	void __fastcall SpeedButton2MouseEnter(TObject *Sender);
	void __fastcall SpeedButton3MouseEnter(TObject *Sender);
	void __fastcall RadioPatternsMouseEnter(TObject *Sender);
	void __fastcall RadioIDsMouseEnter(TObject *Sender);
	void __fastcall CheckBox1MouseEnter(TObject *Sender);
	void __fastcall SpeedButton1MouseLeave(TObject *Sender);
	void __fastcall ImageTileviewMouseEnter(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TFormCustomTileview(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TFormCustomTileview *FormCustomTileview;
//---------------------------------------------------------------------------
#endif
