//---------------------------------------------------------------------------

#include <vcl.h>
#pragma hdrstop


#include "UnitFader.h"
#include "UnitMain.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormFader *FormFader;

extern int outPalette[64];
extern unsigned char bgPal[64];
extern int palBank;
typedef unsigned char FaderTable[24][256];
extern FaderTable metaPaletteTable[10];
extern FaderTable metaPaletteSel;
extern int metaPalette_ppuMask[24*2];
extern int metaPalette_faderID;
extern bool bUseFaderTileset;
extern bool bUseFaderMaps;
extern bool bUseFaderMT;
extern bool bUseFaderPal;
extern bool bUseFaderSprites;
extern bool bUseFaderExports;

extern bool cueUpdateMetasprite;
extern bool cueUpdateMetasprite_noListUpdate;
extern bool cueUpdateMM;
extern bool cueUpdateTiles;
extern bool cueUpdateNametable;
extern bool cueUpdateNametableNoRepaint;


int fader_IDPage;
bool bTrackBarIgnoreChange=false;
bool bChkIgnoreChange=false;
//---------------------------------------------------------------------------
__fastcall TFormFader::TFormFader(TComponent* Owner)
	: TForm(Owner)
{
}
//---------------------------------------------------------------------------
double GetLuminance(TColor colour) {

	colour = (TColor)ColorToRGB(colour);

	int r = GetRValue(colour);
	int g = GetGValue(colour);
	int b = GetBValue(colour);

	return 0.299 * r + 0.587 * g + 0.114 * b;
}
void __fastcall TFormFader::SetIDPageRadio(void)
{
   switch (fader_IDPage) {
			case 0x00: Radio00->Checked=true;  break;
			case 0x40: Radio40->Checked=true;  break;
			case 0x80: Radio80->Checked=true;  break;
			case 0xC0: RadioC0->Checked=true;  break;
			default:
			fader_IDPage=0x00;
			Radio00->Checked=true;
   }
}
void __fastcall TFormFader::SetIDPageVar(void)
{
		if		(Radio00->Checked) fader_IDPage=0x00;
		else if (Radio40->Checked) fader_IDPage=0x40;
		else if (Radio80->Checked) fader_IDPage=0x80;
		else if (RadioC0->Checked) fader_IDPage=0xC0;
		else{
			fader_IDPage=0x00;
            Radio00->Checked=true;
		}
}
void __fastcall TFormFader::DrawAll(void)
{
   //DrawSystemPalette();


	PaintBoxSys->Invalidate();
	PaintBoxFader->Invalidate();
	PaintBoxSubpal->Invalidate();
	//cueUpdateMetasprite;
	cueUpdateMetasprite_noListUpdate=true;
	cueUpdateMM=true;
	cueUpdateTiles=true;
	cueUpdateNametable=true;
	//cueUpdateNametableNoRepaint;

}
void __fastcall TFormFader::GenerateTable(void)
{
//used to generate a first starting point for fader tables during development
//to get the ball rolling - its contents are not meant to be a definitive solution.
//eventually, nexxt will/should reference a set of hand tailored tables on file
//instead.
	int id=0;
	int x=0;
	int y=0;


	for(int f=0;f<17;f++)
	{

	for(int i=0;i<4;i++)
	{


		for(int j=0;j<16;j++)
		{
			if (j<16)
			{
				id=j+i*16;
				if(f==0){
					if (id==0x37 || id==0x38)
							 {
								id=0x30;
							 }
				   else if (id==0x27) id=0x37;
				   else if (id==0x28) id=0x38;
				   else if (id==0x17) id=0x27;
				   else if (id==0x18) id=0x28;
				   else if (id==0x07) id=0x17;
				   else if (id==0x08) id=0x18;

				   else if (id==0x0d) id=0x07;
				   else if (id==0x1d) id=0x08;
				}
				else if(f>0){
					for(int sub=0; sub<f; sub++){

						 if (f==1 && id==0x37) id=0x37;
					else if (f==1 && id==0x27) id=0x27;
					else if (f==1 && id==0x17) id=0x17;
					else if (f==1 && id==0x07) id=0x07;

					else if (f==2 && j==0x07 && i==3) id=0x27;
					else if (f==2 && j==0x07 && i==2) id=0x17;
					else if (f==2 && j==0x07 && i==1) id=0x07;
					else if (f==2 && j==0x07 && i==0) id=0x0f;

					else if (f==3 && j==0x07 && i==3) id=0x17;
					else if (f==3 && j==0x07 && i==2) id=0x07;
					else if (f==3 && j==0x07 && i==1) id=0x0f;
					else if (f==3 && j==0x07 && i==0) id=0x0f;

					else if (f==4 && j==0x07 && i==3) id=0x07;
					else if (f==4 && j==0x07 && i==2) id=0x0f;
					else if (f==4 && j==0x07 && i==1) id=0x0f;
					else if (f==4 && j==0x07 && i==0) id=0x0f;

					else if (f>=5 && j==0x07 && i==3) id=0x0f;
					else if (f>=5 && j==0x07 && i==2) id=0x0f;
					else if (f>=5 && j==0x07 && i==1) id=0x0f;
					else if (f>=5 && j==0x07 && i==0) id=0x0f;

					else if (f==1 && id==0x38) id=0x38;
					else if (f==1 && id==0x28) id=0x28;
					else if (f==1 && id==0x18) id=0x18;
					else if (f==1 && id==0x08) id=0x08;

					else if (f==2 && j==0x08 && i==3) id=0x28;
					else if (f==2 && j==0x08 && i==2) id=0x18;
					else if (f==2 && j==0x08 && i==1) id=0x08;
					else if (f==2 && j==0x08 && i==0) id=0x0f;

					else if (f==3 && j==0x08 && i==3) id=0x18;
					else if (f==3 && j==0x08 && i==2) id=0x08;
					else if (f==3 && j==0x08 && i==1) id=0x0f;
					else if (f==3 && j==0x08 && i==0) id=0x0f;

					else if (f==4 && j==0x08 && i==3) id=0x08;
					else if (f==4 && j==0x08 && i==2) id=0x0f;
					else if (f==4 && j==0x08 && i==1) id=0x0f;
					else if (f==4 && j==0x08 && i==0) id=0x0f;

					else if (f>=5 && j==0x08 && i==3) id=0x0f;
					else if (f>=5 && j==0x08 && i==2) id=0x0f;
					else if (f>=5 && j==0x08 && i==1) id=0x0f;
					else if (f>=5 && j==0x08 && i==0) id=0x0f;

					else if (f==2 && j==0x00 && i==0) id=0x08;
					else if (f==3 && j==0x00 && i==1) id=0x08;
					else if (f==4 && j==0x00 && i==2) id=0x08;
                    else if (f==4 && j==0x0d && i==3) id=0x0c;


					else if (id==0x07) id=0x0f;
					else if (id==0x08) id=0x0f;
					else if (id==0x0c) id=0x0f;
					else if (id==0x3d) id=0x10;

					else if (id==0x2d) id=0x0f;
					else if (id==0x00) id=0x2d;

					else if (id==0x01) id=0x0c;
					else if (id==0x02) id=0x0c;
					else if (id==0x03) id=0x0c;

					else if (id==0x04) id=0x07;
					else if (id==0x05) id=0x07;
					else if (id==0x06) id=0x07;

					else if (id==0x09) id=0x08;
					else if (id==0x0a) id=0x08;
					else if (id==0x0b) id=0x0c;

					else if (id==0x0d) id=0x0f;
					else if (id==0x1d) id=0x0f;

					else if (id>=0x0e && id<0x10) id=0x0f;



					/*
					else if (id==0x37 || id==0x38 && f>1)
							 {
								id-=0x10;
								sub++;
							 }
					*/

					else id-=0x10; }
				}
				x=(i+j*4);
				//x=j+i*16;
				//DrawColFader(x,y+14,w,h,id,false);   //x,y,size,c,sel    //pp==col
				metaPaletteTable[0][y][x] = id;

			}
			else {metaPaletteTable[0][y][x] = 13;} //i*16+j==col
		}



	}
	y++;
	}
}


void __fastcall TFormFader::DrawColSys(int x,int y,int w, int h,int c,bool sel)
{
	TRect r;

	r.left  =x;
	r.top   =y;
	r.right =x+w;
	r.Bottom=y+h;

	PaintBoxSys->Canvas->Brush->Color=TColor(outPalette[c]);
	PaintBoxSys->Canvas->FillRect(r);

	if(sel)
	{
		PaintBoxSys->Canvas->Pen->Color=TColor(0xffffff);
		PaintBoxSys->Canvas->Rectangle(r);
		PaintBoxSys->Canvas->Pen->Color=TColor(0);

		r.left  +=1;
		r.top   +=1;
		r.right -=1;
		r.bottom-=1;

		PaintBoxSys->Canvas->Rectangle(r);
	}
}
void __fastcall TFormFader::DrawColFader(int x,int y,int w, int h,int c,bool sel)
{
	TRect r;

	r.left  =x;
	r.top   =y;
	r.right =x+w;
	r.Bottom=y+h;

	PaintBoxFader->Canvas->Brush->Color=TColor(outPalette[c]);
	PaintBoxFader->Canvas->FillRect(r);

	if(sel)
	{
		PaintBoxFader->Canvas->Pen->Color=TColor(0xffffff);
		PaintBoxFader->Canvas->Rectangle(r);
		PaintBoxFader->Canvas->Pen->Color=TColor(0);

		r.left  +=1;
		r.top   +=1;
		r.right -=1;
		r.bottom-=1;

		PaintBoxFader->Canvas->Rectangle(r);
	}
}
void __fastcall TFormFader::DrawColSubpal(int x,int y,int w, int h,int c,bool sel)
{
	TRect r;

	r.left  =x;
	r.top   =y;
	r.right =x+w;
	r.Bottom=y+h;

	PaintBoxSubpal->Canvas->Brush->Color=TColor(outPalette[c]);
	PaintBoxSubpal->Canvas->FillRect(r);

	if(sel)
	{
		PaintBoxSubpal->Canvas->Pen->Color=TColor(0xffffff);
		PaintBoxSubpal->Canvas->Rectangle(r);
		PaintBoxSubpal->Canvas->Pen->Color=TColor(0);

		r.left  +=1;
		r.top   +=1;
		r.right -=1;
		r.bottom-=1;

		PaintBoxSubpal->Canvas->Rectangle(r);
	}
}
void __fastcall TFormFader::DrawSubpal(int x,int y,int pal,bool fader)
{
    //if changing dimensions, remember to also change click areas. 
	int w=10;
	int h=10;
	int f=metaPalette_faderID;
	if(fader){
		DrawColSubpal(x   ,y,w,h,		metaPaletteTable[0][f][ (bgPal[palBank*16+pal*4+0]&0x0f)*4 +(bgPal[palBank*16+pal*4+0]&0xf0)/16 ],false);
		DrawColSubpal(x+w,y,w,h,		metaPaletteTable[0][f][ (bgPal[palBank*16+pal*4+1]&0x0f)*4 +(bgPal[palBank*16+pal*4+1]&0xf0)/16 ],false);
		DrawColSubpal(x+w*2,y,w,h,		metaPaletteTable[0][f][ (bgPal[palBank*16+pal*4+2]&0x0f)*4 +(bgPal[palBank*16+pal*4+2]&0xf0)/16 ],false);
		DrawColSubpal(x+w*3,y,w,h,		metaPaletteTable[0][f][ (bgPal[palBank*16+pal*4+3]&0x0f)*4 +(bgPal[palBank*16+pal*4+3]&0xf0)/16 ],false);

	}
	else{
		DrawColSubpal(x   ,y,w,h,bgPal[palBank*16+pal*4+0],false);
		DrawColSubpal(x+w,y,w,h,bgPal[palBank*16+pal*4+1],false);
		DrawColSubpal(x+w*2,y,w,h,bgPal[palBank*16+pal*4+2],false);
		DrawColSubpal(x+w*3,y,w,h,bgPal[palBank*16+pal*4+3],false);
	}
}
void __fastcall TFormFader::DrawFaderCanvas(void)
{
   int id=0;
   int x;
   int y=0;
   int w=16;
   int h=12;
   TRect r;

	for(int i=0;i<4;i++){
		for(int j=0;j<16;j++)
		{
			x=(i+j*4)*w;
			if(GetLuminance(TColor(outPalette[j+i*16]))<GetLuminance(clGray)) PaintBoxFader->Canvas->Font->Color = clWhite;
			else PaintBoxFader->Canvas->Font->Color = clBlack;
			PaintBoxFader->Canvas->Brush->Color=TColor(outPalette[j+i*16]);
			PaintBoxFader->Canvas->Font->Name = "Arial";
			PaintBoxFader->Canvas->Font->Size = 7;
			int tmp=fader_IDPage;
			PaintBoxFader->Canvas->TextOut(x+3, y, IntToHex(tmp+j+i*16,2));
		}
	}
	h=(136-14)/(TrackBarMain->Max+1);
	for(int f=0;f<24;f++)
	{

	for(int i=0;i<4*16;i++)
	{

		id=metaPaletteTable[0][f][i];
		x=(i)*w;
		DrawColFader(x,y+14,w,h,id,false);   //x,y,size,c,sel    //pp==col


	}


	y+=h;


	}
    for(int f=0;f<24;f++)
	{

	for(int i=0;i<4*16;i++)
	{


		if(metaPaletteSel[f][i]){
			r.left  	=i*w;
			r.top   	=14+f*h;
			r.right 	=i*w+w+1;
			r.bottom	=14+f*h+h+1;
			PaintBoxFader->Canvas->Brush->Style=bsClear;
			PaintBoxFader->Canvas->Pen->Color=clDkGray;
			PaintBoxFader->Canvas->Pen->Style=psSolid;
			PaintBoxFader->Canvas->Rectangle(r);
			PaintBoxFader->Canvas->Pen->Color=clLtGray;
			PaintBoxFader->Canvas->Pen->Style=psDot;
			PaintBoxFader->Canvas->Rectangle(r);
		}

	}


	y+=h;


	}

}
void __fastcall TFormFader::DrawSystemPalette(void)
{
	/*
	TRect r;
	r.left  =0 ;
	r.top   =0 ;
	r.right = PaintBoxSys->Width;
	r.Bottom= PaintBoxSys->Height;

	PaintBoxSys->Canvas->Brush->Style=bsSolid;
	PaintBoxSys->Canvas->Brush->Color=TColor(0x0);

	PaintBoxSys->Canvas->FillRect(r);
	*/
	//int col=bgPal[palBank*16+palActive*4+bgPalCur];
	int id=0;
	int x;
	int y=0;
	int w=12;
	int h=16;
	int f=metaPalette_faderID;
	for(int i=0;i<4;i++)
	{
		x=0;

		for(int j=0;j<16;j++)
		{
			//if (j<16)
			//{
				DrawColSys(x+w*16+6,y,w,h,metaPaletteTable[0][f][i+j*4],false);   //x,y,size,c,sel    //pp==col
				DrawColSys(x,y,w,h,i*16+j,false);   //x,y,size,c,sel    //pp==col

				id++;

			//}
			//else {DrawColSys(x,y,w,h,13,false);} //i*16+j==col
			x+=w;
		}


		y+=h;
	}

}
void __fastcall TFormFader::DrawSubPalette(void)
{
	int h=10;
	int sw=6;
	DrawSubpal( 	0, 	0,0,false);
	DrawSubpal(40+sw, 	0,1,false);
	DrawSubpal(80+sw*2,	0,2,false);
	DrawSubpal(120+sw*3,0,3,false);

	DrawSubpal( 	0, 	h*2,0,true);
	DrawSubpal(40+sw, 	h*2,1,true);
	DrawSubpal(80+sw*2,	h*2,2,true);
	DrawSubpal(120+sw*3,h*2,3,true);

}
void __fastcall TFormFader::FormShow(TObject *Sender)
{

	DrawAll();
}
//---------------------------------------------------------------------------
void __fastcall TFormFader::PaintBoxSysPaint(TObject *Sender)
{
   DrawSystemPalette();
}
//---------------------------------------------------------------------------
void __fastcall TFormFader::PaintBoxFaderPaint(TObject *Sender)
{
	DrawFaderCanvas();
}
//---------------------------------------------------------------------------
void __fastcall TFormFader::PaintBoxSubpalPaint(TObject *Sender)
{
	DrawSubPalette();
}
//---------------------------------------------------------------------------


void __fastcall TFormFader::FormCreate(TObject *Sender)
{

	SetIDPageVar();
	GenerateTable();
	bTrackBarIgnoreChange=true;
	TrackBarMain->Position=metaPalette_faderID;
	bTrackBarIgnoreChange=false;

}
//---------------------------------------------------------------------------

void __fastcall TFormFader::Radio00Click(TObject *Sender)
{
	SetIDPageVar();
	DrawAll();
}
//---------------------------------------------------------------------------

void __fastcall TFormFader::TrackBarMainChange(TObject *Sender)
{
	int id=TrackBarMain->Position;
	bChkIgnoreChange=true;
	ChkB->Checked=metaPalette_ppuMask[id]&0x80;
	ChkG->Checked=metaPalette_ppuMask[id]&0x40;
	ChkR->Checked=metaPalette_ppuMask[id]&0x20;
	ChkM->Checked=metaPalette_ppuMask[id]&0x01;
	bChkIgnoreChange=false;

	if(bTrackBarIgnoreChange)return;
	metaPalette_faderID=TrackBarMain->Position;




	PaintBoxSys->Invalidate();
	PaintBoxSubpal->Invalidate();

	cueUpdateMetasprite_noListUpdate=true;
	cueUpdateMM=true;
	cueUpdateTiles=true;
	cueUpdateNametable=true;
    FormMain->pal_validate();
	FormMain->DrawPalettes();
}
//---------------------------------------------------------------------------

void __fastcall TFormFader::ChkBClick(TObject *Sender)
{
	if(bChkIgnoreChange) return;
	int id=metaPalette_faderID;
	if(ChkB->Checked) metaPalette_ppuMask[id]|=0x80;
	if(!ChkB->Checked) metaPalette_ppuMask[id]&=~0x80;

}
//---------------------------------------------------------------------------

void __fastcall TFormFader::ChkGClick(TObject *Sender)
{
	if(bChkIgnoreChange) return;
	int id=metaPalette_faderID;
	if(ChkG->Checked) metaPalette_ppuMask[id]|=0x40;
	if(!ChkG->Checked) metaPalette_ppuMask[id]&=~0x40;

}
//---------------------------------------------------------------------------

void __fastcall TFormFader::ChkRClick(TObject *Sender)
{
    if(bChkIgnoreChange) return;
	int id=metaPalette_faderID;
	if(ChkR->Checked) metaPalette_ppuMask[id]|=0x20;
	if(!ChkR->Checked) metaPalette_ppuMask[id]&=~0x20;

}
//---------------------------------------------------------------------------

void __fastcall TFormFader::ChkMClick(TObject *Sender)
{
    if(bChkIgnoreChange) return;
	int id=metaPalette_faderID;
	if(ChkM->Checked) metaPalette_ppuMask[id]|=0x01;
	if(!ChkM->Checked) metaPalette_ppuMask[id]&=~0x01;

}
//---------------------------------------------------------------------------



void __fastcall TFormFader::UpDown1Click(TObject *Sender,
      TUDBtnType Button)
{
	TrackBarMain->Max=UpDown1->Position-1;	
	DrawAll();
}
//---------------------------------------------------------------------------

void __fastcall TFormFader::CheckBox1Click(TObject *Sender)
{
	bUseFaderMaps=CheckBox1->Checked;
	bUseFaderTileset=CheckBox4->Checked;
	bUseFaderPal=CheckBox2->Checked;
	TrackBarMainChange(Sender);
}
//---------------------------------------------------------------------------

void __fastcall TFormFader::SpeedButton8Click(TObject *Sender)
{
	TPoint p = Mouse->CursorPos;
	int x= p.x;
	int y= p.y;
	PopupMenuPresets->Popup(x,y);
}
//---------------------------------------------------------------------------

void __fastcall TFormFader::SpeedButton10Click(TObject *Sender)
{
   TPoint p = Mouse->CursorPos;
   int x= p.x;
   int y= p.y;
   PopupMenuSave->Popup(x,y);
}
//---------------------------------------------------------------------------


void __fastcall TFormFader::SpeedButton6MouseDown(TObject *Sender,
      TMouseButton Button, TShiftState Shift, int X, int Y)
{
	if(Shift.Contains(ssRight)||Shift.Contains(ssCtrl)) {
		 TPoint p = Mouse->CursorPos;
		 int x= p.x;
		 int y= p.y;
		 PopupMenuAB->Popup(x,y);
	}
}
//---------------------------------------------------------------------------

void __fastcall TFormFader::SpeedButton1MouseDown(TObject *Sender,
      TMouseButton Button, TShiftState Shift, int X, int Y)
{
    if(Shift.Contains(ssRight)||Shift.Contains(ssCtrl)) {
		 TPoint p = Mouse->CursorPos;
		 int x= p.x;
		 int y= p.y;
		 PopupMenuChannel->Popup(x,y);
	}
}
//---------------------------------------------------------------------------

