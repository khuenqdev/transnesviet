//---------------------------------------------------------------------------

#ifndef UnitPatternPaintToolboxH
#define UnitPatternPaintToolboxH
//---------------------------------------------------------------------------
#include <Classes.hpp>
#include <Controls.hpp>
#include <StdCtrls.hpp>
#include <Forms.hpp>
#include <Buttons.hpp>
//---------------------------------------------------------------------------
class TFormPatternPaint : public TForm
{
__published:	// IDE-managed Components
	TGroupBox *GroupBox1;
	TSpeedButton *btnPen;
	TSpeedButton *btnBucket;
	TSpeedButton *btnLine;
	TSpeedButton *btnInks;
	TGroupBox *GroupBox2;
	TSpeedButton *btn0;
	TSpeedButton *btn1;
	TSpeedButton *btn2;
	TSpeedButton *btn3;
	TSpeedButton *btnMaskMode;
	TSpeedButton *btnBrush;
	TGroupBox *GroupBox3;
	TLabel *Label1;
	void __fastcall btn0MouseEnter(TObject *Sender);
	void __fastcall btn1MouseEnter(TObject *Sender);
	void __fastcall btn2MouseEnter(TObject *Sender);
	void __fastcall btn3MouseEnter(TObject *Sender);
	void __fastcall btnMaskModeMouseEnter(TObject *Sender);
	void __fastcall btnPenMouseEnter(TObject *Sender);
	void __fastcall btnBrushMouseEnter(TObject *Sender);
	void __fastcall btnBucketMouseEnter(TObject *Sender);
	void __fastcall btnLineMouseEnter(TObject *Sender);
private:	// User declarations
public:		// User declarations
	__fastcall TFormPatternPaint(TComponent* Owner);
};
//---------------------------------------------------------------------------
extern PACKAGE TFormPatternPaint *FormPatternPaint;
//---------------------------------------------------------------------------
#endif
