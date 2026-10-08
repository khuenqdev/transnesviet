//---------------------------------------------------------------------------

#include <vcl.h>

#include <stdio.h>
#include <math.h>
#include <dir.h>
#pragma hdrstop

#include "UnitCustomTileview.h"
#include "UnitMain.h"
#include "UnitCHREditor.h"
//---------------------------------------------------------------------------
#pragma package(smart_init)
#pragma resource "*.dfm"
TFormCustomTileview *FormCustomTileview;

extern bool openByFileDone;
extern bool bBufCtrl;
extern bool bBufShift;
extern bool bBufAlt;
extern unsigned char tileViewTable[];
extern unsigned char tileViewCustom[];
extern int palActive;
extern int nullTile;
extern bool bDrawDestViewShadow;
extern unsigned char chrSelected[];
extern TRect chrSelection;
TRect destViewRect;
TRect viewSelection;
TRect viewSelBuf;
Graphics::TBitmap *viewBuf = new Graphics::TBitmap;

unsigned char viewSelected[256];
bool bOutsideViewSel=true;
int txViewDown=0;
int tyViewDown=0;
int viewSelRectWdt;
int viewSelRectHgt;
bool viewSelectRect=true;

 AnsiString RemoveExt(AnsiString name)
{
	return ChangeFileExt(name,"");
}

//---------------------------------------------------------------------------
__fastcall TFormCustomTileview::TFormCustomTileview(TComponent* Owner)
	: TForm(Owner)
{
}

//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::UpdateUI(bool doTiles){

	if(!Visible) return;
	int ui8=8*2;
    int ui128=128*2;
	int x=0;
	int y=0;
	bool showID = RadioIDs->Checked;
	if(doTiles){
	for(int i=0;i<256;++i)
		{

		FormMain->DrawTile(ImageTileview->Picture,x,y,tileViewCustom[i],tileViewCustom[i],palActive,-1,-1,viewSelected[i],false,2,false,false,false,false,false,showID);
		x+=ui8;


			if(x>=ui128)
			{
				x=0;

				y+=ui8;
			}
		}

		//FormMain->DrawSelection(ImageTileview,chrSelection,2,false,false,true,false);
		//ImageTileview->Picture->Bitmap->Assign(viewBuf);
		viewBuf->Assign(ImageTileview->Picture->Bitmap);
	}

	FormMain->DrawSelection(ImageTileview,viewSelection,2,false,false,false,false);
}
int get_file_size(FILE *file)
{
	int size;

	fseek(file,0,SEEK_END);
	size=ftell(file);
	fseek(file,0,SEEK_SET);

	return size;
}
bool __fastcall TFormCustomTileview::OpenCharmap(AnsiString name){
    bool bView = FormMain->customcharmap1->Checked;
	unsigned char buf[1024];
	FILE *file;
	int i,pp,size,type;

	file=fopen(name.c_str(),"rb");

	//type=-1;

	if(file)
	{
		size=get_file_size(file);



		switch(size)
		{

		case 256:
			fread(buf,256,1,file);
			for(i=0;i<size;++i)	tileViewCustom[i]=buf[i];
			//type=1;
            if(bView) {
				for(int i=0;i<256;i++){
					tileViewTable[i]=tileViewCustom[i];
				}
			}
			break;

		default:


				Application->MessageBox("Wrong file size. Should be 256 bytes.","Error",MB_OK);
				fclose(file);
				return false;

		}
	}
	else{
		AnsiString AnsiFileNotFound=
			"Could not open file.\n\nPlease double-check its path/file/extension,\nor verify its existence:\n"+name;
		Application->MessageBox(AnsiFileNotFound.c_str(),"Warning",MB_OK);
    	return false;
	}
	fclose(file);


	return true;

}
void __fastcall TFormCustomTileview::SpeedButton1Click(TObject *Sender)
{
	if(OpenDialog1->Execute())
	{
		FormMain->BlockDrawing(true);
		if(OpenCharmap(OpenDialog1->FileName))
		{
            if(openByFileDone)FormMain->UpdateAll();
		}
		FormMain->BlockDrawing(false);


	}
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::FormShow(TObject *Sender)
{
	viewSelection=chrSelection;
	UpdateUI(true);
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::FormCreate(TObject *Sender)
{
	ImageTileview->Picture=new TPicture();
	ImageTileview->Picture->Bitmap=new Graphics::TBitmap();
	ImageTileview->Picture->Bitmap->PixelFormat=pf24bit;
	ImageTileview->Stretch=true;
	ImageTileview     ->Picture->Bitmap->SetSize(128*2,128*2);

	viewBuf->PixelFormat = pf24bit;
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::RadioPatternsClick(TObject *Sender)
{
	UpdateUI(true);
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::ImageTileviewMouseMove(
      TObject *Sender, TShiftState Shift, int X, int Y)
{
	int xs,ys,wdt,hgt;

	int tx=X/(8*2);
	int ty=Y/(8*2);
	int id=ty*16+tx;
	bool showID = RadioIDs->Checked;
	bool peek = CheckBox1->Checked;
	ImageTileview->Picture->Bitmap->Assign(viewBuf);
	if(peek) {

	FormMain->DrawTile(ImageTileview->Picture,(tx*8*2),(ty*8*2),tileViewTable[id],tileViewTable[id],palActive,-1,-1,chrSelected[id],false,2,false,false,false,false,false,!showID);
	}

	//this selection routine is copied verbatim from tile selection, then modified for simpler puroposes.
	//some of what it does might not be hooked up to anything as of this time.

	if((!Shift.Contains(ssShift))||(X>=0&&X<(128*2)&&Y>=0&&Y<(128*2)))
	{
		//tx=X/(8*uiScale);
		//ty=Y/(8*uiScale);
		//tileXC=tx;
		//tileYC=ty;

		if(Shift.Contains(ssShift)&&!Shift.Contains(ssCtrl))
		{
			//drag selection
			/*
			if(Shift.Contains(ssRight)&&Shift.Contains(ssShift)&&!bOutsideViewSel)
			{

				viewSelection.left=viewSelBuf.left+tx-txViewDown;
				viewSelection.right=viewSelBuf.right+tx-txViewDown;
				viewSelection.top=viewSelBuf.top+ty-tyViewDown;
				viewSelection.bottom=viewSelBuf.bottom+ty-tyViewDown;



				for (int i=0; i<16; i++)  //long enough loop - felt safer than while
				{
					if(viewSelection.left<0)   	{	viewSelection.left++;
													viewSelection.right++;}
					if(viewSelection.right>0x10)	{	viewSelection.left--;
													viewSelection.right--;}
					if(viewSelection.top<0)   	{	viewSelection.top++;
													viewSelection.bottom++;}
					if(viewSelection.bottom>0x10){	viewSelection.top--;
													viewSelection.bottom--;}
				}
				//cueUpdateTiles=true;
				//cueUpdateNametable=true;


			}  */

			//box selection
			if(Shift.Contains(ssLeft))
				{
					//mouseDraggedTileSel=true;
					//mouseDraggedNTSel=true;


					if(tx<txViewDown) {viewSelection.left=tx+1-(tx<viewSelection.right?1:0);
								  viewSelection.right=txViewDown+1;
								  }
					if(tx>=txViewDown) {viewSelection.right =tx+(tx>=viewSelection.left?1:0);
								  viewSelection.left=txViewDown;

								  }

					if(ty<tyViewDown)  {viewSelection.top=ty-(ty>=viewSelection.bottom ?1:0);
								   viewSelection.bottom=tyViewDown+1;

								   }
					if(ty>=tyViewDown) {viewSelection.bottom=ty+(ty>=viewSelection.top ?1:0);
								   viewSelection.top=tyViewDown;
								  
								   }
				   //tileActive=viewSelection.top*16+viewSelection.left;



					//note: this is also performed in mousedown
					/*
					int exceptionSize =FormCHREditor->btn2x2mode->Down? f+1:1;
					if(   abs(viewSelection.left-viewSelection.right)!=exceptionSize
						||abs(viewSelection.top-viewSelection.bottom)!=exceptionSize)
					{
						viewSelection.left=-1;
						viewSelection.top =-1;

						UpdateUI();
					}
					*/

				
					
		}  //
		if(Shift.Contains(ssLeft) ||Shift.Contains(ssRight))
		{
			for(int i=0;i<256;i++) viewSelected[i]=false;

					//some of this is probably unwarranted now that there is no inverted selection weirdness anymore. Keeping it for redundancy.
					//--------------
					xs=viewSelection.left<viewSelection.right ?viewSelection.left:viewSelection.right;
					ys=viewSelection.top <viewSelection.bottom?viewSelection.top :viewSelection.bottom;

					//first check for negatives, later on we derive absolutes.
					wdt=(viewSelection.right -viewSelection.left);
					hgt=(viewSelection.bottom-viewSelection.top);

					//these are used by the new scroll/wrap tile routines, as well as the new drag-swap.
					viewSelRectWdt=abs(wdt);
					viewSelRectHgt=abs(hgt);

					//overwrite. similar to std::max except i did this instead.

					if (wdt<0)viewSelRectWdt=0;
					if (hgt<0)viewSelRectHgt=0;

					//these are used for the rest of nesst vanilla code below
					wdt=abs(wdt);
					hgt=abs(hgt);


					for(int i=0;i<hgt;i++)
						{
						for(int j=0;j<wdt;j++)
						{
							viewSelected[(i+ys)*16+j+xs]=true;
						}
					}
					viewSelectRect=true;  }
		}

		//multi-select by dragging
		 /*
		if(Shift.Contains(ssCtrl)&&(Shift.Contains(ssLeft)||Shift.Contains(ssRight)))
		{
			for(int tmpi=0;tmpi<255;tmpi++) if (viewSelected[tmpi]) oldCount++;
			bool bTmp = bMultiSelectRemoveMode;
			viewSelected[ty*16+tx]=Shift.Contains(ssLeft)?!bTmp:bTmp;
			viewSelectRect=false;
			for(int tmpi=0;tmpi<255;tmpi++) if (viewSelected[tmpi]) newCount++;
			if(SpeedButtonSelTiles->Down) UpdateNameTable(-1,-1,true);
		}  */
	 }




	FormMain->DrawSelection(ImageTileview,viewSelection,2,false,false,false,false);
	ImageTileview->Refresh();



}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::ImageTileviewMouseLeave(
      TObject *Sender)
{
	ImageTileview->Picture->Bitmap->Assign(viewBuf);	
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::ImageTileviewMouseDown(
      TObject *Sender, TMouseButton Button, TShiftState Shift, int X,
      int Y)
{
	int tx=X/(8*2);
	int ty=Y/(8*2);
	//int id=ty*16+tx;
	txViewDown=tx;    //used for relative positioning when dragging selection, as well as performing positive selections to the left/up.
	tyViewDown=ty;
	//int tile=tx+ty*16;
	bOutsideViewSel=false;

	if((viewSelection.right<=tx)
		|(viewSelection.left>tx)
		|(viewSelection.bottom<=ty)
		|(viewSelection.top>ty))
			bOutsideViewSel=true;
	if(!viewSelectRect) bOutsideViewSel=true;  //&&tileActive!=ty*16+tx

	//if(IsBlockDrawing()) return;
	if(!(X>=0&&X<(128*2)&&Y>=0&&Y<(128*2))) return;

	viewSelRectWdt=1;
	viewSelRectHgt=1;

	if(Shift.Contains(ssLeft)||(bOutsideViewSel)){

		//if(Shift.Contains(ssShift)){
				viewSelection.left=tx;
				viewSelection.top=ty;
				viewSelection.right=viewSelection.left+1;
				viewSelection.bottom=viewSelection.top+1;
				viewSelected[ty*16+tx]=1;
				viewSelRectWdt=1;
				viewSelRectHgt=1;
		 //	}

         viewSelBuf.left		=	viewSelection.left;
			viewSelBuf.top		=	viewSelection.top;
			viewSelBuf.right		=	viewSelection.right;
			viewSelBuf.bottom  	=	viewSelection.bottom;

			destViewRect.left		=	viewSelection.left;
			destViewRect.top		=	viewSelection.top;
			destViewRect.right		=	viewSelection.right;
			destViewRect.bottom  	=	viewSelection.bottom;


			 //	if(bOutsideSel) SetTile(ty*16+tx,true);
			 //	bDragging=true;
			 if(Shift.Contains(ssRight))ImageTileview->BeginDrag(false,-1);

	}else if(Shift.Contains(ssRight)||(!bOutsideViewSel)){


			viewSelBuf.left		=	viewSelection.left;
			viewSelBuf.top		=	viewSelection.top;
			viewSelBuf.right		=	viewSelection.right;
			viewSelBuf.bottom  	=	viewSelection.bottom;

			destViewRect.left		=	viewSelection.left;
			destViewRect.top		=	viewSelection.top;
			destViewRect.right		=	viewSelection.right;
			destViewRect.bottom  	=	viewSelection.bottom;


			 //	if(bOutsideSel) SetTile(ty*16+tx,true);
			 //	bDragging=true;
			 if(Shift.Contains(ssRight))ImageTileview->BeginDrag(false,-1);


		}
		UpdateUI(true);

}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::ImageTileviewDragDrop(TObject *Sender,
	  TObject *Source, int X, int Y)
{
	bool bView = FormMain->customcharmap1->Checked;
	if(destViewRect.left==viewSelection.left&&destViewRect.top==viewSelection.top) return;
	int tX=X/(8*2);
	int tY=Y/(8*2);
	if(tX<0||tX>=(8*2)||tY<0||tY>=(8*2)) return;

	unsigned char tempID;
	int tile,ps,pd, ba, offset;

	bool bClone = ( bBufCtrl && !bBufShift &&  bBufAlt);
	bool bSwap	= (!bBufCtrl && !bBufShift && !bBufAlt);
	bool bMove	= ( bBufCtrl && !bBufShift && !bBufAlt);
	const int tw=16;   //tileset table width
	int xSource = viewSelection.left;
	int ySource = viewSelection.top;

	int w=1;   //init to single tile
	int h=1;

	if (!bOutsideViewSel) //if grabbed from inside selection, retain size
	{
		w=destViewRect.right-destViewRect.left;
		h=destViewRect.bottom-destViewRect.top;
	}

	tile=destViewRect.top*16+destViewRect.left;
	ps=viewSelection.top*16+viewSelection.left;
	pd=tile;
	//ba=bankActive;
	for(int sy=0; sy<h*tw; sy+=tw) {
		for(int sx=0; sx<w; sx++) {
			if (ySource>=tY) {
				if   (xSource>tX) offset=sx+(sy);
				else 			 offset=(w-1)-sx+(sy);
			}
			else {
				if 	 (xSource>tX) offset= sx+(((h-1)*tw)-(sy));
				else 			  offset= (w-1)-sx + (((h-1)*tw)-(sy));
			}

			//swap
			if(bSwap){

				tempID  =tileViewCustom[pd+offset];
				tileViewCustom[pd+offset]= tileViewCustom[ps+offset];
				tileViewCustom[ps+offset]= tempID;

			}

			//move
			if(bMove){
				tileViewCustom[pd+offset]=tileViewCustom[ps+offset];
				tileViewCustom[ps+offset]=tileViewCustom[nullTile];

			}

			//clone
			if(bClone){
				tileViewCustom[pd+offset]=tileViewCustom[ps+offset];
			}
		}
	}


	viewSelection.top=destViewRect.top;
	viewSelection.left=destViewRect.left;
	viewSelection.bottom=destViewRect.bottom;
	viewSelection.right=destViewRect.right;

	if(bView) {
		for(int i=0;i<256;i++){
			tileViewTable[i]=tileViewCustom[i];
		}
	}
	//viewSelection.right=viewSelection.left+w;  //restore selection width/height (SetTile clobbers it).
	//viewSelection.bottom=viewSelection.top+h;
	FormMain->UpdateAll();



}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::ImageTileviewDragOver(TObject *Sender,
      TObject *Source, int X, int Y, TDragState State, bool &Accept)
{
	  int XC,YC;

	  Accept=false;
	  //cueStats=true;
	  if(X>=0&&X<(128*2)&&Y>=0&&Y<(128*2))
		{
			XC=X/(8*2);
			YC=Y/(8*2);
		}
		
		Accept=true;
		if (Accept==true)
	{
		//bImageNameAccepted=false;
		//bImageTileAccepted=true;
		if (!bOutsideViewSel)
		{
			destViewRect.left	=viewSelection.left		+XC-txViewDown;
			destViewRect.right	=viewSelection.right	+XC-txViewDown;
			destViewRect.top	=viewSelection.top		+YC-tyViewDown;
			destViewRect.bottom	=viewSelection.bottom	+YC-tyViewDown;

			for (int i=0; i<16; i++)  //long enough loop
				{
					if(destViewRect.left<0)   	{	destViewRect.left++;
												destViewRect.right++;}
					if(destViewRect.right>0x10)	{	destViewRect.left--;
												destViewRect.right--;}
					if(destViewRect.top<0)   	{	destViewRect.top++;
												destViewRect.bottom++;}
					if(destViewRect.bottom>0x10){	destViewRect.top--;
												destViewRect.bottom--;}
				}

		}

		else
		{
			destViewRect.left=XC;
			destViewRect.top=YC;
			destViewRect.right=XC+1;
			destViewRect.bottom=YC+1;
		}
		bDrawDestViewShadow=true;
		ImageTileview->Picture->Bitmap->Assign(viewBuf);
		UpdateUI(false);
		//cueUpdateTiles=true;
	}
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::ImageTileviewEndDrag(TObject *Sender,
      TObject *Target, int X, int Y)
{
	bDrawDestViewShadow=false;
	UpdateUI(true);
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::SpeedButton3Click(TObject *Sender)
{
	TPoint p = Mouse->CursorPos;
	int x= p.x;
	int y= p.y;
	PopupMenu1->Popup(x,y);
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::ResetViewContents(int tag)
 {
	int num;
	//reset
	for (int i=0;i<256;i++) {tileViewCustom[i]=i;}

	//8x16 mode
	if(tag==1){
		for(int i=0;i<16;i++)
		{
			num=(i/2)*32+(i&1);
			for(int j=0;j<16;j++)
			{
				tileViewCustom[i*16+j]=num;

				num+=2;
			}
		}
	}
	else if(tag==10) FormMain->SetViewTable_SortFreqency(true);
	else if(tag==11) FormMain->SetViewTable_SortDensity(true);
	else if(tag==12) FormMain->SetViewTable_SortDetail(true);
	else if(tag==13) FormMain->SetViewTable_SortEdgeDetail(true);
	else if(tag==14) FormMain->SetViewTable_SortActiveColour(true);



	else if(tag==20) //4x1 -> 2x2 ; left to right blocks
	{
		FormMain->SetViewTable_Destrip(2,true,true);
	}
	else if(tag==21) //4x1 -> 2x2 ; top down blocks
	{
		FormMain->SetViewTable_Destrip(2,false,true);
	}
	else if(tag==22) //16x1 -> 4x4
	{
		FormMain->SetViewTable_Destrip(4,true,true);
	}

	//normal / default
	else for(int i=0;i<256;i++) {tileViewCustom[i]=i;}

	for(int i=0;i<256;i++) {tileViewTable[i]=tileViewCustom[i];}

	//UpdateMetaSprite();
	FormMain->UpdateTiles(true);
	//cueUpdateMetasprite=true;
	//isLastClickedMetaSprite=true;
	//isLastClickedSpriteList=false;
}
void __fastcall TFormCustomTileview::Normal1Click(TObject *Sender)
{
	int a = ((TMenuItem*)Sender)->Tag;
	ResetViewContents(a);
}
//---------------------------------------------------------------------------
void __fastcall TFormCustomTileview::SaveCharmap(int offset, int size)
{
	unsigned char buf[512];
	FILE *file;
	int i,pp,off;
	AnsiString name;


	if(!SaveDialog1->Execute()) return;

	name=RemoveExt(SaveDialog1->FileName)+".charmap";

	if(!FormMain->OverwritePrompt(name)) return;

	file=fopen(name.c_str(),"rb");

	if(file)
	{
		fseek(file,0,SEEK_END);
		i=ftell(file);
		fclose(file);

		if(size!=i)
		{
			if(Application->MessageBox(("Previous file has different size ("+IntToStr(i)+" bytes)!\nDo you really want to overwrite?").c_str(),"Confirm",MB_YESNO)!=IDYES) return;
		}
	}

	file=fopen(name.c_str(),"wb");

	if(!file) return;
	//for future multimaps.
	if((size==256&&offset==0)||size==1024)
	{
		for(int i=0;i<size;++i)buf[i]=tileViewCustom[i]&0xFF;


	}
	else
	{
		pp=offset;

		for(i=0;i<size;++i)
		{
			if(pp>=256) pp=0;

			buf[i]=tileViewCustom[pp]&0xFF;

			++pp;
		}
	}

	fwrite(buf,size,1,file);
	fclose(file);
}
void __fastcall TFormCustomTileview::SpeedButton2Click(TObject *Sender)
{
	FormMain->BlockDrawing(true);
	SaveCharmap(0,256);
	FormMain->BlockDrawing(false);
}
//---------------------------------------------------------------------------

void __fastcall TFormCustomTileview::SpeedButton1MouseEnter(
      TObject *Sender)
{
	FormMain->LabelStats->Caption="Save it as an external binary .charmap file";
}
//---------------------------------------------------------------------------

void __fastcall TFormCustomTileview::SpeedButton2MouseEnter(
	  TObject *Sender)
{
	FormMain->LabelStats->Caption="Load up an external binary .charmap file";
}
//---------------------------------------------------------------------------

void __fastcall TFormCustomTileview::SpeedButton3MouseEnter(
	  TObject *Sender)
{
	FormMain->LabelStats->Caption="Reset custom view to a boilerplate preset";
}
//---------------------------------------------------------------------------

void __fastcall TFormCustomTileview::RadioPatternsMouseEnter(
	  TObject *Sender)
{
	FormMain->LabelStats->Caption="View the charmap as tile patterns (normally)";
}
//---------------------------------------------------------------------------

void __fastcall TFormCustomTileview::RadioIDsMouseEnter(TObject *Sender)
{
	FormMain->LabelStats->Caption="View the charmap as tile order ID:s";
}
//---------------------------------------------------------------------------

void __fastcall TFormCustomTileview::CheckBox1MouseEnter(TObject *Sender)
{
	FormMain->LabelStats->Caption="Turn mouse peek on off.\nWhile on, the tile you hover over shows the tile ID, or the pattern if in tile ID mode.";
}
//---------------------------------------------------------------------------

void __fastcall TFormCustomTileview::SpeedButton1MouseLeave(
	  TObject *Sender)
{
	FormMain->LabelStats->Caption="---";
}
//---------------------------------------------------------------------------

void __fastcall TFormCustomTileview::ImageTileviewMouseEnter(
	  TObject *Sender)
{
	FormMain->LabelStats->Caption="Right-click and drag to swap tiles.\nShift+left click and drag to make a box selection to swap.";
}
//---------------------------------------------------------------------------

