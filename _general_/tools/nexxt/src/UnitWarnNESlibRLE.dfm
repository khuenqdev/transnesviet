object FormWarnNESlibRLE: TFormWarnNESlibRLE
  Left = 0
  Top = 0
  BorderStyle = bsDialog
  Caption = 'Warning: NESlib RLE compatibility'
  ClientHeight = 214
  ClientWidth = 381
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  Position = poMainFormCenter
  OnClose = FormClose
  OnCreate = FormCreate
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object Button1: TButton
    Left = 298
    Top = 184
    Width = 75
    Height = 25
    Caption = 'OK'
    ModalResult = 1
    TabOrder = 0
  end
  object CheckBox1: TCheckBox
    Left = 150
    Top = 189
    Width = 140
    Height = 17
    Caption = 'Do not remind me again'
    TabOrder = 1
  end
  object StaticText1: TStaticText
    Left = 24
    Top = 20
    Width = 330
    Height = 150
    Margins.Left = 12
    Margins.Right = 12
    AutoSize = False
    Caption = 'StaticText1'
    TabOrder = 2
  end
end
