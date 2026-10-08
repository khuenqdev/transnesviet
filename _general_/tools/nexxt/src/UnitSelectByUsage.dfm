object FormSelectByUsage: TFormSelectByUsage
  Left = 0
  Top = 0
  BorderStyle = bsToolWindow
  Caption = 'Tile Finder (usage)'
  ClientHeight = 71
  ClientWidth = 300
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -11
  Font.Name = 'Tahoma'
  Font.Style = []
  OldCreateOrder = False
  OnCreate = FormCreate
  OnShow = FormShow
  PixelsPerInch = 96
  TextHeight = 13
  object SpeedButton1: TSpeedButton
    Left = 212
    Top = 50
    Width = 79
    Height = 18
    Caption = 'Deselect'
    OnClick = SpeedButton1Click
  end
  object Label1: TLabel
    Left = 8
    Top = 50
    Width = 51
    Height = 13
    Caption = 'Threshold:'
  end
  object Label2: TLabel
    Left = 80
    Top = 50
    Width = 6
    Height = 13
    Caption = '0'
  end
  object TrackBar1: TTrackBar
    Left = 0
    Top = 8
    Width = 300
    Height = 36
    Max = 63
    TabOrder = 0
    TabStop = False
    OnChange = TrackBar1Change
  end
  object CheckBox1: TCheckBox
    Left = 116
    Top = 50
    Width = 86
    Height = 17
    TabStop = False
    Caption = 'Has contents'
    Checked = True
    State = cbChecked
    TabOrder = 1
    OnClick = TrackBar1Change
  end
end
